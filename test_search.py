"""測試 Google 搜尋提取邏輯"""
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


# 測試遊戲
game = "Animal Crossing - Happy Home Designer"
platform = "3DS"
query = f"{game} {platform} 遊戲 中文"

print(f"搜尋: {query}")
print("=" * 60)

html = search_google(query)
soup = BeautifulSoup(html, 'html.parser')

# 列出所有包含中文的文字
print("\n所有包含中文的文字片段:")
print("-" * 60)

for i, text_elem in enumerate(soup.find_all(['h3', 'span', 'div', 'p']), 1):
    text = text_elem.get_text().strip()
    if re.search(r'[\u4e00-\u9fff]', text) and len(text) > 0:
        if i <= 30:  # 只顯示前30個
            print(f"\n[{i}] {text[:200]}")
