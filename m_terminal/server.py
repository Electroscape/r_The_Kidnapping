import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
import json
import logging
from datetime import datetime as dt
from datetime import timedelta

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

startTime = False
start_time_file = "startTime.txt"
date_format = "%Y-%m-%d %H:%M:%S"


def save_start_time():
    try:
        f = open(start_time_file, "w+")
        if startTime:
            print("writing")
            f.write(startTime.strftime(date_format))
    except OSError as err:
        print(err)
        logging.error("failed to write startime file")
        pass

def get_start_time() -> bool:
    try:
        f = open(start_time_file, "r")
        saved_time = f.read()
        try:
            saved_time = dt.strptime(saved_time, date_format)
            global startTime
            startTime = saved_time
        except valueError as err:
            print(err)
            return False
    except OSError:
        return False

    return True

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

    if startTime:
        config["startTime"] = startTime.timestamp()
    else:
        config["startTime"] = "false"   # prefer doing things on python rather than JS

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

    # broadcast chat message
    sio.emit('response_to_terminals', json_msg)
    # send it to frontend
    frontend_server_messages(json_msg)

def trigger_timer():
    new_time = dt.now()
    logging.debug("starttime event rcvd")
    global startTime
    global loading_percent
    if not startTime or (new_time - startTime > timedelta(minutes=4)):
        logging.debug("starttime set")
        loading_percent = 100
        sio.emit("response_to_fe", {"username": "tr1", "cmd": "startTimer"})
        startTime = new_time
        save_start_time()


@sio.on('triggers')
def override_triggers(msg):
    # Display message on frontend chatbox
    frontend_server_messages(msg)
    # print in console for debugging
    logging.info(f"msg to arb pi: sio.on('trigger', {str(msg)})")
    msg_value = msg.get("message")
    cmd = msg.get("cmd")
    if msg_value == "start" and cmd == "game":
        trigger_timer()
    sio.emit("trigger", msg)



@sio.on('events')
def events_handler(msg):
    global login_users
    logging.error(f"from events: {msg}")
    username = msg.get("username")
    cmd = msg.get("cmd")
    msg_value = msg.get("message")

    # print(f"sio events handling: {msg}")

    if msg_value == "start" and cmd == "game":
        trigger_timer()

    if username == "server":
        if cmd == "reset":
            sio.emit("samples", {"flag": "unsolved"})  # to reset the flag
    else:
        '''
        if cmd == "auth":
            login_users[msg.get("username")] = msg.get("message")
            if msg.get("username") == "tr2" and msg.get("message") == "rachel":
                sio.emit("to_clients", {"username": "tr1", "cmd": "personalR", "message": "show"})
        '''
        # is this needed?
        sio.emit("to_clients", msg)

    frontend_server_messages(msg)


if __name__ == "__main__":
    get_start_time()
    sio.run(app, debug=True, host='0.0.0.0', port=5500, engineio_logger=True)
    # app.run(debug=True, host='0.0.0.0', port=5500)
