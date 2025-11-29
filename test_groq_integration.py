#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Groq API 整合

這個腳本會測試：
1. Groq API 連線
2. 遊戲名稱翻譯功能
3. TranslationAPIManager 整合
"""

from translation_api import TranslationAPIManager

# 測試遊戲清單
TEST_GAMES = [
    ("Super Mario Bros", "FC紅白機"),
    ("The Legend of Zelda", "FC紅白機"),
    ("Street Fighter II", "街機"),
    ("Final Fantasy VII", "PS1 PlayStation"),
    ("Sonic the Hedgehog", "MD Mega Drive"),
]


def test_groq_api():
    """測試 Groq API 翻譯功能"""

    print("=" * 70)
    print("🧪 Groq API 整合測試")
    print("=" * 70)
    print()

    # 初始化 API 管理器（只啟用 Groq）
    groq_key = "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"

    manager = TranslationAPIManager(
        groq_api_key=groq_key,
        enable_groq=True,
        enable_gemini=False,
        enable_deepl=False,
        enable_mymemory=False,
        enable_googletrans=False
    )

    print("✅ TranslationAPIManager 初始化成功")
    print(f"📝 使用 Groq API Key: {groq_key[:20]}...")
    print()

    # 測試每個遊戲
    print("🎮 開始測試遊戲名稱翻譯...")
    print("-" * 70)

    success_count = 0
    fail_count = 0

    for game_name, platform in TEST_GAMES:
        print(f"\n測試: {game_name} ({platform})")

        try:
            result = manager.translate_game_name(game_name, platform)

            if result:
                print(f"  ✅ 翻譯成功: {game_name} → {result}")
                success_count += 1
            else:
                print(f"  ❌ 翻譯失敗: 返回 None")
                fail_count += 1

        except Exception as e:
            print(f"  ❌ 發生錯誤: {e}")
            fail_count += 1

    # 顯示統計
    print()
    print("=" * 70)
    print("📊 測試結果統計")
    print("=" * 70)
    manager.print_stats()

    print()
    print(f"✅ 成功: {success_count}/{len(TEST_GAMES)}")
    print(f"❌ 失敗: {fail_count}/{len(TEST_GAMES)}")

    # 判斷測試結果
    if fail_count == 0:
        print()
        print("🎉 所有測試通過！Groq API 整合成功！")
        return True
    else:
        print()
        print("⚠️ 部分測試失敗，請檢查錯誤訊息")
        return False


if __name__ == "__main__":
    try:
        success = test_groq_api()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 測試被使用者中斷")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ 測試過程發生嚴重錯誤: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
