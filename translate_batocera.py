#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batocera 遊戲清單批次翻譯工具
自動掃描 Batocera roms 目錄並翻譯所有平台的 gamelist.xml
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from translator import GamelistTranslator

# 載入配置
def load_config():
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 取得 Batocera roms 路徑
def get_batocera_path(config):
    batocera_path = config.get('batocera_mount_path', '')
    
    # 如果未設定,嘗試從 WSL 掛載點取得
    if not batocera_path:
        wsl_path = r"\\wsl$\Ubuntu\mnt\wsl\PHYSICALDRIVE2p2\roms"
        if os.path.exists(wsl_path):
            batocera_path = wsl_path
        else:
            print("錯誤: 找不到 Batocera roms 路徑")
            print(f"請確認是否已掛載 Batocera 分區,或在 config.json 中設定 batocera_mount_path")
            return None
    
    # 驗證路徑存在
    if not os.path.exists(batocera_path):
        print(f"錯誤: Batocera 路徑不存在: {batocera_path}")
        return None
    
    return batocera_path

# 掃描所有平台
def scan_platforms(roms_path):
    """掃描 roms 目錄下所有包含 gamelist.xml 的平台"""
    platforms = []
    
    try:
        for item in os.listdir(roms_path):
            platform_path = os.path.join(roms_path, item)
            
            # 跳過檔案,只處理目錄
            if not os.path.isdir(platform_path):
                continue
            
            # 檢查是否有 gamelist.xml
            gamelist_path = os.path.join(platform_path, "gamelist.xml")
            if os.path.exists(gamelist_path):
                platforms.append({
                    'name': item,
                    'path': platform_path,
                    'gamelist': gamelist_path
                })
    
    except Exception as e:
        print(f"掃描平台時發生錯誤: {e}")
    
    return platforms

# 建立備份
def backup_gamelist(gamelist_path):
    """備份 gamelist.xml 到本機 backups 目錄"""
    try:
        # 建立本機備份目錄
        backup_dir = Path(__file__).parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        # 從路徑中提取平台名稱
        if "roms" in gamelist_path:
            parts = gamelist_path.replace("\\", "/").split("/roms/")
            if len(parts) > 1:
                platform_path = parts[1].split("/")[0]
            else:
                platform_path = "unknown"
        else:
            platform_path = "unknown"
        
        # 備份檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"gamelist_{platform_path}_{timestamp}.xml"
        backup_path = backup_dir / backup_filename
        
        # 複製檔案
        shutil.copy2(gamelist_path, backup_path)
        print(f"  [OK] 已備份至本機: {backup_path}")
        return True
    
    except Exception as e:
        print(f"  [X] 備份失敗: {e}")
        return False

# 翻譯單一平台
def translate_platform(platform_info, config):
    """翻譯單一平台的 gamelist.xml"""
    platform_name = platform_info['name']
    gamelist_path = platform_info['gamelist']
    
    print(f"\n{'='*60}")
    print(f"平台: {platform_name}")
    print(f"路徑: {gamelist_path}")
    print(f"{'='*60}")
    
    # 建立臨時工作目錄
    temp_dir = Path(__file__).parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    temp_gamelist = temp_dir / f"gamelist_{platform_name}.xml"
    
    try:
        # 1. 複製到本機臨時目錄
        print(f"  [1/4] 複製檔案到本機...")
        shutil.copy2(gamelist_path, temp_gamelist)
        
        # 2. 建立備份
        if config.get('auto_backup', True):
            backup_gamelist(gamelist_path)
        
        # 3. 翻譯本機檔案
        print(f"  [2/4] 開始翻譯...")
        translator = GamelistTranslator(
            translations_dir=config.get('translations_dir', 'translations'),
            display_mode=config.get('display_mode', 'chinese_only'),
            translate_desc=config.get('translate_desc', True),
            max_name_length=config.get('max_length', 100),
            search_delay=config.get('search_delay', 2.0)
        )
        
        # 使用本機檔案翻譯 (限制前 10 個遊戲)
        translator.update_gamelist(str(temp_gamelist), platform_name, dry_run=False, limit=10)
        
        # 4. 複製回 Batocera (使用 WSL)
        print("  [3/4] 寫回 Batocera...")
        wsl_target = gamelist_path.replace("\\\\wsl$\\Ubuntu", "").replace("\\", "/")
        
        # 將 Windows 路徑轉換為 WSL 路徑 (D:\... -> /mnt/d/...)
        win_temp = str(temp_gamelist.absolute())
        if ":" in win_temp:
            drive = win_temp[0].lower()
            wsl_temp = f"/mnt/{drive}/{win_temp[3:]}".replace("\\", "/")
        else:
            wsl_temp = win_temp.replace("\\", "/")
        
        # 使用 WSL 複製檔案 (需要 sudo 因為檔案屬於 root)
        cmd = f'wsl sudo cp "{wsl_temp}" "{wsl_target}"'
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, encoding='utf-8', errors='ignore'
        )
        
        if result.returncode == 0:
            print(f"  [4/4] [OK] 翻譯完成並寫回 Batocera!")
            # 清理臨時檔案
            temp_gamelist.unlink()
            return True
        else:
            print(f"  [X] 寫回失敗: {result.stderr}")
            print(f"  翻譯後的檔案保存在: {temp_gamelist}")
            return False
    
    except Exception as e:
        print(f"\n[X] 翻譯時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

# 主程式
def main():
    print("="*60)
    print("Batocera 遊戲清單批次翻譯工具")
    print("="*60)
    
    # 載入配置
    config = load_config()
    
    # 取得 Batocera 路徑
    batocera_path = get_batocera_path(config)
    if not batocera_path:
        sys.exit(1)
    
    print(f"\nBatocera roms 路徑: {batocera_path}")
    
    # 掃描平台
    print("\n正在掃描平台...")
    platforms = scan_platforms(batocera_path)
    
    if not platforms:
        print("未找到任何包含 gamelist.xml 的平台")
        sys.exit(0)
    
    print(f"\n找到 {len(platforms)} 個平台:")
    for i, platform in enumerate(platforms, 1):
        print(f"  {i}. {platform['name']}")
    
    # 自動選擇 3DS 平台進行測試 (有最多遊戲)
    print("\n自動選擇 3DS 平台進行測試...")
    selected_platforms = []
    
    for platform in platforms:
        if platform['name'].lower() == '3ds':
            selected_platforms.append(platform)
            print(f"[OK] 已選擇: {platform['name']}")
            break
    
    if not selected_platforms:
        print("[X] 找不到 3DS 平台,改為翻譯第一個平台")
        if platforms:
            selected_platforms.append(platforms[0])
            print(f"[OK] 已選擇: {platforms[0]['name']}")
        else:
            print("[X] 沒有可用的平台")
            sys.exit(1)
    
    # 開始翻譯
    print(f"\n開始翻譯 {len(selected_platforms)} 個平台...")
    
    success_count = 0
    fail_count = 0
    
    for platform in selected_platforms:
        if translate_platform(platform, config):
            success_count += 1
        else:
            fail_count += 1
    
    # 總結
    print("\n" + "="*60)
    print("翻譯完成!")
    print(f"成功: {success_count} 個平台")
    print(f"失敗: {fail_count} 個平台")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n使用者中斷執行")
        sys.exit(0)
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
