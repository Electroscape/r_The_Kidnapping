export DISPLAY=:0.0
pkill vlc

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"

cvlc --no-embedded-video --fullscreen --no-video-title --video-wallpaper --quiet --loop static/blackscreen.jpg &
echo "show blank screen, bye"