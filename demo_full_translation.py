"""
完整翻譯模擬 - 使用 API 直接翻譯 3DO 遊戲
展示完整流程：讀取 → 翻譯 → 寫回
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import shutil
from translation_api import TranslationAPIManager


def translate_3do_complete():
    """完整翻譯流程演示"""

    print("=" * 70)
    print("Batocera 遊戲清單完整翻譯流程演示")
    print("=" * 70)

    # 設定
    gamelist_path = Path("gamelists_local/3do/gamelist.xml")
    platform = "3do"
    display_mode = "chinese_english"  # 中文 (英文)

    print(f"\n📁 檔案: {gamelist_path}")
    print(f"🎮 平台: {platform.upper()}")
    print(f"📝 模式: {display_mode}")
    print(f"🔧 API: Groq (優先) → Gemini (備援)")

    # 初始化 API
    api_manager = TranslationAPIManager(
        groq_api_key="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",
        gemini_api_key="AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes",
        enable_groq=True,
        enable_gemini=True
    )

    # === 步驟 1: 讀取 XML ===
    print("\n" + "-" * 70)
    print("步驟 1: 讀取遊戲清單")
    print("-" * 70)

    tree = ET.parse(gamelist_path)
    root = tree.getroot()
    games = root.findall('.//game')

    print(f"✅ 讀取完成，共 {len(games)} 個遊戲")

    # === 步驟 2: 翻譯遊戲名稱 ===
    print("\n" + "-" * 70)
    print("步驟 2: 翻譯遊戲名稱")
    print("-" * 70 + "\n")

    translations = {}
    unique_games = set()

    for game in games:
        name_elem = game.find('name')
        if name_elem is not None and name_elem.text:
            original_name = name_elem.text.strip()

            # 去除重複（例如 Wing Commander 有 4 個光碟）
            if original_name not in unique_games:
                unique_games.add(original_name)

                print(f"翻譯: {original_name}")
                chinese_name = api_manager.translate_game_name(
                    original_name, platform)

                if chinese_name:
                    translations[original_name] = chinese_name
                    print(f"  ✅ {chinese_name}\n")
                else:
                    translations[original_name] = None
                    print(f"  ❌ 翻譯失敗\n")

    # === 步驟 3: 格式化名稱 ===
    print("-" * 70)
    print("步驟 3: 格式化遊戲名稱")
    print("-" * 70 + "\n")

    def format_name(english, chinese):
        """根據顯示模式格式化名稱"""
        if not chinese:
            return english

        if display_mode == "chinese_only":
            return chinese
        elif display_mode == "chinese_english":
            return f"{chinese} ({english})"
        elif display_mode == "english_chinese":
            return f"{english} ({chinese})"
        else:  # english_only
            return english

    for original, chinese in translations.items():
        formatted = format_name(original, chinese)
        print(f"{original:45} → {formatted}")

    # === 步驟 4: 備份原檔 ===
    print("\n" + "-" * 70)
    print("步驟 4: 備份原始檔案")
    print("-" * 70)

    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"gamelist_{platform}_{timestamp}.xml"
    shutil.copy2(gamelist_path, backup_path)
    print(f"✅ 備份至: {backup_path}")

    # === 步驟 5: 寫回 XML ===
    print("\n" + "-" * 70)
    print("步驟 5: 更新 XML 檔案")
    print("-" * 70)

    updated_count = 0
    for game in games:
        name_elem = game.find('name')
        if name_elem is not None and name_elem.text:
            original_name = name_elem.text.strip()

            if original_name in translations:
                chinese_name = translations[original_name]
                formatted_name = format_name(original_name, chinese_name)
                name_elem.text = formatted_name
                updated_count += 1

    tree.write(gamelist_path, encoding='utf-8', xml_declaration=True)
    print(f"✅ 已更新 {updated_count} 個遊戲名稱")

    # === 完成 ===
    print("\n" + "=" * 70)
    print("✅ 翻譯完成！")
    print("=" * 70)

    # 統計
    api_manager.print_stats()

    print(f"\n📂 檔案位置:")
    print(f"   原始檔備份: {backup_path}")
    print(f"   翻譯後檔案: {gamelist_path}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    translate_3do_complete()
