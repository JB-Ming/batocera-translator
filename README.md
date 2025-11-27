# Batocera Gamelist 自動翻譯工具需求文件

## 專案目標

開發一個 Python 工具，自動將 Batocera 遊戲模擬器的英文遊戲名稱和描述翻譯成繁體中文，透過 Google 搜尋結果來獲取遊戲的慣用中文譯名。

**核心特色：**
- 使用共享的語系包（字典檔）快速查找翻譯，無需每次搜尋
- 支援多種顯示模式（僅中文、中英混合等）
- 自動遍歷所有平台的 gamelist.xml
- 社群協作，共享翻譯成果
- **提供 Windows 圖形化介面（GUI），可打包成 .exe 執行檔**

---

## GUI 設計需求

### 主視窗佈局

**視窗標題：** Batocera Gamelist 中文化工具 v1.0

**視窗大小：** 800 x 600 像素（可調整大小）

### 介面區塊

#### 1. 路徑設定區
```
┌─ 路徑設定 ─────────────────────────────────┐
│ Roms 目錄: [__________________] [瀏覽...]  │
│ 語系包目錄: [__________________] [瀏覽...]  │
└──────────────────────────────────────────┘
```

**功能：**
- 選擇 Batocera 的 roms 根目錄
- 選擇語系包儲存位置（預設：程式目錄的 translations 資料夾）
- 支援拖放資料夾到輸入框

#### 2. 翻譯設定區
```
┌─ 翻譯設定 ─────────────────────────────────┐
│ 顯示模式: ○ 僅中文                          │
│          ○ 中文 (英文)                     │
│          ○ 英文 (中文)                     │
│          ○ 僅英文（保持原樣）               │
│                                            │
│ ☑ 翻譯遊戲描述                              │
│ 最大名稱長度: [100] 字元                    │
│                                            │
│ 翻譯 API: [googletrans ▼]                 │
│ API Key (選填): [_____________]            │
└──────────────────────────────────────────┘
```

**功能：**
- 單選按鈕選擇顯示模式
- 勾選框控制是否翻譯描述
- 輸入框設定最大長度
- 下拉選單選擇翻譯 API
- API Key 輸入框（如果需要）

#### 3. 進度顯示區
```
┌─ 處理進度 ─────────────────────────────────┐
│ 目前狀態: 準備就緒                          │
│                                            │
│ ▓▓▓▓▓▓▓▓░░░░░░░░░░░░ 40%                 │
│                                            │
│ [日誌輸出區域 - 可捲動]                     │
│ [2025-11-27 14:30:25] 掃描到 3 個平台     │
│ [2025-11-27 14:30:26] 載入 NES 語系包...  │
│ [2025-11-27 14:30:27] 處理 Super Mario... │
│ [2025-11-27 14:30:28] ✓ 從語系包找到翻譯  │
│                                            │
└──────────────────────────────────────────┘
```

**功能：**
- 即時顯示處理狀態
- 進度條顯示完成百分比
- 日誌區域顯示詳細處理過程
- 自動捲動到最新訊息

#### 4. 操作按鈕區
```
┌────────────────────────────────────────────┐
│ [開始翻譯] [預覽模式] [停止] [清空日誌]      │
│                                            │
│ [語系包管理] [匯入語系包] [匯出語系包]       │
│                                            │
│ [設定] [關於]                               │
└────────────────────────────────────────────┘
```

**按鈕功能：**
- **開始翻譯**：執行翻譯作業
- **預覽模式**：Dry-run，只顯示會改什麼
- **停止**：中止正在執行的作業
- **清空日誌**：清除日誌區域內容
- **語系包管理**：開啟語系包管理視窗
- **匯入語系包**：從檔案匯入語系包
- **匯出語系包**：匯出語系包分享
- **設定**：開啟設定視窗
- **關於**：顯示程式資訊

#### 5. 狀態列
```
┌────────────────────────────────────────────┐
│ 語系包: NES (500個) | SNES (800個) | ...  │
│                            v1.0 | 準備就緒  │
└────────────────────────────────────────────┘
```

**功能：**
- 顯示已載入的語系包統計
- 程式版本號
- 目前狀態

---

### 子視窗設計

#### 語系包管理視窗
```
┌─ 語系包管理 ───────────────────────────────┐
│ 平台: [NES ▼]                              │
│                                            │
│ ┌─ 統計資訊 ────────────────────────────┐ │
│ │ 遊戲名稱: 500 個                       │ │
│ │ 描述翻譯: 350 個                       │ │
│ │ 最後更新: 2025-11-27                  │ │
│ └───────────────────────────────────────┘ │
│                                            │
│ ┌─ 翻譯預覽 ────────────────────────────┐ │
│ │ [搜尋: ____________]                  │ │
│ │                                       │ │
│ │ Super Mario Bros → 超級瑪利歐兄弟      │ │
│ │ Contra → 魂斗羅                       │ │
│ │ The Legend of Zelda → 薩爾達傳說      │ │
│ │ ...                                   │ │
│ └───────────────────────────────────────┘ │
│                                            │
│ [編輯] [刪除選中項] [合併本地快取]          │
│ [匯入] [匯出] [關閉]                        │
└──────────────────────────────────────────┘
```

**功能：**
- 下拉選單選擇平台
- 顯示語系包統計資訊
- 可搜尋和預覽翻譯內容
- 編輯、刪除功能
- 合併本地快取到語系包

#### 設定視窗
```
┌─ 設定 ─────────────────────────────────────┐
│ ┌─ 一般設定 ────────────────────────────┐ │
│ │ ☑ 自動備份原始檔案                     │ │
│ │ ☑ 完成後顯示統計報告                   │ │
│ │ ☑ 自動儲存設定                        │ │
│ │ 日誌等級: [INFO ▼]                    │ │
│ └───────────────────────────────────────┘ │
│                                            │
│ ┌─ 搜尋設定 ────────────────────────────┐ │
│ │ 搜尋延遲: [2] 秒                       │ │
│ │ 重試次數: [3] 次                       │ │
│ │ 超時時間: [10] 秒                      │ │
│ └───────────────────────────────────────┘ │
│                                            │
│ ┌─ 進階設定 ────────────────────────────┐ │
│ │ User-Agent: [__________________]      │ │
│ │ ☑ 啟用代理伺服器                       │ │
│ │ 代理地址: [__________________]         │ │
│ └───────────────────────────────────────┘ │
│                                            │
│ [確定] [取消] [套用] [重設預設值]           │
└──────────────────────────────────────────┘
```

---

## GUI 技術實作要點

### 1. 多執行緒處理
- 翻譯作業在獨立執行緒執行
- 避免 GUI 凍結
- 使用 Queue 在執行緒間傳遞訊息

```python
import threading
import queue

def translation_worker(config, log_queue):
    """在背景執行緒執行翻譯"""
    # 翻譯邏輯
    log_queue.put("處理完成")

# 主視窗啟動執行緒
thread = threading.Thread(target=translation_worker, args=(config, log_queue))
thread.start()
```

### 2. 即時日誌更新
```python
def update_log(self):
    """定期檢查 queue 並更新日誌"""
    try:
        while True:
            msg = self.log_queue.get_nowait()
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
    except queue.Empty:
        pass
    # 每 100ms 檢查一次
    self.root.after(100, self.update_log)
```

### 3. 進度條更新
```python
def update_progress(self, current, total):
    """更新進度條"""
    percentage = (current / total) * 100
    self.progress_bar['value'] = percentage
    self.status_label.config(text=f"處理中: {current}/{total}")
```

### 4. 設定檔儲存
```python
import json

def save_config(self):
    """儲存使用者設定"""
    config = {
        'roms_path': self.roms_path.get(),
        'translations_dir': self.translations_dir.get(),
        'display_mode': self.display_mode.get(),
        'translate_desc': self.translate_desc.get(),
        'max_length': self.max_length.get()
    }
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def load_config(self):
    """載入使用者設定"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.roms_path.set(config.get('roms_path', ''))
            # ... 載入其他設定
    except FileNotFoundError:
        pass  # 使用預設值
```

### 5. 錯誤處理和提示
```python
from tkinter import messagebox

def show_error(self, message):
    """顯示錯誤訊息"""
    messagebox.showerror("錯誤", message)

def show_info(self, message):
    """顯示資訊訊息"""
    messagebox.showinfo("提示", message)

def confirm_action(self, message):
    """確認對話框"""
    return messagebox.askyesno("確認", message)
```

---

## 打包成 Windows .exe

### 使用 PyInstaller

#### 1. 安裝 PyInstaller
```bash
pip install pyinstaller
```

#### 2. 建立 spec 檔案（選配）
```python
# batocera_translator.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('translations', 'translations'),  # 包含語系包
        ('config.json', '.'),              # 包含預設設定
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Batocera翻譯工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不顯示命令列視窗
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # 程式圖示
)
```

#### 3. 打包指令
```bash
# 方法 1: 簡單打包（單一 .exe 檔案）
pyinstaller --onefile --windowed --name="Batocera翻譯工具" gui.py

# 方法 2: 使用 spec 檔案
pyinstaller batocera_translator.spec

# 方法 3: 包含圖示和資料檔案
pyinstaller --onefile --windowed \
  --name="Batocera翻譯工具" \
  --icon=icon.ico \
  --add-data="translations;translations" \
  gui.py
```

#### 4. 打包後的目錄結構
```
dist/
└── Batocera翻譯工具.exe  (單一可執行檔)

或

dist/
└── Batocera翻譯工具/
    ├── Batocera翻譯工具.exe
    ├── translations/      # 語系包
    └── (其他依賴檔案)
```

### 減小執行檔大小的技巧

1. **排除不需要的模組**
```bash
pyinstaller --exclude-module matplotlib --exclude-module numpy ...
```

2. **使用 UPX 壓縮**
```bash
pyinstaller --onefile --windowed --upx-dir=/path/to/upx gui.py
```

3. **虛擬環境打包**
- 在乾淨的虛擬環境中只安裝必要套件
- 避免打包不必要的依賴

---

## GUI 程式架構

### 檔案結構
```
batocera-translator/
├── translator.py          # 核心翻譯邏輯（命令列版）
├── gui.py                 # GUI 主程式
├── gui_widgets.py         # 自訂 GUI 元件
├── config.json            # 使用者設定
├── requirements.txt       # 套件需求
├── requirements-gui.txt   # GUI 額外需求
├── icon.ico               # 程式圖示
├── batocera_translator.spec  # PyInstaller 設定
├── translations/          # 語系包目錄
└── build_exe.bat          # Windows 打包腳本
```

### gui.py 程式結構
```python
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from translator import GamelistTranslator

class TranslatorGUI:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """建立 UI 元件"""
        self.create_path_section()
        self.create_settings_section()
        self.create_progress_section()
        self.create_button_section()
        
    def create_path_section(self):
        """建立路徑設定區"""
        pass
        
    def create_settings_section(self):
        """建立翻譯設定區"""
        pass
        
    def start_translation(self):
        """開始翻譯（在新執行緒中）"""
        config = self.get_config()
        thread = threading.Thread(target=self.translation_worker, args=(config,))
        thread.start()
        
    def translation_worker(self, config):
        """背景執行翻譯"""
        translator = GamelistTranslator(**config)
        translator.batch_update()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorGUI(root)
    root.mainloop()
```

---

## 背景說明

### Batocera 簡介
- Batocera 是一個基於 Linux 的復古遊戲模擬器系統
- 遊戲資訊儲存在 XML 格式的 `gamelist.xml` 檔案中
- 每個遊戲平台（NES、SNES、PS1 等）都有獨立的資料夾和 gamelist.xml

### 檔案結構
```
/userdata/roms/
├── nes/
│   ├── gamelist.xml
│   └── [ROM 檔案]
├── snes/
│   ├── gamelist.xml
│   └── [ROM 檔案]
├── megadrive/
│   ├── gamelist.xml
│   └── [ROM 檔案]
└── ...
```

### gamelist.xml 格式範例
```xml
<?xml version="1.0"?>
<gameList>
  <game>
    <path>./SuperMarioBros.nes</path>
    <name>Super Mario Bros (USA)</name>
    <desc>A classic platformer game</desc>
    <image>./images/SuperMarioBros-image.png</image>
    <rating>0.95</rating>
    <releasedate>19850913T000000</releasedate>
    <developer>Nintendo</developer>
    <publisher>Nintendo</publisher>
    <genre>Platform</genre>
    <players>2</players>
  </game>
  <game>
    <path>./Contra.nes</path>
    <name>Contra (USA) [!]</name>
    <desc>Run and gun action game</desc>
    ...
  </game>
</gameList>
```

---

## 功能需求

### 核心功能

#### 1. 遊戲名稱清理
- 移除區域標記：`(USA)`, `(Japan)`, `(Europe)`, `(World)`, `(En)`, `(Ja)` 等
- 移除版本標記：`[!]`, `[a]`, `[b1]`, `[T+Chi]` 等
- 移除括號和方括號內的所有內容
- 移除 ROM 校驗標記：`[h]`, `[p]`, `[o]` 等
- 範例：`Super Mario Bros (USA) [!]` → `Super Mario Bros`

#### 2. 透過 Google 搜尋翻譯
- 使用 Google 搜尋引擎查詢遊戲中文名稱
- 搜尋查詢格式：`{遊戲英文名} {平台名稱} 遊戲 中文`
- 從搜尋結果頁面提取中文譯名
- 優先考慮可信來源（維基百科、巴哈姆特等）

#### 2.5. 翻譯遊戲描述（`<desc>` 欄位）
- 使用翻譯 API 將英文描述翻譯成繁體中文
- 建議使用 Google Translate API 或其他翻譯服務
- 翻譯選項：
  - **googletrans** (免費，但不穩定)
  - **Google Cloud Translation API** (付費，穩定)
  - **其他翻譯 API** (DeepL, Azure, etc.)
- 描述翻譯也要加入快取機制
- 如果描述已是中文，跳過翻譯

#### 3. 中文名稱提取邏輯
需要從搜尋結果 HTML 中智慧提取中文名稱：

**提取策略：**
- 尋找書名號《》內的內容
- 從標題和描述文字中提取含中文的片段
- 過濾掉不相關的文字（年份、平台名、「遊戲」等關鍵字）
- 優先選擇長度適中的結果（4-15 個中文字）

**評分機制：**
- 出現頻率高 → 加分
- 長度適中（4-15字）→ 加分
- 不包含英文字母 → 加分
- 不包含數字 → 加分
- 來自可信來源 → 加分

#### 4. 快取機制改為語系包（字典檔）
- 使用 **KEY-VALUE 格式的 JSON 字典檔**
- 按平台分類的語系包
- 所有用戶可以共享和貢獻

**語系包格式（簡化的字典檔）：**

檔案：`translations_nes.json`
```json
{
  "Super Mario Bros": "超級瑪利歐兄弟",
  "The Legend of Zelda": "薩爾達傳說",
  "Contra": "魂斗羅",
  "Mega Man": "洛克人",
  "Castlevania": "惡魔城"
}
```

檔案：`descriptions_nes.json`（描述翻譯字典）
```json
{
  "A classic platformer game": "經典的平台跳躍遊戲",
  "Run and gun action game": "橫向卷軸射擊遊戲",
  "Adventure game with puzzles": "帶有解謎元素的冒險遊戲"
}
```

**查找優先順序：**
1. 先查對應平台的語系包（translations_平台.json）
2. 再查本地快取（local_cache.json）
3. 都找不到才執行 Google 搜尋
4. 新翻譯的結果加入本地快取
5. 定期將本地快取合併到語系包

**語系包優點：**
- 格式極簡，易於編輯和分享
- 可以用任何文字編輯器手動修改
- Git 友善，易於版本控制和協作
- 載入速度快

#### 5. XML 更新
- 讀取 gamelist.xml
- 備份原始檔案（加上 .backup 副檔名）
- 只修改 `<name>` 標籤的內容
- 保持其他欄位不變
- 使用 UTF-8 編碼儲存

#### 7. 自動遍歷所有 gamelist.xml
- 用戶只需提供 roms 根目錄路徑（例如：`/userdata/roms`）
- 程式自動掃描所有子資料夾
- 找出所有 `gamelist.xml` 檔案
- 根據資料夾名稱識別平台（nes, snes, gba 等）
- 載入對應的語系包
- 批次處理所有找到的 gamelist.xml

**遍歷邏輯：**
```
/userdata/roms/
├── nes/gamelist.xml          → 載入 translations_nes.json
├── snes/gamelist.xml         → 載入 translations_snes.json
├── megadrive/gamelist.xml    → 載入 translations_megadrive.json
├── gba/gamelist.xml          → 載入 translations_gba.json
└── ps1/gamelist.xml          → 載入 translations_ps1.json
```

---

## 技術規格

### 程式語言
- Python 3.7+

### 必要套件
```
beautifulsoup4>=4.12.0  # HTML 解析
requests>=2.31.0        # HTTP 請求
lxml>=4.9.0             # XML 處理（效能較佳）
googletrans==4.0.0rc1   # 免費翻譯 API（描述翻譯用）
pyinstaller>=6.0.0      # 打包成 .exe 執行檔
# tkinter 為 Python 內建，無需額外安裝
```

**GUI 框架選擇：**

推薦使用 **Tkinter**（Python 內建）：
- 優點：內建、輕量、跨平台、容易打包
- 缺點：介面較傳統

**替代方案：**
1. **PyQt5 / PySide6**
   - 優點：介面現代、功能強大
   - 缺點：打包後檔案較大（50MB+）
   
2. **CustomTkinter**
   - 優點：基於 Tkinter，介面更現代
   - 缺點：需額外安裝

**打包工具：**
- **PyInstaller**（推薦）：簡單、支援度高
- **cx_Freeze**：替代選項
- **Nuitka**：編譯成原生程式碼，執行速度快

**翻譯 API 選擇（三選一）：**

1. **googletrans** (推薦先試用)
   - 優點：免費、安裝簡單
   - 缺點：不穩定、可能被封鎖
   - 安裝：`pip install googletrans==4.0.0rc1`

2. **Google Cloud Translation API**
   - 優點：穩定、高品質
   - 缺點：需要 API key、付費（前 50 萬字元/月免費）
   - 安裝：`pip install google-cloud-translate`

3. **其他選項**
   - DeepL API (需付費，但翻譯品質最好)
   - Azure Translator (Microsoft)
   - 百度翻譯 API (中文翻譯較準)

### 平台對照表
```python
PLATFORM_NAMES = {
    'nes': 'FC紅白機',
    'snes': '超級任天堂',
    'megadrive': 'MD Mega Drive',
    'genesis': 'MD Mega Drive',      # 北美版名稱
    'gba': 'GBA Game Boy Advance',
    'gb': 'Game Boy',
    'gbc': 'Game Boy Color',
    'nds': 'NDS Nintendo DS',
    'n64': 'N64 Nintendo 64',
    'ps1': 'PS1 PlayStation',
    'psx': 'PS1 PlayStation',        # 別名
    'ps2': 'PS2 PlayStation 2',
    'psp': 'PSP PlayStation Portable',
    'arcade': '街機',
    'mame': '街機 MAME',
    'fbneo': '街機 FBNeo',
    'neogeo': 'Neo Geo',
    'pcengine': 'PC Engine',
    'mastersystem': 'Master System',
    'gamegear': 'Game Gear',
    'dreamcast': 'Dreamcast',
    'saturn': 'Sega Saturn',
    'atari2600': 'Atari 2600',
    'atari7800': 'Atari 7800',
}
```

### HTTP 請求規格
- User-Agent: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36`
- 搜尋 URL: `https://www.google.com/search?q={query}&hl=zh-TW`
- 請求間隔：至少 2 秒（避免被封鎖）
- 逾時設定：10 秒

---

## 輸入與輸出

### 輸入
1. **roms 根目錄路徑**
   - 例：`/userdata/roms`
   - 程式會自動遍歷所有子資料夾

2. **顯示模式（可選）**
   - `chinese_only`（預設）：僅中文
   - `chinese_english`：中文 (英文)
   - `english_chinese`：英文 (中文)
   - `english_only`：保持英文

3. **最大名稱長度（可選）**
   - 預設：100 字元
   - 超過長度時自動處理

4. **翻譯描述（可選）**
   - `True`（預設）：翻譯描述
   - `False`：只翻譯名稱

5. **dry_run 模式（選填）**
   - `True`: 只顯示會修改什麼，不實際修改檔案
   - `False`: 實際修改檔案

### 輸出
1. **修改後的 gamelist.xml**
   - 更新 `<name>` 標籤內容為中文

2. **備份檔案**
   - 原始檔案備份為 `gamelist.xml.backup`

3. **快取檔案**
   - `translation_cache.json` 儲存翻譯結果

4. **終端機輸出**
```
處理系統: NES
共有 50 個遊戲

搜尋: Super Mario Bros FC紅白機 遊戲 中文
✓ 名稱: Super Mario Bros → 超級瑪利歐兄弟
✓ 描述: A classic platformer game → 經典的平台跳躍遊戲
[1/50] 已更新

搜尋: Contra FC紅白機 遊戲 中文
✓ 名稱: Contra → 魂斗羅
✓ 描述: Run and gun action game → 橫向卷軸射擊遊戲
[2/50] 已更新

...

✓ 已更新 45/50 個遊戲（名稱 + 描述）
```

---

## 程式架構建議

### 類別設計

```python
class GamelistTranslator:
    def __init__(self, 
                 translations_dir="/userdata/translations",
                 local_cache_file="local_cache.json",
                 display_mode="chinese_only",
                 max_name_length=100,
                 translate_desc=True):
        """
        初始化翻譯器
        translations_dir: 語系包目錄
        local_cache_file: 本地快取檔案
        display_mode: 顯示模式 (chinese_only, chinese_english, english_chinese, english_only)
        max_name_length: 名稱最大長度
        translate_desc: 是否翻譯描述
        """
        
    def scan_roms_directory(self, roms_path):
        """
        掃描 roms 目錄，找出所有 gamelist.xml
        返回: [(platform, gamelist_path), ...]
        """
        
    def load_translation_dict(self, platform):
        """載入指定平台的翻譯字典（語系包）"""
        
    def load_description_dict(self, platform):
        """載入指定平台的描述翻譯字典"""
        
    def load_local_cache(self):
        """載入本地快取"""
        
    def save_local_cache(self):
        """儲存本地快取"""
        
    def save_to_translation_dict(self, platform, game_name, chinese_name):
        """將翻譯加入語系包"""
        
    def lookup_translation(self, game_name, platform):
        """
        查找翻譯（按優先順序）
        1. 語系包字典
        2. 本地快取
        3. 返回 None（需要搜尋）
        """
        
    def format_game_name(self, english_name, chinese_name):
        """
        根據顯示模式格式化遊戲名稱
        處理長度限制
        """
        
    def clean_game_name(self, name):
        """清理遊戲名稱（移除區域標記等）"""
        
    def search_google(self, query):
        """搜尋 Google 並返回 HTML"""
        
    def extract_chinese_name(self, html, original_name):
        """從搜尋結果提取中文名稱"""
        
    def translate_name(self, game_name, platform):
        """翻譯遊戲名稱（先查字典，再搜尋）"""
        
    def translate_description(self, description, platform):
        """翻譯遊戲描述（先查字典，再用 API）"""
        
    def update_gamelist(self, gamelist_path, platform, dry_run=False):
        """更新單一 gamelist.xml"""
        
    def batch_update(self, roms_path, dry_run=False):
        """
        批次更新所有平台
        1. 掃描 roms 目錄
        2. 找出所有 gamelist.xml
        3. 依序處理每個平台
        """
        
    def merge_local_to_dict(self, platform=None):
        """將本地快取合併到語系包（可指定平台或全部）"""
        
    def export_translation_dict(self, platform, output_path):
        """匯出語系包（用於分享）"""
        
    def import_translation_dict(self, platform, input_path):
        """匯入別人分享的語系包"""
        
    def show_stats(self, platform=None):
        """顯示語系包統計（可指定平台或全部）"""
```

### 主要流程

```
1. 讀取 gamelist.xml
2. 遍歷每個 <game> 元素
3. 提取 <name> 的值
4. 清理遊戲名稱
5. 檢查快取
   - 如果有快取 → 直接使用
   - 如果沒有 → 執行搜尋
6. Google 搜尋
7. 解析 HTML 提取中文名稱
8. 評分並選擇最佳候選
9. 更新 <name> 標籤
10. 儲存快取
11. 寫入 XML 檔案
```

---

## 使用範例

### 基本使用
```python
# 建立翻譯器（設定顯示模式）
translator = GamelistTranslator(
    translations_dir="/userdata/translations",
    display_mode="chinese_english",  # 中文 (英文)
    max_name_length=100,
    translate_desc=True
)

# 批次更新所有平台（只需提供 roms 根目錄）
translator.batch_update("/userdata/roms")

# 預覽模式（不實際修改）
translator.batch_update("/userdata/roms", dry_run=True)

# 只更新特定平台
translator.update_gamelist("/userdata/roms/nes/gamelist.xml", platform="nes")

# 切換顯示模式
translator.display_mode = "chinese_only"  # 僅中文
translator.batch_update("/userdata/roms")

# 將本地新翻譯合併到語系包
translator.merge_local_to_dict()  # 合併所有平台
translator.merge_local_to_dict(platform="nes")  # 只合併 NES

# 匯出語系包分享給別人
translator.export_translation_dict("nes", "/tmp/translations_nes.json")

# 匯入別人分享的語系包
translator.import_translation_dict("snes", "/tmp/translations_snes_community.json")

# 查看統計
translator.show_stats()  # 所有平台
translator.show_stats("nes")  # 特定平台
```

### 顯示模式範例
```python
# 假設翻譯: Super Mario Bros → 超級瑪利歐兄弟

# 模式 1: chinese_only
translator = GamelistTranslator(display_mode="chinese_only")
# 結果: <n>超級瑪利歐兄弟</n>

# 模式 2: chinese_english
translator = GamelistTranslator(display_mode="chinese_english")
# 結果: <n>超級瑪利歐兄弟 (Super Mario Bros)</n>

# 模式 3: english_chinese
translator = GamelistTranslator(display_mode="english_chinese")
# 結果: <n>Super Mario Bros (超級瑪利歐兄弟)</n>

# 模式 4: english_only
translator = GamelistTranslator(display_mode="english_only")
# 結果: <n>Super Mario Bros</n> (保持原樣)
```

### 命令列介面（選配）
```bash
# 基本用法：處理整個 roms 目錄
python translator.py --roms-path /userdata/roms

# 指定顯示模式
python translator.py --roms-path /userdata/roms --mode chinese_english

# 預覽模式（不實際修改）
python translator.py --roms-path /userdata/roms --dry-run

# 只翻譯名稱，不翻譯描述
python translator.py --roms-path /userdata/roms --no-desc

# 設定最大長度
python translator.py --roms-path /userdata/roms --max-length 80

# 查看語系包統計
python translator.py --stats
python translator.py --stats --platform nes

# 匯出語系包
python translator.py --export nes --output /tmp/translations_nes.json

# 匯入語系包
python translator.py --import snes --input /tmp/translations_snes.json

# 將本地快取合併到語系包
python translator.py --merge
python translator.py --merge --platform nes
```

---

## 錯誤處理

### 必須處理的錯誤情境

1. **檔案不存在**
   - 檢查 gamelist.xml 是否存在
   - 給予清楚的錯誤訊息

2. **網路錯誤**
   - HTTP 請求失敗
   - 逾時處理
   - 重試機制（最多 3 次）
   - 指數退避策略（Exponential Backoff）

3. **解析錯誤**
   - XML 格式錯誤
   - HTML 解析失敗
   - 找不到中文名稱時保持原名

4. **權限錯誤**
   - 無法寫入檔案
   - 無法建立備份
   - 以管理員權限提示

5. **編碼錯誤**
   - 確保使用 UTF-8
   - 處理特殊字元

---

## 特殊考量

### 1. 已有中文名稱的處理
如果遊戲名稱已經包含中文字元，應該跳過翻譯：
```python
def contains_chinese(text):
    """檢查文字是否包含中文字元"""
    return any('\u4e00' <= char <= '\u9fff' for char in text)
```

### 2. 搜尋頻率限制
- 遊戲名稱搜尋：每次間隔至少 2 秒
- 描述翻譯：使用翻譯 API，速度較快
- 避免觸發 Google 的反爬蟲機制
- 考慮加入隨機延遲（2-4 秒）

### 3. 翻譯品質檢查
建議加入手動確認機制：
- 顯示前 10 個翻譯結果（名稱+描述）
- 詢問用戶是否繼續
- 允許手動修正錯誤翻譯
- 提供選項：只翻譯名稱 / 名稱+描述

### 4. 常見遊戲預設對照表
可以內建常見遊戲的翻譯，避免搜尋：
```python
DEFAULT_TRANSLATIONS = {
    "Super Mario Bros": "超級瑪利歐兄弟",
    "Super Mario Bros 2": "超級瑪利歐兄弟2",
    "Super Mario Bros 3": "超級瑪利歐兄弟3",
    "Super Mario World": "超級瑪利歐世界",
    "The Legend of Zelda": "乙爾達傳說",
    "Zelda II The Adventure of Link": "乙爾達傳說II 林克的冒險",
    "Contra": "魂斗羅",
    "Super Contra": "超級魂斗羅",
    "Castlevania": "乙魔城",
    "Mega Man": "洛克人",
    "Mega Man 2": "洛克人2",
    "Metroid": "乂托洛德",
    "Final Fantasy": "太空戰士",
    "Dragon Quest": "勇者鬥乙龍",
    "Street Fighter II": "快打旋風II",
    "Sonic the Hedgehog": "音速小子",
    "Tetris": "俄羅斯方塊",
    "Pac-Man": "小精靈",
    "Donkey Kong": "大金剛",
    # ... 更多常見遊戲
}
```

---

## 測試需求

### 測試案例

1. **基本翻譯測試**
   - 輸入：`Super Mario Bros`
   - 預期輸出：`超級瑪利歐兄弟`

2. **名稱清理測試**
   - 輸入：`Super Mario Bros (USA) [!]`
   - 清理後：`Super Mario Bros`
   - 預期輸出：`超級瑪利歐兄弟`

3. **已有中文測試**
   - 輸入：`超級瑪利歐兄弟`
   - 預期輸出：`超級瑪利歐兄弟`（不變）

4. **找不到翻譯測試**
   - 輸入：非常冷門的遊戲
   - 預期輸出：保持原英文名稱

5. **快取測試**
   - 第一次翻譯：執行搜尋
   - 第二次相同遊戲：從快取讀取

6. **XML 完整性測試**
   - 更新後 XML 格式正確
   - `<name>` 和 `<desc>` 標籤已更新為中文
   - 其他標籤未被修改
   - 編碼為 UTF-8

7. **描述翻譯測試**
   - 輸入：`A classic platformer game`
   - 預期輸出：`經典的平台跳躍遊戲`
   
8. **混合語言測試**
   - 輸入：描述已經部分是中文
   - 預期：保持中文部分，只翻譯英文部分

---

## 預期挑戰與解決方案

### 挑戰 1: Google 搜尋可能被封鎖
**解決方案：**
- 加入請求延遲
- 使用不同的 User-Agent
- 考慮加入代理伺服器支援
- 提供備用翻譯 API 選項

### 挑戰 2: 中文名稱提取不準確
**解決方案：**
- 多重提取策略
- 優先信任可靠來源（維基百科等）
- 加入人工確認機制
- 允許手動編輯翻譯對照表

### 挑戰 3: 不同地區譯名不同
**解決方案：**
- 預設使用台灣慣用譯名
- 搜尋時指定 `hl=zh-TW`
- 提供選項切換簡體/繁體

### 挑戰 4: 處理速度慢
**解決方案：**
- **共享索引檔大幅提升速度**（90%+ 遊戲無需搜尋）
- 快取機制（名稱和描述分別快取）
- 批次處理前顯示預估時間
- 提供選項：只翻譯名稱（較快）或名稱+描述（較慢）
- 使用較快的翻譯 API（Google Cloud 比 googletrans 快）

### 挑戰 5: 描述翻譯品質不佳
**解決方案：**
- 遊戲描述通常是簡短句子，翻譯較準確
- 使用專業翻譯 API（DeepL, Google Cloud）
- 加入遊戲術語詞典（platformer → 平台遊戲）
- 允許手動修正常見描述的翻譯
- **共享索引檔包含人工審核的描述翻譯**

### 挑戰 6: 語系包維護和更新
**解決方案：**
- 建立 GitHub Repository 存放官方語系包
- 社群貢獻新翻譯（Pull Request）
- 定期釋出更新版本
- 自動化測試驗證語系包格式
- 提供語系包品質報告（覆蓋率）

### 挑戰 7: 不同顯示模式的效果
**解決方案：**
- 提供預覽功能（dry-run）
- 範例截圖或說明文件
- 允許隨時切換模式重新處理
- 備份機制確保可以回復

### 挑戰 8: 長度限制的處理
**解決方案：**
- 自動偵測並截斷過長名稱
- 優先保留中文（因為是主要資訊）
- 記錄被截斷的遊戲，供用戶檢查
- 提供手動調整選項

---

## 延伸功能（Optional）

1. **GUI 進階功能**
   - 深色/淺色主題切換
   - 多語言介面（英文/繁中/簡中）
   - 拖放資料夾到視窗
   - 右鍵選單快捷操作
   - 鍵盤快捷鍵（Ctrl+S 儲存設定等）

2. **批次處理功能**
   - 排程翻譯（指定時間執行）
   - 監視資料夾自動翻譯
   - 比較不同設定的效果

3. **語系包編輯器**
   - 內建語系包編輯功能
   - 拼字檢查和建議
   - 翻譯品質評分
   - 批次匯入/匯出

4. **統計和報告**
   - 翻譯成功率圖表
   - 處理時間分析
   - 快取命中率
   - 語系包覆蓋率視覺化

5. **整合其他資料來源**
   - ScreenScraper API
   - TheGamesDB API
   - 本地遊戲資料庫
   - 合併多個來源的翻譯

6. **社群功能**
   - 內建更新檢查
   - 一鍵下載最新語系包
   - 上傳貢獻到社群伺服器
   - 使用者評分和回饋系統

7. **自動更新功能**
   - 檢查程式更新
   - 自動下載最新語系包
   - 增量更新機制

8. **網路功能**
   - 線上語系包瀏覽器
   - 分享連結產生器
   - 雲端同步設定

---

## GUI 測試需求

1. **功能測試**
   - 所有按鈕點擊正常
   - 檔案選擇對話框正常
   - 設定儲存和載入正常
   - 日誌即時更新

2. **介面測試**
   - 不同解析度下正常顯示
   - 視窗縮放正常
   - 中文字元顯示正確
   - 進度條更新流暢

3. **執行緒測試**
   - 翻譯時 GUI 不凍結
   - 可以中途停止
   - 錯誤不會讓程式崩潰

4. **打包測試**
   - .exe 在乾淨的 Windows 上執行
   - 所有資源檔案正確包含
   - 檔案大小合理（<100MB）
   - 不需要安裝 Python 即可執行

---

## Windows .exe 發佈清單

發佈時應包含：

```
Batocera翻譯工具_v1.0/
├── Batocera翻譯工具.exe        # 主程式
├── README.txt                  # 使用說明（繁中）
├── CHANGELOG.txt               # 版本更新紀錄
├── translations/               # 預載語系包
│   ├── translations_nes.json
│   ├── translations_snes.json
│   └── ...
├── 範例檔案/
│   └── sample_gamelist.xml
└── 授權條款.txt                # MIT License
```

**發佈平台建議：**
- GitHub Releases
- 巴哈姆特論壇
- Batocera 官方論壇
- 台灣復古遊戲社群

---

## 檔案清單

最終專案應包含以下檔案：

```
batocera-translator/
├── translator.py                    # 核心翻譯邏輯（命令列版）
├── gui.py                           # GUI 主程式
├── gui_widgets.py                   # 自訂 GUI 元件（選配）
├── config.json                      # 使用者設定（執行後產生）
├── requirements.txt                 # 核心套件需求
├── requirements-gui.txt             # GUI 額外需求
├── icon.ico                         # 程式圖示
├── batocera_translator.spec         # PyInstaller 打包設定
├── build_exe.bat                    # Windows 打包腳本
├── README.md                        # 使用說明
├── local_cache.json                 # 本地快取（執行後產生）
├── translations/                    # 語系包目錄（字典檔）
│   ├── translations_nes.json        # NES 遊戲名稱字典
│   ├── descriptions_nes.json        # NES 遊戲描述字典
│   ├── translations_snes.json       # SNES 遊戲名稱字典
│   ├── descriptions_snes.json       # SNES 遊戲描述字典
│   └── ...
├── dict_manager.py                  # 語系包管理工具（選配）
├── tests/                           # 測試檔案（選配）
│   ├── test_translator.py
│   ├── test_gui.py                  # GUI 測試
│   └── sample_gamelist.xml
└── docs/                            # 文件
    ├── CONTRIBUTING.md              # 貢獻指南
    ├── DICT_FORMAT.md               # 語系包格式說明
    ├── DISPLAY_MODES.md             # 顯示模式說明
    ├── GUI_GUIDE.md                 # GUI 使用指南
    └── SHARING.md                   # 分享語系包教學
```

---

## 授權與版權

建議使用 MIT License，方便社群使用與改進。

---

## 參考資源

- [Batocera 官方文件](https://wiki.batocera.org/)
- [BeautifulSoup 文件](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Python XML 處理](https://docs.python.org/3/library/xml.etree.elementtree.html)
- [PyInstaller 文件](https://pyinstaller.org/en/stable/)
- [Tkinter 官方教學](https://docs.python.org/3/library/tkinter.html)
- [googletrans 套件](https://py-googletrans.readthedocs.io/)

**社群資源（建議建立）：**
- GitHub Repository: 存放共享索引檔和程式碼
- Discord/Telegram 群組: 討論翻譯和貢獻
- 論壇主題: Batocera 官方論壇、巴哈姆特等
- 索引檔下載站: 提供預先建立好的完整索引檔

---

## 聯絡資訊

如有問題或建議，請在 GitHub Issues 中討論。

---

## 開發優先順序建議

### Phase 1 - 核心功能（MVP）
1. 基本 CLI 版本翻譯器（translator.py）
2. 語系包載入與查詢功能
3. Google 搜尋翻譯功能
4. gamelist.xml 讀寫功能
5. 備份機制

### Phase 2 - GUI 介面
1. 基本 GUI 視窗（路徑選擇、開始翻譯）
2. 進度顯示與日誌輸出
3. 多執行緒處理
4. 設定檔儲存/載入

### Phase 3 - 進階功能
1. 語系包管理視窗
2. 預覽模式（Dry-run）
3. 翻譯 API 選擇
4. 描述翻譯功能

### Phase 4 - 打包與發佈
1. PyInstaller 打包設定
2. 測試與除錯
3. 文件撰寫
4. 社群發佈

---

## 版本歷程

| 版本 | 日期 | 說明 |
|------|------|------|
| 1.0 | 2025-11-27 | 初始規格書 |

---

**文件版本：** 1.0  
**最後更新：** 2025-11-27  
**作者：** [Ming]