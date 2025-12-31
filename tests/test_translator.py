#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Phase 3 - Translation

Test Items:
1. Translation Engine core functions
2. Wikipedia API service
3. Search service
4. Translation API service
5. Keep original logic
"""
import sys
import os
from pathlib import Path

# Ensure src module can be found (go up one level from tests/ to project root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.translator import TranslationEngine, TranslationResult
from src.core.dictionary import GameEntry, TranslationSource, DictionaryManager
from src.services.wikipedia import WikipediaService
from src.services.search import SearchService
from src.services.translate import TranslateService
from src.utils.name_cleaner import get_game_key


def test_translation(dictionary_path: str = './dictionaries', 
                     language: str = 'zh-TW',
                     test_limit: int = 5):
    """Test translation functionality"""
    print("=" * 60)
    print("Phase 3: Translation - Functionality Test")
    print("=" * 60)
    print(f"\n[PATH] Dictionary path: {dictionary_path}")
    print(f"[LANG] Target language: {language}")
    print(f"[LIMIT] Test limit: {test_limit} games per platform\n")
    
    # 1. Initialize translation engine
    print("[1] Initialize translation engine...")
    translator = TranslationEngine(target_language=language)
    print(f"    [+] Target language: {translator.target_language}")
    
    # 2. Initialize services
    print("\n[2] Initialize translation services...")
    
    # Wikipedia service
    wiki_service = WikipediaService(request_delay=1.0)
    translator.set_wiki_service(wiki_service)
    print("    [+] Wikipedia service initialized")
    
    # Search service
    search_service = SearchService(request_delay=2.0)
    translator.set_search_service(search_service)
    print("    [+] Search service initialized")
    
    # Translate API service (googletrans)
    translate_service = TranslateService()
    translator.set_translate_api(translate_service)
    print("    [+] Translate API service initialized")
    
    # 3. Test keep original logic
    print("\n[3] Test keep original logic...")
    test_cases = [
        ("FIFA 2024", True),     # Should keep: brand + number
        ("NBA 2K23", True),      # Should keep: brand + number
        ("F-Zero", True),        # Should keep: classic game
        ("Super Mario Bros", False),  # Should translate
        ("The Legend of Zelda", False),  # Should translate
    ]
    
    keep_passed = 0
    for name, expected in test_cases:
        result = translator.should_keep_original(name)
        status = "[OK]" if result == expected else "[FAIL]"
        if result == expected:
            keep_passed += 1
        print(f"    {status} '{name}' -> keep={result} (expected={expected})")
    
    print(f"    [+] Keep original tests: {keep_passed}/{len(test_cases)} passed")
    
    # 4. Test filename cleaning
    print("\n[4] Test filename cleaning...")
    clean_tests = [
        ("Super Mario Bros (USA).nes", "Super Mario Bros"),
        ("Contra [J][!].zip", "Contra"),
        ("Final Fantasy III (v1.1) (USA).sfc", "Final Fantasy III"),
    ]
    
    clean_passed = 0
    for filename, expected in clean_tests:
        result = translator.clean_filename(filename)
        status = "[OK]" if result == expected else "[FAIL]"
        if result == expected:
            clean_passed += 1
        print(f"    {status} '{filename}' -> '{result}' (expected='{expected}')")
    
    print(f"    [+] Filename cleaning tests: {clean_passed}/{len(clean_tests)} passed")
    
    # 5. Test Wikipedia search (if network available)
    print("\n[5] Test Wikipedia search...")
    try:
        wiki_result = wiki_service.search("Super Mario Bros", language)
        if wiki_result:
            print(f"    [+] Wikipedia found: 'Super Mario Bros' -> '{wiki_result}'")
        else:
            print("    [!] Wikipedia: No result (might be network issue)")
    except Exception as e:
        print(f"    [!] Wikipedia test skipped: {e}")
    
    # 6. Test translation with dictionary entries
    print("\n[6] Test translation with sample entries...")
    dict_manager = DictionaryManager(dictionaries_path=dictionary_path)
    
    # Get available platforms
    lang_path = Path(dictionary_path) / language
    if lang_path.exists():
        platforms = [f.stem for f in lang_path.glob('*.json')][:3]  # Test first 3 platforms
    else:
        platforms = []
        print("    [!] No dictionaries found, skipping this test")
    
    translated_count = 0
    skipped_count = 0
    keep_count = 0
    failed_count = 0
    
    for platform in platforms:
        print(f"\n    Platform: {platform}")
        dictionary = dict_manager.load_dictionary(language, platform)
        
        # Test limited entries
        entries_to_test = list(dictionary.values())[:test_limit]
        
        for entry in entries_to_test:
            output = translator.translate_game(
                entry,
                translate_name=True,
                translate_desc=False,  # Skip desc to speed up
                skip_translated=False  # Force translation for testing
            )
            
            if output.result == TranslationResult.SUCCESS:
                if output.name_source == TranslationSource.KEEP.value:
                    keep_count += 1
                    print(f"      [KEEP] {entry.original_name}")
                else:
                    translated_count += 1
                    print(f"      [OK] {entry.original_name} -> {output.name} ({output.name_source})")
                
                # Update entry
                entry.name = output.name
                entry.name_source = output.name_source
                
            elif output.result == TranslationResult.SKIPPED:
                skipped_count += 1
            else:
                failed_count += 1
                print(f"      [FAIL] {entry.original_name}")
        
        # Save updated dictionary
        dict_manager.save_dictionary(language, platform, dictionary)
        print(f"      [+] Saved {platform}.json")
    
    # 7. Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"    Keep original tests:   {keep_passed}/{len(test_cases)}")
    print(f"    Filename clean tests:  {clean_passed}/{len(clean_tests)}")
    print(f"    Translated:            {translated_count}")
    print(f"    Keep original:         {keep_count}")
    print(f"    Skipped:               {skipped_count}")
    print(f"    Failed:                {failed_count}")
    print("=" * 60)
    
    # All basic tests passed
    return keep_passed == len(test_cases) and clean_passed == len(clean_tests)


if __name__ == '__main__':
    # Default settings
    default_dict_path = "./dictionaries"
    default_lang = "zh-TW"
    default_limit = 3  # Limit per platform to avoid too many API calls
    
    if len(sys.argv) > 1:
        dict_path = sys.argv[1]
    else:
        dict_path = default_dict_path
    
    if len(sys.argv) > 2:
        language = sys.argv[2]
    else:
        language = default_lang
    
    if len(sys.argv) > 3:
        limit = int(sys.argv[3])
    else:
        limit = default_limit
    
    success = test_translation(dict_path, language, limit)
    
    if success:
        print("\n[PASS] Phase 3 test passed!")
    else:
        print("\n[FAIL] Phase 3 test failed!")
        sys.exit(1)
