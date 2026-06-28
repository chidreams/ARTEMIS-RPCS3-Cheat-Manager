#!/bin/bash

# ============================================================================
#  Build ARTEMIS into a single standalone Linux executable
#  (the finished binary runs on any Linux system WITHOUT Python installed)
#
#  HOW TO USE:
#    1. Place this file in the same folder as cheat_manager.py
#    2. (optional) place an icon named artemis.ico in the same folder
#    3. Run:  chmod +x build_linux_exe.sh
#    4. Run:  ./build_linux_exe.sh
# ============================================================================

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found."
    echo "Install Python 3 using your package manager and try again."
    exit 1
fi

echo "Installing or updating PyInstaller"
python3 -m pip install --upgrade pyinstaller
if [ $? -ne 0 ]; then
    echo "pip install failed."
    exit 1
fi

ICON=""
if [ -f "artemis.ico" ]; then
    ICON="--icon artemis.ico"
fi

echo
echo "Building ARTEMIS (this may take a moment)"
python3 -m PyInstaller --onefile --windowed --name ARTEMIS $ICON cheat_manager.py
if [ $? -ne 0 ]; then
    echo "Build failed."
    exit 1
fi

echo
echo "Done. Your standalone program is located at: dist/ARTEMIS"
echo "You may copy the binary anywhere. No Python installation is required."
echo "The Artemis-Patches folder and import_patch.yml will be created next to it."
