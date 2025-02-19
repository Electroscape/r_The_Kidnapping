import argparse
import json
import logging
import os
import pygame
from pygame.locals import *
import RPi.GPIO as GPIO
from time import sleep
import subprocess
from threading import Thread
from pathlib import Path
from datetime import datetime as dt

print(f"Current working directory of the script: {os.path.realpath(os.path.dirname(__file__))}")
root_path = Path(os.getcwd())
print(f"root path of the script: {root_path}")
sound_path = root_path.joinpath("sounds")

os.environ["SDL_VIDEODRIVER"] = "dummy"
GPIO.setmode(GPIO.BOARD)


logging.basicConfig(
    filename='log.log',
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{'
)

config = None


class Telephone:
    def __init__(self, cfg, location):
        self.__init_pygame()
        try:
            self.contacts = cfg["contacts"]
            self.sound_path = cfg["PATH"]["sounds"]
            self.language = "deu/"
            # self.location = location
            self.phone_pin = cfg["PIN"][location]["PHONE_switch_pin"]
            GPIO.setup(self.phone_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        except KeyError as er:
            exit(er)
        self.number_dialed = ""
        self.max_digits = 12

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
            if GPIO.input() == GPIO.HIGH:
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

        print("number dialed is " + Number)

        # @Todo: send number update on socket/website
        empty_channel.play(effect)
        pygame.time.delay(100)



logging.info("This is a test log.")
argparser = argparse.ArgumentParser(
    description='Telephone')

argparser.add_argument(
    '-c',
    '--city',
    default='st',
    help='name of the city: [hh / st]'
)


def get_cfg():
    location = argparser.parse_args().city
    with open('src/config.json', 'r') as config_file:
        return Settings(json.load(config_file), location)


def run_system():

    global Number

    logging.info("Telephone now is running")
    lastKeypress = dt.now()
    # a flag to check that the key is pressed once
    # @TODO: replace this ... maybe simply a check if a number has been entered
    keyPressedAtleastOnce = False

    # @TODO: add the socketserver submodule

    while True:

          # if the player takes the call unpause the beep sound and check the dialed number
          if GPIO.input(config["PIN"][city]["PHONE_switch_pin"]) == GPIO.LOW:
               if not keyPressedAtleastOnce:
                    pygame.mixer.music.unpause()

               elif len(Number) < maxNumberOfDigits and lastKeypress == 500:
                    lastKeypress = 0
                    keyPressedAtleastOnce = False
                    logging.info("Player didn't press a button for 5s nor completed 12 digits")
                    pause_current_sound()
                    play_sound(config['PATH']['sounds'] + "dialedWrongNumber.wav")
                    pygame.event.clear()  # clear any button pressed after 12 digits

               elif len(Number) >= maxNumberOfDigits:
                    lastKeypress = 0
                    keyPressedAtleastOnce = False
                    logging.info("Player reached maximum digits")
                    pause_current_sound()
                    play_sound(config['PATH']['sounds'] + "dialedWrongNumber.wav")
                    pygame.event.clear()

               # keep on returning button state

               event = pygame.event.poll()
               # checking if a player didn't press
               # a button after 5s from pressing any button
               if keyPressedAtleastOnce:
                    if   event.type == pygame.KEYDOWN:
                         keyPressedAtleastOnce = False
                         lastKeypress = 0
                    else :
                         sleep(0.01)
                         lastKeypress = lastKeypress + 1
               if event.type == pygame.KEYDOWN:
                    keyPressedAtleastOnce = True
                    lastKeypress = 0
                    checkCorrectDigit(event)
               else:
                    pass
          else:
               keyPressedAtleastOnce = False  # reset flag of pressing the button at least once
               pygame.mixer.music.pause()  # pause beep sound
               Number = ""  # reset dialed number
               pygame.event.clear()  # clear any button pressed after 10 digits

             
def main():
    try:
        global config
        config = get_cfg()
        init_pygame()
        run_system()
    except Exception as exp:
        logging.error(f"Pygame initialization error: {exp}")
        print(f"Pygame initialization error: {exp}")
        print(exp)
    sleep(5)


if __name__ == '__main__':  
     main()