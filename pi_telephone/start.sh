# For clean start
# Kill all relevant programs
sudo pkill -9 -f telephone.py
cd "${0%/*}" || exit 
python3 src/telephone.py -c st
