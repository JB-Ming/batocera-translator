# Google 搜尋自動翻譯演示文檔

## 概述

當 `gamelist.xml` 中某個遊戲名稱不在語系包（translation dictionary）中時，系統會自動執行以下流程：

1. **檢查預設翻譯** - 查找內建的常見遊戲翻譯
2. **檢查語系包** - 在 `translations/translations_{platform}.json` 中查找
3. **檢查本地快取** - 在 `local_cache.json` 中查找
4. **執行 Google 搜尋** - 如果以上都沒找到，則透過 Google 搜尋中文譯名
5. **保存到快取** - 將搜尋結果保存到 `local_cache.json`
6. **更新語系包** - 可選：將快取中的翻譯同步到語系包

## 完整流程示意圖

```
遊戲名稱: "Kirby's Adventure"
    ↓
[檢查預設翻譯字典]
    ↓ 未找到
[檢查語系包 translations_nes.json]
    ↓ 未找到
[檢查本地快取 local_cache.json]
    ↓ 未找到
[執行 Google 搜尋]
    搜尋查詢: "Kirby's Adventure FC紅白機 遊戲 中文"
    提取中文名稱: "星之卡比 夢之泉物語"
    ↓
[保存到本地快取]
    local_cache.json 更新:
    {
      "names": {
        "Kirby's Adventure": "星之卡比 夢之泉物語"
      }
    }
    ↓
[可選：更新語系包]
    translations_nes.json 更新:
    {
      "Kirby's Adventure": "星之卡比 夢之泉物語",
      ...
    }
```

## 關鍵程式碼解析

### 1. 翻譯查找邏輯 (`lookup_translation` 方法)

```python
def lookup_translation(self, game_name: str, platform: str,
                       is_description: bool = False) -> Optional[str]:
    """
    查找翻譯（按優先順序）
    1. 精確匹配：預設翻譯、語系包、本地快取
    2. 模糊匹配（如果啟用）：正規化後比對
    3. 返回 None（需要搜尋）
    """
    
    # 1. 檢查預設翻譯
    if not is_description and game_name in DEFAULT_TRANSLATIONS:
        return DEFAULT_TRANSLATIONS[game_name]
    
    # 2. 檢查語系包
    trans_dict = self.load_translation_dict(platform)
    if game_name in trans_dict:
        return trans_dict[game_name]
    
    # 3. 檢查本地快取
    if game_name in self.local_cache["names"]:
        return self.local_cache["names"][game_name]
    
    # 4. 模糊匹配（如果啟用）
    if self.fuzzy_match:
        # ... 正規化比對邏輯
    
    return None  # 需要搜尋
```

### 2. Google 搜尋 (`translate_name` 方法)

```python
def translate_name(self, game_name: str, platform: str) -> str:
    """翻譯遊戲名稱（先查字典，再搜尋）"""
    
    # 清理名稱（移除區域標記等）
    clean_name = self.clean_game_name(game_name)
    
    # 查找翻譯
    translation = self.lookup_translation(clean_name, platform)
    if translation:
        print(f"✓ 從字典找到翻譯: {clean_name} → {translation}")
        return translation
    
    # Google 搜尋
    platform_name = PLATFORM_NAMES.get(platform, platform)
    query = f"{clean_name} {platform_name} 遊戲 中文"
    print(f"搜尋: {query}")
    
    html = self.search_google(query)
    chinese_name = self.extract_chinese_name(html, clean_name)
    
    if chinese_name:
        print(f"✓ 找到翻譯: {clean_name} → {chinese_name}")
        # 加入本地快取
        self.local_cache["names"][clean_name] = chinese_name
        self.save_local_cache()
        return chinese_name
    else:
        print(f"✗ 找不到翻譯，保持原名: {clean_name}")
        return clean_name
    
    # 延遲避免被封鎖
    time.sleep(self.search_delay)
```

### 3. 提取中文名稱 (`extract_chinese_name` 方法)

```python
def extract_chinese_name(self, html: str, original_name: str) -> Optional[str]:
    """從搜尋結果提取中文名稱"""
    
    soup = BeautifulSoup(html, 'html.parser')
    candidates = {}
    
    # 尋找書名號《》內的內容（加分）
    matches = re.findall(r'《([^》]+)》', text)
    for match in matches:
        if self.contains_chinese(match):
            candidates[match] = candidates.get(match, 0) + 3
    
    # 尋找包含中文的片段
    chinese_parts = re.findall(r'[\u4e00-\u9fff]+', text)
    for part in chinese_parts:
        if 4 <= len(part) <= 15:  # 長度適中
            candidates[part] = candidates.get(part, 0) + 1
    
    # 選擇得分最高的候選
    if candidates:
        best_candidate = max(candidates.items(), key=lambda x: x[1])
        return best_candidate[0]
    
    return None
```

## 演示腳本使用方式

### 方法 1: 完整演示（自動化）

```bash
python demo_google_search.py
```

這個腳本會：
- ✓ 自動選擇一個不在語系包中的遊戲
- ✓ 展示完整的翻譯流程
- ✓ 顯示每個步驟的詳細資訊
- ✓ 自動更新本地快取和語系包

### 方法 2: 互動式測試

```bash
python test_google_search.py
```

這個腳本會：
- ✓ 讓你選擇要測試的遊戲
- ✓ 手動確認每個步驟
- ✓ 詢問是否更新語系包

### 方法 3: 診斷搜尋結果

```bash
python diagnose_search.py
```

這個腳本會：
- ✓ 保存原始 Google 搜尋的 HTML
- ✓ 顯示提取的候選中文名稱
- ✓ 幫助分析為何某些翻譯不準確

## 實際執行範例

### 範例 1: Duck Hunt（打鴨子）

```
步驟 1: 檢查語系包
  ✗ 'Duck Hunt' 不在語系包中

步驟 2: 執行 Google 搜尋
  搜尋查詢: "Duck Hunt FC紅白機 遊戲 中文"
  
步驟 3: 提取中文名稱
  ✓ 找到翻譯: Duck Hunt → 打鴨子
  
步驟 4: 保存到快取
  local_cache.json 已更新

步驟 5: 更新語系包
  translations_nes.json 已更新
  新增: Duck Hunt → 打鴨子
```

### 範例 2: Kirby's Adventure（星之卡比）

```
步驟 1: 檢查語系包
  ✗ 'Kirby's Adventure' 不在語系包中

步驟 2: 執行 Google 搜尋
  搜尋查詢: "Kirby's Adventure FC紅白機 遊戲 中文"
  
步驟 3: 提取中文名稱
  ✓ 找到翻譯: Kirby's Adventure → 星之卡比 夢之泉物語
  
步驟 4: 保存到快取
  local_cache.json 已更新

步驟 5: 更新語系包
  translations_nes.json 已更新
  新增: Kirby's Adventure → 星之卡比 夢之泉物語
```

## 優勢與特點

### 1. 多層快取機制

```
預設翻譯 (內建) → 最快
    ↓
語系包 (檔案) → 快速
    ↓
本地快取 (檔案) → 快速
    ↓
Google 搜尋 (網路) → 慢，但會被快取
```

### 2. 模糊匹配

支援大小寫、空白、標點符號等變化：

```python
"Super Mario Bros (USA)" 
  ↓ 正規化
"super mario bros"
  ↓ 匹配
"Super Mario Bros" → "超級瑪利歐兄弟"
```

### 3. 避免重複搜尋

一旦搜尋過的遊戲會被保存到快取，下次直接從快取讀取，不會再次搜尋。

### 4. 延遲機制

設定搜尋延遲（預設 2 秒），避免被 Google 封鎖：

```python
translator = GamelistTranslator(
    search_delay=2.0  # 每次搜尋間隔 2 秒
)
```

## 檔案結構

```
batocera-translator/
├── translator.py              # 核心翻譯邏輯
├── local_cache.json          # 本地快取（搜尋結果）
├── translations/             # 語系包目錄
│   ├── translations_nes.json    # NES 語系包
│   ├── translations_snes.json   # SNES 語系包
│   └── descriptions_nes.json    # NES 描述翻譯
├── test_roms/                # 測試 ROM 目錄
│   └── nes/
│       └── gamelist.xml         # 測試用 gamelist
├── demo_google_search.py     # 完整演示腳本
├── test_google_search.py     # 互動式測試腳本
└── diagnose_search.py        # 診斷腳本
```

## 配置選項

```python
translator = GamelistTranslator(
    translations_dir="translations",    # 語系包目錄
    local_cache_file="local_cache.json", # 快取檔案
    display_mode="chinese_only",        # 顯示模式
    max_name_length=100,                # 名稱最大長度
    translate_desc=True,                # 是否翻譯描述
    search_delay=2.0,                   # 搜尋延遲（秒）
    fuzzy_match=True                    # 啟用模糊匹配
)
```

## 注意事項

### 1. Google 搜尋限制

- Google 可能會限制頻繁搜尋
- 建議設定適當的延遲時間（2-3 秒）
- 大量翻譯時建議分批處理

### 2. 翻譯準確性

- 自動提取的翻譯可能不完全準確
- 建議人工審核搜尋結果
- 可以手動編輯語系包修正翻譯

### 3. 網路需求

- 需要穩定的網路連線
- Google 搜尋需要訪問 google.com
- 某些地區可能需要設定代理

## 疑難排解

### 問題 1: 搜尋失敗

```
✗ 搜尋失敗: HTTPError 429
```

**解決方法**：增加搜尋延遲時間或稍後再試。

### 問題 2: 翻譯不準確

```
✓ 找到翻譯: Duck Hunt → 請按一下這裡
```

**解決方法**：
1. 使用 `diagnose_search.py` 查看原始 HTML
2. 手動編輯 `translations_nes.json` 修正翻譯
3. 改進 `extract_chinese_name` 方法的提取邏輯

### 問題 3: 本地快取損壞

```
json.decoder.JSONDecodeError
```

**解決方法**：刪除 `local_cache.json` 重新建立。

## 進階使用

### 批次更新語系包

```bash
# 1. 執行翻譯（累積快取）
python translator.py --roms-path ./test_roms --dry-run

# 2. 檢查快取
cat local_cache.json

# 3. 更新語系包（使用演示腳本）
python demo_google_search.py
```

### 手動編輯語系包

```json
{
  "Duck Hunt": "打鴨子",
  "Kirby's Adventure": "星之卡比 夢之泉物語",
  "Ninja Gaiden": "忍者龍劍傳"
}
```

### 匯出/匯入翻譯

```bash
# 匯出
python -c "import json; print(json.dumps(json.load(open('local_cache.json'))['names'], ensure_ascii=False, indent=2))"

# 匯入
# 將翻譯手動添加到 translations_nes.json
```

## 總結

這個 Google 搜尋自動翻譯功能展示了：

✓ **智慧查找** - 多層快取機制，優先使用本地資源
✓ **自動搜尋** - 找不到時自動從 Google 搜尋
✓ **結果快取** - 避免重複搜尋，提升效率
✓ **靈活配置** - 支援多種顯示模式和參數調整
✓ **易於維護** - 語系包和快取都是 JSON 格式，易於編輯

這是一個完整的自動化翻譯解決方案，大幅減少手動翻譯的工作量！
