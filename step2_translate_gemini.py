"""
階段 2：翻譯語系包（使用 Gemini API 批次翻譯）
"""
import json
from pathlib import Path
import google.generativeai as genai
import time

# 設定路徑
TRANSLATIONS_DIR = Path("translations")

# Gemini API 設定
API_KEY = "AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 測試模式：只處理前 N 個平台
TEST_MODE = True
TEST_PLATFORMS = ['nes', 'snes', 'gba']  # 測試用的平台


def batch_translate_with_gemini(to_translate_dict, is_description=False):
    """
    使用 Gemini API 批次翻譯整個字典

    Args:
        to_translate_dict: 待翻譯的字典 {英文: ""}
        is_description: 是否為描述翻譯（影響 prompt）

    Returns:
        翻譯後的字典 {英文: 中文}
    """
    if not to_translate_dict:
        return {}

    # 準備待翻譯的文本列表
    texts = list(to_translate_dict.keys())

    # 建立 prompt（批次翻譯）
    if is_description:
        prompt = f"""你是專業的遊戲本地化專家。請將以下遊戲描述翻譯成台灣繁體中文。

翻譯策略：
1. 保持遊戲術語的準確性和一致性
2. 使用台灣玩家熟悉的遊戲用語
3. 保持描述的流暢度和可讀性
4. 技術名詞（如 ROM, CPU 等）保持原文或使用通用譯名

請以 JSON 格式回傳翻譯結果：
{{
  "原始英文描述1": "繁體中文翻譯1",
  "原始英文描述2": "繁體中文翻譯2"
}}

注意：只回傳 JSON，不要有其他文字或解釋。

待翻譯的描述：
{json.dumps(texts, ensure_ascii=False, indent=2)}"""
    else:
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

    try:
        print(f"  正在呼叫 Gemini API 翻譯 {len(texts)} 個項目...")
        response = model.generate_content(prompt)

        # 解析回應
        response_text = response.text.strip()

        # 移除可能的 markdown 代碼塊標記
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # 解析 JSON
        translations = json.loads(response_text)

        print(f"  ✓ API 回傳 {len(translations)} 個翻譯")
        return translations

    except json.JSONDecodeError as e:
        print(f"  ✗ JSON 解析失敗: {e}")
        print(f"  回應內容前 200 字元: {response_text[:200]}...")
        return {}
    except Exception as e:
        print(f"  ✗ 翻譯失敗: {e}")
        return {}


def translate_dictionary(to_translate_file, output_file, is_description=False):
    """翻譯字典檔案"""
    print(f"\n處理: {to_translate_file.name}")

    # 讀取待翻譯檔案
    with open(to_translate_file, 'r', encoding='utf-8') as f:
        to_translate = json.load(f)

    total = len(to_translate)
    print(f"  待翻譯項目: {total} 個")

    if total == 0:
        print("  ⊘ 跳過（無內容）")
        return 0

    # 批次翻譯
    translated = batch_translate_with_gemini(to_translate, is_description)

    if not translated:
        print("  ✗ 翻譯失敗，使用原文")
        translated = {k: k for k in to_translate.keys()}

    # 儲存翻譯結果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    print(f"  ✓ 已生成: {output_file.name}")

    return len(translated)


def main():
    print("=" * 60)
    print("階段 2：翻譯語系包（Gemini API 批次翻譯）")
    print("=" * 60)

    if TEST_MODE:
        print(f"\n⚠️  測試模式：只處理 {TEST_PLATFORMS} 平台")

    print(f"\nAPI: Gemini 1.5 Flash")
    print(f"模式: 批次翻譯（整包傳送）")
    print("-" * 60)

    total_translated_names = 0
    total_translated_descs = 0

    # 處理所有待翻譯的名稱檔案
    name_files = sorted(TRANSLATIONS_DIR.glob("to_translate_names_*.json"))
    desc_files = sorted(TRANSLATIONS_DIR.glob(
        "to_translate_descriptions_*.json"))

    # 測試模式：過濾平台
    if TEST_MODE:
        name_files = [f for f in name_files
                      if any(p in f.name for p in TEST_PLATFORMS)]
        desc_files = [f for f in desc_files
                      if any(p in f.name for p in TEST_PLATFORMS)]

    print(f"\n找到 {len(name_files)} 個名稱檔案，{len(desc_files)} 個描述檔案")

    # 翻譯名稱
    print("\n" + "=" * 60)
    print("翻譯遊戲名稱")
    print("=" * 60)

    for to_translate_file in name_files:
        platform = to_translate_file.name.replace(
            "to_translate_names_", "").replace(".json", "")
        output_file = TRANSLATIONS_DIR / f"translations_{platform}.json"

        count = translate_dictionary(to_translate_file, output_file,
                                     is_description=False)
        if count:
            total_translated_names += count

        # API 請求間隔
        time.sleep(2)

    # 翻譯描述
    print("\n" + "=" * 60)
    print("翻譯遊戲描述")
    print("=" * 60)

    for to_translate_file in desc_files:
        platform = to_translate_file.name.replace(
            "to_translate_descriptions_", "").replace(".json", "")
        output_file = TRANSLATIONS_DIR / f"descriptions_{platform}.json"

        count = translate_dictionary(to_translate_file, output_file,
                                     is_description=True)
        if count:
            total_translated_descs += count

        # API 請求間隔
        time.sleep(2)

    # 統計報告
    print("\n" + "=" * 60)
    print("階段 2 完成統計")
    print("=" * 60)
    print(f"已翻譯名稱: {total_translated_names} 個")
    print(f"已翻譯描述: {total_translated_descs} 個")
    print(f"\n生成檔案位置:")
    print(f"  - 名稱翻譯: {TRANSLATIONS_DIR}/translations_*.json")
    print(f"  - 描述翻譯: {TRANSLATIONS_DIR}/descriptions_*.json")

    if TEST_MODE:
        print("\n⚠️  這是測試模式的結果")
        print("確認翻譯品質後，請將 TEST_MODE 改為 False 處理所有平台")


if __name__ == "__main__":
    main()
