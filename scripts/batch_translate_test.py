#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次翻譯測試腳本
使用 Gemini API 翻譯 80 個遊戲名稱
"""
from src.utils.settings import SettingsManager
from src.services.gemini import GeminiService
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 確保可以找到 src 模組
sys.path.insert(0, str(Path(__file__).parent))


def clean_game_name(name: str) -> str:
    """清理遊戲名稱，移除年份、地區、版本標記等"""
    import re
    # 移除括號內容：(UK), (1986), [a1], (Disk 1 of 2) 等
    cleaned = re.sub(r'\s*\([^)]*\)\s*', ' ', name)
    cleaned = re.sub(r'\s*\[[^\]]*\]\s*', ' ', cleaned)
    # 移除多餘空格
    cleaned = ' '.join(cleaned.split())
    return cleaned.strip()


def main():
    # 載入設定
    settings_manager = SettingsManager()
    settings = settings_manager.load_settings()

    gemini_api_key = settings.get('gemini_api_key', '')
    if not gemini_api_key:
        # 嘗試從環境變數讀取
        gemini_api_key = os.environ.get('GEMINI_API_KEY', '')

    if not gemini_api_key:
        print("❌ 未設定 Gemini API Key！")
        print("請在程式設定中設定 API Key，或設定環境變數 GEMINI_API_KEY")
        return

    print(f"✅ 找到 Gemini API Key: {gemini_api_key[:10]}...")

    # 初始化 Gemini 服務
    gemini = GeminiService(api_key=gemini_api_key)

    # 載入語系包
    pack_path = Path("language_packs/zh-TW/amstradcpc.json")
    with open(pack_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📦 載入語系包: {len(data)} 個遊戲")

    # 找出需要重新翻譯的遊戲（name_source 為 api 且名稱看起來是直譯的）
    candidates = []
    for key, entry in data.items():
        # 跳過已經有好翻譯的
        if entry.get('name_source') in ['wiki', 'manual', 'pack']:
            continue
        # 收集 api 翻譯的（可能品質較差）
        if entry.get('name_source') == 'api':
            candidates.append((key, entry))

    print(f"🔍 找到 {len(candidates)} 個 API 翻譯的遊戲")

    # 取前 80 個
    to_translate = candidates[:80]
    print(f"📋 準備翻譯 {len(to_translate)} 個遊戲")
    print("-" * 60)

    # 準備批次翻譯的遊戲名稱
    game_names = []
    for key, entry in to_translate:
        clean_name = clean_game_name(entry.get('original_name', key))
        game_names.append(clean_name)

    # 使用 Gemini 批次翻譯
    print("🚀 開始批次翻譯...")
    start_time = time.time()

    try:
        results = gemini.batch_translate_names(game_names, target_lang='zh-TW')
        elapsed = time.time() - start_time
        print(f"⏱️ 翻譯完成！耗時: {elapsed:.2f} 秒")
        print(f"📊 平均每個遊戲: {elapsed/len(game_names):.3f} 秒")
    except Exception as e:
        print(f"❌ 翻譯失敗: {e}")
        return

    # 更新語系包
    print("-" * 60)
    print("📝 更新語系包...")

    updated_count = 0
    now = datetime.now().isoformat(timespec='seconds')

    for i, (key, entry) in enumerate(to_translate):
        clean_name = game_names[i]
        translated = results.get(clean_name, '')

        if translated and translated != clean_name:
            old_name = entry.get('name', '')
            entry['name'] = translated
            entry['name_source'] = 'gemini'
            entry['name_translated_at'] = now
            data[key] = entry
            updated_count += 1
            print(f"  ✓ {clean_name[:30]:<30} → {translated}")
        else:
            print(f"  ✗ {clean_name[:30]:<30} (無翻譯結果)")

    # 存檔
    print("-" * 60)
    print(f"💾 儲存語系包... (更新 {updated_count} 個)")

    with open(pack_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ 完成！")
    print(f"📊 統計:")
    print(f"   - 嘗試翻譯: {len(to_translate)}")
    print(f"   - 成功更新: {updated_count}")
    print(f"   - 總耗時: {elapsed:.2f} 秒")


if __name__ == "__main__":
    main()
