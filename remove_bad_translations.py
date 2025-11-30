"""移除 [中文] 標記的錯誤翻譯"""
import json
import shutil
from datetime import datetime

# 備份
backup_file = f"local_cache_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json.backup"
shutil.copy2("local_cache.json", backup_file)
print(f"✓ 已備份到 {backup_file}")

# 讀取
with open("local_cache.json", encoding='utf-8') as f:
    cache = json.load(f)

# 檢查
names = cache['names']
bad_translations = {k: v for k, v in names.items() if v.startswith('[中文]')}

print(f"\n找到 {len(bad_translations)} 個 [中文] 標記的錯誤翻譯")
print("\n範例:")
for k, v in list(bad_translations.items())[:10]:
    print(f"  {k} → {v}")

# 移除
for key in bad_translations:
    del names[key]

# 儲存
with open("local_cache.json", 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"\n✓ 已移除 {len(bad_translations)} 個錯誤翻譯")
print(f"✓ 剩餘 {len(names)} 個有效翻譯")
