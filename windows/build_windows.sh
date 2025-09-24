#!/bin/bash

# Windows Build Script for Floating CheatSheets
# This script creates a Windows executable and installer

set -e

echo "Building Floating CheatSheets for Windows..."

# Importar utilidades de versión desde el directorio padre
source "$(dirname "$0")/../version_utils.sh"

# Obtener información de versión
PROJECT_VERSION=$(get_project_version)
BUILD_TIMESTAMP=$(get_build_timestamp)
GIT_HASH=$(get_git_hash)

echo "Versión del proyecto: ${PROJECT_VERSION}"
echo "Build timestamp: ${BUILD_TIMESTAMP}"
echo "Git hash: ${GIT_HASH}"

# Create windows directory if it doesn't exist
mkdir -p windows/dist

# Check if we're in a virtual environment, if not create one
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "Installing build dependencies..."
pip install --upgrade pip
pip install pyinstaller

# Install application dependencies (if requirements.txt exists)
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Convert PNG icon to ICO format for Windows
if command -v convert &> /dev/null; then
    echo "Converting icon to ICO format..."
    convert ../assets/icon.png -resize 256x256 ../assets/icon.ico
else
    echo "Warning: ImageMagick not found. Using existing icon.ico or PNG as fallback."
    # Check if ICO exists, if not copy PNG as fallback
    if [ ! -f "../assets/icon.ico" ]; then
        cp ../assets/icon.png ../assets/icon.ico
    fi
fi

# Build the executable
echo "Building Windows executable..."
pyinstaller build_windows.spec --clean --noconfirm

# Verify the build was successful
if [ ! -f "dist/floating-cheatsheets/floating-cheatsheets" ] && [ ! -f "dist/floating-cheatsheets/floating-cheatsheets.exe" ]; then
    echo "ERROR: Build failed - executable not found!"
    exit 1
fi

echo "Build completed successfully!"
echo "Executable created at: windows/dist/floating-cheatsheets/"

# Instructions for creating installer
echo ""
echo "To create the installer:"
echo "1. Install NSIS (Nullsoft Scriptable Install System)"
echo "2. Run: makensis installer.nsi"
echo "3. The installer will be created as: floating-cheatsheets-1.0.0-setup.exe"