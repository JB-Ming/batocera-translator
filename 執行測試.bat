@echo off
REM 執行單元測試

cd /d "%~dp0"
echo ========================================
echo 執行單元測試
echo ========================================
echo.

python -m unittest discover tests -v

echo.
pause
