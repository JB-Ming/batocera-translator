"""單獨測試 vectrex 平台的翻譯"""
import json
from pathlib import Path
import google.generativeai as genai

# 設定
TRANSLATIONS_DIR = Path("translations")
API_KEY = "AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 讀取待翻譯檔案
with open(TRANSLATIONS_DIR / "to_translate_names_vectrex.json", 'r', encoding='utf-8') as f:
    to_translate = json.load(f)

print(f"待翻譯項目: {len(to_translate)} 個\n")

# 準備 prompt
texts = list(to_translate.keys())
prompt = f"""請將以下遊戲名稱從英文翻譯成繁體中文。

請以 JSON 格式回傳翻譯結果，格式如下：
{{
  "原始英文1": "繁體中文翻譯1",
  "原始英文2": "繁體中文翻譯2"
}}

注意事項：
1. 只回傳 JSON，不要有其他文字或解釋
2. 使用台灣地區的常用遊戲譯名
3. 如果是專有名詞或品牌名稱，使用通用譯名
4. 保持簡潔
5. 年份和標籤（如 PD, Prototype, light pen）保持原樣

待翻譯的遊戲名稱：
{json.dumps(texts, ensure_ascii=False, indent=2)}"""

print("正在呼叫 Gemini API...")
response = model.generate_content(prompt)

# 解析回應
response_text = response.text.strip()
if response_text.startswith('```json'):
    response_text = response_text[7:]
if response_text.startswith('```'):
    response_text = response_text[3:]
if response_text.endswith('```'):
    response_text = response_text[:-3]

response_text = response_text.strip()

# 解析並儲存
translations = json.loads(response_text)
print(f"✓ API 回傳 {len(translations)} 個翻譯\n")

# 顯示前 10 個翻譯
print("翻譯範例（前 10 個）：")
print("-" * 80)
for i, (eng, chi) in enumerate(list(translations.items())[:10], 1):
    print(f"{i}. {eng}")
    print(f"   → {chi}\n")

# 儲存
output_file = TRANSLATIONS_DIR / "translations_vectrex_gemini.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"✓ 已儲存至: {output_file}")
