#!/usr/bin/bash


# Displays a dialog with a message and a timeout indicator. The second value
# is the amount of time to display the message.
# A timeout indicator bar will display at the bottom of the dialog box."

if [[ ${1} == "" || ${2} == "" ]]; then


	echo ""
	echo "Usage: yad_msg.bash message[string] time[int]"
	
	echo ""
	echo "yad_msg.bash \"Hello\nthere.\" 3"
	
	echo ""
	echo "The above message will display \"Hello\" and \"there\" on separate lines for 3 seconds and exit."
	echo ""

	exit 1

fi
yad --no-buttons --text="##########################################################\n\n${1}.\n\n##########################################################" --timeout=${2} --timeout-indicator=bottom
