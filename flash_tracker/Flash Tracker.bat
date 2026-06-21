@echo off
rem Doppelklick zum Starten — wechselt in den Ordner und startet ohne Konsole.
cd /d "%~dp0"
start "" pythonw main.py
