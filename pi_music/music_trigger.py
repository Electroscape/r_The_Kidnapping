import os
import json
import vlc
import threading
import time
import math
from communication.Simple_Socket import SocketClient

AUDIO_VOLUME_PERCENT = 70  # Volume level for audio playback

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
        time.sleep(0.1)  # Let VLC start
        player.audio_set_volume(AUDIO_VOLUME_PERCENT)
        time.sleep(0.1)  # Let VLC start
        current_volume = player.audio_get_volume()
        print(f"Current volume: {current_volume}")

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


def ease_in_out(t):
    # Ease-in-out cubic
    return 3 * t**2 - 2 * t**3

def fade_volume(start, end, duration):
    steps = 6  # Less frequent updates = smoother with VLC
    step_duration = duration / steps
    volume_diff = end - start

    for i in range(steps + 1):
        progress = i / steps
        eased_progress = ease_in_out(progress)
        new_volume = int(start + volume_diff * eased_progress)
        with player_lock:
            player.audio_set_volume(new_volume)
            print(f"Setting volume to: {new_volume}")
        time.sleep(step_duration)

def chimney_effect():
    with player_lock:
        original_volume = player.audio_get_volume()
    print(f"Original volume: {original_volume}")

    # player.audio_set_volume(0)
    fade_volume(original_volume, 0, 2)  # Fade down over 2 seconds
    time.sleep(7)                      # Stay muted
    fade_volume(0, original_volume, 4)  # Fade up over 6 seconds



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
    # if command is list, get the first element
    if isinstance(command, list):
        command = command[0]

    if command == "start":
        file = sounds["start"]
        print(f"Playing: {file}")
        start_audio_in_thread(file)

    elif command == "mc_boot":
        file = sounds["mc_boot"]
        print(f"Playing: {file}")
        start_audio_in_thread(file)

    elif command == "chimney":
        print("Chimney effect triggered")
        chimney_effect()

    elif command == "exit":
        print("stop audio")
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
