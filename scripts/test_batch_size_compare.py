#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試不同批次大小對翻譯品質的影響
"""
from src.utils.settings import SettingsManager
from src.services.gemini_batch import GeminiBatchService, GEMINI_AVAILABLE
import warnings
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

warnings.filterwarnings('ignore')


def test_batch_size(api_key: str, game_names: list, batch_size: int, platform: str = "apple2"):
    """測試特定批次大小"""
    print(f"\n{'='*60}")
    print(f"測試批次大小: {batch_size} 筆/次")
    print(f"{'='*60}")

    service = GeminiBatchService(
        api_key=api_key,
        batch_size=batch_size,
        request_delay=1.0
    )

    result = service.translate_batch(
        game_names=game_names,
        language='zh-TW',
        platform=platform
    )

    print(f"  成功: {result.success_count}/{result.total}")
    print(f"  API 呼叫次數: {(len(game_names) + batch_size - 1) // batch_size}")

    # 顯示部分翻譯結果
    print(f"\n  翻譯結果：")
    count = 0
    for original, translated in result.translations.items():
        if count >= 5:
            break
        # 縮短顯示
        orig_short = original[:40] + "..." if len(original) > 40 else original
        print(f"    {orig_short}")
        print(f"      → {translated}")
        count += 1

    return result.translations


def main():
    print("=" * 60)
    print("批次大小對比測試")
    print("=" * 60)

    if not GEMINI_AVAILABLE:
        print("❌ google-generativeai 未安裝")
        return

    settings = SettingsManager().load()
    api_key = settings.get_gemini_api_key()

    if not api_key:
        print("❌ 未設定 Gemini API Key")
        return

    # 選取 30 個遊戲來測試（確保測試公平）
    test_games = [
        "3-D Docking Mission (19xx)(Chris Oberth)",
        "A Mind Forever Voyaging (1985)(Infocom)(Disk 1 of 1 Side A)",
        "Akalabeth (1980)(California Pacific Computer)",
        "Alice In Wonderland (1985)(Windham Classics)(Disk 1 of 1 Side A)",
        "Alien (1982)(Avalon Hill)",
        "Alter Ego (1985)(Activision)(Disk 1 of 3 Side A)",
        "Ancient Art of War, The (1984)(Broderbund)(Disk 1 of 2)",
        "Andromeda Conquest (1982)(Avalon Hill)[a]",
        "Apple Cider Spider (1983)(Sierra)",
        "Arkanoid (1987)(Taito)",
        "Asteroids (1980)(Cavalier Computer)",
        "Autoduel (1985)(Origins)(Disk 1 of 1 Side A)",
        "Bard's Tale II - The Destiny Knight, The (1986)(Electronic Arts)(Disk 1 of 4)",
        "Batman (1988)(Data East)(Disk 1 of 1 Side A)",
        "Battle of Antietam (1985)(SSI)(Disk 1 of 2)",
        "Battletech (1988)(Infocom - Westwood)(Disk 1 of 2)",
        "Beyond Beyond Castle Wolfenstein (19xx)(Mindscape)(Disk 1 of 1 Side A)",
        "Big Mac (19xx)(G. Bredon)",
        "Blacksmith Market Falcons (1981)(-)",
        "Bilestoad, The (19xx)(-)",
        "Championship Lode Runner (1984)(Broderbund)",
        "Choplifter (1982)(Broderbund)",
        "Conan (1984)(Datasoft)",
        "Dig Dug (1983)(Atari)",
        "Donkey Kong (1983)(Atari)",
        "Elite (1985)(Firebird)",
        "F-15 Strike Eagle (1985)(Microprose)",
        "Ghosts 'n Goblins (1987)(Capcom)",
        "Karateka (1984)(Broderbund)",
        "Prince of Persia (1989)(Broderbund)",
    ]

    print(f"\n測試資料: {len(test_games)} 個遊戲")

    # 測試不同批次大小
    batch_sizes = [30, 15, 10]
    results = {}

    for size in batch_sizes:
        results[size] = test_batch_size(api_key, test_games, size)

    # 比較結果
    print("\n" + "=" * 60)
    print("結果比較")
    print("=" * 60)

    # 找出有差異的翻譯
    print("\n翻譯差異：")
    diff_count = 0
    for game in test_games[:15]:  # 只比較前 15 個
        translations = [results[size].get(game, "N/A") for size in batch_sizes]
        if len(set(translations)) > 1:  # 有差異
            diff_count += 1
            game_short = game[:35] + "..." if len(game) > 35 else game
            print(f"\n  {game_short}")
            for size in batch_sizes:
                trans = results[size].get(game, "N/A")
                print(f"    批次{size:2d}: {trans}")

    if diff_count == 0:
        print("  所有翻譯結果一致！")
    else:
        print(f"\n共有 {diff_count} 個遊戲的翻譯有差異")

    print("\n✅ 測試完成！")


if __name__ == "__main__":
    main()
