#!/bin/bash
# pkill python3  <= will kill m_terminal py script
pkill vlc

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"


export DISPLAY=:0.0
# sudo fbi -T 1 -a media/black_screen.jpg &
# cvlc media/black_screen.jpg --no-embedded-video --fullscreen --no-video-title --video-wallpaper --loop 2> /dev/null &

# sleep 5

source venv/bin/activate
# DISPLAY=:0
python3 main.py


