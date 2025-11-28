"""
測試 Gemini API 翻譯功能
"""
import google.generativeai as genai
import time

# 設定 API Key
API_KEY = "AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes"
genai.configure(api_key=API_KEY)

# 建立模型（使用最新的 Gemini 1.5 Flash）
model = genai.GenerativeModel('gemini-1.5-flash')


def translate_with_gemini(text, target_lang='繁體中文'):
    """使用 Gemini 翻譯文字"""
    prompt = f"""請將以下英文翻譯成{target_lang}，只回傳翻譯結果，不要有任何額外說明：

{text}"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"翻譯失敗: {e}")
        return None


def test_game_names():
    """測試遊戲名稱翻譯"""
    print("=" * 60)
    print("測試 Gemini API - 遊戲名稱翻譯")
    print("=" * 60)

    test_names = [
        "Super Mario Bros",
        "The Legend of Zelda",
        "Final Fantasy VII",
        "Street Fighter II",
        "Metal Gear Solid",
        "Castlevania: Symphony of the Night",
        "Crash Bandicoot",
        "Gran Turismo",
        "Resident Evil 2",
        "Tekken 3"
    ]

    print(f"\n測試 {len(test_names)} 個遊戲名稱...\n")

    success_count = 0
    for i, name in enumerate(test_names, 1):
        print(f"[{i}/{len(test_names)}] 翻譯: {name}")
        result = translate_with_gemini(name)

        if result:
            print(f"    → {result}")
            success_count += 1
        else:
            print(f"    ✗ 失敗")

        # 避免請求過快
        if i < len(test_names):
            time.sleep(1)

    print(f"\n成功率: {success_count}/{len(test_names)}")


def test_game_description():
    """測試遊戲描述翻譯"""
    print("\n" + "=" * 60)
    print("測試 Gemini API - 遊戲描述翻譯")
    print("=" * 60 + "\n")

    test_desc = "A classic platformer game where you control a plumber on a quest to rescue Princess Peach from the evil Bowser."

    print(f"原文: {test_desc}\n")
    result = translate_with_gemini(test_desc)

    if result:
        print(f"譯文: {result}")
    else:
        print("✗ 翻譯失敗")


def main():
    print("\n🔧 Gemini API 翻譯測試")
    print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}\n")

    try:
        # 測試遊戲名稱
        test_game_names()

        # 測試遊戲描述
        test_game_description()

        print("\n" + "=" * 60)
        print("✓ 測試完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
