#!/bin/bash
export DISPLAY=:0.0
sudo pkill vlc

cd "${0%/*}"

source venv/bin/activate
#python3 music_trigger.py end &

cvlc --fullscreen --no-video-title --video-on-top --gain=1.0 --quiet --loop  vids/exit.mp4 &
echo "exit video played, bye"