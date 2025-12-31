# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置
用於將 Batocera Gamelist 翻譯工具打包為 Windows 執行檔
"""

import sys
from pathlib import Path

# 專案根目錄
ROOT = Path(SPECPATH)

# 資源檔案（語系包等）
datas = [
    (str(ROOT / 'assets'), 'assets'),           # 圖示等資源
    (str(ROOT / 'language_packs'), 'language_packs'),  # 內建語系包
]

# 隱藏導入（動態載入的模組）
hiddenimports = [
    'googletrans',
    'httpx',
    'httpcore',
]

a = Analysis(
    ['main.py'],               # 主程式入口
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Batocera翻譯工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                # 不顯示控制台視窗
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,                    # 程式圖示（待補充）
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BatoceraTranslator',
)
