Dim folder
folder = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
CreateObject("WScript.Shell").Run "cmd /c """ & folder & "start-server.bat""", 0, False
