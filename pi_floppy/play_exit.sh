export DISPLAY=:0.0
sudo pkill vlc
sudo pkill feh

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"

cvlc --fullscreen --no-video-title --video-on-top --gain=1.0 --quiet  static/vids/exit.mp4 &
echo "exit video played, bye"