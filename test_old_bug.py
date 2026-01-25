"""測試修復前的情況"""
# 模擬之前的錯誤代碼

class OldTranslateService:
    def __init__(self):
        self.cache = {}  # 有這個
        # 沒有 self._cache
    
    def translate(self, text):
        try:
            # 翻譯成功
            result = "翻譯結果"
            # 錯誤：使用不存在的 self._cache
            self._cache['key'] = result  # AttributeError!
            return result
        except Exception:
            return None  # 因為異常，返回 None

# 測試
service = OldTranslateService()
result = service.translate("Donkey Kong")
print(f"舊版本翻譯結果: {result}")
print("即使 Google Translate 翻譯成功，但因為快取錯誤拋出異常，最終返回 None")

print("\n" + "="*50)
print("\n這就是為什麼會出現大量 KEEP：")
print("1. Wikipedia 找不到 → None")
print("2. Gemini 沒設定 → 跳過")  
print("3. Search 找不到 → None")
print("4. Translate API → 翻譯成功但快取失敗 → None")
print("5. 所有方法都是 None → 保留原文 → KEEP")
