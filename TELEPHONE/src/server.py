import socket

host = ""
port = 5560
languageChoice = "The language now is german"

def setupServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # To avoid the error "Address already in use", 
    # This is because the previous execution has left the socket in a TIME_WAIT state, 
    # and can’t be immediately reused.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("The Socket is created")
    
    try:
        s.bind((host,port)) #binds the socket with the address
    except socket.error as msg:
        print(msg)

    s.listen(1) #enable a server to accept connections
    print("Socket bind complete.")
    return s

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
    s = setupServer()
    #Accepts a connection. The socket must be bound to an address and listening for connections.
    connection, address = s.accept() 
    while True:
        
        print("connection is accepted")
        print("Connected to: " + address[0] + ":" + str(address[1]))
        
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
            print("Data has been sent!")
            break
        except socket.error as e:
            print("error in sending data !")
            print("client is closed")
            break
    
    return reply
        
