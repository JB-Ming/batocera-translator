"""檢查翻譯輸出的內容"""
from src.core.translator import TranslationEngine, TranslationOutput
from src.core.dictionary import GameEntry
from src.services.wikipedia import WikipediaService
from src.services.search import SearchService
from src.services.translate import TranslateService

# 初始化翻譯引擎
translator = TranslationEngine(target_language='zh-TW')
translator.set_wiki_service(WikipediaService())
translator.set_search_service(SearchService())
translator.set_translate_api(TranslateService())

test_name = "Pang (Europe)"

print(f"測試遊戲: {test_name}")
print("=" * 70)

entry = GameEntry(key=test_name, original_name=test_name)

print(f"\n1. entry.original_name = '{entry.original_name}'")
print(f"2. entry.name = '{entry.name}'")
print(f"3. entry.name_source = '{entry.name_source}'")

print("\n執行翻譯...")
output = translator.translate_game(
    entry,
    translate_name=True,
    translate_desc=False,
    skip_translated=False
)

print(f"\n翻譯後：")
print(f"4. output.name = '{output.name}'")
print(f"5. output.name_source = '{output.name_source}'")
print(f"6. output.result = {output.result}")

print(f"\n檢查 output.name 是否為真：")
print(f"7. bool(output.name) = {bool(output.name)}")
print(f"8. output.name != '' = {output.name != ''}")
print(f"9. len(output.name) = {len(output.name)}")

print(f"\n模擬 UI 邏輯：")
if output.name:
    print(f"✅ 會更新 entry.name = '{output.name}'")
    print(f"✅ 會更新 entry.name_source = '{output.name_source}'")
else:
    print(f"❌ 不會更新 entry（output.name 為空）")
    print(f"   這會導致 UI 顯示 '→ ()'")
