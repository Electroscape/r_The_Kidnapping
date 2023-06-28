 #!/usr/bin/env python
#!/bin/bash
from threading import Thread
import socket
from tkinter import *

host = '192.168.87.166'
port = 5560
host_PI= ""
window = Tk()
window.geometry("1024x400")
window.title("Change Language")


def setupServer():
    
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # To avoid the error "Address already in use", 
    # This is because the previous execution has left the socket in a TIME_WAIT state, 
    # and can’t be immediately reused.
    sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  
    
    try:
        sc.bind((host_PI,port)) #binds the socket with the address
    except socket.error as msg:
        print("error")
   
    sc.listen(1) #enable a server to accept connections
   
    return sc

def dataReceive():
    #Accepts a connection. The socket must be bound to an address and listening for connections.
    
    
    while True:
        
        s = setupServer()
        connection, address = s.accept() 
        
        data = connection.recv(1024)
       
        data = data.decode('utf-8')
        #Split the data by a space
        dataMessage = data.split(' ', 1)
        #Take first part of the data
        command = dataMessage[0]
        print(command)
        Message.delete("1.0","end")
        Message.insert(END, f"Number dialed : {command}")  
        s.close()
        if len(command) == 12:
            Message.delete("1.0","end")
          
        


def setupSocket():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port)) #establish a connection with our socket
    return s


def germanMessage():
    print("Button is pressed")
    Message.delete("1.0","end")
    buttonGerman['state'] = DISABLED
    buttonEnglish['state'] = DISABLED
    Message.insert(END, 'You have chosen the german language')
    sendDataToServer("GERMAN")

def englishMessage():
    print("Button is pressed")
    buttonGerman['state'] = DISABLED
    buttonEnglish['state'] = DISABLED
    Message.delete("1.0","end")
    Message.insert(END, 'You have chosen the english language')
    sendDataToServer("ENGLISH")

def restart():
    print("Button Reset")
    buttonGerman['state'] = NORMAL
    buttonEnglish['state'] = NORMAL
    Message.delete("1.0","end")
    Message.insert(END, 'Choose language.')

def restartPi():
    print("Button Restart is pressed")
    buttonGerman['state'] = NORMAL
    buttonEnglish['state'] = NORMAL
    Message.delete("1.0","end")
    Message.insert(END, 'The Pi is restarted again!! Please wait for 2 mins \nthen choose the language again!!')
    sendDataToServer("RESTART")

def callPlayers():
    print("Calling Players Now!!")
    buttonGerman['state'] = NORMAL
    buttonEnglish['state'] = NORMAL
    Message.delete("1.0","end")
    Message.insert(END, 'Calling The Players Now !!!!')
    sendDataToServer("CALL")

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
    
    thread = Thread(target=dataReceive,daemon=True)  
    thread.start()
    buttonGerman = Button(window,text="GERMAN",command = germanMessage,height= 5, width=15)
    buttonEnglish = Button(window,text="ENGLISH",command = englishMessage,height= 5, width=15)
    buttonRestart = Button(window,text="Reset Language",command = restart,height= 4, width=15)
    buttonRestartPi = Button(window,text="Restart raspberry pi",command = restartPi,height= 4, width=17, bg="red")
    buttonCall = Button(window,text="Call Players",command = callPlayers,height= 4, width=17)
    Message = Text(window, height = 5, width = 52 ,bg = "light cyan", foreground="black")
    Message.place(x = 315,y = 150)
    buttonGerman.place(x =300, y= 20) 
    buttonRestart.place(x =800, y= 200) 
    buttonRestartPi.place(x =70, y= 300) 
    buttonEnglish.place(x =600, y= 20)
    buttonCall.place(x =70, y= 20)
    window.mainloop()

    
    
