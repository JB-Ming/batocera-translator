@echo off
REM Batocera 翻譯工具 - Windows 打包腳本
REM 
REM 使用方法: 直接雙擊此檔案執行

echo ========================================
echo Batocera 翻譯工具打包腳本
echo ========================================
echo.

REM 檢查是否安裝 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先安裝 Python 3.7+
    pause
    exit /b 1
)

echo [1/4] 檢查並安裝必要套件...
pip install -r requirements-gui.txt
if errorlevel 1 (
    echo [錯誤] 套件安裝失敗
    pause
    exit /b 1
)

echo.
echo [2/4] 清理舊的建置檔案...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/4] 開始打包 (使用 PyInstaller)...
pyinstaller batocera_translator.spec
if errorlevel 1 (
    echo [錯誤] 打包失敗
    pause
    exit /b 1
)

echo.
echo [4/4] 完成！
echo.
echo 執行檔位置: dist\Batocera翻譯工具.exe
echo.

REM 詢問是否開啟資料夾
set /p open="是否開啟 dist 資料夾? (Y/N): "
if /i "%open%"=="Y" (
    explorer dist
)

pause
