"""
階段 1：提取待翻譯內容
從遠端 ROMS 目錄複製 gamelist.xml 並提取待翻譯的 name 和 desc
"""
import json
import shutil
from pathlib import Path
from collections import OrderedDict
import xml.etree.ElementTree as ET

# 設定路徑
ROMS_REMOTE = Path("roms_remote")  # 模擬的遠端 WSL 路徑
GAMELISTS_LOCAL = Path("gamelists_local")
TRANSLATIONS_DIR = Path("translations")
TRANSLATIONS_DIR.mkdir(exist_ok=True)


def clean_text(text):
    """清理文字，移除多餘空白"""
    if not text:
        return ""
    return " ".join(text.strip().split())


def extract_from_gamelist(gamelist_path):
    """從 gamelist.xml 提取 name 和 desc"""
    names = OrderedDict()
    descriptions = OrderedDict()

    try:
        tree = ET.parse(gamelist_path)
        root = tree.getroot()

        for game in root.findall('game'):
            # 提取 name
            name_elem = game.find('name')
            if name_elem is not None and name_elem.text:
                name = clean_text(name_elem.text)
                if name and name not in names:
                    names[name] = ""

            # 提取 desc
            desc_elem = game.find('desc')
            if desc_elem is not None and desc_elem.text:
                desc = clean_text(desc_elem.text)
                if desc and desc not in descriptions:
                    descriptions[desc] = ""

        return names, descriptions
    except Exception as e:
        print(f"   ✗ 解析失敗: {e}")
        return OrderedDict(), OrderedDict()


def main():
    print("=" * 60)
    print("階段 1：提取待翻譯內容")
    print("=" * 60)

    # 清空並重建 gamelists_local
    if GAMELISTS_LOCAL.exists():
        print(f"\n清空本地目錄: {GAMELISTS_LOCAL}")
        shutil.rmtree(GAMELISTS_LOCAL)
    GAMELISTS_LOCAL.mkdir()

    total_platforms = 0
    total_names = 0
    total_descs = 0

    # 遍歷遠端 ROMS 目錄
    print(f"\n掃描遠端目錄: {ROMS_REMOTE}")
    print("-" * 60)

    for platform_dir in sorted(ROMS_REMOTE.iterdir()):
        if not platform_dir.is_dir():
            continue

        platform_name = platform_dir.name
        gamelist_file = platform_dir / "gamelist.xml"

        if not gamelist_file.exists():
            continue

        total_platforms += 1
        print(f"\n[{total_platforms}] 處理平台: {platform_name}")

        # 1. 複製 gamelist.xml 到本地
        local_platform_dir = GAMELISTS_LOCAL / platform_name
        local_platform_dir.mkdir(exist_ok=True)
        local_gamelist = local_platform_dir / "gamelist.xml"

        shutil.copy2(gamelist_file, local_gamelist)
        print(f"   ✓ 已複製: {gamelist_file} -> {local_gamelist}")

        # 2. 提取待翻譯內容
        names, descriptions = extract_from_gamelist(local_gamelist)

        print(f"   ✓ 提取 {len(names)} 個遊戲名稱")
        print(f"   ✓ 提取 {len(descriptions)} 個遊戲描述")

        # 3. 儲存待翻譯語系包
        if names:
            names_file = TRANSLATIONS_DIR / \
                f"to_translate_names_{platform_name}.json"
            with open(names_file, 'w', encoding='utf-8') as f:
                json.dump(names, f, ensure_ascii=False, indent=2)
            print(f"   ✓ 已生成: {names_file}")
            total_names += len(names)

        if descriptions:
            descs_file = TRANSLATIONS_DIR / \
                f"to_translate_descriptions_{platform_name}.json"
            with open(descs_file, 'w', encoding='utf-8') as f:
                json.dump(descriptions, f, ensure_ascii=False, indent=2)
            print(f"   ✓ 已生成: {descs_file}")
            total_descs += len(descriptions)

    # 統計報告
    print("\n" + "=" * 60)
    print("階段 1 完成統計")
    print("=" * 60)
    print(f"處理平台數: {total_platforms}")
    print(f"待翻譯名稱: {total_names} 個")
    print(f"待翻譯描述: {total_descs} 個")
    print(f"\n生成檔案位置:")
    print(f"  - 本地 gamelist: {GAMELISTS_LOCAL}/")
    print(f"  - 待翻譯語系包: {TRANSLATIONS_DIR}/to_translate_*.json")


if __name__ == "__main__":
    main()
