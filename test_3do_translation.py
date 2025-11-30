"""
測試翻譯 3DO 遊戲（使用 API 而非語系包）
"""

from translation_api import TranslationAPIManager


def test_3do_games():
    """測試翻譯 3DO 平台遊戲"""

    print("=" * 70)
    print("測試 3DO 遊戲翻譯（使用 Groq/Gemini API）")
    print("=" * 70)

    manager = TranslationAPIManager(
        groq_api_key="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",
        gemini_api_key="AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes",
        enable_groq=True,
        enable_gemini=True
    )

    games = [
        "Alone in the Dark",
        "Lemmings",
        "Need for Speed, The",
        "Return Fire",
        "Road Rash",
        "Samurai Shodown",
        "Space Hulk - Vengeance of the Blood Angels",
        "Star Control II",
        "Star Fighter",
        "Wing Commander III - Heart of the Tiger"
    ]

    platform = "3do"

    print(f"\n將翻譯 {len(games)} 個 3DO 遊戲\n")

    results = {}
    for i, game in enumerate(games, 1):
        print(f"[{i}/{len(games)}] {game}")
        translation = manager.translate_game_name(game, platform)
        results[game] = translation
        if translation:
            print(f"  ✅ {translation}\n")
        else:
            print(f"  ❌ 翻譯失敗\n")

    # 統計
    print("=" * 70)
    print("統計結果")
    print("=" * 70)
    stats = manager.get_stats()

    print(f"\nGroq API: 成功 {stats['groq']['success']} 次")
    print(f"Gemini API: 成功 {stats['gemini']['success']} 次")

    success = sum(1 for v in results.values() if v)
    print(f"\n總成功率: {success}/{len(games)} ({success/len(games)*100:.1f}%)")

    # 顯示翻譯對照表
    print("\n" + "=" * 70)
    print("翻譯對照表")
    print("=" * 70)
    for eng, chi in results.items():
        if chi:
            print(f"{eng:45} → {chi}")
        else:
            print(f"{eng:45} → (未翻譯)")

    print("=" * 70)


if __name__ == "__main__":
    test_3do_games()
