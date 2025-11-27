#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整演示：當語系包中沒有遊戲時，自動 Google 搜尋並更新

這個腳本會：
1. 選擇一個不在語系包中的遊戲
2. 演示如何從 Google 搜尋獲取翻譯
3. 將結果保存到本地快取
4. 自動更新語系包
"""

from translator import GamelistTranslator
import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))


def print_section(title):
    """打印美化的分隔線"""
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title):
    """打印小標題"""
    print()
    print(f">>> {title}")
    print("-" * 80)


def demo_translate_missing_game():
    """演示翻譯語系包中沒有的遊戲"""

    print_section("演示：語系包缺少遊戲時的自動 Google 搜尋")

    # 測試遊戲列表（選擇不在語系包中的）
    test_games = {
        "Duck Hunt": "打鴨子",
        "Kirby's Adventure": "星之卡比 夢之泉物語",
        "Ninja Gaiden": "忍者龍劍傳",
        "Double Dragon": "雙截龍",
        "Bubble Bobble": "泡泡龍",
    }

    platform = "nes"

    # 步驟 1: 檢查當前語系包
    print_subsection("步驟 1: 檢查當前語系包內容")

    dict_file = Path("translations") / f"translations_{platform}.json"
    with open(dict_file, 'r', encoding='utf-8') as f:
        trans_dict = json.load(f)

    print(f"語系包檔案: {dict_file}")
    print(f"目前包含 {len(trans_dict)} 個翻譯")
    print("\n前 5 個翻譯：")
    for i, (key, value) in enumerate(list(trans_dict.items())[:5], 1):
        print(f"  {i}. {key} → {value}")

    # 步驟 2: 選擇測試遊戲
    print_subsection("步驟 2: 選擇要測試的遊戲")

    print("以下遊戲不在語系包中：")
    for i, (game_name, expected_trans) in enumerate(test_games.items(), 1):
        in_dict = game_name in trans_dict
        status = "✓ 已在語系包" if in_dict else "✗ 不在語系包"
        print(f"  {i}. {game_name:25s} (預期: {expected_trans:15s}) {status}")

    # 選擇第一個不在語系包中的遊戲
    test_game = None
    expected_translation = None
    for game_name, expected_trans in test_games.items():
        if game_name not in trans_dict:
            test_game = game_name
            expected_translation = expected_trans
            break

    if not test_game:
        print("\n所有測試遊戲都已在語系包中！")
        test_game = list(test_games.keys())[0]
        expected_translation = test_games[test_game]
        print(f"將使用第一個遊戲進行測試: {test_game}")
    else:
        print(f"\n選擇測試遊戲: {test_game}")
        print(f"預期翻譯: {expected_translation}")

    # 步驟 3: 建立翻譯器並執行翻譯
    print_subsection("步驟 3: 執行翻譯（觸發 Google 搜尋）")

    translator = GamelistTranslator(
        translations_dir="translations",
        local_cache_file="local_cache.json",
        display_mode="chinese_only",
        translate_desc=False,
        search_delay=1.5,
        fuzzy_match=True
    )

    print(f"翻譯器配置:")
    print(f"  - 語系包目錄: {translator.translations_dir}")
    print(f"  - 本地快取: {translator.local_cache_file}")
    print(f"  - 搜尋延遲: {translator.search_delay} 秒")
    print(f"  - 模糊匹配: {translator.fuzzy_match}")

    print(f"\n正在翻譯: {test_game}")
    print("查找順序:")
    print("  1. 檢查預設翻譯字典...")
    print("  2. 檢查語系包...")
    print("  3. 檢查本地快取...")
    print("  4. 執行 Google 搜尋...")

    try:
        clean_name = translator.clean_game_name(test_game)
        chinese_name = translator.translate_name(clean_name, platform)

        print(f"\n翻譯結果:")
        print(f"  原始名稱: {test_game}")
        print(f"  清理後: {clean_name}")
        print(f"  中文名稱: {chinese_name}")
        print(f"  預期名稱: {expected_translation}")

        if chinese_name == expected_translation:
            print(f"  ✓ 翻譯正確！")
        else:
            print(f"  ⚠ 翻譯可能不準確")

    except Exception as e:
        print(f"\n✗ 翻譯失敗: {e}")
        import traceback
        traceback.print_exc()
        return

    # 步驟 4: 檢查本地快取
    print_subsection("步驟 4: 檢查本地快取更新")

    cache_file = "local_cache.json"
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)

        print(f"本地快取檔案: {cache_file}")
        print(f"\n快取內容 (names):")

        if cache.get("names"):
            for key, value in cache["names"].items():
                is_new = "← 新增" if key == clean_name else ""
                print(f"  {key} → {value} {is_new}")
        else:
            print("  (空)")

        # 檢查是否成功加入快取
        if clean_name in cache.get("names", {}):
            print(f"\n✓ 翻譯已成功加入本地快取")
        else:
            print(f"\n✗ 翻譯未加入快取（可能已存在於語系包中）")
    else:
        print(f"本地快取檔案不存在: {cache_file}")

    # 步驟 5: 更新語系包
    print_subsection("步驟 5: 將快取同步到語系包")

    # 讀取快取
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    # 讀取語系包
    with open(dict_file, 'r', encoding='utf-8') as f:
        trans_dict = json.load(f)

    original_count = len(trans_dict)
    added_count = 0

    # 合併快取到語系包
    for key, value in cache.get("names", {}).items():
        if key not in trans_dict:
            trans_dict[key] = value
            added_count += 1
            print(f"  新增: {key} → {value}")

    if added_count > 0:
        # 排序並儲存
        sorted_dict = dict(sorted(trans_dict.items()))
        with open(dict_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_dict, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 語系包已更新")
        print(f"  原有翻譯: {original_count} 個")
        print(f"  新增翻譯: {added_count} 個")
        print(f"  更新後: {len(trans_dict)} 個")
    else:
        print(f"\n沒有新的翻譯需要更新")

    # 總結
    print_section("演示完成")

    print("\n流程總結：")
    print(f"  1. 遊戲名稱: {test_game}")
    print(f"  2. 語系包中: {'否' if test_game not in trans_dict else '是'}")
    print(
        f"  3. Google 搜尋: {'已執行' if clean_name in cache.get('names', {}) else '未執行'}")
    print(f"  4. 翻譯結果: {chinese_name}")
    print(f"  5. 快取更新: {'是' if clean_name in cache.get('names', {}) else '否'}")
    print(f"  6. 語系包更新: {'是' if added_count > 0 else '否'}")

    print("\n相關檔案：")
    print(f"  - 語系包: {dict_file}")
    print(f"  - 本地快取: {cache_file}")
    print(f"  - 測試 gamelist: test_roms/nes/gamelist.xml")

    print("\n這個演示展示了當語系包中沒有某個遊戲時：")
    print("  ✓ 系統會自動從 Google 搜尋中文譯名")
    print("  ✓ 搜尋結果會先保存到本地快取")
    print("  ✓ 然後可以更新到語系包供日後使用")
    print("  ✓ 避免重複搜尋，提升效率")

    print()


if __name__ == "__main__":
    demo_translate_missing_game()
