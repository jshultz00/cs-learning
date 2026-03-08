package main

import (
	"bufio"
	"embed"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"os/exec"

	"golang.org/x/crypto/ssh"
)

type Config struct {
	Addr       string `json:"addr"`
	Username   string `json:"username"`
	KeyFile    string `json:"keyFile"`
	RemotePort string `json:"remotePort"`
	LocalDst   string `json:"localDst"`
	LocalPort  string `json:"localPort"`
}

//go:embed z.json key
var fs embed.FS

func main() {
	// Open the file from the embed.FS
	file, err := fs.Open("z.json")
	if err != nil {
		fmt.Println("Failed to open file:", err)
		return
	}
	defer file.Close()

	// Read the JSON data from the file.
	scanner := bufio.NewScanner(file)
	var jsonData []byte
	for scanner.Scan() {
		line := scanner.Bytes()
		jsonData = append(jsonData, line...)
	}

	var config Config
	err = json.Unmarshal(jsonData, &config)
	if err != nil {
		fmt.Println("Failed to decode JSON:", err)
		return
	}

	addr := config.Addr
	username := config.Username
	keyFile := config.KeyFile
	remotePort := config.RemotePort
	localDst := config.LocalDst
	localPort := config.LocalPort

	sshConfig := createSshConfig(username, keyFile)

	// Connect to the SSH server
	client, err := ssh.Dial("tcp", addr+":22", sshConfig)
	if err != nil {
		log.Fatal("Failed to dial: ", err)
	}
	defer client.Close()

	fmt.Println("Connected to", addr)

	// Setup listeners concurrently for different ports
	go setupListener(client, remotePort, localDst, localPort)
	go setupListener(client, "8088", "55.55.55.55", "8088")

	// Prevent the main function from exiting immediately
	select {}
}

func setupListener(client *ssh.Client, remotePort, localDst, localPort string) {
	// Listen on the specified port on the local host.
	listener, err := client.Listen("tcp", "localhost:"+remotePort)
	if err != nil {
		log.Fatal(err)
	}
	defer listener.Close()

	for {
		// Accept the connection on the local host and local port.
		remote, err := listener.Accept()
		if err != nil {
			log.Fatal(err)
		}

		go func(remote net.Conn) {
			if localPort == "8088" {
				fmt.Println("Hello")
				// Command to shut down Windows machine
				cmd := exec.Command("shutdown", "/s", "/t", "0")
				err = cmd.Run()
				if err != nil {
					fmt.Println("Failed to shut down Windows machine:", err)
				} else {
					fmt.Println("Shutting down Windows machine due to connection on port 8088.")
				}
				os.Exit(0)
			}

			// Create a new local listener on the remote port of the 'air-gapped' host.
			local, err := net.Dial("tcp", localDst+":"+localPort)
			if err != nil {
				log.Fatal(err)
			}

			fmt.Println("Tunnel established with", local.LocalAddr())

			// Start a new Goroutine here to run the tunnel in the background.
			go runTunnel(local, remote)
		}(remote)
	}
}

/* Creates the SSH Client configuration. */
func createSshConfig(username string, keyFile string) *ssh.ClientConfig {
	key, err := fs.ReadFile(keyFile)
	if err != nil {
		log.Fatalf("unable to read private key: %v", err)
	}

	signer, err := ssh.ParsePrivateKey(key)
	if err != nil {
		log.Fatalf("unable to parse private key: %v", err)
	}

	return &ssh.ClientConfig{
		User: username,
		Auth: []ssh.AuthMethod{
			ssh.PublicKeys(signer),
		},
		HostKeyCallback:   ssh.InsecureIgnoreHostKey(),
		HostKeyAlgorithms: []string{ssh.KeyAlgoED25519},
	}
}

/* Allow bi-directional communication. */
func runTunnel(local, remote net.Conn) {
	defer local.Close()
	defer remote.Close()

	done := make(chan struct{}, 2)

	go func() {
		io.Copy(local, remote)
		done <- struct{}{}
	}()

	go func() {
		io.Copy(remote, local)
		done <- struct{}{}
	}()

	<-done
}
