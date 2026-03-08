# **Usage Manual: Write VBS Word macro that downloads a PE from the Internet and runs it**

## **Introduction**

This document serves as a usage manual for a Word macro designed to create a hidden folder in the Windows startup directory, exempt the folder from Windows Defender scanning, download a specified file into that folder, and execute the file. The macro is intended for cyber operators who need to execute files stealthily on target systems with elevated privileges.

## **Purpose and Application**

The primary purpose of this macro is to automate the process of downloading and executing a file (e.g., `splunkforwarder.exe`) on a Windows system, while maintaining a low profile by using a hidden folder and excluding the folder from Windows Defender scanning. This can be particularly useful in Red Team operations, penetration testing, or simulated adversary activities.

## **Prerequisites**

Before using this macro, ensure the following:

1. **Microsoft Word:** The macro should be embedded in a Word document.
2. **Administrative Privileges:** The macro requires administrative privileges to run certain commands (e.g., creating a hidden folder, modifying Windows Defender settings).
3. **Target System Setup:** The target system should allow macros to run. Ensure that macro security settings are configured appropriately, and that the system is prepared for potential testing.

## **How to Use the Macro**

### **Step 1: Embedding the Macro in a Word Document**

1. Open Microsoft Word and press `ALT + F11` to open the VBA editor.
2. In the VBA editor, insert a new module by selecting `Insert > Module`.
3. Copy and paste the provided macro code into the module.
4. Save the document as a macro-enabled document (`.docm`).

### **Step 2: Distributing the Word Document**

1. Share the `.docm` document with the target user or system.
2. Ensure that the recipient has enabled macros in their Microsoft Word settings.

### **Step 3: Executing the Macro**

1. When the document is opened, the macro will automatically execute if the user has enabled macros.
2. The macro will check for administrative privileges. If it does not have them, it will restart itself with elevated privileges.
3. Once running with the required privileges, the macro will:
   - Create a hidden folder in the startup directory.
   - Exclude the folder from Windows Defender scanning.
   - Download the specified file (`splunkforwarder.exe`) into the hidden folder.
   - Execute the downloaded file.

### **Step 4: Testing the Macro**

1. **Test in a Controlled Environment:** Before deploying in a live environment, test the macro in a controlled, isolated environment to ensure it behaves as expected.
2. **Check for Elevated Privileges:** Verify that the macro correctly restarts with administrative privileges if it doesn't have them initially.
3. **Validate File Exclusion:** Confirm that the folder is created as hidden and is excluded from Windows Defender scans by checking the exclusion list in Windows Defender.
4. **Monitor Execution:** Ensure the file is downloaded into the hidden folder and executed without triggering any security alerts.

## **Use Cases**

- **Stealth Operations:** Use this macro when you need to download and execute files on a target system without triggering security alerts.
- **Red Team Exercises:** Deploy this macro during Red Team engagements to simulate advanced adversary techniques.
- **Persistence Mechanisms:** The hidden folder in the startup directory ensures that the downloaded executable will run every time the system starts, providing persistence.

## **Troubleshooting**

- **Macro Does Not Run:** Ensure that macros are enabled in Word’s security settings.
- **Administrator Privileges Not Acquired:** Check if the system’s UAC settings are preventing the macro from restarting with elevated privileges.
- **File Not Downloading:** Verify the URL and ensure that the target system has network access to the specified URL. The URL used in this scenario is a predefined attacker C2, which might need to be changed according to the testing setup.

---

**Note:** The above guide is intended for educational and professional use within legal and ethical boundaries. Always ensure appropriate permissions are obtained before deploying this macro in any environment.
