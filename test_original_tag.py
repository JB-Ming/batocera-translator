"""測試什麼情況會出現 original 標記"""
import sys
from src.core.translator import TranslationEngine
from src.core.dictionary import GameEntry
from src.services.wikipedia import WikipediaService
from src.services.search import SearchService
from src.services.translate import TranslateService

# 初始化翻譯引擎
translator = TranslationEngine(target_language='zh-TW')
translator.set_wiki_service(WikipediaService())
translator.set_search_service(SearchService())
translator.set_translate_api(TranslateService())

# 測試各種情況
test_cases = [
    ("Mario Kart 8", "正常遊戲，Wikipedia 有收錄"),
    ("Donkey Kong", "Wikipedia 沒有但 API 能翻譯"),
    ("ABC123XYZ", "無意義的字串，API 也無法翻譯"),
    ("12345", "純數字"),
    ("", "空字串"),
    ("測試遊戲", "已經是中文"),
]

print("=" * 70)
print("測試什麼情況會標記為 'original'（之前的 keep）")
print("=" * 70)
print()

for game_name, description in test_cases:
    if not game_name:
        print(f"測試: [空字串] - {description}")
    else:
        print(f"測試: {game_name} - {description}")

    entry = GameEntry(key=game_name or "empty", original_name=game_name)

    try:
        result = translator.translate_game(
            entry,
            translate_name=True,
            translate_desc=False,
            skip_translated=False
        )

        if result.name:
            print(f"  翻譯結果: {result.name}")
            print(f"  來源標記: {result.name_source}")

            if result.name_source == "original":
                print(f"  ⚠️  標記為 original - 所有翻譯方法都失敗")
        else:
            print(f"  翻譯結果: [空]")
            print(f"  來源標記: {result.name_source}")

    except Exception as e:
        print(f"  錯誤: {e}")

    print()

print("=" * 70)
print("結論：")
print("'original' 標記只在以下情況出現：")
print("1. 所有翻譯服務（Wikipedia, Gemini, Search, API）都返回 None")
print("2. 或者翻譯結果與原文完全相同")
print("3. 這是最後的保底機制，確保不會丟失遊戲名稱")
print("=" * 70)
