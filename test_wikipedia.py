"""測試維基百科 API"""
import requests
import json


def search_wikipedia_zh(title):
    """搜尋中文維基百科"""
    # 先搜尋英文維基找到正確頁面
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'langlinks',
        'lllimit': 'max'
    }

    response = requests.get(url, params=params)
    data = response.json()

    pages = data.get('query', {}).get('pages', {})
    for page_id, page_data in pages.items():
        if 'langlinks' in page_data:
            for link in page_data['langlinks']:
                if link['lang'] == 'zh':
                    return link['*']
    return None


# 測試幾個遊戲
games = [
    "Animal Crossing: Happy Home Designer",
    "Professor Layton and the Miracle Mask",
    "Super Mario 3D Land",
    "The Legend of Zelda: Ocarina of Time",
]

for game in games:
    print(f"\n{game}")
    zh_title = search_wikipedia_zh(game)
    if zh_title:
        print(f"  ✓ 中文: {zh_title}")
    else:
        print(f"  ✗ 無中文維基頁面")
