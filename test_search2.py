"""測試不同的搜尋策略"""
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


# 測試不同搜尋策略
game = "Animal Crossing Happy Home Designer"
strategies = [
    f"{game} 維基百科",
    f"{game} 中文維基",
    f"{game} 繁體中文",
    f"{game} wiki 中文",
]

for query in strategies:
    print(f"\n{'='*60}")
    print(f"搜尋: {query}")
    print('='*60)

    html = search_google(query)
    soup = BeautifulSoup(html, 'html.parser')

    # 找包含中文的片段
    found = []
    for elem in soup.find_all(['h3', 'span', 'div', 'p', 'a']):
        text = elem.get_text().strip()
        if re.search(r'[\u4e00-\u9fff]{3,}', text):
            # 排除重定向訊息
            if '重新導向' not in text and '按一下' not in text:
                found.append(text[:150])

    # 去重並顯示前5個
    unique = list(dict.fromkeys(found))[:5]
    if unique:
        for i, text in enumerate(unique, 1):
            print(f"[{i}] {text}")
    else:
        print("(無有效中文結果)")
