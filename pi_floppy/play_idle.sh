export DISPLAY=:0.0
sudo pkill vlc

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"

cvlc --fullscreen --no-video-title --video-on-top --gain=1.0 --quiet --loop static/vids/idle.mp4 &
echo "idle video played, bye"