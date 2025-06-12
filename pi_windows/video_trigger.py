import os
import json
import argparse
from time import sleep
from pathlib import Path

from communication.Simple_Socket import SocketClient, TESocketServer


argparser = argparse.ArgumentParser(description='Telephone')
argparser.add_argument('-s', '--socket', default='client', help='socketmode: [host / client (default)]')
host_mode = argparser.parse_args().socket == "host"


## cd to the script path to find the config.json next to it
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.system('pkill vlc')

class CFG:
    def __init__(self):
        try:
            with open('config.json') as json_file:
                self.cfg = json.loads(json_file.read())
        except ValueError as e:
            print('failure to read config.json')
            print(e)
            exit()
        try:
            self.server_add = self.cfg["add"]
            self.port = self.cfg["port"]
            self.video_file = self.cfg["video_file"]
        except KeyError as e:
            exit("invalid config: {e}")

cfg = CFG()


def init_socket():
    if host_mode:
        return TESocketServer(cfg.port)
    return SocketClient(cfg.server_add, cfg.port)

# Handle messages
def video_handler(command):
    # if command is list, get the first element
    if isinstance(command, list):
        command = command[0]

    if command == "start":
        os.system('pkill vlc')
        os.system(f"DISPLAY=:0.0 cvlc --fullscreen --loop --no-video-title {cfg.video_file} &")

    elif command == "exit":
        pass
        # os.system('pkill vlc')


def main():
    socket = init_socket()

    while not host_mode:
        message = socket.read_buffer()
        if message:
            print(f"Received message: {message}")
            video_handler(message)

    sleep(10)
    socket.transmit("start")
    video_handler("start")

    # Deprecated use VLC > mplayer
    #  os.system("DISPLAY=:0.0 mplayer -fs -loop 0 -xineramascreen 0 KDN-Videos/viewL_long.mp4 &")
    #  os.system("DISPLAY=:0.0 mplayer -fs -loop 0 -xineramascreen 1 KDN-Videos/viewR_long.mp4")


main()