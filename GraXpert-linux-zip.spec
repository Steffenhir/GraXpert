# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['./src/gui.py'],
    pathex=[],
    binaries=[],
    datas=[('./img/*', './img/'), ('./forest-dark.tcl', './'), ('./forest-dark/*', './forest-dark/')],
    hiddenimports=['PIL._tkinter_finder', 'tkinter'],
    hookspath=['./releng'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
    cipher=block_cipher)

exe = EXE(pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GraXpert',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None , icon='./img/Icon.ico')
coll = COLLECT(
    exe,
    a.binaries,
    Tree('locales', prefix='locales/'),
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GraXpert-linux',
)
