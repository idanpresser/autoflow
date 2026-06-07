# -*- mode: python ; coding: utf-8 -*-

# ──── Tesseract-OCR bundling ────────────────────────────────────────────────
# To bundle Tesseract with the build, set TESSERACT_PATH to the install dir,
# e.g. r'C:\Program Files\Tesseract-OCR', and uncomment the datas/binaries
# entries below so PyInstaller copies the engine into the output folder.
# TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR'
# ────────────────────────────────────────────────────────────────────────────

# ──── Icon placeholder ──────────────────────────────────────────────────────
# Set ICON_PATH to an .ico file to brand the executable, then pass
# icon=ICON_PATH in the EXE() call below.
# ICON_PATH = 'assets/autoflow.ico'
# ────────────────────────────────────────────────────────────────────────────

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    # To bundle Tesseract, uncomment the next two lines and comment the empty ones:
    # binaries=[(os.path.join(TESSERACT_PATH, 'tesseract.exe'), 'tesseract')],
    # datas=[(os.path.join(TESSERACT_PATH, 'tessdata'), 'tesseract/tessdata')],
    binaries=[],
    datas=[],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
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
    name='autoflow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    # icon=ICON_PATH,  # Uncomment after setting ICON_PATH above
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='autoflow',
)
