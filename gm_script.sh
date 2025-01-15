# set environment variable to enable sound
XDG_RUNTIME_DIR=/run/user/$(id -u)
export XDG_RUNTIME_DIR

# Hide cursor
# sudo apt install unclutter -y
unclutter -idle 0.1 &

# modify the IP address you want to display
# comment or uncomment to run the browser on the webpage you choose
DISPLAY=:0 /usr/bin/chromium-browser --start-maximized --kiosk --noerrdialogs http://gamemastersoftware/client

# Line to run video
# DISPLAY=:0.0 cvlc --fullscreen --loop --no-video-title --no-audio <video_name> &