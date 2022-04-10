# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('./forest-dark.tcl', './'), ('./img/HELP.png', './img/'), ('./img/GraXpert_LOGO_Hauptvariante.png', './img/'), ('./img/Icon.ico', './img/'), ('./forest-dark/*', './forest-dark')]
binaries = []
hiddenimports = ["*PIL._tkinter_finder'"]
tmp_ret = collect_all('pykrige')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


block_cipher = None


a = Analysis(['src\\gui.py'],
             pathex=[],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='GraXpert-win64',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='img\\Icon.ico')
