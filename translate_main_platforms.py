"""翻譯主要平台"""
import sys
import os
from translator import GamelistTranslator

# 設定控制台編碼
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')


def main():
    # 主要平台列表
    main_platforms = [
        'nes', 'snes', 'megadrive', 'gba', 'n64',
        'ps1', 'psx', 'dreamcast', 'arcade', 'fbneo'
    ]

    print("=" * 60)
    print("開始翻譯主要平台")
    print("=" * 60)

    translator = GamelistTranslator()

    total_translated = 0

    for platform in main_platforms:
        gamelist_path = f"gamelists_local/{platform}/gamelist.xml"

        if not os.path.exists(gamelist_path):
            print(f"\n⊗ {platform}: 檔案不存在，跳過")
            continue

        print(f"\n{'='*60}")
        print(f"處理平台: {platform.upper()}")
        print(f"{'='*60}")

        try:
            updated_count = translator.update_gamelist(gamelist_path, platform)

            total_translated += updated_count
            print(f"\n✓ {platform}: 處理完成")

        except Exception as e:
            print(f"\n✗ {platform} 處理失敗: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("翻譯完成！")
    print(f"{'='*60}")
    print(f"已翻譯: {total_translated} 個遊戲")


if __name__ == "__main__":
    main()
