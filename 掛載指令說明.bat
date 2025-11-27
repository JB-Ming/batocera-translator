@echo off
chcp 65001 > nul
echo ========================================
echo   Batocera userdata 分區掛載指令
echo ========================================
echo.
echo 【重要】此指令需要以系統管理員權限執行
echo.
echo ========================================
echo   步驟 1: 掛載分區
echo ========================================
echo.
echo 執行以下指令掛載 Batocera userdata 分區:
echo.
echo   wsl --mount \\.\PHYSICALDRIVE2 --partition 2
echo.
echo 說明:
echo   - PHYSICALDRIVE2 是您的 Transcend 外接硬碟
echo   - partition 2 是 userdata 分區 (228GB)
echo.
echo ========================================
echo   步驟 2: 驗證掛載
echo ========================================
echo.
echo 掛載後，在 WSL 中執行:
echo.
echo   wsl ls /mnt/wsl/PHYSICALDRIVE2p2
echo.
echo 或查看 roms 資料夾:
echo.
echo   wsl ls /mnt/wsl/PHYSICALDRIVE2p2/roms
echo.
echo   wsl ls /mnt/wsl/PHYSICALDRIVE2p2/share/roms
echo.
echo ========================================
echo   步驟 3: 在 Windows 中存取
echo ========================================
echo.
echo Windows 路徑 (使用檔案總管開啟):
echo.
echo   \\wsl$\Ubuntu\mnt\wsl\PHYSICALDRIVE2p2
echo.
echo 或 roms 資料夾:
echo.
echo   \\wsl$\Ubuntu\mnt\wsl\PHYSICALDRIVE2p2\roms
echo.
echo   \\wsl$\Ubuntu\mnt\wsl\PHYSICALDRIVE2p2\share\roms
echo.
echo ========================================
echo   完成後卸載 (重要！)
echo ========================================
echo.
echo   wsl --unmount \\.\PHYSICALDRIVE2
echo.
echo ========================================
echo.
echo 按任意鍵關閉...
pause > nul
