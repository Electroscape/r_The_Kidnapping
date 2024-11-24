#!/bin/bash
sudo pkill python
sudo pkill flask
sudo pkill chromium

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"

# shellcheck disable=SC2164
source venv/bin/activate

sleep 5 

python3 display.py &
