export DISPLAY=:0.0

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"

cvlc --fullscreen --no-video-title --video-on-top --gain=1.0 --quiet static/vids/zwinger_CCTV.mp4 &
echo "zwinger video played, bye"