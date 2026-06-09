Set WshShell = CreateObject("WScript.Shell")
Dim folder
folder = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
WshShell.Run "cmd /c """ & folder & "start-server.bat""", 0, False
