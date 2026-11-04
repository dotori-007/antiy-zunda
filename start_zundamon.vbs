Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDir

pythonExe = "pythonw.exe"
If fso.FileExists(currentDir & "\venv\Scripts\pythonw.exe") Then
    pythonExe = """" & currentDir & "\venv\Scripts\pythonw.exe"""
ElseIf fso.FileExists(currentDir & "\.venv\Scripts\pythonw.exe") Then
    pythonExe = """" & currentDir & "\.venv\Scripts\pythonw.exe"""
ElseIf fso.FileExists("C:\2026591001\Python_3.10.11_64\pythonw.exe") Then
    pythonExe = """C:\2026591001\Python_3.10.11_64\pythonw.exe"""
End If

WshShell.Run pythonExe & " """ & currentDir & "\app.py""", 0, False
