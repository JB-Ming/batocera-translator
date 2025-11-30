#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 3DO 批次翻譯
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
    translator = GamelistTranslator(translate_desc=False)

    gamelist_path = Path("gamelists_local/3do/gamelist.xml")

    print(f"測試翻譯: {gamelist_path}")

    try:
        result = translator.update_gamelist(
            gamelist_path=str(gamelist_path),
            platform="3do",
            dry_run=False,
            limit=0,
            use_batch=True
        )

        print(f"\n✅ 完成！更新了 {result} 個遊戲")

    except Exception as e:
        import traceback
        print(f"\n❌ 錯誤: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
