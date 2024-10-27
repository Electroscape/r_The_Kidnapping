setup ubuntu 22.04 with automatic user login

put the files into

KDN-Videos/viewL_long.mp4
KDN-Videos/viewR_long.mp4

and Put the following line into crontab

@reboot sleep 15 && export DISPLAY=:0.0 && python3 restart.py &
