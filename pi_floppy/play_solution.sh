export DISPLAY=:0.0
# sudo pkill vlc
sudo pkill feh

# cd to this script dir
# fixes activate venv from crontab 
cd "${0%/*}"

feh -F -Y static/blueprints/Grundriss_1.jpg &

echo "solution played, bye"