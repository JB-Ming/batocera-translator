"""檢查 clean_name 邏輯"""
from src.core.translator import TranslationEngine

translator = TranslationEngine(target_language='zh-TW')

test_names = [
    "Pang (Europe)",
    "Robocop 2 (Europe)",
    "Tintin On The Moon (Europe)",
]

for name in test_names:
    clean = translator.clean_filename(name)
    print(f"原文: {name}")
    print(f"清理後: {clean}")
    print()
