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

# modify the IP address you want to display
# comment or uncomment to run the browser on the webpage you choose
#DISPLAY=:0 /usr/bin/chromium-browser --start-maximized --kiosk --noerrdialogs http://gamemastersoftware/client
DISPLAY=:0 /usr/bin/chromium-browser gamemastersoftware/client --start-fullscreen --kiosk --noerrdialogs --no-first-run --autoplay-policy=no-user-gesture-required
