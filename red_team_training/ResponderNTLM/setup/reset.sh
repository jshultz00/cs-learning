#!/bin/bash

source env_vars.bash

# Kill Responder
echo "[+] Killing Responder..."
sudo pkill -f "responder" 2>/dev/null
tmux kill-window -t "Responder" 2>/dev/null || true

# Kill msfconsole
echo "[+] Killing msfconsole..."
sudo pkill -f "msfconsole" 2>/dev/null
sudo pkill -f "msfrpc" 2>/dev/null

# Delete local artifacts
echo "[+] Deleting local artifacts..."
rm -f test.scf
rm -f "$PayloadName"
sudo rm -f /srv/salt/test.scf

# Clear Responder logs
echo "[+] Clearing Responder logs..."
sudo find /usr/share/responder/logs/ -type f ! -name "*.log" -delete
sudo truncate -s 0 /usr/share/responder/logs/Responder-Session.log
sudo truncate -s 0 /usr/share/responder/logs/Poisoners-Session.log
sudo truncate -s 0 /usr/share/responder/logs/Analyzer-Session.log
sudo truncate -s 0 /usr/share/responder/logs/Config-Responder.log
sleep 2

# Kill any meterpreter sessions on the target
echo "[+] Terminating payload process on target..."
sudo salt "$TargetSaltName" cmd.run "Get-Process -Name '${PayloadName%.*}' -ErrorAction SilentlyContinue | Stop-Process -Force" shell='powershell'
sleep 2

# Delete payload from target machine
echo "[+] Deleting payload from target machine ($TargetSaltName)..."
sudo salt "$TargetSaltName" cmd.run "Remove-Item -Force 'C:\\Users\\$TargetUsername\\Downloads\\$PayloadName' -ErrorAction SilentlyContinue" shell='powershell'
sleep 2

# Delete SCF from file share
echo "[+] Deleting SCF file from file share..."
sudo salt "$TargetSaltName" cmd.run "Remove-Item -Force '\\\\hn-files\\shares\\test.scf' -ErrorAction SilentlyContinue" shell='powershell' runas='holey\administrator' password='P@55w0rd_2022'
sleep 2

echo "[+] Reset complete."
