import logging
import socket
from telephone import Number

host = ""
port = 5560
languageChoice = "The language now is german"


logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{'
)

def setupServer():
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # To avoid the error "Address already in use", 
    # This is because the previous execution has left the socket in a TIME_WAIT state, 
    # and can’t be immediately reused.
    sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    logging.info("The Socket is created")
    
    try:
        sc.bind((host,port)) #binds the socket with the address
    except socket.error as msg:
        logging.error(msg)
   
    sc.listen(1) #enable a server to accept connections
    logging.info("Socket bind complete. \n")
    return sc

def germanLanguage():
    reply = "GERMAN"
    return reply

def englishLanguage():
    reply = "ENGLISH"
    return reply
def restartPi():
    reply = "RESTART"
    return reply


def dataTransfer():
    #Accepts a connection. The socket must be bound to an address and listening for connections.

    connection, address = s.accept() 
    
    while True:
        
        logging.info("connection is accepted")
        logging.info("Connected to: " + address[0] + ":" + str(address[1]))
        
        
        data = connection.recv(1024)
       
        data = data.decode('utf-8')
        #Split the data by a space
        dataMessage = data.split(' ', 1)
        #Take first part of the data
        command = dataMessage[0]
            
        if command == "GERMAN":
            reply = germanLanguage()
            
        elif command == "ENGLISH":
            reply = englishLanguage()
        elif command == "RESTART":
            reply = restartPi()
        else:
            reply = "Wrong command"
        try :
            connection.sendall(str.encode(reply))
            logging.info("Data has been sent!")
            break
        except socket.error as e:
            logging.error("error in sending data !")
            logging.warning("client is closed")
            break
    
    return reply
    
s = setupServer()
