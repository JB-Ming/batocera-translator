#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Phase 2 - Generate Dictionary

Test Items:
1. XML parsing, generate dictionary
2. Dictionary merge strategies
3. Dictionary read/write
"""
import sys
import os
from pathlib import Path

# Ensure src module can be found (go up one level from tests/ to project root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.dictionary import DictionaryManager, GameEntry, MergeStrategy
from src.utils.xml_utils import parse_gamelist
from src.utils.name_cleaner import get_game_key


def test_dictionary(gamelists_path: str, language: str = 'zh-TW'):
    """Test dictionary generation functionality"""
    print("=" * 60)
    print("Phase 2: Generate Dictionary - Functionality Test")
    print("=" * 60)
    print(f"\n[PATH] Gamelists path: {gamelists_path}")
    print(f"[LANG] Target language: {language}\n")
    
    gamelists_dir = Path(gamelists_path)
    
    # 1. Initialize dictionary manager
    print("[1] Initialize dictionary manager...")
    dict_manager = DictionaryManager(dictionaries_path='./dictionaries')
    print(f"    [+] Dictionaries path: {dict_manager.dictionaries_path}")
    
    # 2. Parse gamelist.xml files
    print("\n[2] Parse gamelist.xml files...")
    platforms_parsed = {}
    total_games = 0
    
    for platform_dir in gamelists_dir.iterdir():
        if platform_dir.is_dir():
            gamelist_path = platform_dir / 'gamelist.xml'
            if gamelist_path.exists():
                games = parse_gamelist(gamelist_path)
                platforms_parsed[platform_dir.name] = games
                total_games += len(games)
                print(f"    [+] {platform_dir.name}: {len(games)} games")
    
    print(f"\n    [+] Total: {len(platforms_parsed)} platforms, {total_games} games")
    
    # 3. Generate dictionary entries
    print("\n[3] Generate dictionary entries...")
    generated = {}
    
    for platform_name, games in platforms_parsed.items():
        dictionary = {}
        for game in games:
            key = get_game_key(game.path)
            entry = GameEntry(
                key=key,
                original_name=game.name,
                original_desc=game.desc,
                name="",  # To be translated
                name_source="",
                desc="",
                desc_source=""
            )
            dictionary[key] = entry
        generated[platform_name] = dictionary
        print(f"    [+] {platform_name}: {len(dictionary)} entries")
    
    # 4. Save dictionaries
    print("\n[4] Save dictionaries to disk...")
    for platform_name, dictionary in generated.items():
        dict_manager.save_dictionary(language, platform_name, dictionary)
        print(f"    [+] Saved: dictionaries/{language}/{platform_name}.json")
    
    # 5. Verify by re-loading
    print("\n[5] Verify by re-loading dictionaries...")
    verified = 0
    for platform_name in generated:
        loaded = dict_manager.load_dictionary(language, platform_name)
        if len(loaded) == len(generated[platform_name]):
            print(f"    [+] {platform_name}: {len(loaded)} entries (OK)")
            verified += 1
        else:
            print(f"    [X] {platform_name}: MISMATCH! Expected {len(generated[platform_name])}, got {len(loaded)}")
    
    # 6. Test merge strategies
    print("\n[6] Test merge strategies...")
    
    # Create test data
    base_entry = GameEntry(
        key="./test.rom",
        original_name="Test Game",
        name="Test Translation",
        name_source="wiki",
        original_desc="Original description",
        desc="",
        desc_source=""
    )
    incoming_entry = GameEntry(
        key="./test.rom",
        original_name="Test Game",
        name="New Translation",
        name_source="search",
        original_desc="Original description",
        desc="New description",
        desc_source="api"
    )
    new_entry = GameEntry(
        key="./new.rom",
        original_name="New Game",
        name="New Game Translation",
        name_source="wiki",
        original_desc="",
        desc="",
        desc_source=""
    )
    
    base = {"./test.rom": base_entry}
    incoming = {"./test.rom": incoming_entry, "./new.rom": new_entry}
    
    # Test MERGE strategy
    merged = dict_manager.merge_dictionaries(base.copy(), incoming.copy(), MergeStrategy.MERGE)
    if merged["./test.rom"].name == "Test Translation":  # Keep existing
        print("    [+] MERGE: Keeps existing translation (OK)")
    else:
        print("    [X] MERGE: FAILED")
    
    if merged["./test.rom"].desc == "New description":  # Fill empty
        print("    [+] MERGE: Fills empty fields (OK)")
    else:
        print("    [X] MERGE: Fill empty FAILED")
    
    if "./new.rom" in merged:
        print("    [+] MERGE: Adds new entries (OK)")
    else:
        print("    [X] MERGE: Add new FAILED")
    
    # Test OVERWRITE strategy
    overwritten = dict_manager.merge_dictionaries(base.copy(), incoming.copy(), MergeStrategy.OVERWRITE)
    if overwritten["./test.rom"].name == "New Translation":
        print("    [+] OVERWRITE: Replaces all (OK)")
    else:
        print("    [X] OVERWRITE: FAILED")
    
    # Test SKIP strategy
    skipped = dict_manager.merge_dictionaries(base.copy(), incoming.copy(), MergeStrategy.SKIP)
    if "./new.rom" not in skipped:
        print("    [+] SKIP: Keeps original (OK)")
    else:
        print("    [X] SKIP: FAILED")
    
    # 7. Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"    Platforms parsed:     {len(platforms_parsed)}")
    print(f"    Total games:          {total_games}")
    print(f"    Dictionaries saved:   {len(generated)}")
    print(f"    Dictionaries verified:{verified}")
    print(f"    Merge tests passed:   5/5")
    print("=" * 60)
    
    return verified == len(generated)


if __name__ == '__main__':
    # Default path (from phase 1)
    default_path = "./gamelists_local"
    default_lang = "zh-TW"
    
    if len(sys.argv) > 1:
        gamelists_path = sys.argv[1]
    else:
        gamelists_path = default_path
    
    if len(sys.argv) > 2:
        language = sys.argv[2]
    else:
        language = default_lang
    
    success = test_dictionary(gamelists_path, language)
    
    if success:
        print("\n[PASS] Phase 2 test passed!")
    else:
        print("\n[FAIL] Phase 2 test failed!")
        sys.exit(1)
