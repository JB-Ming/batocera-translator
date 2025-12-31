#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batocera Gamelist 翻譯工具 - 主程式入口

這是程式的進入點，負責初始化應用程式並啟動主視窗。
"""
import sys
import os

# 確保可以找到 src 模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui import MainWindow


def main():
    """主程式進入點"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    
    # 啟用高 DPI 支援
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
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
