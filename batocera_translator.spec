# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包設定檔

使用方法:
    pyinstaller batocera_translator.spec
"""

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('translations', 'translations'),  # 包含語系包目錄
        ('config.json', '.'),              # 包含預設設定
        ('local_cache.json', '.'),         # 包含快取範本
    ],
    hiddenimports=[
        'beautifulsoup4',
        'bs4',
        'requests',
        'lxml',
        'googletrans',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Batocera翻譯工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不顯示命令列視窗
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico'  # 如果有圖示檔案，取消註解
)
