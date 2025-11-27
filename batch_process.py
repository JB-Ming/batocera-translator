"""
批次處理 Batocera 翻譯的完整流程
1. 複製所有 gamelist.xml
2. 提取所有需要翻譯的內容
3. 建立統一字典檔
4. 批次翻譯
5. 寫回所有檔案
"""

import json
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime
from translator import GamelistTranslator


def load_config():
    """載入設定檔"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_gamelist_from_roms(platform_dir):
    """從遊戲檔案生成 gamelist.xml"""
    # 支援的遊戲檔案副檔名
    ROM_EXTENSIONS = {
        '.zip', '.7z', '.rar',  # 壓縮檔
        '.iso', '.cue', '.bin', '.img',  # 光碟映像
        '.nes', '.smc', '.sfc', '.gba', '.gbc', '.gb',  # 任天堂
        '.md', '.smd', '.gen', '.32x',  # SEGA
        '.psx', '.pbp', '.chd',  # PlayStation
        '.n64', '.z64', '.v64',  # N64
        '.nds', '.3ds', '.cia',  # DS/3DS
        '.wad', '.wbfs',  # Wii
        '.gcz', '.gcm',  # GameCube
        '.xex',  # Xbox
        '.cso', '.dax',  # PSP
        '.ws', '.wsc',  # WonderSwan
        '.ngp', '.ngc',  # Neo Geo Pocket
        '.a26', '.a52', '.a78',  # Atari
        '.col',  # ColecoVision
        '.int',  # Intellivision
        '.jag', '.j64',  # Jaguar
        '.lnx',  # Lynx
        '.pce',  # PC Engine
        '.sg', '.sc',  # SG-1000
        '.vec',  # Vectrex
        '.vb',  # Virtual Boy
        '.tap', '.tzx', '.z80', '.sna',  # ZX Spectrum
        '.d64', '.t64', '.prg',  # C64
        '.adf', '.ipf', '.dms',  # Amiga
        '.st', '.stx', '.msa',  # Atari ST
        '.dsk', '.cas',  # MSX/Amstrad
        '.p', '.81',  # ZX81
        '.o', '.o2',  # Odyssey2
        '.bin', '.a52',  # Atari 5200
        '.rom',  # 通用
    }

    # 掃描遊戲檔案
    game_files = []
    for ext in ROM_EXTENSIONS:
        game_files.extend(platform_dir.glob(f"*{ext}"))

    if not game_files:
        return None

    # 建立 XML 結構
    root = ET.Element('gameList')

    for game_file in sorted(game_files):
        # 移除副檔名作為遊戲名稱
        game_name = game_file.stem

        # 移除常見的標籤 (如 (USA), [!], 等)
        import re
        game_name = re.sub(r'\s*[\(\[].*?[\)\]]', '', game_name)
        game_name = game_name.strip()

        if not game_name:
            game_name = game_file.stem

        # 建立 game 元素
        game = ET.SubElement(root, 'game')

        path_elem = ET.SubElement(game, 'path')
        path_elem.text = f"./{game_file.name}"

        name_elem = ET.SubElement(game, 'name')
        name_elem.text = game_name

        # 加入空的 desc 元素供後續翻譯
        desc_elem = ET.SubElement(game, 'desc')
        desc_elem.text = ""

    return ET.ElementTree(root)


def copy_all_gamelists(batocera_path, local_base):
    """
    步驟1: 複製所有 gamelist.xml 到本機
    如果沒有 gamelist.xml,從遊戲檔案自動生成
    保持原本的資料夾結構
    """
    print("\n" + "="*60)
    print("步驟 1: 複製/生成所有 gamelist.xml 到本機")
    print("="*60)

    batocera_roms = Path(batocera_path)
    local_gamelists = Path(local_base)
    local_gamelists.mkdir(exist_ok=True)

    copied_files = []
    generated_count = 0

    # 掃描所有平台
    for platform_dir in batocera_roms.iterdir():
        if not platform_dir.is_dir():
            continue

        # 建立本機目錄
        local_platform_dir = local_gamelists / platform_dir.name
        local_platform_dir.mkdir(exist_ok=True)

        local_gamelist = local_platform_dir / "gamelist.xml"
        gamelist_path = platform_dir / "gamelist.xml"

        try:
            if gamelist_path.exists():
                # 複製現有的 gamelist.xml
                shutil.copy2(gamelist_path, local_gamelist)
                print(f"  ✓ {platform_dir.name} (已複製)")
            else:
                # 從遊戲檔案生成 gamelist.xml
                tree = generate_gamelist_from_roms(platform_dir)
                if tree:
                    xml_str = ET.tostring(
                        tree.getroot(), encoding='unicode', method='xml')
                    xml_content = f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'

                    with open(local_gamelist, 'w', encoding='utf-8') as f:
                        f.write(xml_content)

                    # 也寫一份到 Batocera
                    with open(gamelist_path, 'w', encoding='utf-8') as f:
                        f.write(xml_content)

                    generated_count += 1
                    print(
                        f"  ✓ {platform_dir.name} (已生成 {len(tree.findall('.//game'))} 個遊戲)")
                else:
                    print(f"  - {platform_dir.name} (無遊戲檔案)")
                    continue

            copied_files.append({
                'platform': platform_dir.name,
                'source': str(gamelist_path),
                'local': str(local_gamelist)
            })
        except Exception as e:
            print(f"  ✗ {platform_dir.name}: {e}")

    print(f"\n共處理 {len(copied_files)} 個平台")
    if generated_count > 0:
        print(f"其中 {generated_count} 個平台自動生成了 gamelist.xml")

    # 儲存複製清單
    manifest_path = local_gamelists / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(copied_files, f, ensure_ascii=False, indent=2)

    return copied_files


def extract_all_texts(copied_files):
    """
    步驟2: 提取所有需要翻譯的文字
    建立統一的字典檔
    """
    print("\n" + "="*60)
    print("步驟 2: 提取所有需要翻譯的文字")
    print("="*60)

    all_names = set()
    all_descs = set()

    for file_info in copied_files:
        platform = file_info['platform']
        local_path = file_info['local']

        try:
            tree = ET.parse(local_path)
            root = tree.getroot()

            game_count = 0
            for game in root.findall('.//game'):
                name_elem = game.find('name')
                desc_elem = game.find('desc')

                if name_elem is not None and name_elem.text:
                    all_names.add(name_elem.text.strip())

                if desc_elem is not None and desc_elem.text:
                    # 只提取前500字元
                    desc_text = desc_elem.text.strip()[:500]
                    if desc_text:
                        all_descs.add(desc_text)

                game_count += 1

            print(f"  ✓ {platform}: {game_count} 個遊戲")

        except Exception as e:
            print(f"  ✗ {platform}: {e}")

    print(f"\n提取到:")
    print(f"  - {len(all_names)} 個唯一遊戲名稱")
    print(f"  - {len(all_descs)} 個唯一描述")

    # 建立字典檔
    translation_dict = {
        'names': {name: None for name in sorted(all_names)},
        'descriptions': {desc: None for desc in sorted(all_descs)},
        'created_at': datetime.now().isoformat()
    }

    dict_path = Path(__file__).parent / "translation_master.json"
    with open(dict_path, 'w', encoding='utf-8') as f:
        json.dump(translation_dict, f, ensure_ascii=False, indent=2)

    print(f"\n字典檔已建立: {dict_path}")
    return dict_path


def translate_dictionary(dict_path):
    """
    步驟3: 批次翻譯字典檔
    """
    print("\n" + "="*60)
    print("步驟 3: 批次翻譯字典檔")
    print("="*60)

    with open(dict_path, 'r', encoding='utf-8') as f:
        translation_dict = json.load(f)

    translator = GamelistTranslator(
        translations_dir='translations',
        display_mode='chinese_english',
        translate_desc=True
    )

    # 翻譯名稱
    print("\n翻譯遊戲名稱...")
    total_names = len(translation_dict['names'])
    translated_names = 0

    for idx, name in enumerate(translation_dict['names'].keys(), 1):
        print(f"  [{idx}/{total_names}] {name[:50]}...", end='', flush=True)

        # 嘗試從現有字典檔找
        chinese_name = translator.extract_chinese_name(name, 'UNKNOWN')

        if chinese_name and chinese_name != name:
            translation_dict['names'][name] = chinese_name
            translated_names += 1
            print(f" → {chinese_name}")
        else:
            # Google 搜尋
            result = translator.translate_name(name, 'UNKNOWN')
            if result and result != name:
                translation_dict['names'][name] = result
                translated_names += 1
                print(f" → {result}")
            else:
                translation_dict['names'][name] = name  # 保持原名
                print(" (保持原名)")

    print(f"\n名稱翻譯完成: {translated_names}/{total_names}")

    # 翻譯描述
    print("\n翻譯遊戲描述...")
    total_descs = len(translation_dict['descriptions'])
    translated_descs = 0

    for idx, desc in enumerate(translation_dict['descriptions'].keys(), 1):
        print(f"  [{idx}/{total_descs}] {desc[:50]}...", end='', flush=True)

        result = translator.translate_description(desc)
        if result and result != desc:
            translation_dict['descriptions'][desc] = result
            translated_descs += 1
            print(f" ✓")
        else:
            translation_dict['descriptions'][desc] = desc
            print(" (保持原文)")

    print(f"\n描述翻譯完成: {translated_descs}/{total_descs}")

    # 儲存翻譯結果
    translation_dict['translated_at'] = datetime.now().isoformat()
    with open(dict_path, 'w', encoding='utf-8') as f:
        json.dump(translation_dict, f, ensure_ascii=False, indent=2)

    print(f"\n翻譯字典已更新: {dict_path}")
    return translation_dict


def apply_translations(copied_files, translation_dict, display_mode='chinese_english'):
    """
    步驟4: 套用翻譯到所有 gamelist
    """
    print("\n" + "="*60)
    print("步驟 4: 套用翻譯到所有 gamelist")
    print("="*60)

    updated_count = 0

    for file_info in copied_files:
        platform = file_info['platform']
        local_path = file_info['local']

        try:
            tree = ET.parse(local_path)
            root = tree.getroot()

            game_updated = 0

            for game in root.findall('.//game'):
                name_elem = game.find('name')
                desc_elem = game.find('desc')

                # 更新名稱
                if name_elem is not None and name_elem.text:
                    original_name = name_elem.text.strip()
                    chinese_name = translation_dict['names'].get(original_name)

                    if chinese_name and chinese_name != original_name:
                        # 套用顯示模式
                        if display_mode == 'chinese_english':
                            name_elem.text = f"{chinese_name} ({original_name})"
                        elif display_mode == 'chinese_only':
                            name_elem.text = chinese_name
                        else:
                            name_elem.text = original_name

                        game_updated += 1

                # 更新描述
                if desc_elem is not None and desc_elem.text:
                    original_desc = desc_elem.text.strip()[:500]
                    translated_desc = translation_dict['descriptions'].get(
                        original_desc)

                    if translated_desc and translated_desc != original_desc:
                        desc_elem.text = translated_desc

            # 儲存更新後的檔案
            xml_str = ET.tostring(root, encoding='unicode', method='xml')
            xml_content = f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'

            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)

            print(f"  ✓ {platform}: 更新了 {game_updated} 個遊戲")
            updated_count += 1

        except Exception as e:
            print(f"  ✗ {platform}: {e}")

    print(f"\n共更新 {updated_count} 個平台")


def write_back_to_batocera(copied_files):
    """
    步驟5: 寫回 Batocera
    """
    print("\n" + "="*60)
    print("步驟 5: 寫回 Batocera")
    print("="*60)

    success_count = 0
    failed_files = []

    for file_info in copied_files:
        platform = file_info['platform']
        source_path = file_info['source']
        local_path = file_info['local']

        try:
            # 先備份
            backup_dir = Path(__file__).parent / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"gamelist_{platform}_{timestamp}.xml"
            shutil.copy2(source_path, backup_path)

            # 讀取本機翻譯後的檔案
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 寫回 Batocera
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  ✓ {platform}")
            success_count += 1

        except Exception as e:
            print(f"  ✗ {platform}: {e}")
            failed_files.append({'platform': platform, 'error': str(e)})

    print(f"\n成功寫回 {success_count}/{len(copied_files)} 個平台")

    if failed_files:
        print("\n失敗清單:")
        for item in failed_files:
            print(f"  - {item['platform']}: {item['error']}")


def main():
    """主流程"""
    print("\n" + "="*60)
    print("Batocera 遊戲清單批次翻譯工具 v2.0")
    print("="*60)

    # 載入設定
    config = load_config()
    batocera_path = config['batocera_mount_path']
    local_base = Path(__file__).parent / "gamelists_local"

    # 步驟1: 複製所有 gamelist
    copied_files = copy_all_gamelists(batocera_path, local_base)

    if not copied_files:
        print("\n沒有找到任何 gamelist.xml 檔案!")
        return

    # 步驟2: 提取文字
    dict_path = extract_all_texts(copied_files)

    # 步驟3: 翻譯字典檔
    translation_dict = translate_dictionary(dict_path)

    # 步驟4: 套用翻譯
    apply_translations(copied_files, translation_dict,
                       display_mode=config.get('display_mode', 'chinese_english'))

    # 步驟5: 寫回 Batocera
    write_back_to_batocera(copied_files)

    print("\n" + "="*60)
    print("所有處理完成!")
    print("="*60)


if __name__ == '__main__':
    main()
