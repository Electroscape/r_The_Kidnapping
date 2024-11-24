#!/bin/bash
export DISPLAY=:"0.0"
xdotool getactivewindow
xdotool key F5
sleep 1 &
export DISPLAY=:"0.0" 
unclutter -idle 0
