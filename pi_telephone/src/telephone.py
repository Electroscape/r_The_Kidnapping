import argparse
import json
import logging
import os
import pygame
from pygame.locals import *
import RPi.GPIO as GPIO
from time import sleep
from server import *
import subprocess
from threading import Thread
from Pathlib import Path


print(f"Current working directory of the script: {os.path.realpath(os.path.dirname(__file__))}")
root_path = Path(os.cwd())
sound_path = root_path.joinpah("sounds")


logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{'
)

argparser = argparse.ArgumentParser(
    description='Telephone')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / st]')

city = argparser.parse_args().city

with open('src/config.json', 'r') as config_file:
    config = json.load(config_file)
    logging.info("the config file is read correctly")



GPIO.setmode(GPIO.BOARD)
GPIO.setup(config["PIN"][city]["PHONE_switch_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)


pygame.init()
pygame.display.init()
pygame.mixer.set_num_channels(8)
size = width, height = 300, 200
screen = pygame.display.set_mode(size, 32)


pygame.mixer.music.load(sound_path.joinpath("013_freizeichen_30min.wav"))
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(2.0)
pygame.mixer.music.pause()


maxNumberOfDigits = 12
language = "deu/"
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


class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None, daemon = None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
             
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def playSound(path):
     effect = pygame.mixer.Sound(path)
     effect.set_volume(float(100))
     empty_channel = pygame.mixer.Channel(1)
     empty_channel.play(effect)
     return effect.get_length()


def pauseCurrentSound():
     logging.info("Pausing current sound")
     pygame.mixer.music.pause()
     empty_channel = pygame.mixer.Channel(1)
     empty_channel.stop()


def checkingNumberSound(path):
     pauseCurrentSound()
     logging.info(f"Playing voice record {path}")
     audio_lenght = playSound(path)
     while pygame.mixer.music.get_busy():
          if GPIO.input(config["PIN"][city]["PHONE_switch_pin"]) == GPIO.HIGH:
               pauseCurrentSound()
               break
          else:
               continue


def checkNumber(Number):
     print("checkNumber")

     sleep(0.5)
     if Number in contacts:
          checkingNumberSound(config['PATH']['sounds'] + language + contacts[Number] + ".wav")
     else:
          checkingNumberSound(config['PATH']['sounds'] + "dialedWrongNumber.wav")





def checkCorrectDigit(event):
     print("in")
     s = Initialize_socket()
     global Number
     pauseCurrentSound()
     empty_channel = pygame.mixer.Channel(1)

     # key 48 is 0, 49 and so on, so ....
     digit = event.key - 48
     if 9 > digit > 0:
          Number.ap
          try;
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + f"{digit}.wav")
     else:
          # @todo: maybe remove the checkNumber depending on the wanted use of the #/OK key but return has to stay
          # checkNumber(Number)
          return
     
     logging.info("number dialed is " + Number)

     try:
          s.send(str.encode(Number))
     except Exception as exp:
          logging.info("No. is dialed without opening the GM option")

     
     effect.set_volume(1)
     empty_channel.play(effect)
     pygame.time.delay(100)



def Initialize_socket():
    host = config['IP'][city]['ip_address'] 
    port = config['IP'][city]['port']
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
          s.connect((host,port)) #establish a connection with our socket
    except:
          logging.info("No. is dialed without opening the GM option")

    return s

def runSystem():

     global language
     global Number

     logging.info("Telephone now is running")
     # dialed number
     # time count for a player to press a key
     countTimer = 0
     # a flag to check that the key is pressed once
     keyPressedAtleastOnce = False
     thread = CustomThread(target=dataTransfer,daemon=True) 
     try:
          thread.start()
     except:
          print("Failed to reopen the socket")
     
     while True: 

          if not thread.is_alive():
               # depending on the choice of the language the GM choose
               if thread.join() == "GERMAN":
                    language = "deu/"
                    logging.info("The language now is german")
               if thread.join() == "ENGLISH":
                    language = "eng/"
                    logging.info("The language now is english")
               if thread.join() == "RESTART":
                    logging.info("PI is closing now")
                    restartRaspberryPi()

               thread = CustomThread(target=dataTransfer,daemon=True)
               thread.start()

          # if the player takes the call unpause the beep sound and check the dialed number
          if GPIO.input(config["PIN"][city]["PHONE_switch_pin"]) == GPIO.LOW:
               if not keyPressedAtleastOnce:
                    pygame.mixer.music.unpause()

               # check correct number
               if Number in contacts:
                    checkNumber(Number)
               # countTimer reached 5s and player didn't press a button.
               elif len(Number) < maxNumberOfDigits and countTimer == 500:
                    countTimer = 0
                    keyPressedAtleastOnce = False
                    logging.info("Player didn't press a button for 5s nor completed 12 digits")
                    pauseCurrentSound()
                    checkingNumberSound(config['PATH']['sounds'] + "dialedWrongNumber.wav")
                    pygame.event.clear()  # clear any button pressed after 12 digits
               
               elif len(Number) >= maxNumberOfDigits:
                    countTimer = 0
                    keyPressedAtleastOnce = False
                    logging.info("Player reached maximum digits")
                    pauseCurrentSound()
                    checkingNumberSound(config['PATH']['sounds'] + "dialedWrongNumber.wav")
                    pygame.event.clear()

               # keep on returning button state
               
               event = pygame.event.poll()
               # checking if a player didn't press 
               # a button after 5s from pressing any button
               if keyPressedAtleastOnce:  
                    if   event.type == pygame.KEYDOWN:
                         keyPressedAtleastOnce = False
                         countTimer = 0
                    else :
                         sleep(0.01)
                         countTimer = countTimer +1  
               if event.type == pygame.KEYDOWN:
                    keyPressedAtleastOnce = True
                    countTimer = 0
                    checkCorrectDigit(event)
               else:
                    pass

          else:
               keyPressedAtleastOnce = False  # reset flag of pressing the button at least once
               pygame.mixer.music.pause()  # pause beep sound
               Number = ""  # reset dialed number
               pygame.event.clear()  # clear any button pressed after 10 digits
               
             
def main():
     runSystem()
     
if __name__ == '__main__':  
     main()