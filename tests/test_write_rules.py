# -*- coding: utf-8 -*-
"""
測試 write_rules 功能

此腳本用於驗證 XmlWriter 的 write_rules 設定是否正確：
- 翻譯的 name 可以寫回 gamelist 的 desc
- 翻譯的 desc 可以寫回 gamelist 的 name
- 各種 format 組合都能正確運作
"""

import sys
import tempfile
import shutil
from pathlib import Path

# 將專案根目錄加入 Python Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.writer import XmlWriter, DisplayFormat, WriteStrategy
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
    <game>
        <path>./test_game_2.zip</path>
        <name>Original Game Name 2</name>
        <desc>Original game description 2</desc>
    </game>
    <game>
        <path>./test_game_3.zip</path>
        <name>Original Game Name 3</name>
        <desc>Original game description 3</desc>
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
            name="Translated Name 1",
            name_source="api",
            original_desc="Original game description 1",
            desc="Translated Description 1",
            desc_source="api"
        ),
        "test_game_2": GameEntry(
            key="test_game_2",
            original_name="Original Game Name 2",
            name="Translated Name 2",
            name_source="api",
            original_desc="Original game description 2",
            desc="Translated Description 2",
            desc_source="api"
        ),
        "test_game_3": GameEntry(
            key="test_game_3",
            original_name="Original Game Name 3",
            name="Translated Name 3",
            name_source="api",
            original_desc="Original game description 3",
            desc="Translated Description 3",
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
    """
    測試：翻譯的 name 寫到 desc 欄位
    
    write_rules:
        name: {target: desc, format: translated}
        desc: {target: skip}  (跳過原本的 desc 翻譯)
    """
    print("\n" + "=" * 60)
    print("測試 1: 翻譯的 name 寫到 desc 欄位")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gamelist_path = temp_path / "gamelist.xml"
        backup_path = temp_path / "backups"
        
        # 建立測試檔案
        create_test_gamelist(gamelist_path)
        dictionary = create_test_dictionary()
        
        print(f"\n寫入前的 gamelist.xml:")
        before = read_gamelist_content(gamelist_path)
        for key, data in before.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        # 設定 write_rules：翻譯的 name 寫到 desc
        write_rules = {
            "name": {"target": "desc", "format": "translated"},
            "desc": {"target": "skip"}  # 跳過 desc 的翻譯
        }
        
        # 執行寫入
        writer = XmlWriter(backup_path=str(backup_path))
        result = writer.write_translations(
            xml_path=gamelist_path,
            dictionary=dictionary,
            platform="test",
            strategy=WriteStrategy.DICT_PRIORITY,
            auto_backup=False,
            write_rules=write_rules
        )
        
        print(f"\n寫入結果: 總數={result.total}, 更新={result.updated}, 跳過={result.skipped}")
        
        print(f"\n寫入後的 gamelist.xml:")
        after = read_gamelist_content(gamelist_path)
        for key, data in after.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        # 驗證
        print("\n驗證結果:")
        success = True
        for key in dictionary.keys():
            expected_desc = dictionary[key].name  # 翻譯的 name 應該出現在 desc
            actual_desc = after[key]['desc']
            actual_name = after[key]['name']
            
            # name 應該保持原樣，desc 應該是翻譯的 name
            if actual_desc == expected_desc:
                print(f"  [OK] {key}: desc 正確包含翻譯的 name")
            else:
                print(f"  [FAIL] {key}: desc 不正確")
                print(f"    期望: {expected_desc}")
                print(f"    實際: {actual_desc}")
                success = False
        
        return success


def test_desc_to_name():
    """
    測試：翻譯的 desc 寫到 name 欄位
    
    write_rules:
        name: {target: skip}
        desc: {target: name, format: translated}
    """
    print("\n" + "=" * 60)
    print("測試 2: 翻譯的 desc 寫到 name 欄位")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gamelist_path = temp_path / "gamelist.xml"
        backup_path = temp_path / "backups"
        
        create_test_gamelist(gamelist_path)
        dictionary = create_test_dictionary()
        
        print(f"\n寫入前的 gamelist.xml:")
        before = read_gamelist_content(gamelist_path)
        for key, data in before.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        # 設定 write_rules：翻譯的 desc 寫到 name
        write_rules = {
            "name": {"target": "skip"},
            "desc": {"target": "name", "format": "translated"}
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
        
        print(f"\n寫入結果: 總數={result.total}, 更新={result.updated}, 跳過={result.skipped}")
        
        print(f"\n寫入後的 gamelist.xml:")
        after = read_gamelist_content(gamelist_path)
        for key, data in after.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        print("\n驗證結果:")
        success = True
        for key in dictionary.keys():
            expected_name = dictionary[key].desc  # 翻譯的 desc 應該出現在 name
            actual_name = after[key]['name']
            
            if actual_name == expected_name:
                print(f"  [OK] {key}: name 正確包含翻譯的 desc")
            else:
                print(f"  [FAIL] {key}: name 不正確")
                print(f"    期望: {expected_name}")
                print(f"    實際: {actual_name}")
                success = False
        
        return success


def test_cross_write():
    """
    測試：交叉寫入
    - 翻譯的 name 寫到 desc
    - 翻譯的 desc 寫到 name
    
    write_rules:
        name: {target: desc, format: translated}
        desc: {target: name, format: translated}
    """
    print("\n" + "=" * 60)
    print("測試 3: 交叉寫入 (name→desc, desc→name)")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gamelist_path = temp_path / "gamelist.xml"
        backup_path = temp_path / "backups"
        
        create_test_gamelist(gamelist_path)
        dictionary = create_test_dictionary()
        
        print(f"\n寫入前的 gamelist.xml:")
        before = read_gamelist_content(gamelist_path)
        for key, data in before.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        # 設定 write_rules：交叉寫入
        write_rules = {
            "name": {"target": "desc", "format": "translated"},
            "desc": {"target": "name", "format": "translated"}
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
        
        print(f"\n寫入結果: 總數={result.total}, 更新={result.updated}, 跳過={result.skipped}")
        
        print(f"\n寫入後的 gamelist.xml:")
        after = read_gamelist_content(gamelist_path)
        for key, data in after.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        print("\n驗證結果:")
        success = True
        for key in dictionary.keys():
            expected_name = dictionary[key].desc  # 翻譯的 desc 應該寫到 name
            expected_desc = dictionary[key].name  # 翻譯的 name 應該寫到 desc
            actual_name = after[key]['name']
            actual_desc = after[key]['desc']
            
            name_ok = actual_name == expected_name
            desc_ok = actual_desc == expected_desc
            
            if name_ok and desc_ok:
                print(f"  [OK] {key}: 交叉寫入正確")
            else:
                if not name_ok:
                    print(f"  [FAIL] {key}: name 不正確 (期望: {expected_name}, 實際: {actual_name})")
                if not desc_ok:
                    print(f"  [FAIL] {key}: desc 不正確 (期望: {expected_desc}, 實際: {actual_desc})")
                success = False
        
        return success


def test_format_with_original():
    """
    測試：帶原文格式的寫入
    
    write_rules:
        name: {target: desc, format: trans_orig}
    """
    print("\n" + "=" * 60)
    print("測試 4: 帶原文格式寫入 name→desc (trans_orig)")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gamelist_path = temp_path / "gamelist.xml"
        backup_path = temp_path / "backups"
        
        create_test_gamelist(gamelist_path)
        dictionary = create_test_dictionary()
        
        print(f"\n寫入前的 gamelist.xml:")
        before = read_gamelist_content(gamelist_path)
        for key, data in before.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        # 設定 write_rules：翻譯的 name 寫到 desc，格式為 翻譯(原文)
        write_rules = {
            "name": {"target": "desc", "format": "trans_orig"},
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
        
        print(f"\n寫入結果: 總數={result.total}, 更新={result.updated}, 跳過={result.skipped}")
        
        print(f"\n寫入後的 gamelist.xml:")
        after = read_gamelist_content(gamelist_path)
        for key, data in after.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        print("\n驗證結果:")
        success = True
        for key in dictionary.keys():
            entry = dictionary[key]
            # trans_orig 格式：翻譯 (原文)
            expected_desc = f"{entry.name} ({entry.original_name})"
            actual_desc = after[key]['desc']
            
            if actual_desc == expected_desc:
                print(f"  [OK] {key}: desc 正確包含 翻譯(原文) 格式")
            else:
                print(f"  [FAIL] {key}: desc 不正確")
                print(f"    期望: {expected_desc}")
                print(f"    實際: {actual_desc}")
                success = False
        
        return success


def test_normal_write():
    """
    測試：標準寫入（確保沒有破壞原本功能）
    
    write_rules:
        name: {target: name, format: translated}
        desc: {target: desc, format: translated}
    """
    print("\n" + "=" * 60)
    print("測試 5: 標準寫入 (name→name, desc→desc)")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gamelist_path = temp_path / "gamelist.xml"
        backup_path = temp_path / "backups"
        
        create_test_gamelist(gamelist_path)
        dictionary = create_test_dictionary()
        
        print(f"\n寫入前的 gamelist.xml:")
        before = read_gamelist_content(gamelist_path)
        for key, data in before.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        # 標準寫入規則
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
        
        print(f"\n寫入結果: 總數={result.total}, 更新={result.updated}, 跳過={result.skipped}")
        
        print(f"\n寫入後的 gamelist.xml:")
        after = read_gamelist_content(gamelist_path)
        for key, data in after.items():
            print(f"  {key}:")
            print(f"    name: {data['name']}")
            print(f"    desc: {data['desc']}")
        
        print("\n驗證結果:")
        success = True
        for key in dictionary.keys():
            expected_name = dictionary[key].name
            expected_desc = dictionary[key].desc
            actual_name = after[key]['name']
            actual_desc = after[key]['desc']
            
            name_ok = actual_name == expected_name
            desc_ok = actual_desc == expected_desc
            
            if name_ok and desc_ok:
                print(f"  [OK] {key}: 標準寫入正確")
            else:
                if not name_ok:
                    print(f"  [FAIL] {key}: name 不正確 (期望: {expected_name}, 實際: {actual_name})")
                if not desc_ok:
                    print(f"  [FAIL] {key}: desc 不正確 (期望: {expected_desc}, 實際: {actual_desc})")
                success = False
        
        return success


def main():
    """執行所有測試"""
    print("=" * 60)
    print("Write Rules 功能測試")
    print("=" * 60)
    
    results = {
        "翻譯的 name 寫到 desc": test_name_to_desc(),
        "翻譯的 desc 寫到 name": test_desc_to_name(),
        "交叉寫入": test_cross_write(),
        "帶原文格式寫入": test_format_with_original(),
        "標準寫入": test_normal_write(),
    }
    
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("所有測試通過！write_rules 功能正常運作。")
    else:
        print("有測試失敗，請檢查 write_rules 的實作。")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
