#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Google 搜尋功能 - 模擬語系包中沒有的遊戲

這個測試會：
1. 在 test_roms/nes/gamelist.xml 中加入一個語系包裡沒有的遊戲
2. 執行翻譯器，讓它去 Google 搜尋
3. 將搜尋結果保存到本地快取
4. 最後可以選擇是否更新語系包
"""

from translator import GamelistTranslator
import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))


def add_test_game_to_gamelist(gamelist_path: str, game_name: str):
    """在 gamelist.xml 中新增一個測試遊戲"""

    print(f"正在向 {gamelist_path} 添加測試遊戲: {game_name}")

    # 解析現有的 XML
    tree = ET.parse(gamelist_path)
    root = tree.getroot()

    # 檢查遊戲是否已存在
    for game in root.findall('game'):
        name_elem = game.find('name')
        if name_elem is not None and game_name in name_elem.text:
            print(f"遊戲 '{game_name}' 已存在，跳過新增")
            return False

    # 建立新的遊戲元素
    new_game = ET.SubElement(root, 'game')

    # 添加子元素
    ET.SubElement(
        new_game, 'path').text = f"./{game_name.replace(' ', '')}.nes"
    ET.SubElement(new_game, 'name').text = game_name
    ET.SubElement(
        new_game, 'desc').text = "A classic NES game that needs translation."
    ET.SubElement(new_game, 'developer').text = "Unknown"
    ET.SubElement(new_game, 'publisher').text = "Unknown"
    ET.SubElement(new_game, 'releasedate').text = "19900101T000000"
    ET.SubElement(new_game, 'genre').text = "Action"

    # 儲存檔案
    tree.write(gamelist_path, encoding='utf-8', xml_declaration=True)
    print(f"✓ 已添加測試遊戲: {game_name}")
    return True


def check_in_translation_dict(game_name: str, platform: str = "nes") -> bool:
    """檢查遊戲是否在語系包中"""

    dict_file = Path("translations") / f"translations_{platform}.json"

    if not dict_file.exists():
        print(f"語系包不存在: {dict_file}")
        return False

    with open(dict_file, 'r', encoding='utf-8') as f:
        trans_dict = json.load(f)

    clean_name = game_name.replace(" (USA)", "").replace(" [!]", "").strip()

    if clean_name in trans_dict:
        print(f"✓ '{clean_name}' 在語系包中: {trans_dict[clean_name]}")
        return True
    else:
        print(f"✗ '{clean_name}' 不在語系包中")
        return False


def update_translation_dict_from_cache(platform: str = "nes"):
    """從本地快取更新語系包"""

    cache_file = "local_cache.json"
    dict_file = Path("translations") / f"translations_{platform}.json"

    if not os.path.exists(cache_file):
        print("本地快取不存在")
        return

    # 讀取快取
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    # 讀取現有語系包
    if dict_file.exists():
        with open(dict_file, 'r', encoding='utf-8') as f:
            trans_dict = json.load(f)
    else:
        trans_dict = {}

    # 統計新增項目
    added_count = 0

    # 將快取中的名稱加入語系包
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

        print(f"\n✓ 已將 {added_count} 個翻譯從快取更新到語系包")
    else:
        print("\n沒有新的翻譯需要更新")


def main():
    """主測試流程"""

    print("=" * 70)
    print("測試場景：模擬遊戲不在語系包中，自動 Google 搜尋並更新")
    print("=" * 70)
    print()

    # 測試遊戲名稱（選擇一個不在語系包中的遊戲）
    test_games = [
        "Duck Hunt",           # 打鴨子
        "Kirby's Adventure",   # 星之卡比
        "Ninja Gaiden",        # 忍者龍劍傳
        "Double Dragon",       # 雙截龍
        "Bubble Bobble",       # 泡泡龍
    ]

    # 選擇測試遊戲
    print("可用的測試遊戲：")
    for i, game in enumerate(test_games, 1):
        print(f"{i}. {game}")

    choice = input("\n請選擇要測試的遊戲編號 (1-5，直接按 Enter 使用第一個): ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(test_games):
        test_game = test_games[int(choice) - 1]
    else:
        test_game = test_games[0]

    print(f"\n選擇的測試遊戲: {test_game}")
    print()

    # 步驟 1: 檢查是否在語系包中
    print("步驟 1: 檢查遊戲是否在語系包中")
    print("-" * 70)
    in_dict = check_in_translation_dict(test_game)
    print()

    if in_dict:
        print("⚠️ 遊戲已在語系包中，將繼續測試但不會觸發 Google 搜尋")
        print()

    # 步驟 2: 添加遊戲到測試 gamelist
    print("步驟 2: 將遊戲添加到測試 gamelist.xml")
    print("-" * 70)
    gamelist_path = "test_roms/nes/gamelist.xml"

    if not os.path.exists(gamelist_path):
        print(f"錯誤: {gamelist_path} 不存在")
        return

    add_test_game_to_gamelist(gamelist_path, test_game)
    print()

    # 步驟 3: 執行翻譯器
    print("步驟 3: 執行翻譯器（將觸發 Google 搜尋）")
    print("-" * 70)

    # 建立翻譯器實例
    translator = GamelistTranslator(
        translations_dir="translations",
        local_cache_file="local_cache.json",
        display_mode="chinese_only",
        translate_desc=False,
        search_delay=1.0,  # 縮短延遲以加快測試
        fuzzy_match=True
    )

    # 翻譯單一遊戲（而非整個批次）
    print(f"\n開始翻譯: {test_game}")
    print()

    try:
        clean_name = translator.clean_game_name(test_game)
        chinese_name = translator.translate_name(clean_name, "nes")

        print()
        print(f"翻譯結果: {test_game} → {chinese_name}")
        print()

    except Exception as e:
        print(f"翻譯過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return

    # 步驟 4: 檢查本地快取
    print("步驟 4: 檢查本地快取")
    print("-" * 70)

    if os.path.exists("local_cache.json"):
        with open("local_cache.json", 'r', encoding='utf-8') as f:
            cache = json.load(f)

        print("本地快取內容 (names):")
        for key, value in cache.get("names", {}).items():
            print(f"  {key} → {value}")
        print()
    else:
        print("本地快取不存在")
        print()

    # 步驟 5: 詢問是否更新語系包
    print("步驟 5: 更新語系包")
    print("-" * 70)

    update = input("是否將本地快取的翻譯更新到語系包？(y/N): ").strip().lower()

    if update == 'y':
        update_translation_dict_from_cache("nes")
    else:
        print("跳過更新語系包")

    print()
    print("=" * 70)
    print("測試完成！")
    print("=" * 70)
    print()
    print("總結：")
    print(f"1. 測試遊戲: {test_game}")
    print(f"2. 翻譯結果: {chinese_name}")
    print(f"3. 快取已更新: local_cache.json")
    if update == 'y':
        print(f"4. 語系包已更新: translations/translations_nes.json")
    else:
        print(f"4. 語系包未更新（可手動執行更新）")
    print()
    print("你可以檢查以下檔案：")
    print(f"  - {gamelist_path}")
    print(f"  - local_cache.json")
    print(f"  - translations/translations_nes.json")


if __name__ == "__main__":
    main()
