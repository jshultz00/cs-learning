#!/bin/bash

# Author: Justin Shultz
# ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3 
# Lab: Persist on a Windows machine with a malicious user account
#  
# Description:
# This script simulates a scenario where an attacker uses a malicious user account to gain 
# unauthorized access to a Windows system via RDP. The script demonstrates the attacker 
# navigating through sensitive directories, creating a dummy file in a protected location to 
# simulate data manipulation, displaying the file’s contents, and then deleting it to cover 
# their tracks. The initial execution of whoami confirms the user context, ensuring that the 
# malicious account is operating with the expected permissions. This simulation showcases typical 
# adversary behavior involving persistence, reconnaissance, and cleanup actions on a compromised system.

# Read in common variables and functions.
source ../common.bash

# Open an RDP session to the target system using the malicious account credentials.
xfreerdp /u:john.smith /p:P@55w0rd! /v:172.16.0.102 /sec:nla /cert-ignore /f > /dev/null 2>&1 &
sleep 30

# Capture the window ID of the FreeRDP session.
get_window "FreeRDP: 172.16.0.102"
sleep 5

# Open the Start Menu to search for Command Prompt.
xdotool key --window ${rdpId} Ctrl+Escape
sleep 3
xdotool type --window ${rdpId} 'cmd'
sleep 3

# Simulate pressing Ctrl+Shift+Enter to run Command Prompt as an administrator.
xdotool key --window ${rdpId} ctrl+shift+Return
sleep 5

# Enter whoami to display the current user context.
echo "Checking current user context."
xdotool type --window ${rdpId} "whoami"
sleep 3
xdotool key --window ${rdpId} Return
sleep 5

# Navigate through sensitive directories.
echo "Navigating through sensitive directories."
xdotool type --window ${rdpId} "cd C:\\Windows\\System32"
sleep 3
xdotool key --window ${rdpId} Return
sleep 3
xdotool type --window ${rdpId} "dir"
sleep 3
xdotool key --window ${rdpId} Return
sleep 5

xdotool type --window ${rdpId} "cd ..\\..\\ProgramData"
sleep 3
xdotool key --window ${rdpId} Return
sleep 3
xdotool type --window ${rdpId} "dir"
sleep 3
xdotool key --window ${rdpId} Return
sleep 5

xdotool type --window ${rdpId} "cd C:\\Windows\\Temp"
sleep 3
xdotool key --window ${rdpId} Return
sleep 3
xdotool type --window ${rdpId} "dir"
sleep 3
xdotool key --window ${rdpId} Return
sleep 5

# Create a dummy file in the specified directory.
echo "Creating a dummy file to simulate malicious activity."
xdotool type --window ${rdpId} "echo 'Sensitive data' > C:\\Windows\\System32\\a.txt"
sleep 3
xdotool key --window ${rdpId} Return
sleep 5

# Display the contents of the dummy file.
echo "Displaying the contents of the dummy file."
xdotool type --window ${rdpId} "type C:\\Windows\\System32\\a.txt"
sleep 3
xdotool key --window ${rdpId} Return
sleep 5

# Simulate using the malicious account to cover tracks by deleting the dummy file.
echo "Deleting the dummy file to cover tracks."
xdotool type --window ${rdpId} "del C:\\Windows\\System32\\a.txt"
sleep 3
xdotool key --window ${rdpId} Return
sleep 5

# Exit the command prompt.
xdotool type --window ${rdpId} 'exit'
sleep 3
xdotool key --window ${rdpId} Return
sleep 5

# Demonstrate access and exit the RDP session gracefully.
echo "Access demonstration complete, closing the RDP session."

# Kill the RDP session.
killall xfreerdp
sleep 5

echo "RDP session closed."
