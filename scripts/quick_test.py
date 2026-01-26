#!/usr/bin/env python3
"""快速測試 Gemini 批次翻譯 - 160 個遊戲分 2 次"""
from src.utils.settings import SettingsManager
from src.services.gemini import GeminiService
import json
import time
import re
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def clean_name(name: str) -> str:
    """清理遊戲名稱"""
    cleaned = re.sub(r'\s*\([^)]*\)\s*', ' ', name)
    cleaned = re.sub(r'\s*\[[^\]]*\]\s*', ' ', cleaned)
    return ' '.join(cleaned.split()).strip()


def main():
    # 載入設定取得 API Key
    settings_mgr = SettingsManager()
    settings = settings_mgr.load()
    api_key = settings.get_gemini_api_key()

    if not api_key:
        print("❌ 未設定 Gemini API Key!")
        return

    print(f"✅ API Key: {api_key[:15]}...")

    # 載入語系包
    pack_path = Path("language_packs/zh-TW/amstradcpc.json")
    with open(pack_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 找出需要翻譯的 (name_source = api)
    candidates = [(k, v)
                  for k, v in data.items() if v.get('name_source') == 'api']
    print(f"📦 找到 {len(candidates)} 個 API 翻譯的遊戲")

    # 取 160 個
    to_translate = candidates[:160]

    # 初始化 Gemini
    gemini = GeminiService(api_key=api_key, request_delay=0.5)

    # 準備名稱清單
    names_map = {}  # clean_name -> (key, entry)
    for key, entry in to_translate:
        clean = clean_name(entry.get('original_name', key))
        names_map[clean] = (key, entry)

    names_list = list(names_map.keys())

    # 直接翻譯（gemini 沒有 batch 方法，逐一翻譯）
    print(f"\n🚀 開始翻譯 {len(names_list)} 個遊戲...")
    print("-" * 50)

    start = time.time()
    all_results = {}

    for i, name in enumerate(names_list):
        try:
            result = gemini.translate_game_name(name, language='zh-TW')
            if result:
                all_results[name] = result
                print(f"[{i+1}/{len(names_list)}] {name[:25]:<25} -> {result}")
            else:
                print(f"[{i+1}/{len(names_list)}] {name[:25]:<25} -> (無結果)")
        except Exception as e:
            print(f"[{i+1}/{len(names_list)}] {name[:25]:<25} -> 錯誤: {e}")

    total_time = time.time() - start
    print(f"\n⏱️ 總耗時: {total_time:.2f} 秒")

    # 更新語系包
    print(f"\n📝 更新語系包...")
    now = datetime.now().isoformat(timespec='seconds')
    updated = 0

    for clean, translated in all_results.items():
        if clean in names_map and translated and translated != clean:
            key, entry = names_map[clean]
            old = entry.get('name', '')
            entry['name'] = translated
            entry['name_source'] = 'gemini'
            entry['name_translated_at'] = now
            data[key] = entry
            updated += 1
            print(f"  {clean[:25]:<25} -> {translated}")

    # 存檔
    with open(pack_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成!")
    print(f"📊 統計:")
    print(f"   翻譯數量: {len(names_list)}")
    print(f"   成功更新: {updated}")
    print(f"   總耗時: {total_time:.2f} 秒")
    print(f"   平均每個: {total_time / max(len(names_list), 1):.3f} 秒")


if __name__ == "__main__":
    main()
