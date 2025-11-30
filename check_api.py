#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 API 設定
"""

import sys
import codecs
from translator import GamelistTranslator

# 設定控制台編碼
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def main():
    translator = GamelistTranslator()

    print("API 管理器狀態：")
    print(f"  Groq 啟用: {translator.api_manager.enable_groq}")
    print(
        f"  Groq API Key: {'✅ 存在' if translator.api_manager.groq_api_key else '❌ 不存在'}")
    print(f"  Gemini 啟用: {translator.api_manager.enable_gemini}")
    print(
        f"  Gemini API Key: {'✅ 存在' if translator.api_manager.gemini_api_key else '❌ 不存在'}")

    print("\n測試批次翻譯...")
    result = translator.api_manager.translate_game_names_batch(
        ["Final Fantasy VI", "Chrono Trigger", "Metal Gear Solid"],
        "超級任天堂"
    )

    print(f"\n翻譯結果: {result}")


if __name__ == "__main__":
    main()
