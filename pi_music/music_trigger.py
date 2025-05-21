import os
import json
import vlc
import threading
import time
from communication.Simple_Socket import SocketClient

# Initialize VLC instance
instance = vlc.Instance()
player = instance.media_player_new()

# Shared state
current_audio_thread = None
player_lock = threading.Lock()

sounds = {
    "start": "sound/start.mp3",
    "mc_boot": "sound/mc_boot.mp3",
    "finish": "sound/finish.mp3",
}

## cd to the script path to find the config.json next to it
os.chdir(os.path.dirname(os.path.abspath(__file__)))



# Audio playback thread target
def play_audio(file_path):
    with player_lock:
        player.stop()  # Stop any previous audio
        media = instance.media_new(file_path)
        player.set_media(media)
        player.play()

    # Wait until audio ends or is stopped externally
    while True:
        state = player.get_state()
        if state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error):
            break
        time.sleep(0.1)

# Manage new audio playback safely
def start_audio_in_thread(file_path):
    global current_audio_thread

    # Stop previous thread if running
    if current_audio_thread and current_audio_thread.is_alive():
        stop_audio()
        current_audio_thread.join()

    # Start new audio thread
    current_audio_thread = threading.Thread(target=play_audio, args=(file_path,))
    current_audio_thread.start()


def stop_audio():
    global player
    with player_lock:
        player.stop()


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

# Handle messages
def audio_handler(command):
    if command == "start":
        file = sounds["start"]
        print(f"Playing: {file}")
        start_audio_in_thread(file)

    elif command == "mc_boot":
        file = sounds["mc_boot"]
        print(f"Playing: {file}")
        start_audio_in_thread(file)

    elif command == "stop":
        stop_audio()
    else:
        print(f"Unknown command: {command}")


def main():
    arbiter_socket = init_socket()

    while True:
        message = arbiter_socket.read_buffer()
        if message:
            print(f"Received: {message}")
            audio_handler(message)
            


# Main loop
if __name__ == "__main__":
    main()

