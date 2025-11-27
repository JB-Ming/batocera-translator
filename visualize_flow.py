#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
視覺化演示：Google 搜尋自動翻譯流程

這個腳本展示完整的翻譯查找和更新流程，包括：
1. 多層查找機制
2. Google 搜尋觸發條件
3. 快取更新邏輯
4. 語系包同步
"""

import json
from pathlib import Path


def print_header(title):
    """打印標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_step(step_num, title):
    """打印步驟"""
    print(f"\n【步驟 {step_num}】{title}")
    print("-" * 80)


def visualize_translation_flow():
    """視覺化翻譯流程"""

    print_header("Google 搜尋自動翻譯流程演示")

    # 範例遊戲
    test_game = "Ninja Gaiden"
    expected_translation = "忍者龍劍傳"
    platform = "nes"

    print(f"範例遊戲: {test_game}")
    print(f"預期翻譯: {expected_translation}")
    print(f"平台: {platform.upper()}")

    # 步驟 1: 檢查預設翻譯字典
    print_step(1, "檢查預設翻譯字典 (DEFAULT_TRANSLATIONS)")

    default_translations = {
        "Super Mario Bros": "超級瑪利歐兄弟",
        "The Legend of Zelda": "薩爾達傳說",
        "Contra": "魂斗羅",
        # ... 其他預設翻譯
    }

    print("預設翻譯字典內容（部分）：")
    for key, value in list(default_translations.items())[:5]:
        print(f"  {key:25s} → {value}")

    if test_game in default_translations:
        print(f"\n✓ 找到翻譯: {default_translations[test_game]}")
        print("【流程結束】直接返回翻譯")
        return
    else:
        print(f"\n✗ '{test_game}' 不在預設字典中")
        print("【繼續】進入下一步...")

    # 步驟 2: 檢查語系包
    print_step(2, f"檢查語系包 (translations_{platform}.json)")

    # 讀取實際的語系包
    dict_file = Path("translations") / f"translations_{platform}.json"
    if dict_file.exists():
        with open(dict_file, 'r', encoding='utf-8') as f:
            trans_dict = json.load(f)
    else:
        trans_dict = {}

    print(f"語系包路徑: {dict_file}")
    print(f"包含翻譯數: {len(trans_dict)} 個")
    print("\n語系包內容（部分）：")
    for key, value in list(trans_dict.items())[:5]:
        print(f"  {key:25s} → {value}")

    if test_game in trans_dict:
        print(f"\n✓ 找到翻譯: {trans_dict[test_game]}")
        print("【流程結束】直接返回翻譯")
        return
    else:
        print(f"\n✗ '{test_game}' 不在語系包中")
        print("【繼續】進入下一步...")

    # 步驟 3: 檢查本地快取
    print_step(3, "檢查本地快取 (local_cache.json)")

    cache_file = Path("local_cache.json")
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    else:
        cache = {"names": {}, "descriptions": {}}

    print(f"快取檔案路徑: {cache_file}")
    print(f"包含翻譯數: {len(cache.get('names', {}))} 個")
    print("\n快取內容：")
    if cache.get('names'):
        for key, value in cache['names'].items():
            print(f"  {key:25s} → {value}")
    else:
        print("  (空)")

    if test_game in cache.get('names', {}):
        print(f"\n✓ 找到翻譯: {cache['names'][test_game]}")
        print("【流程結束】直接返回翻譯")
        return
    else:
        print(f"\n✗ '{test_game}' 不在本地快取中")
        print("【繼續】進入下一步...")

    # 步驟 4: 執行 Google 搜尋
    print_step(4, "執行 Google 搜尋")

    platform_names = {
        'nes': 'FC紅白機',
        'snes': '超級任天堂',
        # ...
    }

    platform_name = platform_names.get(platform, platform)
    query = f"{test_game} {platform_name} 遊戲 中文"

    print("🔍 搜尋配置：")
    print(f"  遊戲名稱: {test_game}")
    print(f"  平台名稱: {platform_name}")
    print(f"  搜尋查詢: {query}")
    print(f"  搜尋 URL: https://www.google.com/search?q={query}&hl=zh-TW")

    print("\n🌐 執行搜尋...")
    print("  > 發送 HTTP GET 請求")
    print("  > 接收 HTML 回應")
    print("  > 解析 HTML 內容")

    print("\n📝 提取中文翻譯...")
    print("  策略 1: 尋找書名號《》中的內容")
    print("  策略 2: 尋找標題標籤 <h3> 中的中文")
    print("  策略 3: 尋找包含中文的文字片段")
    print("  策略 4: 計算候選詞得分，選擇最佳翻譯")

    # 模擬提取結果
    extracted_translation = expected_translation

    print(f"\n✓ 提取成功: {extracted_translation}")
    print("【繼續】保存翻譯...")

    # 步驟 5: 保存到本地快取
    print_step(5, "保存到本地快取")

    print("更新前的快取：")
    print(f"  翻譯數量: {len(cache.get('names', {}))} 個")

    # 模擬更新
    cache.setdefault('names', {})[test_game] = extracted_translation

    print("\n執行更新：")
    print(f"  新增: {test_game} → {extracted_translation}")

    print("\n更新後的快取：")
    print(f"  翻譯數量: {len(cache['names'])} 個")

    print("\n💾 保存到檔案: local_cache.json")
    print("✓ 快取已更新")

    # 步驟 6: （可選）更新語系包
    print_step(6, "（可選）將快取同步到語系包")

    print("這一步可以批次執行，將多個翻譯一次性更新到語系包")
    print("\n同步策略：")
    print("  1. 讀取本地快取中的所有翻譯")
    print("  2. 讀取現有的語系包")
    print("  3. 合併新翻譯（跳過已存在的）")
    print("  4. 排序並保存")

    # 模擬更新
    original_count = len(trans_dict)
    trans_dict[test_game] = extracted_translation
    new_count = len(trans_dict)

    print(f"\n語系包更新：")
    print(f"  原有翻譯: {original_count} 個")
    print(f"  新增翻譯: {new_count - original_count} 個")
    print(f"  更新後: {new_count} 個")

    print(f"\n💾 保存到檔案: translations_{platform}.json")
    print("✓ 語系包已更新")

    # 總結
    print_header("流程總結")

    print("完整的翻譯查找流程：\n")
    print("  1️⃣  檢查預設翻譯     ✗ 未找到")
    print("  2️⃣  檢查語系包       ✗ 未找到")
    print("  3️⃣  檢查本地快取     ✗ 未找到")
    print("  4️⃣  執行 Google 搜尋 ✓ 找到翻譯")
    print("  5️⃣  保存到本地快取   ✓ 已更新")
    print("  6️⃣  更新語系包       ✓ 已更新")

    print(f"\n最終結果:")
    print(f"  遊戲名稱: {test_game}")
    print(f"  中文翻譯: {extracted_translation}")

    print("\n關鍵優勢:")
    print("  ✅ 自動化：無需手動查找翻譯")
    print("  ✅ 智慧化：多層快取機制，避免重複搜尋")
    print("  ✅ 可擴展：持續累積翻譯資料庫")
    print("  ✅ 可共享：語系包可供社群使用")

    print("\n下次翻譯相同遊戲時：")
    print("  1️⃣  檢查預設翻譯     ✗ 未找到")
    print("  2️⃣  檢查語系包       ✓ 找到！（直接返回，無需搜尋）")
    print("  ⚡ 速度快，效率高！")


def show_file_structure():
    """顯示相關檔案結構"""

    print_header("相關檔案結構")

    print("batocera-translator/")
    print("│")
    print("├── translator.py              # 核心翻譯邏輯")
    print("│   ├── DEFAULT_TRANSLATIONS   # 預設翻譯字典")
    print("│   ├── lookup_translation()   # 翻譯查找")
    print("│   ├── translate_name()       # Google 搜尋")
    print("│   └── extract_chinese_name() # 提取翻譯")
    print("│")
    print("├── local_cache.json           # 本地快取")
    print("│   └── {")
    print("│         \"names\": {")
    print("│           \"Duck Hunt\": \"打鴨子\",")
    print("│           \"Ninja Gaiden\": \"忍者龍劍傳\"")
    print("│         }")
    print("│       }")
    print("│")
    print("├── translations/              # 語系包目錄")
    print("│   ├── translations_nes.json")
    print("│   ├── translations_snes.json")
    print("│   └── descriptions_nes.json")
    print("│")
    print("├── demo_google_search.py      # 完整演示腳本")
    print("├── test_google_search.py      # 互動式測試")
    print("└── diagnose_search.py         # 診斷工具")


if __name__ == "__main__":
    visualize_translation_flow()
    show_file_structure()

    print("\n" + "=" * 80)
    print("💡 提示：")
    print("  - 執行 'python demo_google_search.py' 查看實際演示")
    print("  - 執行 'python test_google_search.py' 進行互動式測試")
    print("  - 執行 'python diagnose_search.py' 診斷搜尋結果")
    print("=" * 80 + "\n")
