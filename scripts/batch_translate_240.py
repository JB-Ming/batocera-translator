#!/usr/bin/env python3
"""批次翻譯 240 筆（分 3 次，每次 80 筆）"""
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
    cleaned = re.sub(r'\s*\([^)]*\)\s*', ' ', name)
    cleaned = re.sub(r'\s*\[[^\]]*\]\s*', ' ', cleaned)
    return ' '.join(cleaned.split()).strip()


def main():
    settings_mgr = SettingsManager()
    settings = settings_mgr.load()
    api_key = settings.get_gemini_api_key()
    if not api_key:
        print("❌ 未設定 Gemini API Key!")
        return
    print(f"✅ API Key: {api_key[:15]}...")
    pack_path = Path("language_packs/zh-TW/amstradcpc.json")
    with open(pack_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    candidates = [(k, v)
                  for k, v in data.items() if v.get('name_source') == 'api']
    print(f"📦 找到 {len(candidates)} 個 API 翻譯的遊戲")
    to_translate = candidates[:240]
    names_map = {}
    for key, entry in to_translate:
        clean = clean_name(entry.get('original_name', key))
        names_map[clean] = (key, entry)
    names_list = list(names_map.keys())
    batches = [names_list[i:i+80] for i in range(0, len(names_list), 80)]
    gemini = GeminiService(api_key=api_key, request_delay=0.5)
    all_results = {}
    total_time = 0
    for batch_idx, batch in enumerate(batches):
        print(f"\n🚀 第 {batch_idx+1} 批: {len(batch)} 個遊戲")
        print("-" * 50)
        start = time.time()
        for i, name in enumerate(batch):
            try:
                result = gemini.translate_game_name(name, language='zh-TW')
                if result:
                    all_results[name] = result
                    print(f"[{i+1}/{len(batch)}] {name[:25]:<25} -> {result}")
                else:
                    print(f"[{i+1}/{len(batch)}] {name[:25]:<25} -> (空白)")
            except Exception as e:
                print(f"[{i+1}/{len(batch)}] {name[:25]:<25} -> 錯誤: {e}")
        batch_time = time.time() - start
        total_time += batch_time
        print(f"⏱️ 批次耗時: {batch_time:.2f} 秒")
    print(f"\n📝 更新語系包...")
    now = datetime.now().isoformat(timespec='seconds')
    updated = 0
    for clean, translated in all_results.items():
        if clean in names_map and translated and translated != clean:
            key, entry = names_map[clean]
            entry['name'] = translated
            entry['name_source'] = 'gemini'
            entry['name_translated_at'] = now
            data[key] = entry
            updated += 1
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
