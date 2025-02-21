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

print(f"Current working directory of the script: {os.path.realpath(os.path.dirname(__file__))}")
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

logging.info("This is a test log.")
argparser = argparse.ArgumentParser(
    description='Telephone')

argparser.add_argument(
    '-c',
    '--city',
    default='st',
    help='name of the city: [hh / st]'
)
location = argparser.parse_args().city


class Telephone:
    def __init__(self, _location):
        cfg = self.__get_cfg()
        self.__init_pygame()
        self.number_dialed = ""
        # currently not used, but hard to see
        self.max_digits = 12

        try:
            self.contacts = cfg["contacts"]
            self.sound_path = cfg["PATH"]["sounds"]
            self.language = "deu/"
            self.location = _location
            # set to board, board 12 is GPIO 18
            self.phone_pin = cfg["PIN"][_location]["PHONE_switch_pin"]
            GPIO.setup(self.phone_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.last_keypress = dt.now()
            self.loop = Thread(target=self.main_loop, daemon=True)
            self.loop.start()

        except KeyError as er:
            exit(er)

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

    def set_sound(self):
        effect = pygame.mixer.Sound(self.sound_path)
        empty_channel = pygame.mixer.Channel(1)
        empty_channel.play(effect)
        return effect.get_length()

    def play_sound(self, do_exit=False):
        self.pause_current_sound()
        logging.info(f"Playing voice record {self.sound_path}")
        duration = self.set_sound()
        start_time = dt.now()
        while pygame.mixer.music.get_busy() and (start_time - dt.now()).seconds < duration:
            if GPIO.input(self.phone_pin):
                self.pause_current_sound()
                return
            else:
                continue

    @staticmethod
    def pause_current_sound():
        logging.info("Pausing current sound")
        pygame.mixer.music.pause()
        empty_channel = pygame.mixer.Channel(1)
        empty_channel.stop()

    def check_number(self):
        print("checkNumber")
        sleep(0.5)

        sound_file = self.contacts.get(self.number_dialed, False)
        if sound_file:

            self.play_sound(self.sound_path.joinpath(self.language + sound_file))

        else:
            self.play_sound(self.sound_path.joinpath("dialedWrongNumber.wav"), do_exit=True)

    def reset_dialing(self):
        self.number_dialed = ""

    def digit_dialed(self, event):
        print(f"keyevent: {event} with eventkey {event.key}")
        self.pause_current_sound()
        empty_channel = pygame.mixer.Channel(1)

        # key 48 is 0, 49 and so on, so ....
        # technically things like pygame.K_1 is available, just kept it similar
        digit = event.key - 48
        if digit > 9 or digit < 0:
            print(f"unkown eventkey received: {event.key}")
            return

        self.number_dialed += f"{digit}"

        try:
            effect = pygame.mixer.Sound(sound_path.joinpath(f"{digit}.wav"))
        except Exception as exp:
            print(exp)
            return
        # @todo: maybe remove the checkNumber depending on the wanted use of the #/OK key but return has to stay

        print("number dialed is " + self.number_dialed)

        # @Todo: send number update on socket/website
        empty_channel.play(effect)
        pygame.time.delay(100)

    def main_loop(self):
        logging.info("mainloop")

        while True:
            # phone put down, resetting
            if not GPIO.input(self.phone_pin):
                self.number_dialed = ""
                pygame.mixer.music.pause()  # pause beep sound
                pygame.event.clear()  # clear any button pressed after 10 digits
                continue

            for event in pygame.event.get():  # Get all events instead of polling once
                if event.type == pygame.KEYDOWN:
                    logging.info(f"Key pressed: {event.key}")
                    self.digit_dialed(event)

            if not self.number_dialed:
                pygame.mixer.music.unpause()
            elif (self.last_keypress - dt.now()).total_seconds() > 0.5:
                self.check_number()


def main():
    phone = Telephone(location)
    logging.info("running")
    while True:
        print("idk do website things")


if __name__ == '__main__':  
     main()