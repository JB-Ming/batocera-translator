#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理並優化快取檔案
"""

import json
import sys
import codecs
from pathlib import Path

# 設定控制台編碼
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def contains_chinese(text: str) -> bool:
    """檢查文字是否包含中文字元"""
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def clean_cache():
    """清理快取檔案，移除無意義的翻譯"""
    cache_file = Path("local_cache.json")

    if not cache_file.exists():
        print("❌ 找不到 local_cache.json")
        return

    print("📦 載入快取檔案...")
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    original_count = len(cache.get("names", {}))
    print(f"   原始翻譯數量: {original_count} 筆\n")

    # 分類統計
    stats = {
        "valid_en_to_zh": [],      # 有效：英文→中文
        "invalid_same": [],         # 無效：原文=譯文
        "invalid_zh_to_zh": [],     # 無效：中文→中文
        "invalid_en_to_en": [],     # 無效：英文→英文
        "other": []                 # 其他
    }

    for key, value in cache.get("names", {}).items():
        if key == value:
            stats["invalid_same"].append((key, value))
        elif not contains_chinese(key) and contains_chinese(value):
            stats["valid_en_to_zh"].append((key, value))
        elif contains_chinese(key) and contains_chinese(value):
            stats["invalid_zh_to_zh"].append((key, value))
        elif not contains_chinese(key) and not contains_chinese(value):
            stats["invalid_en_to_en"].append((key, value))
        else:
            stats["other"].append((key, value))

    # 顯示統計
    print("📊 快取統計：\n")
    print(f"  ✅ 有效翻譯（英文→中文）: {len(stats['valid_en_to_zh'])} 筆")
    print(f"  ❌ 無效翻譯（原文=譯文）: {len(stats['invalid_same'])} 筆")
    print(f"  ❌ 無效翻譯（中文→中文）: {len(stats['invalid_zh_to_zh'])} 筆")
    print(f"  ❌ 無效翻譯（英文→英文）: {len(stats['invalid_en_to_en'])} 筆")
    print(f"  ⚠️  其他類型: {len(stats['other'])} 筆\n")

    # 顯示無效範例
    if stats["invalid_same"]:
        print("無效翻譯範例（原文=譯文）：")
        for key, value in stats["invalid_same"][:5]:
            print(f"  • {key} → {value}")
        if len(stats["invalid_same"]) > 5:
            print(f"  ... 還有 {len(stats['invalid_same']) - 5} 筆\n")

    if stats["invalid_zh_to_zh"]:
        print("無效翻譯範例（中文→中文）：")
        for key, value in stats["invalid_zh_to_zh"][:5]:
            print(f"  • {key} → {value}")
        if len(stats["invalid_zh_to_zh"]) > 5:
            print(f"  ... 還有 {len(stats['invalid_zh_to_zh']) - 5} 筆\n")

    # 清理快取
    print("\n🧹 清理快取...")
    cleaned_cache = {
        "names": {},
        "descriptions": cache.get("descriptions", {})
    }

    # 只保留有效的翻譯
    for key, value in stats["valid_en_to_zh"]:
        cleaned_cache["names"][key] = value

    cleaned_count = len(cleaned_cache["names"])
    removed_count = original_count - cleaned_count

    print(f"   保留: {cleaned_count} 筆")
    print(f"   移除: {removed_count} 筆")
    print(f"   節省空間: {removed_count / original_count * 100:.1f}%\n")

    # 備份原始檔案
    backup_file = cache_file.with_suffix('.json.backup')
    print(f"💾 備份原始檔案到: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    # 儲存清理後的快取
    print(f"💾 儲存清理後的快取...")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_cache, f, ensure_ascii=False, indent=2)

    print("\n✅ 快取清理完成！")
    print(f"\n有效翻譯範例：")
    for key, value in stats["valid_en_to_zh"][:10]:
        print(f"  ✓ {key} → {value}")
    if len(stats["valid_en_to_zh"]) > 10:
        print(f"  ... 還有 {len(stats['valid_en_to_zh']) - 10} 筆")


if __name__ == "__main__":
    clean_cache()
