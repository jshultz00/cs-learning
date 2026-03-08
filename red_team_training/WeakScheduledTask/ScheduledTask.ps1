<#
    Author: Justin Shultz
    ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
    Lab: Write a PS script that creates a modifiable Scheduled Task file

    Description:
    This script creates an insecure scheduled task that is modifiable
    by any user due to its weak permissions.
#>

# Define the path of the executable or batch file
$filePath = "C:\Temp\VulnerableTask.bat"

# Create the batch file (or modify the path to an existing executable)
New-Item -Path $filePath -ItemType File -Force
Add-Content -Path $filePath -Value "@echo off`nrem Placeholder script - vulnerable to editing."

# Set permissions on the batch file using icacls
icacls $filePath /grant Everyone:F /T /C
Write-Output "Permissions set for $filePath using icacls."

# Define the scheduled task name
$taskName = "VulnerableTask"

# Check if the scheduled task already exists, and remove it if it does
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Output "Existing scheduled task '$taskName' removed."
}

# Create the scheduled task to run the file with SYSTEM privileges
$action = New-ScheduledTaskAction -Execute $filePath
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount

# Register the scheduled task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal
Write-Output "Scheduled task '$taskName' created."

# Define the path to the scheduled task in the system tasks directory
$taskPath = "C:\Windows\System32\Tasks\$taskName"

# Verify the task path exists before setting permissions
if (Test-Path $taskPath) {
    # Set permissions on the scheduled task using icacls
    icacls $taskPath /grant Everyone:F /T /C
    Write-Output "Permissions set for the scheduled task '$taskName' using icacls."
} else {
    Write-Output "Error: Task file '$taskPath' not found. Permissions could not be set."
}

Write-Output "Script completed. Any user can edit $filePath and the scheduled task."
