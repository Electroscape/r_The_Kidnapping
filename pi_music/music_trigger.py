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
media_player = instance.media_player_new()
media_list_player = instance.media_list_player_new()
media_list_player.set_media_player(media_player)

# Shared state
current_audio_thread = None
player_lock = threading.Lock()

sounds = {
    "start": ("sound/start.mp3", True),       #     looping
    "mc_boot": ("sound/mc_boot.mp3", False),  # Not looping
    "finish": ("sound/finish.mp3", False),    # Not looping
}

## cd to the script path to find the config.json next to it
os.chdir(os.path.dirname(os.path.abspath(__file__)))



# Audio playback thread target
def play_audio(file_path, loop=False):
    media = instance.media_new(file_path)
    media_list = instance.media_list_new()
    media_list.add_media(media)

    media_list_player.set_media_list(media_list)

    if loop:
        media_list_player.set_playback_mode(vlc.PlaybackMode.loop)
    else:
        media_list_player.set_playback_mode(vlc.PlaybackMode.default)

    media_list_player.play()
    time.sleep(0.1)  # Let VLC start
    media_player.audio_set_volume(AUDIO_VOLUME_PERCENT)
    current_volume = media_player.audio_get_volume()
    print(f"Current volume: {current_volume}")

    # Wait until audio ends or is stopped externally
    if not loop:
        while True:
            state = media_player.get_state()
            if state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error):
                break
            time.sleep(0.1)

# Manage new audio playback safely
def start_audio_in_thread(file_path, loop=False):
    global current_audio_thread

    # Stop previous thread if running
    if current_audio_thread and current_audio_thread.is_alive():
        stop_audio()
        current_audio_thread.join()

    # Start new audio thread
    current_audio_thread = threading.Thread(target=play_audio, args=(file_path, loop))
    current_audio_thread.start()


def stop_audio():
    global media_list_player
    with player_lock:
        media_list_player.stop()


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
            media_player.audio_set_volume(new_volume)
            print(f"Setting volume to: {new_volume}")
        time.sleep(step_duration)

def chimney_effect():
    with player_lock:
        original_volume = media_player.audio_get_volume()
    print(f"Original volume: {original_volume}")

    # player.audio_set_volume(0)
    fade_volume(original_volume, 0, 2)  # Fade down over 2 seconds
    time.sleep(7)                      # Stay muted
    fade_volume(0, original_volume, 4)  # Fade up over 4 seconds



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

    if command in sounds:
        file, loop = sounds[command]
        print(f"Playing: {file}")
        start_audio_in_thread(file, loop)

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
