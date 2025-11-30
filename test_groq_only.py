"""
測試 Groq API Key 是否有效
"""

from translation_api import TranslationAPIManager


def test_groq_key():
    """測試你的 Groq API Key"""

    print("=" * 60)
    print("測試 Groq API Key 有效性")
    print("=" * 60)

    # 使用你在 gui.py 中預設的 Groq Key
    groq_key = "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"

    manager = TranslationAPIManager(
        groq_api_key=groq_key,
        gemini_api_key=None,  # 不使用 Gemini
        enable_groq=True,
        enable_gemini=False   # 停用 Gemini
    )

    test_games = [
        "Tetris",
        "Asteroids",
        "Breakout"
    ]

    print(f"\n使用 Groq Key: {groq_key[:20]}...")
    print(f"測試遊戲: {test_games}\n")

    results = []
    for game in test_games:
        print(f"翻譯: {game}")
        result = manager.translate_game_name(game, "arcade")
        results.append(result)
        print(f"  → {result}\n")

    # 統計
    stats = manager.get_stats()
    print("=" * 60)
    print("統計結果")
    print("=" * 60)
    print(f"Groq 成功: {stats['groq']['success']} 次")
    print(f"Groq 失敗: {stats['groq']['fail']} 次")

    success_count = sum(1 for r in results if r is not None)
    print(f"\n翻譯成功: {success_count}/{len(test_games)}")

    if success_count == len(test_games):
        print("\n✅ Groq API Key 有效且運作正常！")
    elif success_count > 0:
        print(f"\n⚠️ 部分成功 ({success_count}/{len(test_games)})")
        print("   可能接近免費額度上限")
    else:
        print("\n❌ Groq API Key 無效或已超過額度")
        print("   請檢查：")
        print("   1. API Key 是否正確")
        print("   2. 是否超過免費額度（30次/分鐘、14,400次/天）")

    print("=" * 60)


if __name__ == "__main__":
    test_groq_key()
