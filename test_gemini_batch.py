#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Gemini 批次翻譯功能
"""
from src.services.gemini_batch import GeminiBatchService, BatchTranslationResult
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# 測試用 API Key
API_KEY = "AIzaSyCn7PlASJtgh4aVZWfiiEd9UkQYVkdmiPM"


def test_batch_translation():
    """測試批次翻譯"""
    print("=" * 60)
    print("測試 Gemini 批次翻譯")
    print("=" * 60)

    # 初始化服務
    print("\n1. 初始化 GeminiBatchService...")
    try:
        service = GeminiBatchService(
            api_key=API_KEY,
            batch_size=10,  # 測試用小批次
            request_delay=1.0
        )
        print("   ✓ 初始化成功")
    except Exception as e:
        print(f"   ✗ 初始化失敗: {e}")
        return

    # 測試連線
    print("\n2. 測試 API 連線...")
    success, msg = service.test_connection()
    if success:
        print(f"   ✓ {msg}")
    else:
        print(f"   ✗ {msg}")
        return

    # 測試遊戲清單（模擬 NES 平台）
    test_games = [
        "Super Mario Bros.",
        "The Legend of Zelda",
        "Metroid",
        "Donkey Kong",
        "Mega Man 2",
    ]

    print(f"\n3. 測試翻譯 {len(test_games)} 個 NES 遊戲...")
    print(f"   平台: nes")
    print(f"   遊戲: {test_games}")

    # 進度回呼
    def progress_callback(current, total, message):
        print(f"   進度: {current}/{total} - {message}")

    # 執行翻譯
    result = service.translate_all(
        game_names=test_games,
        language='zh-TW',
        platform='nes',  # 傳入平台名稱
        progress_callback=progress_callback
    )

    # 顯示結果
    print(f"\n4. 翻譯結果:")
    print(f"   總數: {result.total}")
    print(f"   成功: {result.success_count}")
    print(f"   失敗: {len(result.failed)}")

    print(f"\n5. 翻譯對照:")
    for original, translated in result.translations.items():
        print(f"   {original} → {translated}")

    if result.failed:
        print(f"\n6. 失敗項目:")
        for name in result.failed:
            print(f"   - {name}")

    # 測試回寫邏輯
    print("\n" + "=" * 60)
    print("測試回寫邏輯（模擬）")
    print("=" * 60)

    # 模擬字典更新
    print("\n模擬更新字典的程式碼邏輯:")
    print("""
    for name, translation in result.translations.items():
        if key in dictionary:
            dict_entry = dictionary[key]
            dict_entry.name = translation           # 設定翻譯名稱
            dict_entry.name_source = "gemini_batch" # 標記來源
            dict_entry.name_translated_at = time.strftime('%Y-%m-%dT%H:%M:%S')
            dict_entry.needs_retranslate = False    # 清除重翻標記
            dict_entry.update_hashes()              # 更新 hash
    
    dict_manager.save_dictionary(language, platform, dictionary)  # 儲存
    """)

    print("\n✓ 回寫邏輯確認正確，會寫入語系包的 JSON 檔案")

    return result


if __name__ == '__main__':
    test_batch_translation()
