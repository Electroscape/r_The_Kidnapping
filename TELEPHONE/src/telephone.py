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


'''
=========================================================================================================
Current Working Directory
=========================================================================================================
'''
print(f"Current working directory of the script: {os.path.realpath(os.path.dirname(__file__))}")

'''
=========================================================================================================
Initiialize logging
=========================================================================================================
'''

logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{'
)

'''
=========================================================================================================
Argument parser
=========================================================================================================
'''

argparser = argparse.ArgumentParser(
    description='Telephone')

argparser.add_argument(
    '-c',
    '--city',
    help='name of the city: [hh / st]')

city = argparser.parse_args().city

'''
=========================================================================================================
Load config
=========================================================================================================
'''
with open('src/config.json', 'r') as config_file:

    config = json.load(config_file)
    logging.info("the config file is read correctly")

'''
=========================================================================================================
set GPIOs
=========================================================================================================
'''
# Setting GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(config["PIN"][city]["PHONE_switch_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

'''
=========================================================================================================
Initialize pygame
=========================================================================================================
'''
# Initialize pygame

pygame.init()
pygame.display.init()
pygame.mixer.set_num_channels(8)
size = width, height = 300, 200
screen = pygame.display.set_mode(size, 32)

'''
=========================================================================================================
Run as a start the beep sound
=========================================================================================================
'''
# setting at the beginning the beep sound 
pygame.mixer.music.load(config['PATH']['sounds'] + "/013_freizeichen_30min.wav")
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(2.0)
pygame.mixer.music.pause()

'''
=========================================================================================================
Initialize size of code digits, language and entered number
=========================================================================================================
'''
maxNumberOfDigits = 12
numberAlbrecht = "071101232267"
language = "deu/"
Number = ""

def restartRaspberryPi():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]


'''
=========================================================================================================
Initialize a thread class
=========================================================================================================
'''

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

'''
=========================================================================================================
Playing and Pausing the Sound
=========================================================================================================
'''
# play sound based on a specific scenario
def playSound(path):
     effect = pygame.mixer.Sound(path)
     effect.set_volume(float(100))
     empty_channel = pygame.mixer.Channel(1)
     empty_channel.play(effect)
 
# pause any current sound
def pauseCurrentSound():
     logging.info("Pausing current sound")
     pygame.mixer.music.pause()
     empty_channel = pygame.mixer.Channel(1)
     empty_channel.stop()

'''
=========================================================================================================
Number checking methods
=========================================================================================================
'''
# play correct number sound 
def checkingNumberSound(path):
     pauseCurrentSound()
     logging.info(f"Playing voice record {path}")
     playSound(path)
     while pygame.mixer.music.get_busy():
          if GPIO.input(config["PIN"][city]["PHONE_switch_pin"]) == GPIO.HIGH:
               pauseCurrentSound()
               break
          else:
               continue


def checkNumber(Number):
     
     sleep(0.5)
     if Number == "86753489":
          checkingNumberSound(config['PATH']['sounds'] + language + "TaxiGerst.wav")
     elif Number in numberAlbrecht:
          if Number == numberAlbrecht:
               checkingNumberSound(config['PATH']['sounds'] + language + "Albrecht.wav")
     elif Number == "90011123":
          checkingNumberSound(config['PATH']['sounds'] + language +"Accomplice.wav")
     
     elif len(Number) < 12:
          return
     else:
          checkingNumberSound(config['PATH']['sounds'] + "dialedWrongNumber.wav")



def checkCorrectDigit(event):

     global Number
     pygame.mixer.music.pause()
     empty_channel = pygame.mixer.Channel(1)

     if(event.key == 48):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "ZERO.wav")
          Number = Number + "0"
     elif(event.key == 49):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "ONE.wav")
          Number = Number + "1"
     elif(event.key == 50):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "TWO.wav")
          Number = Number + "2"
     elif(event.key == 51):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "THREE.wav")
          Number = Number + "3"
     elif(event.key == 52):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "FOUR.wav")
          Number = Number + "4"
     elif(event.key == 53):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "FIVE.wav")
          Number = Number + "5"
     elif(event.key == 54):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "SIX.wav")
          Number = Number + "6"
     elif(event.key == 55):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "SEVEN.wav")
          Number = Number + "7"
     elif(event.key == 56):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "EIGHT.wav")
          Number = Number + "8"
     elif(event.key == 57):
          effect = pygame.mixer.Sound(config['PATH']['sounds'] + "NINE.wav")
          Number = Number + "9"
     else:
          # @todo: maybe remove the checkNumber depending on the wanted use of the #/OK key but return has to stay
          # checkNumber(Number)
          return
     
     effect.set_volume(1)
     empty_channel.play(effect)
     pygame.time.delay(100)

'''
=========================================================================================================
Running the telephone 
=========================================================================================================
'''    

def runSystem():

     global language
     global Number

     logging.info("Telephone now is running")
     # dialed number
     # time count for a player to press a key
     countTimer = 0
     # a flag to check that the key is pressed once
     keyPressedAtleastOnce = False
     return_values = ""
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

               thread = None
               thread = CustomThread(target=dataTransfer,daemon=True)
               thread.start()

          # if the player takes the call unpause the beep sound and check the dialed number
          if GPIO.input(config["PIN"][city]["PHONE_switch_pin"]) == GPIO.LOW:

               pygame.mixer.music.unpause()

               # countTimer reached 5s and player didn't press a button.
               if len(Number) < 12 and countTimer == 500 :
                    countTimer = 0
                    keyPressedAtleastOnce = False
                    logging.info("Player didn't press a button for 5s nor completed 10 digits")
                    pauseCurrentSound()
                    checkingNumberSound(config['PATH']['sounds'] + "dialedWrongNumber.wav")
               
               # check correct number

               if len(Number) == 12 or len(Number)==8:
                    checkNumber(Number)


               # keep on returning button state
               
               event = pygame.event.poll()
               # checking if a player didn't press 
               # a button after 5s from pressing any button
               if keyPressedAtleastOnce :  
                    if   event.type == KEYDOWN:
                         keyPressedAtleastOnce = False
                         countTimer = 0
                    else : 
                         # decreased
                         sleep(0.01)
                         countTimer = countTimer +1  
               if event.type == KEYDOWN  :
                    keyPressedAtleastOnce = True
                    countTimer = 0
                    checkCorrectDigit(event)
               else:
                    pass

          else:
               keyPressedAtleastOnce = False #reset flag of pressing the button at least once
               pygame.mixer.music.pause() #pause beep sound
               Number ="" # reset dialed number
               pygame.event.clear() #clear any button pressed after 10 digits
               
             
def main():
     # by default the language is german
     language = "deu/"
     runSystem()
     
if __name__ == '__main__':  
     main()