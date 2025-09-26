# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the base directory (parent of windows folder)
import os
spec_file = os.path.abspath(SPEC)
base_dir = Path(spec_file).parent.parent

# Add source directory to path
sys.path.insert(0, str(base_dir / 'src'))

block_cipher = None

a = Analysis(
    [str(base_dir / 'src' / 'main.py')],
    pathex=[str(base_dir / 'src')],
    binaries=[],
    datas=[
        (str(base_dir / 'data'), 'data'),  # Include data directory
        (str(base_dir / 'assets'), 'assets'),  # Include assets
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'json',
        'pathlib',
        'math',
        'datetime',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='floating-cheatsheets',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(base_dir / 'assets' / 'icon.ico'),  # App icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='floating-cheatsheets',
)