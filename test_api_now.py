#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試實際 API 翻譯（全新遊戲）
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
    # 初始化翻譯器（chinese_english 模式以便看到翻譯效果）
    translator = GamelistTranslator(
        translate_desc=False,
        display_mode="chinese_english"  # 顯示：中文譯名 (English Name)
    )

    gamelist_path = Path("test_api_new.xml")

    print(f"\n{'=' * 60}")
    print(f"測試實際 API 批次翻譯")
    print(f"遊戲：Final Fantasy VI, Chrono Trigger, Metal Gear Solid")
    print(f"{'=' * 60}\n")

    try:
        result = translator.update_gamelist(
            gamelist_path=str(gamelist_path),
            platform="snes",
            dry_run=False,
            limit=0,
            use_batch=True  # 使用批次翻譯
        )

        print(f"\n{'=' * 60}")
        print(f"✅ 完成！翻譯了 {result} 個遊戲")
        print(f"{'=' * 60}\n")

        # 顯示翻譯結果
        print("✅ 翻譯後的 XML 內容：\n")
        with open(gamelist_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取遊戲名稱
            import re
            names = re.findall(r'<name>(.*?)</name>', content)
            for name in names:
                print(f"  ✓ {name}")

    except Exception as e:
        import traceback
        print(f"\n❌ 錯誤: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
