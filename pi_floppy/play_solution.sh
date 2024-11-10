export DISPLAY=:0.0
pkill vlc

cvlc --fullscreen --no-video-title --video-on-top --gain=1.0 --quiet --loop solution.mp4 &
echo "solution played, bye"