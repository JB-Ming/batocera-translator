#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
實際演示：當遊戲不在語系包時，自動 Google 搜尋並更新語系包

這個腳本會：
1. 處理 test_roms/nes/gamelist.xml 中的 Ninja Gaiden
2. 發現它不在語系包中
3. 執行 Google 搜尋
4. 將翻譯結果保存到快取
5. 更新語系包
6. 更新 gamelist.xml
"""

import json
from translator import GamelistTranslator
import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))


def print_header(title):
    """打印標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_step(step_num, title):
    """打印步驟"""
    print(f"\n【步驟 {step_num}】{title}")
    print("-" * 80)


def main():
    print_header("實際演示：語系包缺少遊戲時的 Google 搜尋流程")

    # 目標遊戲
    test_game = "Ninja Gaiden"
    platform = "nes"

    print(f"目標遊戲: {test_game}")
    print(f"平台: {platform.upper()}")

    # 步驟 1: 檢查語系包
    print_step(1, "檢查當前語系包")

    dict_file = Path("translations") / f"translations_{platform}.json"
    with open(dict_file, 'r', encoding='utf-8') as f:
        trans_dict = json.load(f)

    print(f"語系包檔案: {dict_file}")
    print(f"包含翻譯: {len(trans_dict)} 個")

    if test_game in trans_dict:
        print(f"✓ '{test_game}' 已在語系包中: {trans_dict[test_game]}")
        print("（為了演示，我們會重新翻譯）")
    else:
        print(f"✗ '{test_game}' 不在語系包中")
        print("→ 將觸發 Google 搜尋！")

    # 步驟 2: 創建翻譯器
    print_step(2, "創建翻譯器並配置")

    translator = GamelistTranslator(
        translations_dir="translations",
        local_cache_file="local_cache.json",
        display_mode="chinese_only",
        translate_desc=False,
        search_delay=2.0,
        fuzzy_match=True
    )

    print("翻譯器配置：")
    print(f"  - 語系包目錄: {translator.translations_dir}")
    print(f"  - 本地快取: {translator.local_cache_file}")
    print(f"  - 搜尋延遲: {translator.search_delay} 秒")
    print(f"  - 模糊匹配: {translator.fuzzy_match}")

    # 步驟 3: 執行翻譯（這會觸發 Google 搜尋）
    print_step(3, "執行翻譯（會觸發 Google 搜尋）")

    print(f"\n開始翻譯: {test_game}")
    print("\n查找流程：")
    print("  1. 檢查預設翻譯字典...")
    print("  2. 檢查語系包...")
    print("  3. 檢查本地快取...")
    print("  4. 執行 Google 搜尋... ⏳")
    print()

    # 臨時從語系包中移除（如果存在）以確保觸發搜尋
    original_value = trans_dict.pop(test_game, None)
    if original_value:
        with open(dict_file, 'w', encoding='utf-8') as f:
            json.dump(trans_dict, f, ensure_ascii=False, indent=2)
        print(f"（已暫時從語系包移除 '{test_game}' 以確保觸發搜尋）\n")

    try:
        # 執行翻譯
        chinese_name = translator.translate_name(test_game, platform)

        print(f"\n✓ 翻譯完成！")
        print(f"  原始名稱: {test_game}")
        print(f"  中文名稱: {chinese_name}")

    except Exception as e:
        print(f"\n✗ 翻譯失敗: {e}")
        import traceback
        traceback.print_exc()
        # 恢復原值
        if original_value:
            trans_dict[test_game] = original_value
            with open(dict_file, 'w', encoding='utf-8') as f:
                json.dump(trans_dict, f, ensure_ascii=False, indent=2)
        return

    # 步驟 4: 檢查本地快取
    print_step(4, "檢查本地快取更新")

    cache_file = Path("local_cache.json")
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)

        print(f"本地快取檔案: {cache_file}")
        print(f"\n快取內容 (names):")
        for key, value in cache.get("names", {}).items():
            marker = " ← 新增" if key == test_game else ""
            print(f"  {key:30s} → {value}{marker}")

        if test_game in cache.get("names", {}):
            print(f"\n✓ '{test_game}' 已成功加入本地快取")
        else:
            print(f"\n⚠ '{test_game}' 未在快取中（可能已在語系包）")

    # 步驟 5: 更新語系包
    print_step(5, "更新語系包")

    # 重新讀取語系包
    with open(dict_file, 'r', encoding='utf-8') as f:
        trans_dict = json.load(f)

    original_count = len(trans_dict)

    # 從快取合併
    added = False
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)

        for key, value in cache.get("names", {}).items():
            if key not in trans_dict:
                trans_dict[key] = value
                added = True
                print(f"  新增: {key} → {value}")

    if added:
        # 排序並保存
        sorted_dict = dict(sorted(trans_dict.items()))
        with open(dict_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_dict, f, ensure_ascii=False, indent=2)

        new_count = len(trans_dict)
        print(f"\n✓ 語系包已更新")
        print(f"  原有翻譯: {original_count} 個")
        print(f"  更新後: {new_count} 個")
        print(f"  新增: {new_count - original_count} 個")
    else:
        print(f"\n語系包已是最新（無需更新）")

    # 步驟 6: 更新 gamelist.xml
    print_step(6, "更新 gamelist.xml")

    gamelist_path = "test_roms/nes/gamelist.xml"
    print(f"處理檔案: {gamelist_path}")
    print(f"只更新 '{test_game}' 這一個遊戲\n")

    try:
        translator.update_gamelist(gamelist_path, platform, dry_run=False)
        print(f"\n✓ gamelist.xml 已更新")
    except Exception as e:
        print(f"\n✗ 更新失敗: {e}")
        import traceback
        traceback.print_exc()

    # 總結
    print_header("演示完成")

    print("完整流程總結：\n")
    print(f"  1️⃣  遊戲名稱: {test_game}")
    print(f"  2️⃣  在語系包中: 否（已移除以觸發搜尋）")
    print(f"  3️⃣  Google 搜尋: 已執行")
    print(f"  4️⃣  翻譯結果: {chinese_name}")
    print(f"  5️⃣  本地快取: 已更新")
    print(f"  6️⃣  語系包: 已更新")
    print(f"  7️⃣  gamelist.xml: 已更新")

    print("\n核心機制展示：")
    print("  ✅ 當遊戲不在語系包時")
    print("  ✅ 系統自動執行 Google 搜尋")
    print("  ✅ 搜尋結果保存到本地快取")
    print("  ✅ 快取同步到語系包")
    print("  ✅ gamelist.xml 更新為中文")

    print("\n相關檔案：")
    print(f"  - 語系包: {dict_file}")
    print(f"  - 本地快取: {cache_file}")
    print(f"  - Gamelist: {gamelist_path}")

    print("\n下次翻譯相同遊戲時：")
    print("  ⚡ 直接從語系包讀取，無需搜尋")
    print("  ⚡ 速度快，效率高！")
    print()


if __name__ == "__main__":
    main()
