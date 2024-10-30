from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
import socketio

from rfid import RFID

import logging

logging.basicConfig(filename='floppy.log', level=logging.INFO,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'EscapeTerminal#'

# standard Python
sio = socketio.Client()
server_ip = "http://raspi-4-pod-t1:5500"  # <= change server ip here
self_sio = SocketIO(app, cors_allowed_origins="*")

cards = {
    "1": "Triangle.webm",
    "2": "Circle.webm",
    "3": "Hexagon.webm",
    "4": "Dot.webm",
    "5": "Killswitch.webm",
    "0": "0.webm"
}

valid_cards = list(cards.keys())
for c in valid_cards:
    cards[c] = f"static/media/floppy/PD_{cards[c]}"


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("m_floppy.html", cards=cards, floppy=get_status())


@app.route("/get_status", methods=["GET", "POST"])
def get_status():
    res_dict = nfc_reader.get_data()
    return {
        "show": cards[res_dict["data"]],
        "status": res_dict["status"]
    }


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


@sio.on("rfid_event")
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
    # sio.emit("msg_to_server", data)


print("creating RFID instance")
nfc_reader = RFID(server_ip=server_ip, cards=valid_cards)


def check_for_updates():
    prev_data = nfc_reader.get_data().copy()
    while True:
        # self_sio.sleep(2)
        # while not nfc_reader.connected:
        # print(f"in polling mode {prev_data}")

        if prev_data != nfc_reader.get_data():
            prev_data = nfc_reader.get_data().copy()
            logging.info("updates to frontend from polling")
            self_sio.emit("floppy_fe", prev_data)
            logging.debug(f"emitting update {prev_data}")
            logging.info(f"sent: {prev_data}")


'''
while not sio.connected:
    try:
        sio.connect(server_ip)
    except Exception as exp:
        logging.debug(f"re-try connect to server: {server_ip}")
        logging.debug(exp)
'''


# polling updates if server is offline
self_sio.start_background_task(check_for_updates)

if __name__ == "__main__":
    self_sio.run(app, debug=True, host='0.0.0.0', port=5555)
