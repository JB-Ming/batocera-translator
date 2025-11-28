"""測試新的翻譯策略（官方譯名優先）"""
import json
from pathlib import Path
import google.generativeai as genai

TRANSLATIONS_DIR = Path("translations")
API_KEY = "AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 讀取 NES 平台的待翻譯檔案
with open(TRANSLATIONS_DIR / "to_translate_names_nes.json", 'r', encoding='utf-8') as f:
    to_translate = json.load(f)

print(f"測試遊戲: {list(to_translate.keys())[0]}\n")

texts = list(to_translate.keys())
prompt = f"""你是專業的遊戲本地化專家，精通各種遊戲平台的官方中文譯名。

請為以下遊戲提供台灣地區的正式譯名，按照以下優先順序：

1. **官方譯名優先**：如果該遊戲在台灣、香港或中國大陸有官方中文版，請使用台灣地區的官方譯名
   - 例如：Super Mario Bros. → 超級瑪利歐兄弟
   - 例如：The Legend of Zelda → 薩爾達傳說
   - 例如：Street Fighter → 快打旋風

2. **通用譯名次之**：如果沒有官方譯名，但有廣為流傳的譯名，使用該譯名
   - 例如：Pac-Man → 小精靈

3. **意譯方式**：如果完全沒有既有譯名，根據遊戲內容進行合理翻譯
   - 保持簡潔、易懂
   - 符合台灣遊戲玩家的用語習慣

4. **保持原文**：以下情況保持英文原文
   - 品牌專有名詞（如 Sonic, Tetris 等已成為通用名稱的遊戲）
   - 開發版本標記（Prototype, Beta, Demo）
   - 技術標籤（PD, light pen 等）
   - 年份和括號內的補充資訊

請以 JSON 格式回傳結果：
{{
  "原始英文名稱1": "台灣官方譯名或合適譯名1",
  "原始英文名稱2": "台灣官方譯名或合適譯名2"
}}

注意：只回傳 JSON，不要有其他文字、解釋或註解。

遊戲列表：
{json.dumps(texts, ensure_ascii=False, indent=2)}"""

print("使用新策略呼叫 Gemini API...\n")
response = model.generate_content(prompt)

response_text = response.text.strip()
if response_text.startswith('```json'):
    response_text = response_text[7:]
if response_text.startswith('```'):
    response_text = response_text[3:]
if response_text.endswith('```'):
    response_text = response_text[:-3]
response_text = response_text.strip()

translations = json.loads(response_text)

print("翻譯結果：")
print("-" * 80)
for eng, chi in translations.items():
    print(f"原文: {eng}")
    print(f"譯名: {chi}")
    print()
