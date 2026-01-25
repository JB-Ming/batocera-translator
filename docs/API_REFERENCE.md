# 翻譯 API 參考文件

本文件說明 Batocera Gamelist Translator 使用的翻譯 API。

---

## 翻譯流程

程式會依照以下優先順序查找遊戲的中文譯名：

```
1. 維基百科 API → 2. DuckDuckGo 搜尋 → 3. Google 翻譯 → 4. 保留原文
```

- **遊戲名稱**：依序嘗試 1 → 2 → 3 → 4
- **遊戲描述**：直接使用 3（翻譯 API）

---

## API 詳細說明

### 1. 維基百科 API（優先使用）

| 項目 | 內容 |
|------|------|
| **端點** | `https://zh.wikipedia.org/w/api.php` |
| **用途** | 搜尋遊戲的正式中文譯名 |
| **費用** | 免費 |
| **速率限制** | 每秒 1 次請求（內建延遲） |

#### 使用方式

搜尋遊戲名稱：
```
GET https://zh.wikipedia.org/w/api.php
?action=query
&format=json
&list=search
&srsearch={遊戲名稱} video game
&srlimit=3
&variant=zh-tw
```

#### 優點

- 取得官方/常用譯名（如「超級瑪利歐兄弟」「薩爾達傳說」）
- 可同時取得遊戲介紹作為描述翻譯
- 使用 `variant=zh-tw` 確保返回繁體中文

#### 對應程式碼

- 檔案：`src/services/wikipedia.py`
- 類別：`WikipediaService`

---

### 2. DuckDuckGo Instant Answer API

| 項目 | 內容 |
|------|------|
| **端點** | `https://api.duckduckgo.com/` |
| **用途** | 當維基百科找不到時，透過網路搜尋取得譯名 |
| **費用** | 免費 |
| **速率限制** | 每秒 0.5 次請求（內建延遲） |

#### 使用方式

```
GET https://api.duckduckgo.com/
?q={遊戲名稱} 遊戲 中文
&format=json
&no_redirect=1
&no_html=1
```

#### 優點

- 可搜尋到維基百科沒有收錄的遊戲
- 支援從巴哈姆特等遊戲資料庫取得譯名

#### 對應程式碼

- 檔案：`src/services/search.py`
- 類別：`SearchService`

---

### 3. Google 翻譯 API（googletrans）

| 項目 | 內容 |
|------|------|
| **套件** | `googletrans==4.0.0-rc1` |
| **端點** | Google Translate 網頁版（非官方 API） |
| **用途** | 直接翻譯遊戲名稱或描述 |
| **費用** | 免費 |
| **速率限制** | 每秒 1 次請求（內建延遲） |

#### 使用方式

```python
from googletrans import Translator
translator = Translator()
result = translator.translate("Super Mario Bros", dest='zh-tw')
print(result.text)  # 超級馬里奧兄弟
```

#### 注意事項

⚠️ **此服務不穩定**：
- 使用非官方 API，可能隨時被 Google 封鎖
- 大量請求可能被限制 IP
- 翻譯品質不如維基百科的官方譯名

#### 對應程式碼

- 檔案：`src/services/translate.py`
- 類別：`GoogleTransService`

---

### 4. DeepL API（可選）

| 項目 | 內容 |
|------|------|
| **端點** | `https://api-free.deepl.com/v2/translate` |
| **用途** | 高品質翻譯（需 API Key） |
| **費用** | 免費額度：每月 50 萬字元 |
| **申請網址** | https://www.deepl.com/pro-api |

#### 使用方式

```
POST https://api-free.deepl.com/v2/translate
Content-Type: application/x-www-form-urlencoded

auth_key={API_KEY}
&text={要翻譯的文字}
&target_lang=ZH
```

#### 設定方式

在程式的「設定」對話框中：
1. 選擇翻譯 API：DeepL
2. 輸入 API Key

#### 優點

- 翻譯品質較高
- 服務穩定

#### 對應程式碼

- 檔案：`src/services/translate.py`
- 類別：`DeepLService`

---

## 保留原文判定

以下情況會保留英文原文，不進行翻譯：

| 情況 | 範例 |
|------|------|
| 運動遊戲年份系列 | FIFA 2024, NBA 2K23, NFL 24 |
| 經典保留原名的遊戲 | F-Zero, R-Type, G-Darius |
| 翻譯結果與原文相同 | （維基百科標題仍為英文） |

對應程式碼：`src/core/translator.py` 的 `KEEP_ORIGINAL_PATTERNS`

---

## 翻譯來源標記

字典檔中 `name_source` 和 `desc_source` 欄位記錄翻譯來源：

| 標記值 | 說明 |
|--------|------|
| `wiki` | 維基百科 API |
| `search` | 網路搜尋（DuckDuckGo） |
| `api` | 翻譯 API（Google/DeepL） |
| `keep` | 保留原文（符合保留規則） |
| `manual` | 手動填入 |
| `pack` | 語系包匯入 |

---

## 程式碼架構

```
src/
├── core/
│   └── translator.py      # 翻譯引擎（整合所有 API）
└── services/
    ├── wikipedia.py       # 維基百科 API 封裝
    ├── search.py          # DuckDuckGo 搜尋封裝
    └── translate.py       # Google/DeepL 翻譯 API 封裝
```

---

## 費用摘要

| API | 費用 |
|-----|------|
| 維基百科 | 免費 |
| DuckDuckGo | 免費 |
| Google 翻譯 (googletrans) | 免費（不穩定） |
| DeepL | 免費額度 50 萬字/月 |

---

## 延伸閱讀

- [MediaWiki API 文件](https://www.mediawiki.org/wiki/API:Main_page)
- [DuckDuckGo Instant Answer API](https://duckduckgo.com/api)
- [DeepL API 文件](https://www.deepl.com/docs-api)
