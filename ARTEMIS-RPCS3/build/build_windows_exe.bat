@echo off
REM ===========================================================================
REM  Build ARTEMIS into a single standalone Windows .exe
REM  (the finished .exe runs on any Windows PC WITHOUT Python installed)
REM
REM  HOW TO USE:
REM    1. Put this .bat in the SAME folder as cheat_manager.py
REM    2. (optional) drop an icon named  artemis.ico  in that folder
REM    3. Double-click this file
REM    4. When it finishes, your program is:   dist\ARTEMIS.exe
REM ===========================================================================
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python was not found on PATH.
    echo     Install Python 3 from https://www.python.org/downloads/
    echo     and tick "Add Python to PATH" during setup, then run this again.
    pause
    exit /b 1
)

echo === Installing / updating PyInstaller ===
python -m pip install --upgrade pyinstaller
if errorlevel 1 ( echo [!] pip install failed. & pause & exit /b 1 )

set ICON=
if exist "artemis.ico" set ICON=--icon artemis.ico

echo.
echo === Building ARTEMIS.exe (this takes a minute) ===
python -m PyInstaller --onefile --windowed --name ARTEMIS %ICON% cheat_manager.py
if errorlevel 1 ( echo [!] Build failed. & pause & exit /b 1 )

echo.
echo ===========================================================================
echo  DONE.  Your standalone program is:   dist\ARTEMIS.exe
echo  You can copy that single .exe anywhere - no Python needed to run it.
echo  (The Artemis-Patches folder and import_patch.yml are created next to it.)
echo ===========================================================================
pause
endlocal
