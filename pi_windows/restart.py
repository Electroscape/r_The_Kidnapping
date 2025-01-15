import os

os.system('pkill vlc')

def main():
   # Change filename viewL or viewR as needed
   os.system("DISPLAY=:0.0 cvlc --fullscreen --loop --no-video-title --no-audio KDN-Videos/viewR_long.mp4 &")
   
   # Deprecated use VLC > mplayer 
   #  os.system("DISPLAY=:0.0 mplayer -fs -loop 0 -xineramascreen 0 KDN-Videos/viewL_long.mp4 &")
   #  os.system("DISPLAY=:0.0 mplayer -fs -loop 0 -xineramascreen 1 KDN-Videos/viewR_long.mp4")

main()

