' Doppelklick zum Starten — komplett ohne sichtbares Konsolenfenster.
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")
sh.CurrentDirectory = fso.GetParentFolderName(WScript.ScriptFullName)
sh.Run "pythonw main.py", 0, False
