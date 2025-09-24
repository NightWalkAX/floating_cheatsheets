#!/bin/bash

# Manual build script for testing locally before pushing to GitHub

set -e

echo "=== Manual Build Script for Floating CheatSheets ==="
echo "This script will build both Linux (.deb) and Windows (.exe) packages locally"
echo ""

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Importar utilidades de versión
source "$(dirname "$0")/version_utils.sh"

# Mostrar información de versión
PROJECT_VERSION=$(get_project_version)
echo "Versión del proyecto: ${PROJECT_VERSION}"
echo "Timestamp de build: $(get_build_timestamp)"
echo "Git hash: $(get_git_hash)"
echo ""

# Build Linux package
echo "Building Linux package..."
if [ -f "build_deb.sh" ]; then
    chmod +x build_deb.sh
    ./build_deb.sh
    echo "✅ Linux .deb package created"
else
    echo "❌ build_deb.sh not found"
fi

# Build Windows package (if on Linux with Wine or on Windows with Git Bash)
echo ""
echo "Building Windows package..."
if [ -d "windows" ] && [ -f "windows/build_windows.sh" ]; then
    chmod +x windows/build_windows.sh
    (cd windows && ./build_windows.sh)
    if [ $? -eq 0 ]; then
        echo "✅ Windows build script executed successfully"
        echo "Note: To create the installer, you need NSIS installed and run: makensis windows/installer.nsi"
    else
        echo "❌ Windows build failed"
    fi
else
    echo "❌ Windows build files not found"
fi

echo ""
echo "=== Build Summary ==="
echo "Linux package: $(ls -1 *.deb 2>/dev/null || echo 'Not found')"
echo "Windows executable: $(ls -1 windows/dist/floating-cheatsheets/floating-cheatsheets* 2>/dev/null || echo 'Not found')"
echo ""
echo "To test the GitHub Actions workflow locally, you can use:"
echo "  act -j build-linux"
echo "  act -j build-windows"
echo ""
echo "Done!"