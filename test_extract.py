"""測試改進的搜尋提取"""
import requests
from bs4 import BeautifulSoup
import re


def search_google(query):
    url = f"https://www.google.com/search?q={query}&hl=zh-TW"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    return response.text


# 測試
game = "Animal Crossing Happy Home Designer"
print(f"搜尋: {game}")
print("=" * 60)

html = search_google(game)
soup = BeautifulSoup(html, 'html.parser')

# 找標題
print("\n找到的標題 (h1, h2, h3):")
print("-" * 60)
for heading in soup.find_all(['h1', 'h2', 'h3']):
    text = heading.get_text().strip()
    if re.search(r'[\u4e00-\u9fff]', text):
        print(f"\n{text}")

        # 測試正則匹配
        original_name = game.replace('-', '').replace(':', '')
        match = re.search(
            r'([^\(]+)\s*\([^)]*' + re.escape(original_name) + r'[^)]*\)', text, re.IGNORECASE)
        if match:
            print(f"  ✓ 匹配成功! 中文部分: {match.group(1).strip()}")
