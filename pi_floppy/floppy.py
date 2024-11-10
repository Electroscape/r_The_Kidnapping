from flask import Flask, render_template, send_from_directory, request, abort
from flask_socketio import SocketIO
import socketio

from rfid import RFID

import logging
import json

# Open and read the JSON file
with open('config.json', 'r') as file:
    config_data = json.load(file)


logging.basicConfig(filename='floppy.log', level=logging.INFO,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'EscapeTerminal#'

# Standard socketio lib to communicate between rpis
sio = socketio.Client()
# floppy_ip = config_data["ip"]["floppy"]

# Flask socket to communicate between backend and frontend
self_sio = SocketIO(app, cors_allowed_origins="*")

# Global dictionary to hold content for each display
display_content = {
    "lcd-1": "default_image1.jpg",
    "lcd-2": "default_image2.jpg",
    "lcd-3": "default_image3.jpg"
}

cards = {
    "1": "Triangle.webm",
    "2": "Circle.webm",
    "3": "Hexagon.webm",
    "4": "Dot.webm",
    "5": "Killswitch.webm",
    "0": "scan"
}

valid_cards = list(cards.keys())
for c in valid_cards:
    cards[c] = f"static/media/floppy/PD_{cards[c]}"

@app.route("/", methods=["GET", "POST"])
def index():
    content = json.dumps(nfc_reader.get_data())
    return render_template("m_floppy.html", cards=cards, floppy=content)

@app.route('/lcd-<int:number>')
def lcd(number):
    if number < 1 or number > 3:
        abort(404)  # Return a 404 error for invalid display numbers

    lcd_key = f'lcd-{number}'
    content = display_content[lcd_key]
    return render_template('display.html', content=content)

@app.route('/update', methods=['POST'])
def update_content():
    res_dict = nfc_reader.get_data()

    data = request.json
    for lcd, content in data.items():
        if lcd in display_content:
            display_content[lcd] = content

    send_data = {
        "status": "success", 
        "show": cards[res_dict["data"]],
        "updated": display_content}
    print(send_data)
    return send_data


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
            self_sio.emit("floppy_fe", prev_data)
            logging.debug(f"emitting update {prev_data}")
            logging.info(f"sent: {prev_data}")


# polling updates if server is offline
self_sio.start_background_task(check_for_updates)

if __name__ == "__main__":
    self_sio.run(app, debug=True, host='0.0.0.0', port=5666)
