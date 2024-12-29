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

python floppy.py &
sleep 5 

unclutter -idle 0 &

# modify the IP address you want to display
# comment or uncomment to run the browser on the webpage you choose
DISPLAY=:0.0 /usr/bin/chromium-browser --start-fullscreen --noerrdialogs --disable-infobars --disable-session-crashed-bubble --disable-component-update --disable-background-networking --disable-default-apps --kiosk --no-first-run --autoplay-policy=no-user-gesture-required 0.0.0.0:5666 &
