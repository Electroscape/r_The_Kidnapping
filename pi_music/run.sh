#!/bin/bash
export DISPLAY=:"0.0"
export XAUTHORITY=/home/pi/.Xauthority
#sleep 5  # Or however long needed for X to load

# fixes activate venv from crontab
cd "${0%/*}"

# set environment variable to enable sound
XDG_RUNTIME_DIR=/run/user/$(id -u)
export XDG_RUNTIME_DIR

sudo pkill python

# Hide cursor
#unclutter -idle  &
source venv/bin/activate
python music_trigger.py &

#sleep 5

# modify the IP address you want to display
# comment or uncomment to run the browser on the webpage you choose
#DISPLAY=:0 /usr/bin/chromium-browser --start-maximized --kiosk --noerrdialogs http://gamemastersoftware/client
#DISPLAY=:0.0 chromium-browser gamemastersoftware/client --kiosk
DISPLAY=:0.0 /usr/bin/chromium-browser --start-fullscreen --noerrdialogs --kiosk --no-first-run --autoplay-policy=no-user-gesture-required gamemastersoftware/client &
