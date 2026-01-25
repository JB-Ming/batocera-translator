"""測試翻譯功能是否會卡住"""
import sys
import time
from src.core.translator import TranslationEngine
from src.core.dictionary import GameEntry
from src.services.wikipedia import WikipediaService
from src.services.search import SearchService
from src.services.translate import TranslateService


def test_translation():
    print("初始化翻譯引擎...")
    translator = TranslationEngine(target_language='zh-TW')

    # 設置服務
    translator.set_wiki_service(WikipediaService())
    translator.set_search_service(SearchService())
    translator.set_translate_api(TranslateService())

    # 測試遊戲列表
    test_games = [
        "Donkey Kong",
        "Metroid",
    ]

    print("\n開始測試翻譯...\n")

    for i, game_name in enumerate(test_games, 1):
        print(f"[{i}/{len(test_games)}] 翻譯: {game_name}")

        # 創建測試條目
        entry = GameEntry(
            key=game_name,
            original_name=game_name
        )

        # 測試各個服務
        print("\n  === 測試各服務 ===")

        # Wikipedia
        wiki_service = WikipediaService()
        wiki_result = wiki_service.search(game_name, 'zh-TW')
        print(f"  Wikipedia: {wiki_result}")

        # Search
        search_service = SearchService()
        search_result = search_service.search(game_name, 'zh-TW')
        print(f"  Search: {search_result}")

        # Translate API
        translate_service = TranslateService()
        translate_result = translate_service.translate(game_name, 'zh-TW')
        print(f"  Translate: {translate_result}")

        print("\n  === 完整翻譯流程 ===")

        # 記錄開始時間
        start_time = time.time()

        try:
            # 翻譯（設置5秒超時）
            result = translator.translate_game(
                entry,
                translate_name=True,
                translate_desc=False,
                skip_translated=False
            )

            elapsed = time.time() - start_time

            if result.name:
                print(f"  ✓ 結果: {result.name}")
                print(f"  來源: {result.name_source}")
                print(f"  耗時: {elapsed:.2f}秒")
            else:
                print(f"  ✗ 翻譯失敗")
                print(f"  耗時: {elapsed:.2f}秒")

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"  ✗ 錯誤: {str(e)}")
            print(f"  耗時: {elapsed:.2f}秒")

        print()

        # 檢查是否卡住（超過10秒）
        if elapsed > 10:
            print("⚠️ 警告：翻譯時間過長，可能有卡住問題！")
            break

    print("\n測試完成！")


if __name__ == "__main__":
    test_translation()
