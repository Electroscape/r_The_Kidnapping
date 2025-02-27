import argparse
import json
import logging
import os
import pygame
from pygame.locals import *
try:
    import RPi.GPIO as GPIO
except ImportError:
    import Mock.GPIO as GPIO
from time import sleep
import subprocess
from threading import Thread
from pathlib import Path
from datetime import datetime as dt, timedelta
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

root_path = Path(os.getcwd())
print(f"root path of the script: {root_path}")
sound_path = root_path.joinpath("sounds")

# os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "x11"

GPIO.setmode(GPIO.BOARD)


logging.basicConfig(
    filename='log.log',
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{'
)

config = None
argparser = argparse.ArgumentParser(description='Telephone')
argparser.add_argument('-c', '--city', default='st', help='name of the city: [hh / st]')

location = argparser.parse_args().city

dialed_numbers = []


class Telephone:
    def __init__(self, _location):
        cfg = self.__get_cfg()
        self.__init_pygame()
        self.number_dialed = ""
        # currently not used, but hard to see
        self.max_digits = 12
        self.sound_end_time = False
        try:
            self.contacts = cfg["contacts"]
            self.language = "deu/"
            self.dial_delay = 1.5
            self.location = _location
            # set to board, board 12 is GPIO 18
            self.phone_pin = cfg["PIN"][_location]["PHONE_switch_pin"]
            GPIO.setup(self.phone_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.last_keypress = dt.now()
            self.checking_number = False
            self.loop = Thread(target=self.main_loop, daemon=True)
            self.loop.start()

        except KeyError as er:
            logging.error(er)

    @staticmethod
    def __get_cfg():
        try:
            with open('config.json', 'r') as config_file:
                return json.load(config_file)
        except (FileNotFoundError, ValueError) as err:
            logging.error(f"failed to fetch config file {err}")
            exit(f"failed to fetch config file {err}")

    @staticmethod
    def __init_pygame():
        pygame.init()
        screen = pygame.display.set_mode((800, 600))  # Virtual screen
        pygame.mixer.set_num_channels(8)

        pygame.mixer.music.load(sound_path.joinpath("013_freizeichen_30min.wav"))
        pygame.mixer.music.play(-1, 0.0)
        # number must be smaller than 1
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.pause()
        logging.info("pygame init done")

    @staticmethod
    def set_sound(sound_file):
        effect = pygame.mixer.Sound(sound_file)
        channel = pygame.mixer.Channel(1)
        channel.play(effect)
        sleep(0.1)
        return effect.get_length()

    def play_sound(self, sound_file, dialing=False):
        print(sound_file)

        self.pause_current_sound()
        duration = self.set_sound(sound_file)

        if dialing:
            return
        print(f"Sound duration is: {duration:.2f} seconds")
        print(dt.now())
        self.sound_end_time = dt.now() + timedelta(seconds=duration)

    def set_german(self, is_german):
        if is_german:
            self.language = "/deu"
        else:
            self.language = "/eng"

    @staticmethod
    def pause_current_sound():
        logging.info("Pausing all sounds")
        pygame.mixer.stop()  # Stops all channels
        pygame.mixer.music.stop()

    def check_number(self):
        print("checkNumber")
        global dialed_numbers

        sound_file = self.contacts.get(self.number_dialed, False)
        if sound_file:
            self.play_sound(sound_path.joinpath("014_wahl&rufzeichen.wav"))
            self.play_sound(sound_path.joinpath(self.language + sound_file))
            dialed_numbers.append(sound_file)
        else:
            self.play_sound(sound_path.joinpath("dialedWrongNumber.wav"))
            dialed_numbers.append(self.number_dialed)
        self.play_sound(sound_path.joinpath("beepSound.wav"))
        self.reset_dialing()
        dialed_numbers = dialed_numbers[-5:]

    def reset_dialing(self):
        self.number_dialed = ""
        send_number("")

    def digit_dialed(self, event):
        print(f"keyevent: {event} with eventkey {event.key}")
        self.pause_current_sound()

        # key 48 is 0, 49 and so on, so ....
        # technically things like pygame.K_1 is available, just kept it similar
        digit = event.key - 48
        if digit > 9 or digit < 0:
            print(f"unkown eventkey received: {event.key}")
            return

        self.number_dialed += f"{digit}"
        send_number(self.number_dialed)
        print("number dialed is " + self.number_dialed)

        self.play_sound(sound_path.joinpath(f"{digit}.wav"), dialing=True)
        return

    def main_loop(self):
        logging.info("mainloop")

        while True:
            try:
                if not GPIO.input(self.phone_pin):
                    self.number_dialed = ""
                    pygame.mixer.music.pause()
                    pygame.event.clear()
                    self.checking_number = False  # Reset flag when phone is put down
                    continue

                print(f"{self.sound_end_time} vs {dt.now()}")
                if self.sound_end_time and self.sound_end_time > dt.now():
                    self.pause_current_sound()
                    self.sound_end_time = False
                    print("ended sound")

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        logging.info(f"Key pressed: {event.key}")
                        self.last_keypress = dt.now()
                        self.digit_dialed(event)
                        self.checking_number = False  # Reset flag when a new key is pressed

                if not self.number_dialed:
                    pygame.mixer.music.unpause()
                elif (dt.now() - self.last_keypress).total_seconds() > self.dial_delay and not self.checking_number:
                    self.checking_number = True  # Set flag to prevent multiple calls
                    self.check_number()
            except Exception as exp:
                logging.error(exp)

            sleep(0.1)


@app.route("/set-language", methods=["POST"])
def set_language():
    data = request.get_json()
    if "language" in data:
        selected_language = data["language"]
        phone.set_german(selected_language == "de")
        print(f"Language changed to: {selected_language}")
        return jsonify({"message": "Language updated", "language": selected_language}), 200
    return jsonify({"error": "Invalid request"}), 400


def send_number(number):
    print(f"Emitting number: {number}")
    try:
        socketio.emit("update_number", number)
    except Exception as exp:
        logging.error(exp)


@app.route("/get-history")
def get_history():
    return jsonify({"history": dialed_numbers})


# Web route to render the frontend
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


def main():
    global phone
    phone = Telephone(location)
    logging.info("Telephone app is running")
    phone.play_sound(sound_path.joinpath("014_wahl&rufzeichen.wav"))
    socketio.run(app, debug=True, host='0.0.0.0', port=5500)


if __name__ == '__main__':
    main()
