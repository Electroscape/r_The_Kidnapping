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
export DISPLAY=:"0.0" 
unclutter -idle 0 &

# modify the IP address you want to display
# comment or uncomment to run the browser on the webpage you choose
# Added multiple flags to allow autoplay:
# --autoplay-policy=no-user-gesture-required - Allow autoplay without user gesture
# --disable-features=PreloadMediaEngagementData - Disable media engagement checks
# --disable-features=MediaEngagementBypassAutoplayPolicies - Bypass autoplay policies
DISPLAY=:0.0 /usr/bin/chromium \
  --start-fullscreen \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-component-update \
  --disable-background-networking \
  --disable-default-apps \
  --kiosk \
  --no-first-run \
  --autoplay-policy=no-user-gesture-required \
  --disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies \
  0.0.0.0:5666 &