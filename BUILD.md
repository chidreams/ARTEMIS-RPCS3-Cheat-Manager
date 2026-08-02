# Building ARTEMIS-RPCS3 Cheat Manager

This document explains how to build standalone versions of ARTEMIS-RPCS3 for Windows, Linux, and macOS.  
All builds use PyInstaller to create a single executable that does not require Python to be installed.

## Windows Build

Use the file named build_windows_exe.bat.  
Place the file in the same folder as cheat_manager.py.  
Double-click the file to begin the build.  
The finished program is located at dist/ARTEMIS.exe.

## Linux Build

Use the file named build_linux_exe.sh.  
Place the file in the same folder as cheat_manager.py.  
Run chmod +x build_linux_exe.sh.  
Run ./build_linux_exe.sh.  
The finished program is located at dist/ARTEMIS.

## macOS Build

Use the file named build_macos_app.sh.  
Place the file in the same folder as cheat_manager.py.  
Run chmod +x build_macos_app.sh.  
Run ./build_macos_app.sh.  
The finished program is located at dist/ARTEMIS.app.

## Optional Icons

Windows uses artemis.ico.  
macOS uses artemis.icns.  
Linux uses artemis.ico.  
Place the icon file next to cheat_manager.py before building.

## Output Files

All builds place the final executable inside the dist folder.  
The Artemis-Patches folder and import_patch.yml are created next to the executable when it is run.

## Requirements

Python 3 must be installed.  
PyInstaller is installed automatically during the build process.
