import argparse
import json
import logging
import os
import pygame
from pygame.locals import *
import RPi.GPIO as GPIO
from time import sleep
import sys

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
flags = FULLSCREEN
screen = pygame.display.set_mode(size, flags, 32)

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
Initialize size of code digits
=========================================================================================================
'''
maxNumberOfDigits = 10


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
     logging.info(f"Playing voice record {path}")
     playSound(path)
     while pygame.mixer.music.get_busy():
          if GPIO.input(config["PIN"][city]["PHONE_switch_pin"]) == GPIO.HIGH:
               pauseCurrentSound()
               break
          else:
               continue


def checkNumber(Number):
     logging.info(f"The Number {Number} is being checked ")
     if Number == "0401234444":
          pauseCurrentSound()
          checkingNumberSound(config['PATH']['sounds'] + "SoundClip3.wav")
     elif Number == "0401235554":
          pauseCurrentSound()
          checkingNumberSound(config['PATH']['sounds'] + "SoundClip4.wav")
     elif Number == "0711456667":
          pauseCurrentSound()
          checkingNumberSound(config['PATH']['sounds'] + "SoundClip5.wav")
     else:
          pauseCurrentSound()
          checkingNumberSound(config['PATH']['sounds'] + "dialedWrongNumber.wav")

'''
=========================================================================================================
Running the telephone 
=========================================================================================================
'''    

def runSystem():

     logging.info("Telephone now is running")
     # dialed number
     Number = ""
     # time count for a player to press a key
     countTimer = 0
     # a flag to check that the key is pressed once
     keyPressedAtleastOnce = False
     
     while True: 

          # if the player takes the call unpause the beep sound and check the dialed number
          if GPIO.input(config["PIN"][city]["PHONE_switch_pin"]) == GPIO.LOW:

               pygame.mixer.music.unpause()

               # countTimer reached 5s and player didn't press a button.
               if len(Number) < 10 and countTimer == 50 :
                    countTimer = 0
                    keyPressedAtleastOnce = False
                    logging.info("Player didn't press a button for 5s nor completed 10 digits")
                    pauseCurrentSound()
                    checkingNumberSound(config['PATH']['sounds'] + "dialedWrongNumber.wav")
               
               # check correct number
               if len(Number) == 10:
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
                         sleep(0.1)
                         countTimer = countTimer +1
                    
               if event.type == KEYDOWN :

                    keyPressedAtleastOnce = True
                    countTimer = 0

                    pygame.mixer.music.pause()
                    empty_channel = pygame.mixer.Channel(1)

                    if(event.key == 48):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "ZERO.wav")
                         Number = Number + "0"
                    if(event.key == 49):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "ONE.wav")
                         Number = Number + "1"
                    if(event.key == 50):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "TWO.wav")
                         Number = Number + "2"
                    if(event.key == 51):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "THREE.wav")
                         Number = Number + "3"
                    if(event.key == 52):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "FOUR.wav")
                         Number = Number + "4"
                    if(event.key == 53):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "FIVE.wav")
                         Number = Number + "5"
                    if(event.key == 54):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "SIX.wav")
                         Number = Number + "6"
                    if(event.key == 55):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "SEVEN.wav")
                         Number = Number + "7"
                    if(event.key == 56):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "EIGHT.wav")
                         Number = Number + "8"
                    if(event.key == 57):
                         effect = pygame.mixer.Sound(config['PATH']['sounds'] + "NINE.wav")
                         Number = Number + "9"

                    effect.set_volume(1)
                    empty_channel.play(effect)
                    pygame.time.delay(250)


               else:
                    pass


          else:
             
               keyPressedAtleastOnce = False #reset flag of pressing the button at least once
               pygame.mixer.music.pause() #pause beep sound
               Number ="" # reset dialed number
               pygame.event.clear() #clear any button pressed after 10 digits
               
             

def main():
     runSystem()
     

if __name__ == '__main__': 
     
     main()