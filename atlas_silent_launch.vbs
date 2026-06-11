' Launches Atlas completely silently - no window, no flash, nothing visible
Dim WshShell, AtlasDir, PythonExe, Script

AtlasDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)
PythonExe = AtlasDir & "\venv\Scripts\pythonw.exe"
Script = AtlasDir & "\start_atlas.py"

Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = AtlasDir

' pythonw.exe is the windowless version of python.exe - no terminal ever appears
WshShell.Run Chr(34) & PythonExe & Chr(34) & " " & Chr(34) & Script & Chr(34), 0, False
