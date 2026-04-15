Option Explicit

Dim shell, fso, scriptDir, batPath
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batPath = scriptDir & "\new_help.bat"

' Launches the existing BAT file from its own folder.
shell.Run """" & batPath & """", 1, False
