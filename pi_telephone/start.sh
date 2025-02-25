# For clean start
# Kill all relevant programs
sudo pkill -9 -f telephone.py

# pkill python
pkill flask
pkill chromium

cd "${0%/*}" || exit
export DISPLAY=:0.0
python3 telephone.py -c st
