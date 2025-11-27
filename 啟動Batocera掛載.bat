@echo off
chcp 65001 > nul
echo ===================================
echo   Batocera 磁碟自動掛載工具
echo ===================================
echo.
echo 正在啟動...
echo.

REM 以系統管理員權限執行
python detect_batocera.py

echo.
echo 按任意鍵繼續...
pause > nul
