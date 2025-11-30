"""
最終測試：使用有效的 Groq 和 Gemini API Keys
驗證完整翻譯功能
"""

from translation_api import TranslationAPIManager


def test_with_valid_keys():
    """使用有效的 API Keys 測試"""

    print("=" * 60)
    print("使用有效 API Keys 測試翻譯功能")
    print("=" * 60)

    manager = TranslationAPIManager(
        groq_api_key="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",
        gemini_api_key="AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes",
        enable_groq=True,
        enable_gemini=True
    )

    test_games = [
        ("Super Mario Bros", "nes"),
        ("The Legend of Zelda", "nes"),
        ("Street Fighter II", "arcade"),
        ("Final Fantasy VII", "ps1"),
        ("Sonic the Hedgehog", "megadrive")
    ]

    print("\n測試遊戲翻譯（Groq 優先，Gemini 備援）\n")

    results = []
    for game, platform in test_games:
        print(f"翻譯: {game} ({platform})")
        result = manager.translate_game_name(game, platform)
        results.append(result)
        if result:
            print(f"  ✅ {result}\n")
        else:
            print(f"  ❌ 翻譯失敗\n")

    # 統計
    print("=" * 60)
    print("統計結果")
    print("=" * 60)
    stats = manager.get_stats()

    print(f"\nGroq API:")
    print(f"  成功: {stats['groq']['success']} 次")
    print(f"  失敗: {stats['groq']['fail']} 次")

    print(f"\nGemini API:")
    print(f"  成功: {stats['gemini']['success']} 次")
    print(f"  失敗: {stats['gemini']['fail']} 次")

    success_count = sum(1 for r in results if r is not None)
    total = len(test_games)

    print(f"\n總成功率: {success_count}/{total} ({success_count/total*100:.1f}%)")

    if success_count == total:
        print("\n🎉 完美！所有遊戲都成功翻譯")
        if stats['groq']['success'] == total:
            print("   ✅ 全部使用 Groq API（最快速度）")
        elif stats['gemini']['success'] == total:
            print("   ✅ 全部使用 Gemini API（備援方案）")
        else:
            print(
                f"   ✅ Groq {stats['groq']['success']} 次 + Gemini {stats['gemini']['success']} 次")
    else:
        print(f"\n⚠️ 部分失敗：{total - success_count} 個遊戲未翻譯")

    print("=" * 60)


if __name__ == "__main__":
    test_with_valid_keys()
