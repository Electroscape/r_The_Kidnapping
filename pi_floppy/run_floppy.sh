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
sleep 15 

# modify the IP address you want to display
# comment or uncomment to run the browser on the webpage you choose
DISPLAY=:0.0 /usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk 0.0.0.0:5666 &
