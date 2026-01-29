# -*- coding: utf-8 -*-
"""
簡化的 write_rules 功能測試
"""

import sys
import tempfile
from pathlib import Path

# 將專案根目錄加入 Python Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.writer import XmlWriter, WriteStrategy
from src.core.dictionary import GameEntry


def create_test_gamelist(path: Path):
    """建立測試用的 gamelist.xml"""
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<gameList>
    <game>
        <path>./test_game_1.zip</path>
        <name>Original Game Name 1</name>
        <desc>Original game description 1</desc>
    </game>
</gameList>
'''
    path.write_text(content, encoding='utf-8')


def create_test_dictionary():
    """建立測試用的翻譯字典"""
    # 注意: get_game_key 會移除副檔名，所以 key 應該是 "test_game_1" 而不是 "test_game_1.zip"
    return {
        "test_game_1": GameEntry(
            key="test_game_1",
            original_name="Original Game Name 1",
            name="Translated Name",  # 使用 ASCII 避免顯示問題
            name_source="api",
            original_desc="Original game description 1",
            desc="Translated Description",   # 使用 ASCII
            desc_source="api"
        ),
    }


def read_gamelist_content(path: Path):
    """讀取並解析 gamelist.xml"""
    import xml.etree.ElementTree as ET
    tree = ET.parse(path)
    root = tree.getroot()
    
    games = {}
    for game in root.findall('game'):
        path_elem = game.find('path')
        name_elem = game.find('name')
        desc_elem = game.find('desc')
        
        if path_elem is not None and path_elem.text:
            # 移除 ./ 前綴
            key = path_elem.text.replace('./', '')
            # 移除副檔名，與 get_game_key 一致
            if '.' in key:
                key = key.rsplit('.', 1)[0]
            games[key] = {
                'name': name_elem.text if name_elem is not None else '',
                'desc': desc_elem.text if desc_elem is not None else '',
            }
    return games


def test_name_to_desc():
    """測試：翻譯的 name 寫到 desc 欄位"""
    print("=" * 60)
    print("TEST: name -> desc")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gamelist_path = temp_path / "gamelist.xml"
        backup_path = temp_path / "backups"
        
        create_test_gamelist(gamelist_path)
        dictionary = create_test_dictionary()
        
        print("\nBEFORE:")
        before = read_gamelist_content(gamelist_path)
        for key, data in before.items():
            print(f"  name: {data['name']}")
            print(f"  desc: {data['desc']}")
        
        # write_rules: name -> desc
        write_rules = {
            "name": {"target": "desc", "format": "translated"},
            "desc": {"target": "skip"}
        }
        
        writer = XmlWriter(backup_path=str(backup_path))
        result = writer.write_translations(
            xml_path=gamelist_path,
            dictionary=dictionary,
            platform="test",
            strategy=WriteStrategy.DICT_PRIORITY,
            auto_backup=False,
            write_rules=write_rules
        )
        
        print(f"\nRESULT: total={result.total}, updated={result.updated}, skipped={result.skipped}")
        
        print("\nAFTER:")
        after = read_gamelist_content(gamelist_path)
        for key, data in after.items():
            print(f"  name: {data['name']}")
            print(f"  desc: {data['desc']}")
        
        # 驗證
        expected_desc = "Translated Name"  # 翻譯的 name 應該出現在 desc
        actual_desc = after["test_game_1"]['desc']
        
        print(f"\nVERIFY:")
        print(f"  Expected desc: {expected_desc}")
        print(f"  Actual desc  : {actual_desc}")
        
        if actual_desc == expected_desc:
            print("  STATUS: PASS")
            return True
        else:
            print("  STATUS: FAIL")
            return False


def test_standard():
    """測試：標準寫入"""
    print("\n" + "=" * 60)
    print("TEST: Standard (name -> name, desc -> desc)")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gamelist_path = temp_path / "gamelist.xml"
        backup_path = temp_path / "backups"
        
        create_test_gamelist(gamelist_path)
        dictionary = create_test_dictionary()
        
        print("\nBEFORE:")
        before = read_gamelist_content(gamelist_path)
        for key, data in before.items():
            print(f"  name: {data['name']}")
            print(f"  desc: {data['desc']}")
        
        # 標準 write_rules
        write_rules = {
            "name": {"target": "name", "format": "translated"},
            "desc": {"target": "desc", "format": "translated"}
        }
        
        writer = XmlWriter(backup_path=str(backup_path))
        result = writer.write_translations(
            xml_path=gamelist_path,
            dictionary=dictionary,
            platform="test",
            strategy=WriteStrategy.DICT_PRIORITY,
            auto_backup=False,
            write_rules=write_rules
        )
        
        print(f"\nRESULT: total={result.total}, updated={result.updated}, skipped={result.skipped}")
        
        print("\nAFTER:")
        after = read_gamelist_content(gamelist_path)
        for key, data in after.items():
            print(f"  name: {data['name']}")
            print(f"  desc: {data['desc']}")
        
        expected_name = "Translated Name"
        expected_desc = "Translated Description"
        actual_name = after["test_game_1"]['name']
        actual_desc = after["test_game_1"]['desc']
        
        print(f"\nVERIFY:")
        print(f"  Expected name: {expected_name}, Actual: {actual_name}")
        print(f"  Expected desc: {expected_desc}, Actual: {actual_desc}")
        
        if actual_name == expected_name and actual_desc == expected_desc:
            print("  STATUS: PASS")
            return True
        else:
            print("  STATUS: FAIL")
            return False


if __name__ == "__main__":
    r1 = test_standard()
    r2 = test_name_to_desc()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Standard write: {'PASS' if r1 else 'FAIL'}")
    print(f"  Name to desc:   {'PASS' if r2 else 'FAIL'}")
    
    sys.exit(0 if r1 and r2 else 1)
