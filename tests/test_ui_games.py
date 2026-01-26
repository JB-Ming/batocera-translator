"""測試截圖中沒翻譯的遊戲"""
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

# 測試截圖中的遊戲
test_games = [
    "Pang (Europe)",
    "Panza Kick Boxing (Europe)",
    "Pro Tennis Tour (Europe)",
    "Plotting (Europe)",
    "Robocop 2 (Europe)",
    "Super Pinball Magic (Europe)",
    "Tintin On The Moon (Europe)",
    "Wild Streets (Europe)",
]

print("測試截圖中顯示 '→ ()' 的遊戲")
print("=" * 70)
print()

for game_name in test_games:
    print(f"原文: {game_name}")

    entry = GameEntry(key=game_name, original_name=game_name)

    result = translator.translate_game(
        entry,
        translate_name=True,
        translate_desc=False,
        skip_translated=False
    )

    print(f"  翻譯: {result.name}")
    print(f"  來源: {result.name_source}")

    if result.name == translator.clean_filename(game_name):
        print(f"  ⚠️  翻譯結果與清理後的原文相同")

    print()

print("=" * 70)
print("結論：檢查翻譯引擎是否正常運作")
