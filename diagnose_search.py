#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷 Google 搜尋功能 - 查看實際的搜尋 HTML 內容

這個腳本會：
1. 對一個遊戲執行 Google 搜尋
2. 保存原始 HTML 以供分析
3. 顯示提取的中文候選詞
"""

from translator import GamelistTranslator
import os
import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))


def diagnose_google_search(game_name: str, platform: str = "nes"):
    """診斷 Google 搜尋過程"""

    print("=" * 80)
    print(f"診斷 Google 搜尋: {game_name}")
    print("=" * 80)

    translator = GamelistTranslator()

    # 構建搜尋查詢
    from translator import PLATFORM_NAMES
    platform_name = PLATFORM_NAMES.get(platform, platform)
    query = f"{game_name} {platform_name} 遊戲 中文"

    print(f"\n搜尋查詢: {query}")
    print(f"搜尋 URL: https://www.google.com/search?q={query}&hl=zh-TW")

    # 執行搜尋
    print("\n正在搜尋...")
    html = translator.search_google(query)

    if not html:
        print("✗ 搜尋失敗，無法取得 HTML")
        return

    print(f"✓ 已取得 HTML ({len(html)} 字元)")

    # 保存 HTML
    html_file = f"google_search_{game_name.replace(' ', '_')}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ HTML 已保存至: {html_file}")

    # 提取中文名稱
    print("\n正在提取中文翻譯...")
    chinese_name = translator.extract_chinese_name(html, game_name)

    if chinese_name:
        print(f"✓ 提取結果: {chinese_name}")
    else:
        print("✗ 未能提取中文翻譯")

    # 手動分析 HTML（簡化版）
    print("\n分析 HTML 內容...")
    from bs4 import BeautifulSoup
    import re

    soup = BeautifulSoup(html, 'html.parser')

    # 尋找書名號
    print("\n1. 搜尋書名號《》中的內容:")
    book_title_pattern = re.compile(r'《([^》]+)》')
    book_titles = book_title_pattern.findall(html)

    if book_titles:
        for i, title in enumerate(book_titles[:10], 1):  # 只顯示前 10 個
            print(f"   {i}. {title}")
    else:
        print("   未找到書名號內容")

    # 尋找標題中的中文
    print("\n2. 搜尋標題 <h3> 中的中文:")
    h3_tags = soup.find_all('h3')
    chinese_in_h3 = []

    for h3 in h3_tags[:10]:  # 只顯示前 10 個
        text = h3.get_text()
        if translator.contains_chinese(text):
            chinese_in_h3.append(text.strip())

    if chinese_in_h3:
        for i, text in enumerate(chinese_in_h3, 1):
            print(f"   {i}. {text[:100]}")  # 限制長度
    else:
        print("   未找到包含中文的標題")

    # 尋找包含遊戲名稱和中文的段落
    print(f"\n3. 搜尋同時包含 '{game_name}' 和中文的段落:")
    all_text = soup.get_text()
    lines = all_text.split('\n')
    relevant_lines = []

    for line in lines:
        line = line.strip()
        if game_name.lower() in line.lower() and translator.contains_chinese(line):
            if len(line) > 10 and len(line) < 200:  # 過濾太短或太長的
                relevant_lines.append(line)

    if relevant_lines:
        for i, line in enumerate(relevant_lines[:10], 1):
            print(f"   {i}. {line}")
    else:
        print("   未找到相關段落")

    print("\n" + "=" * 80)
    print("診斷完成")
    print("=" * 80)
    print(f"\n你可以查看保存的 HTML 檔案來進一步分析:")
    print(f"  {html_file}")


if __name__ == "__main__":
    # 測試多個遊戲
    test_games = [
        ("Kirby's Adventure", "nes"),
        ("Ninja Gaiden", "nes"),
        ("Double Dragon", "nes"),
    ]

    print("這個工具會診斷 Google 搜尋功能，查看實際提取的內容\n")
    print("測試遊戲:")
    for i, (game, platform) in enumerate(test_games, 1):
        print(f"  {i}. {game} ({platform})")

    choice = input("\n請選擇要診斷的遊戲編號 (1-3，或按 Enter 使用第一個): ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(test_games):
        game_name, platform = test_games[int(choice) - 1]
    else:
        game_name, platform = test_games[0]

    print()
    diagnose_google_search(game_name, platform)
