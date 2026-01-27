#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試 Gemini 1.5 Flash 批次翻譯 - 只跑 300 筆
"""
from src.utils.settings import SettingsManager
from src.services.gemini_batch import GeminiBatchService, GEMINI_AVAILABLE
import json
import sys
import os

# 加入專案根目錄
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    print("=" * 60)
    print("Gemini 1.5 Flash 批次翻譯測試 (300 筆)")
    print("=" * 60)

    if not GEMINI_AVAILABLE:
        print("❌ google-generativeai 未安裝")
        return

    # 載入設定
    settings_manager = SettingsManager()
    settings = settings_manager.load()
    api_key = settings.get_gemini_api_key()

    if not api_key:
        print("❌ 未設定 Gemini API Key")
        print("請在 config/settings.json 中設定 gemini_api_key")
        return

    print(f"✅ API Key 已設定 (長度: {len(api_key)})")

    # 從 apple2.json 讀取測試資料
    language_pack_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "language_packs", "zh-TW", "apple2.json"
    )

    if not os.path.exists(language_pack_path):
        print(f"❌ 找不到測試資料: {language_pack_path}")
        return

    with open(language_pack_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 取出前 300 筆「尚未翻譯」的遊戲名稱
    untranslated = []
    for key, value in data.items():
        if not value.get('name') or value.get('name') == '':
            # 取 original_name 來翻譯
            original = value.get('original_name', key)
            untranslated.append(original)
        if len(untranslated) >= 300:
            break

    print(f"✅ 找到 {len(untranslated)} 筆未翻譯的遊戲")

    if len(untranslated) == 0:
        print("沒有需要翻譯的遊戲")
        return

    # 顯示前 5 筆作為預覽
    print("\n📋 預覽前 5 筆：")
    for i, name in enumerate(untranslated[:5], 1):
        print(f"  {i}. {name}")

    print(f"\n🚀 開始批次翻譯 {len(untranslated)} 筆遊戲...")
    print(f"   模型: gemini-1.5-flash")
    print(f"   批次大小: {settings.gemini_batch_size}")
    print()

    # 建立服務
    service = GeminiBatchService(
        api_key=api_key,
        batch_size=settings.gemini_batch_size,
        request_delay=1.0
    )

    # 執行翻譯
    result = service.translate_all(
        game_names=untranslated,
        language='zh-TW',
        platform='apple2',
        progress_callback=lambda cur, total, msg: print(
            f"  [{cur}/{total}] {msg}")
    )

    print()
    print("=" * 60)
    print("📊 翻譯結果統計")
    print("=" * 60)
    print(f"  總數: {result.total}")
    print(f"  成功: {result.success_count}")
    print(f"  失敗: {len(result.failed)}")
    print(f"  成功率: {result.success_count / result.total * 100:.1f}%")

    # 顯示一些翻譯結果
    print("\n📝 翻譯結果預覽 (前 10 筆)：")
    count = 0
    for original, translated in result.translations.items():
        if count >= 10:
            break
        print(f"  {original}")
        print(f"    → {translated}")
        count += 1

    # 如果有失敗的，顯示前 5 筆
    if result.failed:
        print(f"\n⚠️ 失敗的遊戲 (前 5 筆)：")
        for name in result.failed[:5]:
            print(f"  - {name}")

    print("\n✅ 測試完成！")


if __name__ == "__main__":
    main()
