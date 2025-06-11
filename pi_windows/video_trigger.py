import os
import json
import argparse
from time import sleep

from communication.Simple_Socket import SocketClient, TESocketServer


argparser = argparse.ArgumentParser(description='Telephone')
argparser.add_argument('-s', '--socket', default='client', help='socketmode: [host / client (default)]')
host_mode = argparser.parse_args().socket == "host"


VIDEO_FILE = "~/KDN-Videos/viewR_long.mp4"

## cd to the script path to find the config.json next to it
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.system('pkill vlc')

def get_cfg():
    try:
        with open('config.json') as json_file:
            return json.loads(json_file.read())
    except ValueError as e:
        print('failure to read config.json')
        print(e)
        exit()


def init_socket():
    cfg = get_cfg()
    try:
        server_add = cfg["add"]
        port = cfg["port"]
    except KeyError:
        exit("missing server configuration")
    if host_mode:
        return TESocketServer(port)
    return SocketClient(server_add, port)

# Handle messages
def video_handler(command):
    # if command is list, get the first element
    if isinstance(command, list):
        command = command[0]

    if command == "start":
        os.system('pkill vlc')
        os.system(f"DISPLAY=:0.0 cvlc --fullscreen --loop --no-video-title {VIDEO_FILE} &")

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

    # Deprecated use VLC > mplayer
    #  os.system("DISPLAY=:0.0 mplayer -fs -loop 0 -xineramascreen 0 KDN-Videos/viewL_long.mp4 &")
    #  os.system("DISPLAY=:0.0 mplayer -fs -loop 0 -xineramascreen 1 KDN-Videos/viewR_long.mp4")


main()