# -*- mode: python ; coding: utf-8 -*-
# dormitory.spec — PyInstaller build spec for Dormitory System (ONEFILE mode)

import os

block_cipher = None

ROOT = os.path.abspath('.')

a = Analysis(
    ['main.py'],
    pathex=[ROOT],
    binaries=[],
    datas=[
        ('dormitory.db', '.'),
        ('icons', 'icons'),
        ('pdf', 'pdf'),
        ('pdf_text', 'pdf_text'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSvg',
        'PySide6.QtPrintSupport',
        'sqlite3',
        'hashlib',
        'resources_rc',
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

# --onefile: tüm bağımlılıklar tek EXE içinde
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,      # <-- binaries dahil
    a.zipfiles,      # <-- zipfiles dahil
    a.datas,         # <-- datas dahil
    [],
    name='DormitorySystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # GUI mod, konsol penceresi yok
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
