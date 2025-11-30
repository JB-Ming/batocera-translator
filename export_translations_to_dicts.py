"""將 local_cache.json 匯出成各平台的語系包（按字母排序）"""
import json
import os
from pathlib import Path
from collections import defaultdict


def main():
    # 讀取快取
    with open('local_cache.json', encoding='utf-8') as f:
        cache = json.load(f)

    names_cache = cache.get('names', {})
    print(f"載入 {len(names_cache)} 筆翻譯")

    # 掃描 gamelists_local 目錄
    gamelists_dir = Path('gamelists_local')
    translations_dir = Path('translations')
    translations_dir.mkdir(exist_ok=True)

    platforms = sorted([d.name for d in gamelists_dir.iterdir() if d.is_dir()])

    print(f"\n找到 {len(platforms)} 個平台")
    print("="*60)

    total_exported = 0

    for platform in platforms:
        gamelist_file = gamelists_dir / platform / 'gamelist.xml'

        if not gamelist_file.exists():
            continue

        print(f"\n處理平台: {platform.upper()}")

        # 解析 XML 提取遊戲名稱
        import xml.etree.ElementTree as ET
        tree = ET.parse(gamelist_file)
        root = tree.getroot()

        platform_translations = {}

        for game in root.findall('game'):
            name_elem = game.find('name')
            if name_elem is not None and name_elem.text:
                game_name = name_elem.text

                # 移除 [中文] 標記（如果有）
                clean_name = game_name.replace('[中文]', '')

                # 檢查快取中是否有翻譯
                if clean_name in names_cache:
                    chinese_name = names_cache[clean_name]
                    # 只保留有效的英文→中文翻譯
                    if (chinese_name and
                        not chinese_name.startswith('[中文]') and
                            chinese_name != clean_name):
                        platform_translations[clean_name] = chinese_name

        if platform_translations:
            # **按照 key 字母排序**
            sorted_translations = dict(sorted(platform_translations.items()))

            # 儲存到語系包
            output_file = translations_dir / f'translations_{platform}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_translations, f, ensure_ascii=False, indent=2)

            total_exported += len(sorted_translations)
            print(f"  ✓ 匯出 {len(sorted_translations)} 筆翻譯")
            print(f"    → {output_file}")
        else:
            print(f"  ⊗ 無翻譯資料")

    print(f"\n{'='*60}")
    print(
        f"完成！共匯出 {total_exported} 筆翻譯到 {len([f for f in translations_dir.glob('translations_*.json')])} 個語系包")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
