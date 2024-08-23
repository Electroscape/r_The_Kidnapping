import logging
import socket
from telephone import number

host = ""
port = 5560
languageChoice = "The language now is german"


logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{'
)

def setup_server():
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # To avoid the error "Address already in use", 
    # This is because the previous execution has left the socket in a TIME_WAIT state, 
    # and can’t be immediately reused.
    sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    logging.info("The Socket is created")
    
    try:
        sc.bind((host,port))
    except socket.error as msg:
        logging.error(msg)
   
    sc.listen(1)
    logging.info("Socket bind complete. \n")
    return sc

def german_language():
    reply = "GERMAN"
    return reply

def english_language():
    reply = "ENGLISH"
    return reply
def restart_pi():
    reply = "RESTART"
    return reply


def data_transfer():

    connection, address = s.accept() 
    
    while True:
        
        logging.info("connection is accepted")
        logging.info("Connected to: " + address[0] + ":" + str(address[1]))
        
        
        data = connection.recv(1024)
       
        data = data.decode('utf-8')
        # Split the data by a space
        # Take first part of the data
        command = data.split(' ', 1)[0]
            
        if command == "GERMAN":
            reply = german_language()
        elif command == "ENGLISH":
            reply = english_language()
        elif command == "RESTART":
            reply = restart_pi()
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
    
s = setup_server()
