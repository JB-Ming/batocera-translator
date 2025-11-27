#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 translator.py 的功能
"""

from translator import GamelistTranslator
import unittest
import os
import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGamelistTranslator(unittest.TestCase):
    """測試翻譯器功能"""

    def setUp(self):
        """測試前準備"""
        self.translator = GamelistTranslator(
            translations_dir="translations",
            display_mode="chinese_only",
            translate_desc=False
        )

    def test_clean_game_name(self):
        """測試遊戲名稱清理"""
        # 測試移除區域標記
        self.assertEqual(
            self.translator.clean_game_name("Super Mario Bros (USA) [!]"),
            "Super Mario Bros"
        )

        # 測試移除版本標記
        self.assertEqual(
            self.translator.clean_game_name("Contra (Japan) [b1]"),
            "Contra"
        )

        # 測試多重標記
        self.assertEqual(
            self.translator.clean_game_name(
                "The Legend of Zelda (USA) (Rev 1) [!]"),
            "The Legend of Zelda"
        )

    def test_contains_chinese(self):
        """測試中文檢測"""
        self.assertTrue(self.translator.contains_chinese("超級瑪利歐"))
        self.assertTrue(self.translator.contains_chinese("Super Mario 超級瑪利歐"))
        self.assertFalse(self.translator.contains_chinese("Super Mario Bros"))
        self.assertFalse(self.translator.contains_chinese(""))

    def test_format_game_name(self):
        """測試名稱格式化"""
        # 僅中文模式
        self.translator.display_mode = "chinese_only"
        result = self.translator.format_game_name(
            "Super Mario Bros", "超級瑪利歐兄弟")
        self.assertEqual(result, "超級瑪利歐兄弟")

        # 中文(英文)模式
        self.translator.display_mode = "chinese_english"
        result = self.translator.format_game_name(
            "Super Mario Bros", "超級瑪利歐兄弟")
        self.assertEqual(result, "超級瑪利歐兄弟 (Super Mario Bros)")

        # 英文(中文)模式
        self.translator.display_mode = "english_chinese"
        result = self.translator.format_game_name(
            "Super Mario Bros", "超級瑪利歐兄弟")
        self.assertEqual(result, "Super Mario Bros (超級瑪利歐兄弟)")

    def test_lookup_translation(self):
        """測試翻譯查找"""
        # 預設翻譯
        result = self.translator.lookup_translation("Super Mario Bros", "nes")
        self.assertEqual(result, "超級瑪利歐兄弟")

        # 語系包翻譯
        result = self.translator.lookup_translation("Contra", "nes")
        self.assertIsNotNone(result)

    def test_max_length(self):
        """測試長度限制"""
        self.translator.max_name_length = 20
        long_name = "超級瑪利歐兄弟" * 10  # 很長的名稱

        result = self.translator.format_game_name("Test", long_name)
        self.assertLessEqual(len(result), 23)  # 20 + "..."


class TestTranslationDict(unittest.TestCase):
    """測試語系包載入"""

    def setUp(self):
        self.translator = GamelistTranslator()

    def test_load_translation_dict(self):
        """測試載入語系包"""
        nes_dict = self.translator.load_translation_dict("nes")
        self.assertIsInstance(nes_dict, dict)

        # 檢查是否有預期的翻譯
        if nes_dict:
            self.assertIn("Super Mario Bros", nes_dict)

    def test_load_description_dict(self):
        """測試載入描述字典"""
        desc_dict = self.translator.load_description_dict("nes")
        self.assertIsInstance(desc_dict, dict)


if __name__ == "__main__":
    unittest.main()
