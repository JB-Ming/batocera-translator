#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batocera Gamelist 翻譯工具 - 主程式入口

這是程式的進入點，負責初始化應用程式並啟動主視窗。
"""
from src.ui import MainWindow
import sys
import os
from pathlib import Path

# 確保可以找到 src 模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _ensure_config_dir():
    """
    確保 config 資料夾存在（在任何其他操作之前）

    這是為了解決 PyInstaller 打包後，config 目錄可能未被正確包含的問題。
    在程式啟動的最早階段就建立必要的目錄結構。
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包後的執行檔目錄
        app_root = Path(sys.executable).parent
    else:
        # 開發模式
        app_root = Path(__file__).parent

    # 建立 config 目錄結構
    config_dir = app_root / 'config'
    (config_dir / 'dictionaries').mkdir(parents=True, exist_ok=True)
    (config_dir / 'cache').mkdir(parents=True, exist_ok=True)
    (config_dir / 'backups').mkdir(parents=True, exist_ok=True)


# 在 import 其他模組之前就確保 config 目錄存在
_ensure_config_dir()


def main():
    """主程式進入點"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt

    # 啟用高 DPI 支援
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(
            Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(
            Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # 建立應用程式
    app = QApplication(sys.argv)
    app.setApplicationName("Batocera Gamelist 翻譯工具")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("BatoceraTranslator")

    # 設定樣式
    app.setStyle("Fusion")

    # 建立並顯示主視窗
    window = MainWindow()
    window.show()

    # 執行應用程式
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
