@echo off
rem Baut EINMALIG eine eigenstaendige FlashTracker.exe (kein Python noetig
rem zum spaeteren Starten). Danach liegt sie in:  dist\FlashTracker.exe
cd /d "%~dp0"

echo Installiere PyInstaller (falls noetig)...
python -m pip install pyinstaller

echo Baue FlashTracker.exe ...
python -m PyInstaller --noconsole --onefile --name FlashTracker ^
  --add-data "sounds;sounds" ^
  --add-data "champion_words.txt;." ^
  main.py

echo.
echo Fertig! Die EXE liegt in:  dist\FlashTracker.exe
echo Du kannst sie auf den Desktop ziehen und per Doppelklick starten.
pause
