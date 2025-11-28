"""
階段 3：應用翻譯並寫回
套用翻譯語系包到 gamelist.xml 並寫回遠端目錄
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

# 設定路徑
GAMELISTS_LOCAL = Path("gamelists_local")
ROMS_REMOTE = Path("roms_remote")  # 模擬的遠端 WSL 路徑
TRANSLATIONS_DIR = Path("translations")
BACKUPS_DIR = Path("backups")
BACKUPS_DIR.mkdir(exist_ok=True)

# 顯示模式
DISPLAY_MODES = {
    'chinese_only': '{chinese}',
    'chinese_english': '{chinese} ({english})',
    'english_chinese': '{english} ({chinese})',
    'english_only': '{english}'
}


def load_translations(platform):
    """載入指定平台的翻譯語系包"""
    names_file = TRANSLATIONS_DIR / f"translations_{platform}.json"
    descs_file = TRANSLATIONS_DIR / f"descriptions_{platform}.json"

    names_dict = {}
    descs_dict = {}

    if names_file.exists():
        with open(names_file, 'r', encoding='utf-8') as f:
            names_dict = json.load(f)

    if descs_file.exists():
        with open(descs_file, 'r', encoding='utf-8') as f:
            descs_dict = json.load(f)

    return names_dict, descs_dict


def format_text(english, chinese, mode='chinese_only'):
    """根據顯示模式格式化文字"""
    if not chinese or chinese == english:
        return english

    template = DISPLAY_MODES.get(mode, DISPLAY_MODES['chinese_only'])
    return template.format(english=english, chinese=chinese)


def clean_text(text):
    """清理文字"""
    if not text:
        return ""
    return " ".join(text.strip().split())


def apply_translations(gamelist_path, platform, names_dict, descs_dict,
                       display_mode='chinese_only'):
    """套用翻譯到 gamelist.xml"""
    tree = ET.parse(gamelist_path)
    root = tree.getroot()

    stats = {'names': 0, 'descs': 0, 'total_games': 0}

    for game in root.findall('game'):
        stats['total_games'] += 1

        # 翻譯 name
        name_elem = game.find('name')
        if name_elem is not None and name_elem.text:
            original_name = clean_text(name_elem.text)
            if original_name in names_dict:
                translated = names_dict[original_name]
                new_name = format_text(original_name, translated,
                                       display_mode)
                name_elem.text = new_name
                stats['names'] += 1

        # 翻譯 desc
        desc_elem = game.find('desc')
        if desc_elem is not None and desc_elem.text:
            original_desc = clean_text(desc_elem.text)
            if original_desc in descs_dict:
                translated = descs_dict[original_desc]
                new_desc = format_text(original_desc, translated,
                                       display_mode)
                desc_elem.text = new_desc
                stats['descs'] += 1

    return tree, stats


def main():
    print("=" * 70)
    print("階段 3：應用翻譯並寫回")
    print("=" * 70)

    # 顯示模式選擇（可由使用者選擇）
    display_mode = 'chinese_only'  # 可改為 chinese_english 等
    print(f"\n顯示模式: {display_mode}")
    print(f"格式範例: {DISPLAY_MODES[display_mode]}")
    print("-" * 70)

    total_platforms = 0
    total_games = 0
    total_names_translated = 0
    total_descs_translated = 0

    # 遍歷本地 gamelist
    for platform_dir in sorted(GAMELISTS_LOCAL.iterdir()):
        if not platform_dir.is_dir():
            continue

        platform = platform_dir.name
        local_gamelist = platform_dir / "gamelist.xml"

        if not local_gamelist.exists():
            continue

        total_platforms += 1
        print(f"\n[{total_platforms}] 處理平台: {platform}")

        # 1. 載入翻譯語系包
        names_dict, descs_dict = load_translations(platform)
        print(f"   載入語系包: {len(names_dict)} 個名稱, "
              f"{len(descs_dict)} 個描述")

        if not names_dict and not descs_dict:
            print("   ⊘ 跳過（無翻譯資料）")
            continue

        # 2. 套用翻譯
        tree, stats = apply_translations(local_gamelist, platform,
                                         names_dict, descs_dict,
                                         display_mode)

        print(f"   翻譯統計: 遊戲 {stats['total_games']} 個, "
              f"名稱 {stats['names']} 個, "
              f"描述 {stats['descs']} 個")

        total_games += stats['total_games']
        total_names_translated += stats['names']
        total_descs_translated += stats['descs']

        # 3. 備份遠端原始檔案
        remote_gamelist = ROMS_REMOTE / platform / "gamelist.xml"
        if remote_gamelist.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BACKUPS_DIR / f"gamelist_{platform}_{timestamp}.xml"
            shutil.copy2(remote_gamelist, backup_file)
            print(f"   ✓ 已備份: {backup_file.name}")

        # 4. 寫回遠端目錄（模擬 WSL 路徑）
        tree.write(remote_gamelist, encoding='utf-8', xml_declaration=True)
        print(f"   ✓ 已寫回: {remote_gamelist}")

    # 統計報告
    print("\n" + "=" * 70)
    print("階段 3 完成統計")
    print("=" * 70)
    print(f"處理平台數: {total_platforms}")
    print(f"總遊戲數: {total_games}")
    print(f"已翻譯名稱: {total_names_translated}")
    print(f"已翻譯描述: {total_descs_translated}")
    print(f"\n備份位置: {BACKUPS_DIR}/")
    print(f"遠端位置: {ROMS_REMOTE}/")
    print("\n流程完成！所有翻譯已套用並寫回遠端目錄。")


if __name__ == "__main__":
    main()
