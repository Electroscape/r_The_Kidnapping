import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
import json
import logging
from datetime import datetime as dt

# Next two lines are for the issue: https://github.com/miguelgrinberg/python-engineio/issues/142
from engineio.payload import Payload

Payload.max_decode_packets = 200

from ring_list import RingList

chat_history = RingList(300)
chat_history.append('Welcome to the server window')

now = dt.now()
log_name = now.strftime("logs/server %m_%d_%Y  %H_%M_%S.log")
logging.basicConfig(filename=log_name, level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


def read_json(filename: str, from_static=True) -> dict:
    """
    json read function is used to get the json data from a file and load it to a dict

    :param from_static: (bool) fetch the file from static folder
    :param filename: json file name inside static folder
    :return: dict
    """
    if from_static:
        filename = f"static/{filename}"

    try:
        with open(filename, "r") as f_in:
            json_data = json.load(f_in)
        return json_data

    except IOError:
        print(f"folder '{filename}' not found")
        return {}


samples = read_json("json/samples.json")
sample_icons = {
    "blocked": "fa-solid fa-ban",
    "locked": "fas fa-lock",
    "unlocked": "fas fa-lock-open",
    "released": "fa-solid fa-check"
}
login_users = {
    "tr1": "empty",
    "tr2": "empty"
}

version = read_json("json/ver_config.json").get("server", {})
hint_msgs = read_json("json/hints.json")
loading_percent = 0

app = Flask(__name__)
app.config['SECRET_KEY'] = 'EscapeTerminal#'

ip_conf = read_json(f"ip_config.json", from_static=False)

ip_conf = [f"http://{ip}" for ip in ip_conf.values() if isinstance(ip, str)]
all_cors = ip_conf + ['*']

#  engineio_logger=True, for really detailed logs
sio = SocketIO(app, ping_timeout=120, ping_interval=20)


class StatusVars:
    def __init__(self):
        self.uploadProgress = "disable"
        self.laserlock_cable = "broken"


game_status = StatusVars()


@app.route("/", methods=["GET", "POST"])
def index():
    config = {
        "title": "Server Terminal",
        "id": "server",
        "lang": "en",
        "version": version
    }
    # ip_address = request.remote_addr
    # logging.info("Requester IP: " + ip_address)
    return render_template("server_home.html", g_config=config, chat_msg=chat_history.get(), hint_msgs=hint_msgs)


@app.route("/get_globals", methods=["GET", "POST"])
def get_globals():
    return {}


@app.route('/get_chat', methods=['GET', 'POST'])
def get_chat():
    return chat_history.get()


@app.route("/get_progress", methods=["GET", "POST"])
def get_progress():
    return {"percent": loading_percent}


@sio.on("connect")
def on_connect():
    logging.info("New socket connected")


@sio.on("disconnect")
def vid_on_disconnect():
    sid = "request.sid"
    display_name = "display name here"

    logging.debug("Member left: {}<{}>".format(display_name, sid))

    sio.emit('response_to_fe', {
        "update": f"user {sid} left"
    })


def frontend_server_messages(json_msg):
    if json_msg.get("update"):
        return
    chat_history.append(json_msg)
    sio.emit('response_to_fe', json_msg)


@sio.on('msg_to_server')
def handle_received_messages(json_msg):
    logging.info('server received message: ' + str(json_msg))
    if json_msg.get("keypad_update"):
        global samples
        # "gas_control keypad 0 wrong"
        page, _, num, status = json_msg.get("keypad_update").split()
        if page.startswith("/gas_control"):
            if status == "correct":
                samples[int(num)]["status"] = "unlocked"
                samples[int(num)]["icon"] = sample_icons["unlocked"]
                sio.emit("samples", samples)
                sio.emit("samples", f"sample {int(num) + 1} {samples[int(num)]['status']}")
            else:
                # TODO emit message for wrong trials?
                print("gas control wrong trial")

        elif page.startswith("/gas_analysis"):
            if status == "correct":
                samples[int(num)]["status"] = "released"
                samples[int(num)]["icon"] = sample_icons["released"]
            trigger_msg = {
                "username": "arb",
                "cmd": "dispenser",
                "message": "dishout"
            }
            sio.emit("trigger", trigger_msg)
            # should I add ~5 sec delay here?
            # after trigger msg and before sending the samples updates msg
            # for the physical world to take place.
            if all_samples_solved():
                sio.emit("samples", {"flag": "done"})
            else:
                # unblock next sample
                samples[int(num) + 1]["status"] = "locked"
                samples[int(num) + 1]["icon"] = sample_icons["locked"]

            sio.emit("samples", samples)
            sio.emit("samples", f"sample {int(num) + 1} {samples[int(num)]['status']}")

    elif json_msg.get("levels") and "correct" in str(json_msg):
        sio.emit("to_clients", {
            "username": "tr2",
            "cmd": "elancell",
            "message": "solved"
        })
    elif "/lab_control" in str(json_msg):
        logging.info("access to laser-lock requested")
        print(f"access to laser-lock requested, gamestatus is: {game_status.laserlock_cable}")
        # access the laserlock lab
        if game_status.laserlock_cable == "broken":
            sio.emit("trigger", {"username": "arb", "cmd": "laserlock", "message": "fail"})
        else:
            sio.emit("trigger", {"username": "arb", "cmd": "laserlock", "message": "access"})
    elif json_msg.get("cmd") == "cleanroom":
        logging.info(f"cleanroom status: {json_msg.get('message')}")
        # access the cleanroom
        sio.emit("trigger", {"username": "arb", "cmd": "cleanroom", "message": json_msg.get("message")})
        # also update TR2
        sio.emit("to_clients", {"username": "tr2", "cmd": "cleanroom", "message": json_msg.get("message")})
    elif json_msg.get("cmd") == "upload":
        msg = json_msg.get("message")
        if msg in ["elancell", "rachel"]:
            sio.emit("trigger", {"username": "arb", "cmd": "upload", "message": msg})
    else:
        # broadcast chat message
        sio.emit('response_to_terminals', json_msg)
    # send it to frontend
    frontend_server_messages(json_msg)


@sio.on('triggers')
def override_triggers(msg):
    # Display message on frontend chatbox
    frontend_server_messages(msg)
    # print in console for debugging
    logging.info(f"msg to arb pi: sio.on('trigger', {str(msg)})")
    # emit message on "trigger" channel for the arb RPi
    # Therefore listener on the arb Pi is @sio.on("trigger")
    sio.emit("trigger", msg)


@sio.on('events')
def events_handler(msg):
    global login_users
    username = msg.get("username")
    cmd = msg.get("cmd")
    msg_value = msg.get("message")

    # print(f"sio events handling: {msg}")

    if username == "server":
        global samples
        global loading_percent

        if cmd == "loadingbar":
            loading_percent = int(msg.get("message"))
            sio.emit("to_clients", {"username": "tr1", "cmd": "loadingbar", "message": loading_percent})
            sio.emit("to_clients", {"username": "tr2", "cmd": "loadingbar", "message": loading_percent})
        elif cmd == "reset":
            samples = read_json("json/samples.json")
            sio.emit("samples", samples)
            sio.emit("samples", {"flag": "unsolved"})  # to reset the flag
            if msg_value == "resetAll":
                logging.info("Server: Reset all")
                # reset global variables
                login_users = {
                    "tr1": "empty",
                    "tr2": "empty"
                }
                # emit default state messages to terminals
                sio.emit("to_clients", {"username": "tr1", "cmd": "auth", "message": "empty"})
                sio.emit("to_clients", {"username": "tr2", "cmd": "auth", "message": "empty"})
                sio.emit("to_clients", {"username": "tr1", "cmd": "usbBoot", "message": "disconnect"})
                sio.emit("to_clients", {"username": "tr1", "cmd": "laserlock", "message": "broken"})
                game_status.laserlock_cable = "broken"
                sio.emit("to_clients", {"username": "tr1", "cmd": "laserlock_auth", "message": "normal"})
                sio.emit("to_clients", {"username": "tr2", "cmd": "mSwitch", "message": "off"})
                sio.emit("to_clients", {"username": "tr2", "cmd": "elancell", "message": "disable"})
                sio.emit("to_clients", {"username": "tr2", "cmd": "microscope", "message": "0"})
                sio.emit("to_clients", {"username": "tr2", "cmd": "cleanroom", "message": "lock"})
                sio.emit("to_clients", {"username": "tr2", "cmd": "breach", "message": "secure"})
                sio.emit("to_clients", {"username": "tr1", "cmd": "personalR", "message": "hide"})
    else:
        if cmd == "auth":
            login_users[msg.get("username")] = msg.get("message")
            if msg.get("username") == "tr2" and msg.get("message") == "rachel":
                sio.emit("to_clients", {"username": "tr1", "cmd": "personalR", "message": "show"})
        elif cmd == "usbBoot" and username == "tr1":
            loading_percent = 90
            # reset laserlock status on boot event
            sio.emit("to_clients", {"username": "tr1", "cmd": "laserlock_auth", "message": "normal"})
        elif cmd == "laserlock":
            print(msg)
            if msg_value in ["broken", "fixed"]:
                game_status.laserlock_cable = msg_value
            # dict_cmd = {"username": "arb", "cmd": "laserlock", "message": msg_value}
            # send cable override to arbiter
            # logging.info(f"msg to arbiter: {str(dict_cmd)}")
            # sio.emit("trigger", dict_cmd)

        sio.emit("to_clients", msg)
    frontend_server_messages(msg)


def loadingbar_timer():
    global loading_percent

    while True:
        # only starts after booting
        if loading_percent > 0:
            sio.emit("to_clients", {"username": "tr1", "cmd": "loadingbar", "message": loading_percent})
            sio.emit("to_clients", {"username": "tr2", "cmd": "loadingbar", "message": loading_percent})
            frontend_server_messages({"username": "tr1/tr2", "cmd": "loadingbar", "message": loading_percent})
            # 90 min / 20 loading bars = 4.5 min = 270 seconds
            # remove 1 progress bar every 270 seconds
            sio.sleep(int(60 * 4.5))
            loading_percent -= 5


progressbar_task = sio.start_background_task(loadingbar_timer)


if __name__ == "__main__":
    sio.run(app, debug=True, host='0.0.0.0', port=5500, engineio_logger=True)
    # app.run(debug=True, host='0.0.0.0', port=5500)
