import os
import json

from communication.Simple_Socket import SocketClient

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
    return SocketClient(server_add, port)

def main():
    arbiter_socket = init_socket()

    while True:
        if arbiter_socket.read_buffer():
            os.system('pkill vlc')
            os.system("DISPLAY=:0.0 cvlc --fullscreen --loop --no-video-title ~/KDN-Videos/viewR_long.mp4 &")

    # Deprecated use VLC > mplayer
    #  os.system("DISPLAY=:0.0 mplayer -fs -loop 0 -xineramascreen 0 KDN-Videos/viewL_long.mp4 &")
    #  os.system("DISPLAY=:0.0 mplayer -fs -loop 0 -xineramascreen 1 KDN-Videos/viewR_long.mp4")


main()