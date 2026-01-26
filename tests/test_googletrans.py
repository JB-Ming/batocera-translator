"""直接測試 Google Translate"""
from googletrans import Translator

translator = Translator()

test_words = ["Donkey Kong", "Metroid"]

for word in test_words:
    try:
        print(f"翻譯: {word}")
        result = translator.translate(word, dest='zh-tw', src='en')
        print(f"  結果: {result.text}")
        print(f"  原文: {result.origin}")
        print(f"  來源語言: {result.src}")
    except Exception as e:
        print(f"  錯誤: {e}")
    print()
