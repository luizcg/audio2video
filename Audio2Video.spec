# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Audio2Video Converter.
Generates a Windows executable with bundled FFmpeg.

Usage:
    pyinstaller Audio2Video.spec

Output:
    dist/Audio2Video/  (one-folder build)
"""

import sys
from pathlib import Path

block_cipher = None

# Project root
PROJECT_ROOT = Path(SPECPATH)

# Data files to include
datas = [
    # FFmpeg binaries (must be present in bin/ before building)
    (str(PROJECT_ROOT / 'bin' / 'ffmpeg.exe'), 'bin'),
    (str(PROJECT_ROOT / 'bin' / 'ffprobe.exe'), 'bin'),
    # License files
    (str(PROJECT_ROOT / 'LICENSES'), 'LICENSES'),
]

# Check if FFmpeg binaries exist (warn if not)
ffmpeg_path = PROJECT_ROOT / 'bin' / 'ffmpeg.exe'
ffprobe_path = PROJECT_ROOT / 'bin' / 'ffprobe.exe'
if not ffmpeg_path.exists() or not ffprobe_path.exists():
    print("\n" + "="*60)
    print("AVISO: ffmpeg.exe e/ou ffprobe.exe não encontrados em bin/")
    print("O build continuará, mas o executável não funcionará sem eles.")
    print("Baixe o FFmpeg de: https://www.gyan.dev/ffmpeg/builds/")
    print("="*60 + "\n")
    # Remove missing files from datas
    datas = [(src, dst) for src, dst in datas if Path(src).exists()]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name='Audio2Video',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI mode - no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if (PROJECT_ROOT / 'assets' / 'icon.ico').exists() else None,
    # Windows metadata
    version_info=None,  # Can add version info file later
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Audio2Video',
)
