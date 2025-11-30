"""從 gamelist.xml 移除 [中文] 標記"""
import os
import xml.etree.ElementTree as ET
import shutil
from datetime import datetime
from pathlib import Path


def clean_gamelist(file_path):
    """清理單個 gamelist.xml"""
    # 解析 XML
    tree = ET.parse(file_path)
    root = tree.getroot()

    changed = False
    for game in root.findall('game'):
        name_elem = game.find('name')
        if name_elem is not None and name_elem.text:
            original = name_elem.text
            if original.startswith('[中文]'):
                # 移除 [中文] 標記
                new_name = original.replace('[中文]', '')
                name_elem.text = new_name
                changed = True
                print(f"  修正: {original} → {new_name}")

    return changed, tree


def main():
    gamelists_dir = Path("gamelists_local")
    fixed_count = 0
    total_fixes = 0

    for platform_dir in gamelists_dir.iterdir():
        if not platform_dir.is_dir():
            continue

        gamelist_file = platform_dir / "gamelist.xml"
        if not gamelist_file.exists():
            continue

        print(f"\n檢查 {platform_dir.name}...")

        try:
            changed, tree = clean_gamelist(gamelist_file)

            if changed:
                # 備份
                backup_file = f"backups/gamelist_{platform_dir.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fixed.xml"
                os.makedirs("backups", exist_ok=True)
                shutil.copy2(gamelist_file, backup_file)

                # 儲存
                xml_str = ET.tostring(
                    tree.getroot(), encoding='unicode', method='xml')
                xml_content = f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'

                with open(gamelist_file, 'w', encoding='utf-8') as f:
                    f.write(xml_content)

                fixed_count += 1
                print(f"  ✓ 已修正並儲存")
            else:
                print(f"  OK，無需修正")

        except Exception as e:
            print(f"  ✗ 處理失敗: {e}")

    print(f"\n{'='*60}")
    print(f"完成！已修正 {fixed_count} 個平台的 gamelist.xml")


if __name__ == "__main__":
    main()
