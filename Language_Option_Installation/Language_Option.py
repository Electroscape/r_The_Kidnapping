 #!/usr/bin/env python
#!/bin/bash
 
import socket
import tkinter as tk
from tkinter import *

host = '192.168.87.127'
port = 5560
window = tk.Tk()
window.geometry("1024x400")
window.title("Change Language")


def setupSocket():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port)) #establish a connection with our socket
    return s

    

def germanMessage():
    print("Button is pressed")
    Message.delete("1.0","end")
    buttonGerman['state'] = tk.DISABLED
    buttonEnglish['state'] = tk.DISABLED
    Message.insert(END, 'You have chosen the german language')
    sendDataToServer("GERMAN")

def englishMessage():
    print("Button is pressed")
    buttonGerman['state'] = tk.DISABLED
    buttonEnglish['state'] = tk.DISABLED
    Message.delete("1.0","end")
    Message.insert(END, 'You have chosen the english language')
    sendDataToServer("ENGLISH")

def restart():
    print("Button Reset")
    buttonGerman['state'] = tk.NORMAL
    buttonEnglish['state'] = tk.NORMAL
    Message.delete("1.0","end")
    Message.insert(END, 'Choose language.')

def restartPi():
    print("Button Restart is pressed")
    buttonGerman['state'] = tk.NORMAL
    buttonEnglish['state'] = tk.NORMAL
    Message.delete("1.0","end")
    Message.insert(END, 'The Pi is restarted again!! Please wait for 2 mins \nthen choose the language again!!')
    sendDataToServer("RESTART")

def sendDataToServer(language):
    try :
        s = setupSocket()
        s.send(str.encode(language))
        reply = s.recv(1024)
        print(reply.decode('utf-8'))
    except:
        Message.delete("1.0","end")
        Message.insert(END, 'This message will pop out when you restart the Pi \n,so wait till the telephone opens for 1.5 mins')

    
        

if __name__ == '__main__': 
    
    buttonGerman = tk.Button(window,text="GERMAN",command = germanMessage,height= 5, width=15)
    buttonEnglish = tk.Button(window,text="ENGLISH",command = englishMessage,height= 5, width=15)
    buttonRestart = tk.Button(window,text="Reset Language",command = restart,height= 4, width=15)
    buttonRestartPi = tk.Button(window,text="Restart raspberry pi",command = restartPi,height= 4, width=17, bg="red")
    Message = Text(window, height = 5, width = 52 ,bg = "light cyan", foreground="black")
    Message.place(x = 315,y = 150)
    buttonGerman.place(x =300, y= 20) 
    buttonRestart.place(x =800, y= 200) 
    buttonRestartPi.place(x =70, y= 300) 
    buttonEnglish.place(x =600, y= 20)
    window.mainloop()

    
    
