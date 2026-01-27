#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試不同批次大小對翻譯品質的影響（使用不同遊戲避免快取）
"""
from src.utils.settings import SettingsManager
from src.services.gemini_batch import GeminiBatchService, GEMINI_AVAILABLE
import warnings
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

warnings.filterwarnings('ignore')


def main():
    print("=" * 60)
    print("批次大小品質測試（無快取影響）")
    print("=" * 60)

    if not GEMINI_AVAILABLE:
        print("❌ google-generativeai 未安裝")
        return

    settings = SettingsManager().load()
    api_key = settings.get_gemini_api_key()

    if not api_key:
        print("❌ 未設定 Gemini API Key")
        return

    # 載入 apple2.json，取出尚未有快取的遊戲
    language_pack_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "language_packs", "zh-TW", "mame.json"  # 用 mame 來測試（數量多）
    )

    with open(language_pack_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 取出有 original_name 且未翻譯的遊戲
    all_games = []
    for key, value in data.items():
        if not value.get('name') or value.get('name') == '':
            original = value.get('original_name', key)
            if original:
                all_games.append(original)

    print(f"找到 {len(all_games)} 個未翻譯的 MAME 遊戲")

    if len(all_games) < 60:
        print("遊戲數量不足，無法進行測試")
        return

    # 分成三組不同的遊戲，每組 20 個
    group_a = all_games[0:20]    # 用批次 20 測試
    group_b = all_games[20:40]  # 用批次 10 測試
    group_c = all_games[40:60]  # 用批次 5 測試

    results = {}

    # 測試批次 20
    print(f"\n{'='*60}")
    print(f"測試 A：批次大小 20 筆/次")
    print(f"{'='*60}")
    service = GeminiBatchService(
        api_key=api_key, batch_size=20, request_delay=1.0)
    result_a = service.translate_batch(group_a, 'zh-TW', 'mame')
    print(f"  成功: {result_a.success_count}/{result_a.total}")
    print(f"  範例翻譯：")
    for i, (orig, trans) in enumerate(result_a.translations.items()):
        if i >= 3:
            break
        print(f"    {orig[:30]}... → {trans}")

    # 測試批次 10
    print(f"\n{'='*60}")
    print(f"測試 B：批次大小 10 筆/次")
    print(f"{'='*60}")
    service = GeminiBatchService(
        api_key=api_key, batch_size=10, request_delay=1.0)
    result_b = service.translate_batch(group_b, 'zh-TW', 'mame')
    print(f"  成功: {result_b.success_count}/{result_b.total}")
    print(f"  範例翻譯：")
    for i, (orig, trans) in enumerate(result_b.translations.items()):
        if i >= 3:
            break
        print(f"    {orig[:30]}... → {trans}")

    # 測試批次 5
    print(f"\n{'='*60}")
    print(f"測試 C：批次大小 5 筆/次")
    print(f"{'='*60}")
    service = GeminiBatchService(
        api_key=api_key, batch_size=5, request_delay=1.0)
    result_c = service.translate_batch(group_c, 'zh-TW', 'mame')
    print(f"  成功: {result_c.success_count}/{result_c.total}")
    print(f"  範例翻譯：")
    for i, (orig, trans) in enumerate(result_c.translations.items()):
        if i >= 3:
            break
        print(f"    {orig[:30]}... → {trans}")

    # 總結
    print(f"\n{'='*60}")
    print(f"總結")
    print(f"{'='*60}")
    print(f"  批次 20：成功率 {result_a.success_count/result_a.total*100:.1f}%")
    print(f"  批次 10：成功率 {result_b.success_count/result_b.total*100:.1f}%")
    print(f"  批次  5：成功率 {result_c.success_count/result_c.total*100:.1f}%")

    print("\n✅ 測試完成！")


if __name__ == "__main__":
    main()
