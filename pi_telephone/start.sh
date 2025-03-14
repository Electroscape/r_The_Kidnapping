# For clean start
# Kill all relevant programs
sudo pkill -9 -f telephone.py

# pkill python
pkill flask
pkill chromium

cd "${0%/*}" || exit
export XDG_RUNTIME_DIR=/run/user/1000
export PULSE_SERVER=unix:/run/user/1000/pulse/native
export DISPLAY=:0

# Delay to ensure services are ready
sleep 2

python3 telephone.py -c st
