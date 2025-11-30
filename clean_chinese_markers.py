"""清理語系包中的 [中文] 標記"""
import json
from pathlib import Path


def clean_translation_files():
    """清理所有語系包中的 [中文] 標記"""
    translations_dir = Path("translations")

    if not translations_dir.exists():
        print("❌ translations 資料夾不存在")
        return

    total_cleaned = 0
    total_files = 0

    # 處理所有 translations_*.json 檔案
    for json_file in sorted(translations_dir.glob("translations_*.json")):
        platform = json_file.stem.replace("translations_", "")

        try:
            # 讀取 JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)

            # 統計錯誤
            before_count = sum(1 for v in translations.values() if '[中文]' in v)

            if before_count == 0:
                continue

            # 清理 [中文] 標記，保留原始遊戲名稱
            cleaned_translations = {}
            for key, value in translations.items():
                if '[中文]' in value:
                    # 移除 [中文] 前綴，恢復原文
                    cleaned_translations[key] = key
                else:
                    cleaned_translations[key] = value

            # 寫回檔案
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_translations, f,
                          ensure_ascii=False, indent=2)

            total_cleaned += before_count
            total_files += 1

            print(f"✓ {platform:20s}: 清理 {before_count:4d} 個錯誤翻譯")

        except Exception as e:
            print(f"✗ {platform:20s}: 錯誤 - {e}")

    print("\n" + "=" * 60)
    print(f"清理完成！")
    print(f"處理檔案數: {total_files}")
    print(f"清理錯誤數: {total_cleaned}")
    print("=" * 60)


if __name__ == "__main__":
    clean_translation_files()
