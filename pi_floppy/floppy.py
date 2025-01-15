from flask import Flask, jsonify, redirect, render_template, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import socket
import eventlet
import threading
import subprocess

from rfid import RFID

import logging
import json

# Open and read the JSON file
with open('config.json', 'r') as json_file:
    cfg = json.loads(json_file.read())
    LCD_PORT = cfg["lcds_port"]
    SERVER_PORT = cfg["server_port"]
    DISPLAY_IPS = {
        key: value for key, value in cfg["ip"].items() if key.startswith('lcd')
    }
    FLOPPY_PI = cfg["ip"]["floppy"]


logging.basicConfig(filename='floppy.log', level=logging.INFO,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'EscapeTerminal#'
CORS(app)  # Enable CORS for all routes
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

# Start with mc not booted
mc_boot = False
# Global rfid data value
rfid_data = {"data": "0"}

print("creating RFID instance")
nfc_reader = RFID(cards=valid_cards)

# Function to send command to a specific display RPi
def send_command(rpi_name, command):
    # If not booted,, no commands
    if not mc_boot:
        return False
    
    rpi_ip = DISPLAY_IPS[rpi_name]
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((rpi_ip, LCD_PORT))
            client_socket.sendall(command.encode('utf-8'))
            print(f"Sent command to {rpi_name} ({rpi_ip}): {command}")
    except Exception as e:
        print(f"Failed to send command to {rpi_name} ({rpi_ip}): {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    if not mc_boot:
        return redirect("/boot")

    content = json.dumps(nfc_reader.get_data())
    return render_template("m_floppy.html", cards=cards, floppy=content)


@app.route('/boot', methods=['GET', 'POST'])
def pre_entry_point():
    return render_template("no_boot.html")

# API route to check if the mc_boot is activated
@app.route('/check_boot_trigger', methods=['GET'])
def check_boot_trigger():
    return jsonify({'mc_boot': mc_boot})


# API route to check if the rfid data is activated
@app.route('/check_rfid_data', methods=['GET'])
def check_rfid_trigger():
    return jsonify(rfid_data)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

@self_sio.event
def connect():
    logging.info("Self is connected!")


@self_sio.on("msg_to_backend")
def on_msg(data):
    logging.info(f"from frontend: {data} -> forward to server")
    # TODO: here I emit to arbiter
    # Manual override
    # Check if data is a not string
    if not isinstance(data, str):
        print(f"data not str: {data}")
        return
    
    process_command(data)

# Function to execute the received command
def execute_command(command: str) -> None:
    try:
        if command == "zwinger":
            # Run script
            subprocess.Popen(["bash", f"play_{command}.sh"])

    except Exception as e:
        print(f"Error executing command: {e}")


def check_for_updates():
    global rfid_data
    prev_data = nfc_reader.get_data().copy()
    while True:
        # self_sio.sleep(2)
        # while not nfc_reader.connected:
        # print(f"in polling mode {prev_data}")

        if prev_data != nfc_reader.get_data():
            prev_data = nfc_reader.get_data().copy()
            logging.info("updates to frontend from polling")
            # Update displays
            lcd = prev_data.get("data")
            print(f"Card changed, updating LCDs: {lcd}")
            if lcd and lcd == "0":
                for display in DISPLAY_IPS:
                    send_command(display, "play_idle")
            else:
                send_command(f"lcd-{lcd}", "play_solution")

            # Update frontend
            self_sio.emit("floppy_fe", prev_data)
            rfid_data = prev_data
            logging.debug(f"emitting update {prev_data}")
            logging.info(f"sent: {prev_data}")


def process_command(data: str) -> None:
    global mc_boot
    global rfid_data

    data = data.strip()
    rfid_data = {"data": data}

    if data == "0":
        print(f"frontend on scan tab")
    elif data == 'idle':
        mc_boot = True
        for display in DISPLAY_IPS:
            send_command(display, "play_idle")

    elif data == 'reset':
        for display in DISPLAY_IPS:
            send_command(display, "play_blackscreen")
        mc_boot = False

    elif data == 'zwinger':
        execute_command(data)

    elif data in valid_cards:
        print(f"data is valid card: {data}")
        # for display in DISPLAY_IPS:
        #     send_command(display, "play_idle")
        send_command(f"lcd-{data}", "play_solution")
    # sio.emit("msg_to_server", data)

# Function to run the Flask Socket.IO server
def run_flask():
    self_sio.run(app, debug=False, host="0.0.0.0", port=5666)

# Create the Eventlet TCP server
def handle_client(client_socket, client_address):
    """Handle each client connection."""
    print(f"Client connected: {client_address}")
    
    try:
        while True:
            # Receive raw data (max 1024 bytes per chunk)
            data = client_socket.recv(1024)
            if not data:
                break  # If no data, close the connection
            # Print received data (decoded from bytes to string)
            data_str = data.decode('utf-8')
            print(f"Received data: {data_str}")
            process_command(data_str)

    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        print(f"Closing connection with {client_address}")
        client_socket.close()

# Main server function
def start_server():
    # Create the listener socket using eventlet.listen
    server_socket = eventlet.listen(('0.0.0.0', SERVER_PORT))

    print(f"Server listening on port {SERVER_PORT}...")
    
    # Use eventlet's green socket for concurrency
    while True:
        # Accept incoming client connection
        client_socket, client_address = server_socket.accept()
        # Handle the client in a new green thread
        eventlet.spawn_n(handle_client, client_socket, client_address)


# Main entry point
if __name__ == "__main__":
    # Create threads for servers
    eventlet_thread = threading.Thread(target=start_server)
    rfid_thread = threading.Thread(target=check_for_updates)
    flask_thread = threading.Thread(target=run_flask)

    # Start threads
    eventlet_thread.start()
    flask_thread.start()
    rfid_thread.start()

    # Wait for threads to finish
    flask_thread.join()
    eventlet_thread.join()
    rfid_thread.join()
