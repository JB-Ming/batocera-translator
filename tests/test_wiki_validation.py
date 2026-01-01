#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證 Wiki 翻譯驗證邏輯修正
"""
from src.services.wikipedia import WikipediaService

def test_is_valid_translation():
    """測試 _is_valid_translation 方法"""
    wiki = WikipediaService()
    
    print("=" * 60)
    print("測試 _is_valid_translation 方法")
    print("=" * 60)
    
    test_cases = [
        # (result, original, language, expected)
        ("Now Production", "Ms. Pac-Man", "zh-TW", False),  # 純英文，應該無效
        ("超級瑪利歐兄弟", "Super Mario Bros", "zh-TW", True),  # 中文，有效
        ("Ms. Pac-Man", "Ms. Pac-Man", "zh-TW", False),  # 與原文相同，無效
        ("小乖妹", "Ms. Pac-Man", "zh-TW", True),  # 中文譯名，有效
        ("Pac-Man Championship", "Pac-Man", "zh-TW", False),  # 純英文，無效
        ("太空侵略者", "Space Invaders", "zh-TW", True),  # 中文，有效
        ("Space Invaders", "Space Invaders", "en", True),  # 英文語系，保留原文有效
    ]
    
    passed = 0
    for result, original, language, expected in test_cases:
        actual = wiki._is_valid_translation(result, original, language)
        status = "[OK]" if actual == expected else "[FAIL]"
        if actual == expected:
            passed += 1
        print(f"  {status} _is_valid_translation('{result}', '{original}', '{language}') = {actual} (expected: {expected})")
    
    print(f"\n結果: {passed}/{len(test_cases)} 通過")
    return passed == len(test_cases)

if __name__ == '__main__':
    success = test_is_valid_translation()
    if success:
        print("\n[PASS] 所有測試通過！")
    else:
        print("\n[FAIL] 部分測試失敗")
        exit(1)
