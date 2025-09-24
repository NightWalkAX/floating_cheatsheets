# Developer Documentation

## Building Releases

### Automatic Builds (GitHub Actions)

Every push to the `main` branch triggers an automated build process that:

1. **Linux Build**: Creates a `.deb` package using the existing `build_deb.sh` script
2. **Windows Build**: Creates an executable using PyInstaller and an installer using NSIS
3. **Release**: Automatically creates/updates a GitHub release tagged as "latest" with both files

### Manual Local Builds

#### Prerequisites

**Linux:**
- Python 3.10+
- Debian build tools: `sudo apt-get install build-essential debhelper devscripts`
- For icon conversion: `sudo apt-get install imagemagick`

**Windows:**
- Python 3.10+
- PyInstaller: `pip install pyinstaller`
- NSIS (for installer creation)

#### Build Commands

```bash
# Build everything (Linux + Windows preparation)
./build_all.sh

# Linux only
./build_deb.sh

# Windows only (from windows/ directory)
cd windows
./build_windows.sh
makensis installer.nsi  # Requires NSIS
```

## Release Process

### Automatic Release (Recommended)

1. Make your changes
2. Commit and push to `main` branch
3. GitHub Actions will automatically:
   - Build both Linux and Windows versions
   - Create/update the "latest" release
   - Upload both `.deb` and `.exe` files

### Manual Release

If you need to create a manual release:

1. Build packages locally using `./build_all.sh`
2. Create a new GitHub release
3. Upload the generated files:
   - `floating-cheatsheets_1.0.0_all.deb`
   - `windows/floating-cheatsheets-1.0.0-setup.exe`

## Project Structure

```
floating_cheatsheets/
├── src/                      # Python source code
├── data/                     # Default data files
├── assets/                   # Icons and resources
├── debian/                   # Debian packaging files
├── windows/                  # Windows build configuration
│   ├── build_windows.spec   # PyInstaller configuration
│   ├── installer.nsi        # NSIS installer script
│   └── build_windows.sh     # Build script
├── .github/workflows/        # GitHub Actions CI/CD
│   └── release.yml          # Main workflow
├── setup/                   # Manual installation scripts
├── build_deb.sh            # Linux build script
├── build_all.sh            # Combined build script
├── requirements.txt        # Python dependencies
└── LICENSE                 # MIT License
```

## Configuration Files

### PyInstaller (build_windows.spec)
- Configures Windows executable creation
- Includes data files and assets
- Sets application icon and metadata

### NSIS Installer (installer.nsi)
- Creates Windows installer
- Sets up shortcuts and registry entries
- Includes uninstaller

### GitHub Actions (release.yml)
- Multi-platform builds (Ubuntu for Linux, Windows for Windows)
- Automatic artifact uploading
- Release creation with proper versioning

## Troubleshooting

### Common Issues

1. **Icon conversion fails**: Install ImageMagick or manually convert `assets/icon.png` to `assets/icon.ico`
2. **NSIS not found**: Install NSIS from https://nsis.sourceforge.io/
3. **PyInstaller issues**: Ensure all dependencies are in `requirements.txt`
4. **GitHub Actions permissions**: Ensure repository has write permissions for releases

### Testing Locally

Use [act](https://github.com/nektos/act) to test GitHub Actions locally:

```bash
# Test Linux build
act -j build-linux

# Test Windows build (requires Windows runner)
act -j build-windows
```

## Version Management

Update version in these files when releasing:
- `.github/workflows/release.yml` (APP_VERSION)
- `windows/installer.nsi` (APP_VERSION)
- `debian/changelog`
- Any hardcoded version strings

## Dependencies

### Runtime Dependencies (requirements.txt)
- tkinter (usually included with Python)
- Standard library modules only

### Build Dependencies
- PyInstaller (Windows builds)
- Debian build tools (Linux builds)
- NSIS (Windows installer)
- ImageMagick (icon conversion)