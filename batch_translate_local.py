#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次翻譯本地所有 gamelists，產生完整語系包
"""

import os
import sys
import json
from pathlib import Path
from translator import GamelistTranslator

# 設定控制台編碼
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def main():
    """批次翻譯本地 gamelists_local 目錄下所有平台"""

    local_dir = Path("gamelists_local")

    if not local_dir.exists():
        print(f"❌ 找不到目錄: {local_dir}")
        return

    # 初始化翻譯器（使用批次翻譯模式）
    translator = GamelistTranslator(
        translate_desc=False  # 只翻譯名稱
    )

    print("=" * 60)
    print("批次翻譯本地 Gamelists - 產生完整語系包")
    print("=" * 60)

    # 取得所有平台目錄
    platforms = []
    for item in local_dir.iterdir():
        if item.is_dir():
            gamelist_path = item / "gamelist.xml"
            if gamelist_path.exists():
                platforms.append(item.name)

    platforms.sort()
    print(f"\n✅ 找到 {len(platforms)} 個平台:\n")
    for platform in platforms:
        print(f"  - {platform}")

    print(f"\n{'=' * 60}")
    print(f"開始批次翻譯...")
    print(f"{'=' * 60}\n")

    # 逐一翻譯
    total_games = 0
    total_translated = 0

    for idx, platform in enumerate(platforms, 1):
        print(f"\n{'▼' * 30}")
        print(f"[{idx}/{len(platforms)}] {platform.upper()}")
        print(f"{'▼' * 30}")

        gamelist_path = local_dir / platform / "gamelist.xml"

        try:
            # 使用批次翻譯模式（use_batch=True）
            result = translator.update_gamelist(
                gamelist_path=str(gamelist_path),
                platform=platform,
                dry_run=False,
                limit=0,  # 處理全部
                use_batch=True  # 批次翻譯
            )

            print(f"✅ {platform} 完成")

        except Exception as e:
            import traceback
            print(f"❌ {platform} 發生錯誤: {e}")
            traceback.print_exc()
            continue

    print(f"\n{'=' * 60}")
    print(f"批次翻譯完成！")
    print(f"{'=' * 60}")

    # 顯示語系包統計
    master_file = Path("translation_master.json")
    if master_file.exists():
        with open(master_file, 'r', encoding='utf-8') as f:
            master = json.load(f)

        print(f"\n📦 語系包統計:")
        print(f"  - 主字典檔: translation_master.json")
        print(f"  - 遊戲名稱: {len(master.get('names', {}))} 筆")
        print(f"  - 描述翻譯: {len(master.get('descriptions', {}))} 筆")

    local_cache = Path("local_cache.json")
    if local_cache.exists():
        with open(local_cache, 'r', encoding='utf-8') as f:
            cache = json.load(f)

        print(f"\n📦 本地快取統計:")
        print(f"  - 快取檔案: local_cache.json")
        print(f"  - 遊戲名稱: {len(cache.get('names', {}))} 筆")

    print(f"\n✅ 語系包已產生，可用於實際翻譯！")


if __name__ == "__main__":
    main()
