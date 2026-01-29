# Batocera Gamelist 自動翻譯工具

<p align="center">
  <strong>🎮 讓你的復古遊戲收藏說中文！</strong>
</p>

<p align="center">
  <a href="../../releases/latest"><img src="https://img.shields.io/github/v/release/JB-Ming/batocera-translator?style=for-the-badge&logo=github" alt="Latest Release"></a>
  <a href="../../releases"><img src="https://img.shields.io/github/downloads/JB-Ming/batocera-translator/total?style=for-the-badge&logo=github" alt="Downloads"></a>
  <img src="https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.11+-green?style=for-the-badge&logo=python" alt="Python">
</p>

---

## 這是什麼？

這是一個專為 **Batocera** 復古遊戲模擬器設計的多語系翻譯工具。

如果你使用 Batocera 來玩復古遊戲，可能會發現遊戲清單裡全是英文名稱：「Super Mario Bros」、「The Legend of Zelda」、「Contra」...

這個工具可以自動將這些英文名稱翻譯成你想要的語言：「超級瑪利歐兄弟」、「薩爾達傳說」、「魂斗羅」

不只遊戲名稱，連遊戲簡介也能一併翻譯！

---

## 主要特色

| 特色 | 說明 |
|------|------|
| ✨ **一鍵翻譯** | 選擇你的遊戲資料夾，點一下就能全部翻譯完成 |
| 🌏 **多語系支援** | 支援繁體中文、簡體中文、日文、韓文等語言 |
| 📚 **共享語系包** | 提供預先翻譯好的語系包，大部分遊戲不需要上網搜尋 |
| 🎯 **多種顯示模式** | 可選擇只顯示翻譯、翻譯+原文、或保持原樣 |
| 💾 **安全備份** | 翻譯前會自動備份原始檔案，不用擔心出問題 |
| 🖥️ **圖形化介面** | 不需要懂程式，打開就能用 |
| 🤖 **AI 智能翻譯** | 支援 Gemini AI，提供更準確的遊戲描述 |
| ⚡ **效能優化** | 智能排序、平行處理，翻譯速度大幅提升 |
| 🔍 **自動補充描述** | 空白描述自動搜尋維基百科或 AI 生成 |
| 💾 **全局快取系統** | SQLite 持久化快取，重複翻譯速度提升 90%+ |
| 🌐 **HTTP 連接池** | 連接重用優化，減少網路延遲 |

---

## 支援的遊戲平台

這個工具支援 Batocera 中所有使用 `gamelist.xml` 的遊戲平台：

| 縮寫 | 平台名稱 | 縮寫 | 平台名稱 |
|------|----------|------|----------|
| nes | 紅白機 FC | snes | 超級任天堂 |
| megadrive | Mega Drive | genesis | Sega Genesis |
| gba | Game Boy Advance | gb | Game Boy |
| gbc | Game Boy Color | nds | Nintendo DS |
| n64 | Nintendo 64 | ps1/psx | PlayStation |
| ps2 | PlayStation 2 | psp | PlayStation Portable |
| arcade | 街機 | mame | MAME 街機 |
| neogeo | Neo Geo | dreamcast | Dreamcast |
| saturn | Sega Saturn | pcengine | PC Engine |

---

## 快速開始

### 步驟一：下載並解壓縮

前往 [Releases 頁面](../../releases/latest) 下載最新版本，解壓縮到任意位置。

### 步驟二：啟動程式

雙擊執行 `Batocera翻譯工具.exe`，會看到主視窗。

### 步驟三：設定路徑

點選「瀏覽...」按鈕，選擇你的 Roms 目錄：
- Windows 本機：例如 `D:\Games\roms`
- WSL 環境：例如 `\\wsl.localhost\Ubuntu\userdata\roms`

### 步驟四：選擇目標語系

從下拉選單選擇要翻譯成的語言（預設為繁體中文）。

### 步驟五：開始翻譯

**方式一：一鍵全部**
- 點「一鍵全部」按鈕，程式會依序執行所有四個階段

**方式二：逐階段執行（推薦驗證用）**
- ①掃描取回：掃描 ROM 目錄，複製 gamelist.xml 到暫存區
- ②產生字典：解析 gamelist.xml，產生字典檔
- ③翻譯：透過維基百科/網路搜尋翻譯遊戲名稱
- ④寫回：將翻譯結果寫回 gamelist.xml

翻譯完成後，`gamelists_local/` 目錄內的結構與原始 ROM 目錄相同，可直接複製覆蓋回原位。

---

## 常見問題

### Q：程式會改動我的遊戲 ROM 嗎？

**不會！** 這個工具只會修改 `gamelist.xml` 這個遊戲清單檔案，你的遊戲 ROM 檔案完全不會被動到。

### Q：翻譯錯了怎麼辦？

程式在翻譯前會自動備份原始檔案到 `backups/` 資料夾。你可以隨時把備份檔案複製回去還原。

### Q：為什麼有些遊戲沒有被翻譯？

可能的原因：
1. 語系包中沒有這款遊戲的翻譯
2. 網路搜尋找不到對應的譯名
3. 遊戲名稱判定為保留原文（如 F-Zero、NBA 2K23）

### Q：可以只翻譯名稱不翻譯描述嗎？

可以！在設定中取消勾選「翻譯遊戲描述」選項即可。

### Q：翻譯速度很慢？

大部分遊戲可以透過語系包直接查詢，速度很快。如果語系包中沒有的遊戲，需要上網搜尋，每次搜尋之間會間隔 2-4 秒以避免被封鎖。建議先匯入最新的語系包。

### Q：WSL 路徑是什麼？

如果你的 Batocera 是透過 WSL 安裝的，可以使用以下路徑格式：
- 新版：`\\wsl.localhost\Ubuntu\userdata\roms`
- 舊版：`\\wsl$\Ubuntu\userdata\roms`

### Q：字典檔和設定檔存在哪裡？

程式會將使用者資料（字典檔、設定檔）存放在程式目錄下的 `config/` 資料夾：

```
程式目錄/
├── Batocera翻譯工具.exe
├── config/                    # 使用者資料目錄
│   ├── dictionaries/          # 字典檔
│   ├── cache/                 # 快取
│   └── settings.json          # 設定檔
└── ...
```

這樣方便備份和管理，也避免 Microsoft Store Python 的沙盒問題。

---

# 技術規格

> 以下內容供開發者與進階使用者參考

---

## 工作原理

程式採用「掃描 → 產生字典 → 翻譯 → 寫回」的四階段流程。

### 階段一：掃描與取回

程式掃描指定的 ROM 資料夾，依資料夾名稱識別各遊戲平台，並將每個平台的 `gamelist.xml` 複製到本地暫存區。

**平台選擇功能：** 可選擇全部處理、僅處理勾選的平台、或排除指定平台。

### 階段二：產生字典檔

程式解析 `gamelist.xml`，將遊戲資料整理成字典檔（每個平台一份 JSON）。

**字典檔 KEY 格式：** 使用遊戲檔名（不含路徑前綴與副檔名）作為識別 KEY，例如 `Super Mario Bros (USA)` 而非 `./Super Mario Bros (USA).nes`。

**字典檔欄位：**

| 欄位 | 說明 |
|------|------|
| `key` | 遊戲識別 KEY（檔名，不含副檔名）|
| `original_name` | 遊戲原始名稱 |
| `name` / `name_source` | 遊戲名稱翻譯與來源標記 |
| `desc` / `desc_source` | 遊戲描述翻譯與來源標記 |

**翻譯來源標記值：** `wiki`（維基百科）、`search`（網路搜尋）、`api`（API 直譯）、`keep`（保留原文）、`manual`（手動填入）、`pack`（語系包匯入）

### 階段三：翻譯

**翻譯查找優先順序：**

```
1. 本地字典 → 2. 語系包 → 3. 維基百科 → 4. 其他網站 → 5. 保留原文/API直譯
```

**翻譯流程：** 

```
維基百科 → Gemini AI → 網路搜尋 → API 直譯
```

1. **維基百科**：優先查詢官方譯名（免費，最準確）
2. **Gemini AI**：使用 AI 智能翻譯（需 API Key，品質高）
3. **網路搜尋**：搜尋社群譯名（免費，結果不穩定）
4. **API 直譯**：Google Translate 直譯（免費，品質一般）

找到有效結果後立即返回，避免浪費 API 額度。

**保留原文判定：** 維基百科標題仍為英文、純數字或品牌+數字組合（如 FIFA 2024）、翻譯結果與原文相同。

**空白描述自動搜尋：** 當遊戲描述為空時，自動使用遊戲名稱（優先使用已翻譯的名稱）搜尋維基百科或 Gemini AI 生成描述。

### 階段四：寫回

將字典檔中的翻譯寫回 `gamelist.xml`。

**輸出目標：** 覆寫原始路徑（預設）、寫入本地暫存區、自訂路徑。

**顯示格式：** 僅中文、中文(英文)、英文(中文)、僅保留原文。

**格式保留：** 寫回時會保留原始 XML 檔案的結構與縮排格式，直接覆蓋回原始位置不需額外處理。

---

## UI 設定選項

### 字典檔衝突處理

| 選項 | 說明 |
|------|------|
| 合併（預設） | 保留已翻譯內容，加入新遊戲 |
| 僅補空白 | 只填入空白欄位 |
| 覆寫 | 完全取代 |
| 跳過 | 不處理該平台 |

### 翻譯設定

| 選項 | 說明 |
|------|------|
| 翻譯遊戲名稱/描述 | 選擇要處理的欄位 |
| 搜尋時包含平台名稱 | 搜尋關鍵字前加上平台名 |
| 搜尋失敗時使用 API 直譯 | 最後手段 |
| 自動偵測保留原文 | 啟用保留原文判定邏輯 |
| Gemini API Key | 設定 Google Gemini AI 的 API 金鑰（選填） |
| 請求間隔 (ms) | API 請求間隔時間，預設 500ms |
| 翻譯執行緒數 | 平行處理執行緒數量，預設 3 |
| 批次處理大小 | 每批處理的遊戲數量，預設 20 |

### 已翻譯項目處理

| 選項 | 說明 |
|------|------|
| 跳過已翻譯（預設） | 有 source 標記的項目不重新翻譯 |
| 僅重新翻譯直譯項目 | 僅對 source = api 的重新搜尋 |
| 全部重新翻譯 | 忽略現有翻譯 |

### 寫回設定

| 選項 | 說明 |
|------|------|
| name/desc 處理策略 | 跳過已翻譯 / 字典優先 / XML 優先 / 全部覆寫 |
| 寫入前自動備份 | 預設開啟 |
| 僅預覽不寫入 | 顯示變更但不修改檔案 |

### 寫回規則 (write_rules)

進階的欄位映射功能，可自訂翻譯內容要寫入哪個欄位：

```json
"write_rules": {
  "name": {
    "target": "name",     // 目標欄位：name / desc / skip
    "format": "translated" // 格式：translated / trans_orig / orig_trans / original
  },
  "desc": {
    "target": "desc",
    "format": "translated"
  }
}
```

**target 目標欄位說明：**

| 值 | 說明 |
|-----|------|
| `name` | 寫入 gamelist.xml 的 `<name>` 欄位 |
| `desc` | 寫入 gamelist.xml 的 `<desc>` 欄位 |
| `skip` | 跳過不寫入 |

**format 格式說明：**

| 值 | 範例輸出 |
|-----|----------|
| `translated` | `超級瑪利歐兄弟` |
| `trans_orig` | `超級瑪利歐兄弟 (Super Mario Bros)` |
| `orig_trans` | `Super Mario Bros (超級瑪利歐兄弟)` |
| `original` | `Super Mario Bros` |

**常見應用場景：**

| 場景 | 設定方式 |
|------|----------|
| 標準翻譯 | name→name, desc→desc |
| 只翻譯名稱，跳過描述 | name→name, desc→skip |
| 把翻譯的名稱寫到描述 | name→desc, desc→skip |
| 交叉寫入（測試用） | name→desc, desc→name |

### 翻譯 API 設定

| 選項 | 說明 |
|------|------|
| API 類型 | googletrans / Google Cloud / DeepL / Azure |
| API Key | 付費 API 的金鑰 |

---

## 進度與日誌

程式採用雙輸出設計：即時顯示在 UI 上，同時寫入日誌檔案。

### UI 即時顯示

處理進度（含進度條）、當前動作、翻譯來源標記、結果統計。

### 日誌檔案

**位置：** `logs/` 資料夾，檔名含時間戳記。

**格式：** `[時間] [級別] [模組] 訊息`

**級別：** DEBUG（灰）、INFO（白）、WARN（黃）、ERROR（紅）、SUCCESS（綠）

### UI 日誌面板功能

即時捲動、暫停捲動、級別篩選、搜尋功能、匯出日誌、清除畫面。

### 執行摘要

每次執行結束後輸出摘要，包含處理統計（成功/保留原文/跳過/失敗）、耗時、日誌檔案位置。

---

## 預覽模式

點擊「預覽模式」可在實際寫入前查看變更內容：變更前後對照、變更類型標示（新增/覆寫/跳過）、篩選功能、展開詳細。

---

## 手動編輯字典

如需修正翻譯錯誤：

1. 開啟程式目錄下的 `config\dictionaries\{language}\{platform}.json`
2. 找到對應的遊戲 Key
3. 修改 `name` 或 `desc` 欄位
4. 將 `source` 標記改為 `manual`
5. 存檔後重新執行寫回

---

## 中斷與續傳

| 功能 | 說明 |
|------|------|
| 取消執行 | 翻譯進行中可點擊「取消」按鈕中斷 |
| 自動存檔 | 已完成的翻譯會即時存入字典檔 |
| 斷點續傳 | 下次執行時會跳過已有 source 的項目 |

---

## 錯誤處理

| 錯誤類型 | 處理方式 |
|----------|----------|
| 網路斷線 | 暫停並顯示重試按鈕，已完成部分已存檔 |
| API 限流 | 自動增加間隔時間並重試 |
| API 額度用盡 | 提示使用者更換 API 或等待重置 |
| XML 格式錯誤 | 跳過該檔案並記錄日誌 |
| 字典檔損毀 | 嘗試從備份回復或重新產生 |

---

## 多語系支援

| 語系代碼 | 語言名稱 | 維基百科 |
|----------|----------|----------|
| `zh-TW` | 繁體中文 | zh.wikipedia.org |
| `zh-CN` | 簡體中文 | zh.wikipedia.org |
| `ja` | 日文 | ja.wikipedia.org |
| `ko` | 韓文 | ko.wikipedia.org |
| `en` | 英文 | en.wikipedia.org |

選擇目標語系後，程式會自動搜尋對應語言的維基百科，並使用對應語言的翻譯 API。

---

## 字典檔與語系包

字典檔與語系包採用相同格式，差別僅在 `source` 標記：本地翻譯標記為 `wiki`/`search`/`api`/`manual`，語系包匯入標記為 `pack`。

**匯入語系包：** 程式內建基本語系包，可從 GitHub 下載最新版本或手動匯入 JSON 檔案。

**匯入合併規則：** 本地已有翻譯的項目會保留，僅填入空白項目。

**匯出與貢獻：** 使用「匯出字典」功能匯出後，可提交 Pull Request 貢獻給社群。

---

## 資料夾結構

### 程式目錄（安裝位置）

```
BatoceraTranslator/
├── Batocera翻譯工具.exe   # 主程式
├── config/               # 使用者資料目錄
│   ├── dictionaries/     # 字典檔（依語系分類）
│   │   ├── zh-TW/
│   │   ├── ja/
│   │   └── ko/
│   ├── cache/            # 快取資料庫
│   ├── backups/          # 原始檔案備份
│   └── settings.json     # 程式設定
├── gamelists_local/      # gamelist.xml 暫存區
├── language_packs/       # 內建語系包
└── logs/                 # 日誌檔案
```

💡 所有使用者資料都在 `config/` 資料夾內，方便備份和管理。

---

## 程式架構

程式採用 Python 開發，使用 PyQt6 建構圖形介面。

**模組分層：**
- **核心層**：掃描器、字典管理、翻譯引擎、XML 寫回
- **服務層**：維基百科 API、Google 搜尋、翻譯 API
- **UI 層**：主視窗、設定對話框、進度元件、日誌面板
- **工具層**：日誌管理、檔案操作、XML 解析、檔名清理

**技術選型：** Python 3.11+、PyQt6、PyInstaller、Google Translate / DeepL

**非同步處理：** 翻譯過程在背景執行，UI 可即時顯示進度，使用者可隨時取消，已完成的翻譯會即時存檔。

---

## 系統需求

- **作業系統**：Windows 10 / 11
- **如使用 WSL**：Windows 10 1903 以上版本

---

## 版本更新紀錄

| 版本 | 日期 | 說明 |
|------|------|------|
| 1.0 | 2025-11-27 | 初始版本 |
| 1.1 | 2026-01-25 | ✨ 新增 Gemini AI 智能翻譯<br>⚡ 智能平台排序（遊戲少的優先）<br>🔍 空白描述自動搜尋<br>⚡ 效能優化：平行處理與降低延遲<br>📦 優化打包流程 |
| 1.2 | 2026-01-25 | 🚀 **架構優化**<br>💾 全局快取系統（SQLite 持久化）<br>🌐 HTTP 連接池優化<br>⚡ 重複翻譯速度提升 90%+<br>📊 快取統計功能 |
| 1.3 | 2026-01-26 | 🔧 **專案重構**<br>📁 檔案結構整理<br>🤖 GitHub Actions 自動發布<br>📦 自動版號遞增<br>📚 文件更新 |

---

## 進階功能說明

### 🤖 Gemini AI 智能翻譯

支援使用 Google Gemini AI 生成更準確的遊戲描述：

1. 前往 [Google AI Studio](https://aistudio.google.com/apikey) 取得免費 API Key
2. 在程式設定中填入 API Key
3. 翻譯時會自動使用 AI 生成描述

### ⚡ 效能優化功能

- **智能平台排序**：自動按遊戲數量從少到多處理，快速看到成果
- **平行處理**：支援多執行緒翻譯，預設 5 個執行緒
- **降低延遲**：API 請求間隔優化至 200ms
- **批次處理**：每批處理 50 個遊戲，平衡速度與記憶體
- **全局快取**：SQLite 持久化快取，重複翻譯速度提升 90%+
- **HTTP 連接池**：連接重用，減少 TCP 握手開銷

詳細說明請參考 [docs/PERFORMANCE_OPTIMIZATION.md](docs/PERFORMANCE_OPTIMIZATION.md)

### 💾 快取系統

程式使用 SQLite 資料庫持久化快取所有翻譯結果：

- **自動快取**：所有 API 查詢結果自動快取
- **持久保存**：程式重啟後快取仍然有效
- **智能過期**：30 天未使用自動清理
- **命中統計**：追蹤快取效能

**快取位置**：程式目錄下的 `config\cache\`

**效能提升**：
- 首次翻譯：正常速度，建立快取
- 重複翻譯：速度提升 90%+
- 部分重複：速度提升 30-70%

詳細說明請參考 [docs/OPTIMIZATION_COMPLETED.md](docs/OPTIMIZATION_COMPLETED.md)

### 🔍 空白描述自動搜尋

當遊戲描述為空時，程式會自動：

1. 使用已翻譯的遊戲名稱搜尋維基百科
2. 如果有設定 Gemini API，使用 AI 生成描述
3. 找不到就保持空白

詳細說明請參考 [docs/EMPTY_DESC_AUTO_SEARCH.md](docs/EMPTY_DESC_AUTO_SEARCH.md)

---

## 開發者資訊

### 專案結構

```
batocera-translator/
├── main.py                 # 程式入口
├── requirements.txt        # Python 依賴
├── BatoceraTranslator.spec # PyInstaller 配置
│
├── src/                    # 原始碼
│   ├── core/              # 核心邏輯 (掃描、字典、翻譯、寫回)
│   ├── services/          # 服務層 (API 整合)
│   ├── ui/                # 使用者介面 (PyQt6)
│   └── utils/             # 工具函式
│
├── tests/                  # 測試檔案
├── docs/                   # 技術文件
├── scripts/                # 工具腳本
├── assets/                 # 資源檔案
├── language_packs/         # 內建語系包
└── gamelists_local/        # 本地遊戲列表暫存
```

### 自動發布流程

本專案使用 GitHub Actions 自動發布：

1. **觸發條件**：push 到 main/master 分支
2. **版號遞增**：自動從上一個 tag 遞增 patch 版本
3. **Commit 格式**：需要符合以下格式才會觸發發布
   - `feat: 新功能描述` - 新功能
   - `fix: 修復描述` - 錯誤修復
   - `[release] 任何訊息` - 強制發布
   - `release: 發布描述` - 發布版本

### 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行程式
python main.py

# 執行測試
pytest tests/

# 打包執行檔
pip install pyinstaller
pyinstaller BatoceraTranslator.spec
```

---

## 技術文件

更多技術細節請參考 `docs/` 資料夾：

- [API_REFERENCE.md](docs/API_REFERENCE.md) - 翻譯 API 參考文件
- [CONTRIBUTING.md](docs/CONTRIBUTING.md) - 語系包貢獻指南
- [PERFORMANCE_OPTIMIZATION.md](docs/PERFORMANCE_OPTIMIZATION.md) - 效能優化說明
- [SMART_PLATFORM_SORTING.md](docs/SMART_PLATFORM_SORTING.md) - 智能平台排序功能
- [EMPTY_DESC_AUTO_SEARCH.md](docs/EMPTY_DESC_AUTO_SEARCH.md) - 空白描述自動搜尋
- [HOW_TO_ENABLE_OPTIMIZATION.md](docs/HOW_TO_ENABLE_OPTIMIZATION.md) - 優化設定指南

---

## 授權條款

本專案採用 MIT License 授權，歡迎自由使用與改進。

---

## 聯絡與回饋

- 🐛 回報問題：請到 [GitHub Issues](../../issues) 開 Issue
- 💬 討論交流：歡迎在 Issues 中討論
- 🤝 貢獻翻譯：歡迎提交 Pull Request
- 📦 下載最新版：[Releases](../../releases/latest)

---

<p align="center">
  <strong>讓復古遊戲更親切，讓回憶更美好！</strong>
</p>