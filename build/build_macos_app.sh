#!/bin/bash

# ============================================================================
#  Build ARTEMIS into a macOS .app bundle and standalone binary
#  (runs on macOS without requiring Python installed)
#
#  HOW TO USE:
#    1. Place this file in the same folder as cheat_manager.py
#    2. (optional) place an icon named artemis.icns in the same folder
#    3. Run:  chmod +x build_macos_app.sh
#    4. Run:  ./build_macos_app.sh
# ============================================================================

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found."
    echo "Install Python 3 from python.org or Homebrew and try again."
    exit 1
fi

echo "Installing or updating PyInstaller"
python3 -m pip install --upgrade pyinstaller
if [ $? -ne 0 ]; then
    echo "pip install failed."
    exit 1
fi

ICON=""
if [ -f "artemis.icns" ]; then
    ICON="--icon artemis.icns"
fi

echo
echo "Building ARTEMIS.app (this may take a moment)"
python3 -m PyInstaller --onefile --windowed --name ARTEMIS $ICON cheat_manager.py
if [ $? -ne 0 ]; then
    echo "Build failed."
    exit 1
fi

echo
echo "Done. Your macOS application is located at: dist/ARTEMIS.app"
echo "You may copy the .app anywhere. No Python installation is required."
echo "The Artemis-Patches folder and import_patch.yml will be created next to it."
