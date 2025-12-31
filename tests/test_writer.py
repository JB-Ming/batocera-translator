#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Phase 4 - Write Back to XML

Test Items:
1. XML writer initialization
2. Display format functions
3. Backup functionality
4. Write translations to XML
5. Preview changes
"""
import sys
import os
import shutil
from pathlib import Path

# Ensure src module can be found (go up one level from tests/ to project root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.writer import XmlWriter, DisplayFormat, WriteStrategy, WriteResult
from src.core.dictionary import DictionaryManager, GameEntry
from src.utils.name_cleaner import get_game_key


def test_writer(gamelists_path: str = './gamelists_local',
                dictionary_path: str = './dictionaries',
                language: str = 'zh-TW'):
    """Test XML writer functionality"""
    print("=" * 60)
    print("Phase 4: Write Back to XML - Functionality Test")
    print("=" * 60)
    print(f"\n[PATH] Gamelists path: {gamelists_path}")
    print(f"[PATH] Dictionary path: {dictionary_path}")
    print(f"[LANG] Target language: {language}\n")
    
    gamelists_dir = Path(gamelists_path)
    
    # 1. Initialize XML writer
    print("[1] Initialize XML writer...")
    writer = XmlWriter(backup_path='./backups')
    print(f"    [+] Backup path: {writer.backup_path}")
    
    # 2. Test display format
    print("\n[2] Test display format functions...")
    test_cases = [
        (DisplayFormat.TRANSLATED_ONLY, "Translated", "Original", "Translated"),
        (DisplayFormat.TRANSLATED_ORIGINAL, "Translated", "Original", "Translated (Original)"),
        (DisplayFormat.ORIGINAL_TRANSLATED, "Translated", "Original", "Original (Translated)"),
        (DisplayFormat.ORIGINAL_ONLY, "Translated", "Original", "Original"),
    ]
    
    format_passed = 0
    for fmt, trans, orig, expected in test_cases:
        result = writer._format_text(trans, orig, fmt)
        status = "[OK]" if result == expected else "[FAIL]"
        if result == expected:
            format_passed += 1
        print(f"    {status} {fmt.name}: '{result}' (expected='{expected}')")
    
    print(f"    [+] Display format tests: {format_passed}/{len(test_cases)} passed")
    
    # 3. Test with sample platform
    print("\n[3] Find sample platform for testing...")
    dict_manager = DictionaryManager(dictionaries_path=dictionary_path)
    
    # Find a platform with gamelist
    sample_platform = None
    sample_xml_path = None
    sample_dictionary = {}
    
    if gamelists_dir.exists():
        for platform_dir in gamelists_dir.iterdir():
            if platform_dir.is_dir():
                gamelist_path = platform_dir / 'gamelist.xml'
                if gamelist_path.exists():
                    dictionary = dict_manager.load_dictionary(language, platform_dir.name)
                    if dictionary:
                        sample_platform = platform_dir.name
                        sample_xml_path = gamelist_path
                        sample_dictionary = dictionary
                        break
    
    if not sample_platform:
        print("    [!] No sample platform found, skipping write tests")
        return format_passed == len(test_cases)
    
    print(f"    [+] Using platform: {sample_platform}")
    print(f"    [+] XML path: {sample_xml_path}")
    print(f"    [+] Dictionary size: {len(sample_dictionary)} entries")
    
    # 4. Add some test translations to dictionary
    print("\n[4] Add test translations to dictionary...")
    translations_added = 0
    for key, entry in list(sample_dictionary.items())[:5]:
        if not entry.name:
            entry.name = f"Test Translation for {entry.original_name}"
            entry.name_source = "test"
            translations_added += 1
    print(f"    [+] Added {translations_added} test translations")
    
    # 5. Test preview changes
    print("\n[5] Test preview changes (dry run)...")
    changes = writer.preview_changes(sample_xml_path, sample_dictionary)
    print(f"    [+] Preview found {len(changes)} changes")
    for change in changes[:3]:  # Show first 3
        print(f"        - {change['field']}: '{change['before'][:30]}...' -> '{change['after'][:30]}...'")
    
    # 6. Test backup functionality
    print("\n[6] Test backup functionality...")
    backup_path = writer.backup_file(sample_xml_path, sample_platform)
    backup_exists = backup_path.exists()
    print(f"    [+] Backup created: {backup_path}")
    print(f"    [+] Backup exists: {backup_exists}")
    
    # 7. Test write translations (preview only, don't actually modify)
    print("\n[7] Test write translations (preview mode)...")
    result = writer.write_translations(
        xml_path=sample_xml_path,
        dictionary=sample_dictionary,
        platform=sample_platform,
        display_format=DisplayFormat.TRANSLATED_ONLY,
        strategy=WriteStrategy.DICT_PRIORITY,
        auto_backup=False,  # Already backed up
        preview_only=True   # Don't actually write
    )
    print(f"    [+] Total games: {result.total}")
    print(f"    [+] Would update: {result.updated}")
    print(f"    [+] Would skip: {result.skipped}")
    
    # 8. Test actual write (on a copy)
    print("\n[8] Test actual write (on a copy)...")
    
    # Create a test copy
    test_xml_path = gamelists_dir / sample_platform / 'gamelist_test.xml'
    shutil.copy2(sample_xml_path, test_xml_path)
    print(f"    [+] Created test copy: {test_xml_path}")
    
    # Write to test copy
    result = writer.write_translations(
        xml_path=test_xml_path,
        dictionary=sample_dictionary,
        platform=sample_platform,
        display_format=DisplayFormat.TRANSLATED_ONLY,
        strategy=WriteStrategy.DICT_PRIORITY,
        auto_backup=False,
        preview_only=False
    )
    print(f"    [+] Total games: {result.total}")
    print(f"    [+] Updated: {result.updated}")
    print(f"    [+] Skipped: {result.skipped}")
    
    # Verify write
    import xml.etree.ElementTree as ET
    tree = ET.parse(test_xml_path)
    root = tree.getroot()
    games_with_translation = 0
    for game in root.findall('game'):
        name_elem = game.find('name')
        if name_elem is not None and 'Test Translation' in (name_elem.text or ''):
            games_with_translation += 1
    
    print(f"    [+] Verified: {games_with_translation} games have test translation")
    
    # Clean up test file
    test_xml_path.unlink()
    print(f"    [+] Cleaned up test file")
    
    # 9. Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"    Display format tests:  {format_passed}/{len(test_cases)}")
    print(f"    Backup created:        {backup_exists}")
    print(f"    Preview changes:       {len(changes)}")
    print(f"    Write verified:        {games_with_translation > 0}")
    print("=" * 60)
    
    return format_passed == len(test_cases) and backup_exists


if __name__ == '__main__':
    # Default settings
    default_gamelists = "./gamelists_local"
    default_dicts = "./dictionaries"
    default_lang = "zh-TW"
    
    if len(sys.argv) > 1:
        gamelists_path = sys.argv[1]
    else:
        gamelists_path = default_gamelists
    
    if len(sys.argv) > 2:
        dict_path = sys.argv[2]
    else:
        dict_path = default_dicts
    
    if len(sys.argv) > 3:
        language = sys.argv[3]
    else:
        language = default_lang
    
    success = test_writer(gamelists_path, dict_path, language)
    
    if success:
        print("\n[PASS] Phase 4 test passed!")
    else:
        print("\n[FAIL] Phase 4 test failed!")
        sys.exit(1)
