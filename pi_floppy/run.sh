#!/bin/bash
pkill python
pkill flask
pkill chromium

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"

# shellcheck disable=SC2164
source venv/bin/activate

sleep 5 &

# comment or uncomment to run floppy
FLASK_APP=floppy:app flask run --host 0.0.0.0 --port 5555  --no-debugger --no-reload  &
sleep 15 &

# modify the IP address you want to display
# comment or uncomment to run the browser on the webpage you choose
DISPLAY=:0 /usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk 0.0.0.0:5555 &
