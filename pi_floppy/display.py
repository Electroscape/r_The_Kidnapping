import socket
import subprocess
import json

# Open and read the JSON file
with open('config.json', 'r') as json_file:
    cfg = json.loads(json_file.read())
    PORT = cfg["lcds_port"]  # You can set any port here, but it should be the same on all display RPis
    

# Define the IP and port for the display
HOST = '0.0.0.0'   # Listen on all interfaces

prev_command = ""

# Function to execute the received command
def execute_command(command: str) -> None:
    global prev_command
    
    if command == prev_command:
        # for same command, no execution
        return None
    elif prev_command == "play_solution":
            subprocess.Popen(["sudo", "pkill", "feh"])
            # make copy of previous command
            prev_command = (command + '.')[:-1]
            return None
    else:
        # make copy of previous command
        prev_command = (command + '.')[:-1]

    
    try:
        if command.startswith("play_"):
            # Run script
            subprocess.Popen(["bash", f"{command}.sh"])

    except Exception as e:
        print(f"Error executing command: {e}")

# Execute init command
execute_command("play_blackscreen")

# Set up the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server started on {HOST}:{PORT}. Waiting for commands...")

    while True:
        client_socket, addr = server_socket.accept()
        with client_socket:
            print(f"Connected by {addr}")
            command = client_socket.recv(1024).decode('utf-8')
            if command:
                print(f"Received command: {command}")
                execute_command(command)
