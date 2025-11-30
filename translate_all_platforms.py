"""正式翻譯所有本地平台（按字母順序）"""
import sys
import os
import json
from pathlib import Path
from translator import GamelistTranslator

# 設定控制台編碼
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')


def main():
    # 讀取設定檔
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}

    gamelists_dir = Path("gamelists_local")

    # **按字母順序排列平台**
    platforms = sorted([d.name for d in gamelists_dir.iterdir() if d.is_dir()])

    print("=" * 60)
    print(f"正式翻譯所有平台（共 {len(platforms)} 個）")
    print("=" * 60)

    # 傳遞 API 設定
    translator = GamelistTranslator(
        enable_groq=config.get('enable_groq', True),
        enable_gemini=config.get('enable_gemini', True)
    )

    total_platforms = len(platforms)
    processed_count = 0
    total_translated = 0

    for idx, platform in enumerate(platforms, 1):
        gamelist_path = gamelists_dir / platform / "gamelist.xml"

        if not gamelist_path.exists():
            print(f"\n[{idx}/{total_platforms}] ⊗ {platform.upper()}: 檔案不存在，跳過")
            continue

        print(f"\n{'='*60}")
        print(f"[{idx}/{total_platforms}] 處理平台: {platform.upper()}")
        print(f"{'='*60}")

        try:
            updated_count = translator.update_gamelist(
                str(gamelist_path), platform)

            total_translated += updated_count
            processed_count += 1

            print(f"\n[OK] [{idx}/{total_platforms}] {platform.upper()}: 處理完成")

        except Exception as e:
            print(
                f"\n[ERROR] [{idx}/{total_platforms}] {platform.upper()} 處理失敗: {e}")

    print(f"\n{'='*60}")
    print("正式翻譯完成！")
    print(f"{'='*60}")
    print(f"處理平台數: {processed_count}/{total_platforms}")
    print(f"總翻譯遊戲數: {total_translated}")


if __name__ == "__main__":
    main()
