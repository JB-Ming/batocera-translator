# Batocera 翻譯工具 - 流程模擬說明

## 模擬完成概要

✅ **階段 1：提取待翻譯內容**
- 處理平台數：75 個
- 待翻譯名稱：57,920 個
- 待翻譯描述：13,858 個
- 生成檔案：`translations/to_translate_*.json`

✅ **階段 2：翻譯語系包**
- 使用模擬翻譯（格式：`[中文]原文`）
- 生成翻譯名稱：57,920 個
- 生成翻譯描述：13,858 個
- 生成檔案：`translations/translations_*.json` 和 `translations/descriptions_*.json`

✅ **階段 3：應用翻譯並寫回**
- 處理平台數：75 個
- 總遊戲數：43,265 個
- 已翻譯名稱：43,259 個
- 備份檔案：150+ 個（存於 `backups/`）
- 已寫回：`roms_remote/`

## 目錄結構

```
batocera-translator/
├── step1_extract.py           # 階段1：提取腳本
├── step2_translate.py         # 階段2：翻譯腳本（模擬）
├── step3_apply.py             # 階段3：應用腳本
├── run_all_steps.py           # 完整流程執行器
│
├── gamelists_local/           # 本地工作目錄（從遠端複製）
│   ├── nes/gamelist.xml
│   ├── snes/gamelist.xml
│   └── ...（75個平台）
│
├── roms_remote/               # 模擬遠端 WSL 目錄（已翻譯）
│   ├── nes/gamelist.xml       # ← 已套用翻譯
│   ├── snes/gamelist.xml
│   └── ...
│
├── translations/              # 翻譯語系包
│   ├── to_translate_names_nes.json      # 待翻譯
│   ├── translations_nes.json            # 已翻譯
│   ├── to_translate_descriptions_nes.json
│   ├── descriptions_nes.json
│   └── ...（每平台兩組檔案）
│
└── backups/                   # 原始檔案備份
    ├── gamelist_nes_20251128_100725.xml
    └── ...（150+ 個備份）
```

## 使用方式

### 方式 1：執行完整流程
```bash
python run_all_steps.py
```

### 方式 2：分階段執行
```bash
# 階段 1：提取
python step1_extract.py

# 階段 2：翻譯（目前是模擬）
python step2_translate.py

# 階段 3：應用並寫回
python step3_apply.py
```

## 翻譯結果範例

### 原始檔案（gamelists_local/nes/gamelist.xml）
```xml
<name>2048</name>
<desc>2048 is an originally Smartphone Game...</desc>
```

### 翻譯後（roms_remote/nes/gamelist.xml）
```xml
<name>[中文]2048</name>
<desc>2048 is an originally Smartphone Game...</desc>
```

*註：實際使用時，`[中文]` 會被真實的中文翻譯替換*

## 實際部署步驟

### 1. 替換模擬翻譯為真實翻譯 API

編輯 `step2_translate.py`，將 `mock_translate()` 函數替換為：

```python
# 方案 A：使用 Google Translate API
from googletrans import Translator
translator = Translator()

def translate_text(text, target='zh-TW'):
    result = translator.translate(text, dest=target)
    return result.text

# 方案 B：使用 DeepL API
import deepl
auth_key = "YOUR_AUTH_KEY"
translator = deepl.Translator(auth_key)

def translate_text(text, target='zh-TW'):
    result = translator.translate_text(text, target_lang='zh')
    return result.text

# 方案 C：使用本地 LLM (Ollama)
import ollama

def translate_text(text):
    response = ollama.chat(model='llama2', messages=[
        {'role': 'user', 'content': f'Translate to Traditional Chinese: {text}'}
    ])
    return response['message']['content']
```

### 2. 修改遠端路徑為實際 WSL 路徑

編輯 `step1_extract.py` 和 `step3_apply.py`：

```python
# 將模擬路徑
ROMS_REMOTE = Path("roms_remote")

# 改為實際 WSL 路徑
ROMS_REMOTE = Path(r"\\wsl.localhost\Ubuntu\userdata\roms")
# 或舊版格式
ROMS_REMOTE = Path(r"\\wsl$\Ubuntu\userdata\roms")
```

### 3. 設定顯示模式

編輯 `step3_apply.py` 中的 `display_mode` 變數：

```python
# 可選模式：
display_mode = 'chinese_only'      # 僅中文
display_mode = 'chinese_english'   # 中文 (英文)
display_mode = 'english_chinese'   # 英文 (中文)
display_mode = 'english_only'      # 僅英文
```

## WSL 路徑存取方式

### 查詢 WSL 發行版名稱
```powershell
wsl -l -v
```

### 路徑格式
```
新版：\\wsl.localhost\<發行版>\<路徑>
舊版：\\wsl$\<發行版>\<路徑>

範例：
\\wsl.localhost\Ubuntu\userdata\roms
\\wsl$\Ubuntu-20.04\userdata\roms
```

### Python 中使用
```python
from pathlib import Path
wsl_path = Path(r"\\wsl.localhost\Ubuntu\userdata\roms")

# 列出目錄
for item in wsl_path.iterdir():
    print(item)

# 複製檔案（無需 sudo）
import shutil
shutil.copy2(wsl_path / "nes/gamelist.xml", "local/nes/")
```

## 安全機制

✅ **自動備份**：所有原始檔案在修改前自動備份到 `backups/`  
✅ **本地優先**：先在 `gamelists_local/` 操作，確認無誤後才寫回  
✅ **時間戳記**：備份檔案名稱包含時間戳記，不會覆蓋  
✅ **無需 sudo**：使用 Windows CLI 存取 WSL，避免權限問題  

## 注意事項

1. **翻譯 API 限制**
   - Google Translate 免費版可能有請求限制
   - 建議加入請求延遲（每次 1-2 秒）
   - 或使用付費 API（Google Cloud Translation, DeepL）

2. **大量遊戲處理**
   - 57,920 個名稱翻譯可能需要較長時間
   - 建議先測試少量平台
   - 可分批處理

3. **編碼問題**
   - 確保所有檔案使用 UTF-8 編碼
   - Windows PowerShell 可能需要設定 `chcp 65001`

4. **WSL 連線**
   - WSL 必須已啟動（存取時會自動啟動）
   - 確保 WSL 中的檔案系統可存取

## 後續改進建議

- [ ] 加入 GUI 介面（使用 Tkinter 或 PyQt）
- [ ] 支援多種翻譯 API 選擇
- [ ] 加入翻譯品質檢查
- [ ] 建立社群共享的翻譯語系包
- [ ] 加入進度條和即時預覽
- [ ] 支援翻譯語系包的匯入/匯出
- [ ] 加入統計報告和視覺化

## 相關檔案

- 完整需求文件：`README.md`
- 階段 1 腳本：`step1_extract.py`
- 階段 2 腳本：`step2_translate.py`
- 階段 3 腳本：`step3_apply.py`
- 完整流程：`run_all_steps.py`

---

**模擬完成日期**：2025-11-28  
**處理平台數**：75 個  
**處理遊戲數**：43,265 個  
**狀態**：✅ 三階段流程驗證成功
