<#
    Author: Justin Shultz
    ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
    Lab: Write a PS script that creates an unquoted Windows Service

    Description:
    This script creates a service vulnerable to an unquoted Windows service attack.
#>

# Define service details
$serviceName = "CoolService"
$servicePath = "C:\stuff\cool stuff\service.exe"

# Create the executable path (dummy executable)
New-Item -Path "C:\stuff" -ItemType Directory -Force
icacls "c:\stuff" /grant everyone:F
New-Item -Path "C:\stuff\cool stuff" -ItemType Directory -Force
Invoke-WebRequest -Uri "http://9.53.99.47/service.exe" -OutFile $servicePath

# Register the service with an unquoted path
New-Service -Name $serviceName -BinaryPathName $servicePath -StartupType Automatic
