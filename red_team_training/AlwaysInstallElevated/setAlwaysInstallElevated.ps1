# Name: Justin Shultz
# Student ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
# Lab: Write a PS script that enables the AlwaysInstallElevated registry key

# Thank you for taking the time to grade this submission!

# Check for AlwaysInstallElevated in HKCU
$hkcuKey = Get-ItemProperty -Path "HKCU:\Software\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue

# Check for AlwaysInstallElevated in HKLM
$hklmKey = Get-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue

if (($hkcuKey -and $hkcuKey.AlwaysInstallElevated -eq 1) -or ($hklmKey -and $hklmKey.AlwaysInstallElevated -eq 1)) {
    Write-Output "AlwaysInstallElevated is already enabled."
} else {
    # Set AlwaysInstallElevated to 1 in HKCU
    New-ItemProperty -Path "HKCU:\Software\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -Value 1 -PropertyType DWORD -Force
    
    # Set AlwaysInstallElevated to 1 in HKLM
    New-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -Value 1 -PropertyType DWORD -Force
}


