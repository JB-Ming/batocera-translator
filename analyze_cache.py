"""分析 local_cache.json 內容"""
import json

with open('local_cache.json', encoding='utf-8') as f:
    cache = json.load(f)

names = cache.get('names', {})

print(f"總翻譯數: {len(names)}")

# 分類
chinese_marked = [k for k, v in names.items() if v.startswith('[中文]')]
valid_translations = []
same_as_original = []
other = []

for k, v in names.items():
    if v.startswith('[中文]'):
        continue
    elif not v or k == v:
        same_as_original.append(k)
    elif any('\u4e00' <= c <= '\u9fff' for c in v):
        valid_translations.append((k, v))
    else:
        other.append((k, v))

print(f"\n分類統計:")
print(f"  [中文]標記: {len(chinese_marked)} 筆")
print(f"  有效翻譯 (英→中): {len(valid_translations)} 筆")
print(f"  原文相同: {len(same_as_original)} 筆")
print(f"  其他 (英→英): {len(other)} 筆")

print(f"\n[中文]標記範例 (前 10 個):")
for k in chinese_marked[:10]:
    print(f"  {k} → {names[k]}")

print(f"\n有效翻譯範例 (前 10 個):")
for k, v in valid_translations[:10]:
    print(f"  {k} → {v}")
