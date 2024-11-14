export DISPLAY=:0.0
pkill vlc

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"

cvlc --fullscreen --no-video-title --video-on-top --gain=1.0 --quiet --loop static/vids/blackscreen.mp4 &
echo "show blank screen, bye"