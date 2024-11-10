export DISPLAY=:0.0
pkill vlc

cvlc --fullscreen --no-video-title --video-on-top --gain=1.0 --quiet --loop idle.mp4 &
echo "idle video played, bye"