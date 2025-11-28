"""
階段 2：翻譯語系包
模擬翻譯過程，將待翻譯的內容轉換成翻譯語系包
（實際應用時，這裡會呼叫 Google Translate API、DeepL 或本地 LLM）
"""
import json
from pathlib import Path

# 設定路徑
TRANSLATIONS_DIR = Path("translations")

# 模擬翻譯函數（實際使用時替換成真實的翻譯 API）


def mock_translate(text):
    """模擬翻譯：簡單在前面加上 [中文]"""
    # 實際應該是：
    # return google_translate(text, target='zh-TW')
    # 或：return deepl_translate(text, target='zh-TW')
    # 或：return llm_translate(text)
    return f"[中文]{text}"


def translate_dictionary(to_translate_file, output_file):
    """翻譯字典檔案"""
    print(f"\n處理: {to_translate_file.name}")

    # 讀取待翻譯檔案
    with open(to_translate_file, 'r', encoding='utf-8') as f:
        to_translate = json.load(f)

    total = len(to_translate)
    print(f"  待翻譯項目: {total} 個")

    if total == 0:
        print("  ⊘ 跳過（無內容）")
        return

    # 執行翻譯
    translated = {}
    for i, (english, _) in enumerate(to_translate.items(), 1):
        # 模擬翻譯（實際使用時呼叫真實的翻譯 API）
        chinese = mock_translate(english)
        translated[english] = chinese

        # 顯示進度（每 100 個顯示一次）
        if i % 100 == 0 or i == total:
            print(f"  進度: {i}/{total} ({i*100//total}%)")

    # 儲存翻譯結果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    print(f"  ✓ 已生成: {output_file.name}")

    return total


def main():
    print("=" * 60)
    print("階段 2：翻譯語系包（模擬模式）")
    print("=" * 60)
    print("\n注意：這是模擬模式，實際使用時應替換成真實的翻譯 API")
    print("可選方案：")
    print("  1. Google Translate API")
    print("  2. DeepL API")
    print("  3. Azure Translator")
    print("  4. 本地 LLM (Ollama, LM Studio)")
    print("-" * 60)

    total_translated_names = 0
    total_translated_descs = 0

    # 處理所有待翻譯的名稱檔案
    name_files = sorted(TRANSLATIONS_DIR.glob("to_translate_names_*.json"))
    desc_files = sorted(TRANSLATIONS_DIR.glob(
        "to_translate_descriptions_*.json"))

    print(f"\n找到 {len(name_files)} 個名稱檔案，{len(desc_files)} 個描述檔案")

    # 翻譯名稱
    print("\n" + "=" * 60)
    print("翻譯遊戲名稱")
    print("=" * 60)

    for to_translate_file in name_files:
        platform = to_translate_file.name.replace(
            "to_translate_names_", "").replace(".json", "")
        output_file = TRANSLATIONS_DIR / f"translations_{platform}.json"

        count = translate_dictionary(to_translate_file, output_file)
        if count:
            total_translated_names += count

    # 翻譯描述
    print("\n" + "=" * 60)
    print("翻譯遊戲描述")
    print("=" * 60)

    for to_translate_file in desc_files:
        platform = to_translate_file.name.replace(
            "to_translate_descriptions_", "").replace(".json", "")
        output_file = TRANSLATIONS_DIR / f"descriptions_{platform}.json"

        count = translate_dictionary(to_translate_file, output_file)
        if count:
            total_translated_descs += count

    # 統計報告
    print("\n" + "=" * 60)
    print("階段 2 完成統計")
    print("=" * 60)
    print(f"已翻譯名稱: {total_translated_names} 個")
    print(f"已翻譯描述: {total_translated_descs} 個")
    print(f"\n生成檔案位置:")
    print(f"  - 名稱翻譯: {TRANSLATIONS_DIR}/translations_*.json")
    print(f"  - 描述翻譯: {TRANSLATIONS_DIR}/descriptions_*.json")
    print("\n提示：實際使用時，請將 mock_translate() 替換成真實的翻譯 API")


if __name__ == "__main__":
    main()
