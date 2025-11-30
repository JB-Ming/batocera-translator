#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試實際 API 翻譯（非快取）
"""

import sys
import codecs
from pathlib import Path
from translator import GamelistTranslator

# 設定控制台編碼
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def main():
    # 清空本地快取以確保會呼叫 API
    import json
    cache_file = Path("local_cache.json")
    if cache_file.exists():
        print("暫時清空快取以測試 API...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            old_cache = json.load(f)

        # 只保留非測試遊戲的快取
        new_cache = {"names": {}, "descriptions": {}}
        test_names = ["Super Mario Bros.", "The Legend of Zelda", "Tetris",
                      "Sonic the Hedgehog", "Street Fighter II"]

        for key, value in old_cache.get("names", {}).items():
            if key not in test_names:
                new_cache["names"][key] = value

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(new_cache, f, ensure_ascii=False, indent=2)

    # 初始化翻譯器（chinese_english 模式以便看到翻譯效果）
    translator = GamelistTranslator(
        translate_desc=False,
        display_mode="chinese_english"  # 顯示：中文譯名 (English Name)
    )

    gamelist_path = Path("test_new_games.xml")

    print(f"\n{'=' * 60}")
    print(f"測試實際 API 翻譯（批次模式）")
    print(f"{'=' * 60}\n")

    try:
        result = translator.update_gamelist(
            gamelist_path=str(gamelist_path),
            platform="nes",
            dry_run=False,
            limit=0,
            use_batch=True  # 使用批次翻譯
        )

        print(f"\n{'=' * 60}")
        print(f"✅ 完成！翻譯了 {result} 個遊戲")
        print(f"{'=' * 60}\n")

        # 顯示翻譯結果
        print("翻譯後的 XML 內容：\n")
        with open(gamelist_path, 'r', encoding='utf-8') as f:
            print(f.read())

    except Exception as e:
        import traceback
        print(f"\n❌ 錯誤: {e}")
        traceback.print_exc()

    finally:
        # 恢復原始快取
        if cache_file.exists() and 'old_cache' in locals():
            print("\n恢復原始快取...")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(old_cache, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
