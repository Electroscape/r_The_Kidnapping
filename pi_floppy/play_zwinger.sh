export DISPLAY=:0.0
sudo pkill chromium
sudo pkill vlc

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"

cvlc --fullscreen --no-video-title --video-on-top --gain=1.0 --quiet --loop static/vids/zwinger_CCTV.mp4 &
echo "zwinger video played, bye"