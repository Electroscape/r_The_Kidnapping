#!/bin/bash
export DISPLAY=:0.0

cd "${0%/*}"

sudo pkill vlc

source venv/bin/activate
pkill -f "music_trigger.py end_deu"
pkill -f "music_trigger.py end_eng"


echo "restart, bye"