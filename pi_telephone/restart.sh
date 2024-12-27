cd "${0%/*}" || exit
export DISPLAY=:0.0
xhost +
bash start.sh
