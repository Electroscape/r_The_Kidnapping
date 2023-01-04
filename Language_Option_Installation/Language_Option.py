 #!/usr/bin/env python
#!/bin/bash
 
import socket
import tkinter as tk
from tkinter import *

host = '192.168.178.186'
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
    

def sendDataToServer(language):
    s = setupSocket()
    s.send(str.encode(language))
    reply = s.recv(1024)
    print(reply.decode('utf-8'))
    
        

if __name__ == '__main__': 
    
    buttonGerman = tk.Button(window,text="GERMAN",command = germanMessage,height= 5, width=15)
    buttonEnglish = tk.Button(window,text="ENGLISH",command = englishMessage,height= 5, width=15)
    buttonRestart = tk.Button(window,text="Restart",command = restart,height= 4, width=10)
    Message = Text(window, height = 5, width = 52 ,bg = "light cyan", foreground="black")
    Message.place(x = 315,y = 200)
    buttonGerman.place(x =300, y= 20) 
    buttonRestart.place(x =800, y= 200) 
    buttonEnglish.place(x =600, y= 20)
    window.mainloop()

    
    
