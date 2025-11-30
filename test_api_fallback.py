"""
測試 API 降級機制
驗證當 Groq API 失敗時，系統會自動切換到 Gemini API
"""

from translation_api import TranslationAPIManager
import json


def test_fallback_mechanism():
    """測試 API 降級機制"""

    print("=" * 60)
    print("測試 API 降級機制")
    print("=" * 60)

    # 情境 1: 使用無效的 Groq API Key（模擬 API 失敗）
    print("\n【情境 1】使用無效的 Groq API Key（模擬失敗）")
    print("-" * 60)

    manager = TranslationAPIManager(
        groq_api_key="gsk_INVALID_KEY_FOR_TESTING",  # 無效 Key（故意測試失敗）
        gemini_api_key="AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes",  # 有效的 Gemini Key
        enable_groq=True,
        enable_gemini=True
    )

    test_games = [
        "Donkey Kong",
        "Pac-Man",
        "Space Invaders"
    ]

    print(f"\n測試遊戲: {test_games}\n")

    for game in test_games:
        print(f"翻譯: {game}")
        result = manager.translate_game_name(game, "arcade")
        print(f"  結果: {result}")
        print(f"  預期: Groq 失敗 → 自動使用 Gemini\n")

    # 顯示統計
    print("\n" + "=" * 60)
    print("統計報告")
    print("=" * 60)
    stats = manager.get_stats()

    print(f"\nGroq API:")
    print(f"  成功: {stats['groq']['success']} 次")
    print(f"  失敗: {stats['groq']['fail']} 次")
    print(f"  ⚠️ 預期: 全部失敗（因為使用無效 Key）")

    print(f"\nGemini API:")
    print(f"  成功: {stats['gemini']['success']} 次")
    print(f"  失敗: {stats['gemini']['fail']} 次")
    print(f"  ✅ 預期: 全部成功（作為備援 API）")

    # 驗證結果
    print("\n" + "=" * 60)
    print("驗證結果")
    print("=" * 60)

    groq_failed = stats['groq']['fail']
    gemini_success = stats['gemini']['success']

    if groq_failed == len(test_games):
        if gemini_success == len(test_games):
            print("\n✅ 測試通過！")
            print("   - Groq API 失敗時成功降級到 Gemini")
            print("   - 所有遊戲都獲得翻譯")
        else:
            print("\n⚠️ 部分通過")
            print(f"   - Groq 正確失敗 ({groq_failed}/{len(test_games)})")
            print(f"   - Gemini 成功 {gemini_success}/{len(test_games)} 個")
            print("   - 可能是 Gemini API Key 也無效")
    else:
        print("\n❌ 測試失敗！")
        print("   降級機制可能有問題")

    print("\n" + "=" * 60)

    # 情境 2: 完全停用 Groq（只使用 Gemini）
    print("\n【情境 2】完全停用 Groq API（只使用 Gemini）")
    print("-" * 60)

    manager2 = TranslationAPIManager(
        groq_api_key="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",  # 有效的 Groq Key
        gemini_api_key="AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes",  # 有效的 Gemini Key
        enable_groq=False,  # 停用 Groq
        enable_gemini=True
    )

    test_game = "Galaga"
    print(f"\n翻譯: {test_game}")
    result = manager2.translate_game_name(test_game, "arcade")
    print(f"  結果: {result}")
    print(f"  預期: 直接使用 Gemini（不嘗試 Groq）")

    stats2 = manager2.get_stats()
    print(f"\nGroq API: 成功 {stats2['groq']['success']} 次（預期 0）")
    print(
        f"Gemini API: 成功 {stats2['gemini']['success']} 次（預期 1 或 0，取決於 Key 是否有效）")

    if stats2['groq']['success'] == 0:
        print("\n✅ 測試通過！Groq 已完全停用")
        if stats2['gemini']['success'] == 0:
            print("   ⚠️ 注意：Gemini 也未成功翻譯（可能是 API Key 無效）")
    else:
        print("\n❌ 測試失敗！")

    print("\n" + "=" * 60)

    # 情境 3: 超過免費額度的模擬（查看錯誤訊息）
    print("\n【情境 3】模擬 API 超過免費額度")
    print("-" * 60)
    print("\n提示：")
    print("  - Groq 免費額度: 30次/分鐘、14,400次/天")
    print("  - Gemini 免費額度: 15次/分鐘、1,500次/天")
    print("  - 當超過額度時，會顯示錯誤並自動切換到備援 API")
    print("\n如果你的 Groq Key 已超過額度，執行此測試會看到降級效果。")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_fallback_mechanism()
