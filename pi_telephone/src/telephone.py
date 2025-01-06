import argparse
import json
import logging
import os
import pygame
from pygame.locals import *
import RPi.GPIO as GPIO
from time import sleep
# from server import *
import subprocess
from threading import Thread
from pathlib import Path
from datetime import datetime as dt

print(f"Current working directory of the script: {os.path.realpath(os.path.dirname(__file__))}")
root_path = Path(os.getcwd())
print(f"root path of the script: {root_path}")
sound_path = root_path.joinpath("sounds")

os.environ["SDL_VIDEODRIVER"] = "dummy"


logging.basicConfig(
    filename='log.log',
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{'
)

logging.info("This is a test log.")
argparser = argparse.ArgumentParser(
    description='Telephone')

argparser.add_argument(
    '-c',
    '--city',
    default='st',
    help='name of the city: [hh / st]'
)

city = argparser.parse_args().city

with open('src/config.json', 'r') as config_file:
    config = json.load(config_file)
    logging.info("the config file is read correctly")



GPIO.setmode(GPIO.BOARD)
GPIO.setup(config["PIN"][city]["PHONE_switch_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)


def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Virtual screen
    pygame.mixer.set_num_channels(8)

    pygame.mixer.music.load(sound_path.joinpath("013_freizeichen_30min.wav"))
    pygame.mixer.music.play(-1, 0.0)
    # number must be smaller than 1
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.pause()


maxNumberOfDigits = 12
Number = ""

contacts = {
     "90011123": "Accomplice",
     "071101232267": "Albrecht",
     "86753489": "TaxiGerst"
}


def restartRaspberryPi():
    command = "sudo reboot"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.communicate()[0]



def set_sound(path):
    """
    :param path:
    :return duration:
    """
    effect = pygame.mixer.Sound(path)
    empty_channel = pygame.mixer.Channel(1)
    empty_channel.play(effect)
    return effect.get_length()


def pauseCurrentSound():
     logging.info("Pausing current sound")
     pygame.mixer.music.pause()
     empty_channel = pygame.mixer.Channel(1)
     empty_channel.stop()


def play_sound(path, do_exit=False):
     pauseCurrentSound()
     logging.info(f"Playing voice record {path}")
     duration = playSound(path)
     start_time = dt.now()
     while pygame.mixer.music.get_busy() and (start_time - dt.now).seconds < duration :
          if GPIO.input(config["PIN"][city]["PHONE_switch_pin"]) == GPIO.HIGH:
               pauseCurrentSound()
               return
          else:
               continue


def checkNumber(Number):
     print("checkNumber")
     sleep(0.5)
     if Number in contacts:
          play_sound(config['PATH']['sounds'] + language + contacts[Number] + ".wav")
     else:
          play_sound(config['PATH']['sounds'] + "dialedWrongNumber.wav", True)


def checkCorrectDigit(event):
     print("in")
     s = Initialize_socket()
     global Number
     pauseCurrentSound()
     empty_channel = pygame.mixer.Channel(1)

     # key 48 is 0, 49 and so on, so ....
     digit = event.key - 48
     if 9 > digit > 0:
        try:
            effect = pygame.mixer.Sound(config['PATH']['sounds'] + f"{digit}.wav")
        except:
            pass
     else:
          # @todo: maybe remove the checkNumber depending on the wanted use of the #/OK key but return has to stay
          # checkNumber(Number)
          return
     
     logging.info("number dialed is " + Number)

     try:
          s.send(str.encode(Number))
     except Exception as exp:
          logging.info("No. is dialed without opening the GM option")

     empty_channel.play(effect)
     pygame.time.delay(100)


def reset_dialing():
    return


def runSystem():

    language = "deu/"
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
                    pauseCurrentSound()
                    play_sound(config['PATH']['sounds'] + "dialedWrongNumber.wav")
                    pygame.event.clear()  # clear any button pressed after 12 digits

               elif len(Number) >= maxNumberOfDigits:
                    lastKeypress = 0
                    keyPressedAtleastOnce = False
                    logging.info("Player reached maximum digits")
                    pauseCurrentSound()
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
        init_pygame()
        runSystem()
    except Exception as exp:
        logging.error(f"Pygame initialization error: {exp}")
        print(f"Pygame initialization error: {exp}")
        print(exp)
    sleep(5)
     
if __name__ == '__main__':  
     main()