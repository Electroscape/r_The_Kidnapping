from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
import socket
import socketio

from rfid import RFID

import logging
import json

# Open and read the JSON file
with open('config.json', 'r') as json_file:
    cfg = json.loads(json_file.read())
    PORT = cfg["port"]
    DISPLAY_IPS = {
        key: value for key, value in cfg["ip"].items() if key.startswith('lcd')
    }
    FLOPPY_PI = cfg["ip"]["floppy"]


logging.basicConfig(filename='floppy.log', level=logging.INFO,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'EscapeTerminal#'

# Standard socketio lib to communicate between rpis
sio = socketio.Client()

# Flask socket to communicate between backend and frontend
self_sio = SocketIO(app, cors_allowed_origins="*")

cards = {
    "1": "1.png",
    "2": "2.png",
    "3": "3.png",
    "0": "scan"
}

valid_cards = list(cards.keys())
for c in valid_cards:
    cards[c] = f"static/blueprints/plan_{cards[c]}"


# Function to send command to a specific display RPi
def send_command(rpi_name, command):
    rpi_ip = DISPLAY_IPS[rpi_name]
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((rpi_ip, PORT))
            client_socket.sendall(command.encode('utf-8'))
            print(f"Sent command to {rpi_name} ({rpi_ip}): {command}")
    except Exception as e:
        print(f"Failed to send command to {rpi_name} ({rpi_ip}): {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    content = json.dumps(nfc_reader.get_data())
    return render_template("m_floppy.html", cards=cards, floppy=content)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@sio.event
def connect():
    print("Connected to Server!")


@sio.event
def disconnect():
    logging.info("floppy is disconnected from server")


# Here I receive updates on socket
@sio.on("floppy_event")
def rfid_updates(data):
    logging.debug(f"RFID EVENT: {data}")
    logging.info(f"rfid message: {data}")
    if data.get("cmd") == "status":
        data["status"] = data["message"]
        nfc_reader.set_rfid_status(data["message"])
    elif data.get("cmd") == "sample":
        data["data"] = data["message"]
        nfc_reader.set_rfid_data(data["message"])

    self_sio.emit("floppy_fe", nfc_reader.get_data())


@self_sio.event
def connect():
    logging.info("Self is connected!")


@self_sio.on("msg_to_backend")
def on_msg(data):
    logging.info(f"from frontend: {data} -> forward to server")
    # TODO: here I emit to arbiter
    # sio.emit("msg_to_server", data)


print("creating RFID instance")
nfc_reader = RFID(cards=valid_cards)


def check_for_updates():
    prev_data = nfc_reader.get_data().copy()
    while True:
        # self_sio.sleep(2)
        # while not nfc_reader.connected:
        # print(f"in polling mode {prev_data}")

        if prev_data != nfc_reader.get_data():
            prev_data = nfc_reader.get_data().copy()
            logging.info("updates to frontend from polling")
            # Update frontend
            self_sio.emit("floppy_fe", prev_data)

            # Update displays
            # TODO: choose display here
            lcd = prev_data.get("data")
            if lcd and lcd == "0":
                for dispaly in DISPLAY_IPS:
                    send_command(dispaly, "play_idle")
            else:
                send_command(f"lcd-{lcd}", "play_solution")

            logging.debug(f"emitting update {prev_data}")
            logging.info(f"sent: {prev_data}")


# polling updates if server is offline
self_sio.start_background_task(check_for_updates)

if __name__ == "__main__":
    self_sio.run(app, debug=True, host='0.0.0.0', port=5666)
