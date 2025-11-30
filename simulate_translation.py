"""
完整翻譯流程模擬測試
使用 gamelists_local/3do/gamelist.xml 進行測試
"""

from translator import GamelistTranslator
from pathlib import Path


def simulate_translation():
    """模擬完整翻譯流程"""

    print("=" * 70)
    print("Batocera 遊戲清單翻譯工具 - 完整流程模擬")
    print("=" * 70)

    # 初始化翻譯器
    translator = GamelistTranslator(
        groq_api_key="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",
        gemini_api_key="AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes",
        deepl_api_key=None,
        translations_dir="translations",
        local_cache_file="local_cache.json",
        display_mode="chinese_english",  # 中文 (英文)
        max_name_length=100,
        translate_desc=False,  # 先不翻譯描述，只翻譯名稱
        enable_groq=True,
        enable_gemini=True,
        enable_deepl=False,
        enable_mymemory=False,
        enable_googletrans=False
    )

    # 測試檔案路徑
    gamelist_path = Path("gamelists_local/3do/gamelist.xml")
    platform = "3do"

    print(f"\n📁 目標檔案: {gamelist_path}")
    print(f"🎮 平台: {platform.upper()}")
    print(f"📝 顯示模式: 中文 (英文)")
    print(f"🔧 API 設定: Groq (優先) → Gemini (備援)")

    if not gamelist_path.exists():
        print(f"\n❌ 錯誤：找不到檔案 {gamelist_path}")
        return

    print(f"\n✅ 檔案存在，開始處理...")
    print("\n" + "-" * 70)

    # 執行翻譯（dry_run=True 只預覽，不實際修改）
    print("\n🔍 預覽模式（不實際修改檔案）\n")
    translator.update_gamelist(
        str(gamelist_path),
        platform=platform,
        dry_run=True
    )

    print("\n" + "-" * 70)

    # 詢問是否實際執行
    print("\n⚠️  以上是預覽結果")
    response = input("\n是否要實際執行翻譯並修改檔案？(y/n): ")

    if response.lower() == 'y':
        print("\n" + "=" * 70)
        print("開始實際翻譯...")
        print("=" * 70 + "\n")

        translator.update_gamelist(
            str(gamelist_path),
            platform=platform,
            dry_run=False
        )

        print("\n" + "=" * 70)
        print("✅ 翻譯完成！")
        print("=" * 70)

        # 顯示統計
        translator.api_manager.print_stats()

        print("\n📂 檔案已更新:")
        print(f"   - 翻譯後: {gamelist_path}")
        print(f"   - 備份檔: backups/gamelist_3do_*.xml")

    else:
        print("\n❌ 已取消實際翻譯")
        print("   (預覽模式不會修改檔案)")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    simulate_translation()
