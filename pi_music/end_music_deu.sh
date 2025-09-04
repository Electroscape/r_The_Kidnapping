#!/bin/bash
export DISPLAY=:0.0

cd "${0%/*}"

source venv/bin/activate
python3 music_trigger.py end_deu &

#cvlc --fullscreen --no-video-title --video-on-top --gain=1.0 --quiet --loop  vids/exit.mp4 &
echo "exit alarm deu played, bye"