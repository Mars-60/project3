' Open_Atlas.vbs
' This script opens Atlas in your browser.
' Assign a keyboard shortcut to this file via its .lnk shortcut.

Dim atlasPath
atlasPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\frontend\atlas.html"

CreateObject("WScript.Shell").Run "explorer.exe """ & atlasPath & """", 0, False