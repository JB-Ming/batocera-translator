# API 設定指南

本工具支援多種免費翻譯 API，採用智慧降級策略，確保翻譯不中斷。

## 📋 翻譯策略總覽

### 🎮 遊戲名稱翻譯（台灣慣用譯名）
```
1. 語系包字典查詢 (最快，免費)
   ↓ 找不到
2. Google 搜尋 (抓取維基百科、巴哈姆特等網站譯名)
   ↓ 找不到
3. Groq API (AI 推斷，速度最快) ⭐
   ↓ 失敗/無額度
4. Gemini API (AI 推斷，備援) ⭐
   ↓ 失敗/無額度
5. 保持英文原名 (避免亂翻)
```

### 📝 遊戲描述翻譯（流暢中文）
```
1. 描述字典查詢 (最快，免費)
   ↓ 找不到
2. DeepL API (品質最好) ⭐
   ↓ 失敗/無額度
3. MyMemory API (免費，無需 Key)
   ↓ 失敗
4. googletrans (最後手段)
```

---

## 🔑 API 申請教學

### 1️⃣ Groq API（最推薦）⭐⭐⭐

**用途**：遊戲名稱本地化（AI 推斷台灣慣用譯名）

**免費額度**：
- 每分钟 **30 次請求**（比 Gemini 多 2 倍！）
- 每天 **14,400 次請求**
- **完全免費！**

**申請步驟**：
1. 前往 https://console.groq.com/
2. 點擊 "Sign Up" 註冊帳號（可用 Google 登入）
3. 點擊 "API Keys" 選單
4. 點擊 "Create API Key"
5. 輸入名稱（例如：Batocera Translator）
6. 複製 API Key（格式：`gsk_...`）

**特色**：
- ✅ **速度超快**：Groq 的 LPU 架構比傳統 GPU 快 10 倍以上
- ✅ **免費額度高**：30次/分钟，足夠大多數情況使用
- ✅ **Llama 3.1 70B 模型**：理解遊戲文化，知道台灣慣用譯名
- ✅ **無需信用卡**：只需 Email 即可註冊

**範例回應**：
```
問：Super Mario Bros (FC紅白機)
答：超級瑪利歐兄弟

問：The Legend of Zelda (FC紅白機)
答：薩爾達傳說

問：Street Fighter II (Arcade)
答：快打旋風II
```

**為什麼推薦 Groq？**
- 🚀 速度最快：翻譯遊戲名稱幾乎是瞬間完成
- 🆓 額度充足：30次/分钟，足夠處理大型遊戲庫
- 🎯 品質優異：Llama 3.1 70B 模型的中文能力非常好

---

### 2️⃣ Google Gemini API（備援）⭐

**用途**：遊戲名稱本地化（Groq 失敗時使用）

**免費額度**：
- 每分鐘 15 次請求
- 每天 1,500 次請求
- 完全免費！

**申請步驟**：
1. 前往 https://ai.google.dev/
2. 點擊 "Get API key in Google AI Studio"
3. 登入 Google 帳號
4. 點擊 "Create API Key"
5. 複製 API Key

**特色**：
- ✅ 理解遊戲文化，知道台灣慣用譯名
- ✅ 能區分「瑪利歐」vs「馬里奧」
- ✅ 可以根據平台和年代推斷正確譯名
- ✅ 免費額度高，適合個人使用

**範例回應**：
```
問：Super Mario Bros (FC紅白機)
答：超級瑪利歐兄弟

問：The Legend of Zelda (FC紅白機)
答：薩爾達傳說
```

---

### 3️⃣ DeepL API Free（推薦）⭐

**用途**：遊戲描述翻譯（高品質中文）

**免費額度**：
- 每月 500,000 字元
- 免信用卡註冊

**申請步驟**：
1. 前往 https://www.deepl.com/pro-api
2. 點擊 "Sign up for free"
3. 填寫 Email 和密碼
4. 選擇 "DeepL API Free" 方案
5. 在 Account 頁面取得 API Key

**特色**：
- ✅ 業界公認翻譯品質第一
- ✅ 中文翻譯自然流暢
- ✅ 50 萬字元足夠翻譯數千個遊戲描述
- ✅ 不需信用卡

---

### 4️⃣ MyMemory API（備用）

**用途**：遊戲描述翻譯（DeepL 失敗時使用）

**免費額度**：
- 每天 10,000 字（不需註冊）
- 無需 API Key

**使用方式**：
- 在 GUI 中勾選「MyMemory API」
- 不需填寫 API Key
- 自動作為 DeepL 的備援

**特色**：
- ✅ 完全免費，無需註冊
- ✅ 自動降級，不用管理
- ⚠️ 品質較 DeepL 差，但可接受

---

### 5️⃣ googletrans（最後手段）

**用途**：所有 API 都失敗時的備援

**免費額度**：
- 無限制（但不穩定）

**使用方式**：
- 預設已啟用
- 不需 API Key
- 自動作為最後備援

**特色**：
- ✅ 完全免費
- ⚠️ 經常被 Google 封鎖
- ⚠️ 翻譯品質不穩定

---

## ⚙️ GUI 設定教學

### 步驟 1：填寫 API Key

在「翻譯設定」區域：

1. **Groq API（遊戲名稱，速度最快）** ⭐ **優先使用**
   - ☑ 勾選「Groq API (遊戲名稱，速度最快)」
   - 填寫 Key: `gsk_...` （你的 API Key）

2. **Gemini API（遊戲名稱備援）**
   - ☑ 勾選「Gemini API (遊戲名稱備援)」
   - 填寫 Key: `AIzaSy...` （你的 API Key）
   - 💡 建議填寫，作為 Groq 的備援

3. **DeepL API（描述翻譯）**
   - ☑ 勾選「DeepL API (描述翻譯)」
   - 填寫 Key: `xxxxxxxx-...` （你的 API Key）

4. **MyMemory API（描述翻譯，免費無需 Key）**
   - ☑ 勾選「MyMemory API」
   - 不需填寫 Key

5. **googletrans（備用）**
   - ☑ 勾選「googletrans」
   - 不需填寫 Key

### 步驟 2：啟動翻譯

點擊「開始翻譯」，程式會自動：
1. 先查詢語系包字典（最快）
2. 找不到時用 Google 搜尋
3. 搜尋失敗時用 **Groq AI** 推斷（速度最快）
4. Groq 失敗時用 **Gemini AI** 推斷（備援）
5. 描述翻譯依序嘗試 DeepL → MyMemory → googletrans

---

## 💡 使用建議

### 最佳配置（推薦）⭐

✅ **Groq API** - 遊戲名稱本地化（速度最快，優先使用）  
✅ **Gemini API** - 遊戲名稱備援  
✅ **DeepL API** - 高品質描述翻譯  
✅ **MyMemory API** - 描述翻譯備援  
✅ **googletrans** - 最後備援  

這個配置可以：
- 🎯 確保遊戲名稱是台灣玩家認識的
- 📝 描述翻譯流暢自然
- 🆓 完全免費
- 🔄 多重備援，不怕失敗

### 省錢配置（只用免費 API）

✅ **MyMemory API**（無需註冊）  
✅ **googletrans**（備援）  
❌ Gemini API（不填 Key）  
❌ DeepL API（不填 Key）  

這個配置：
- 完全不需註冊
- 品質較差
- 遊戲名稱只能靠 Google 搜尋

### 高品質配置（有預算）

✅ **Gemini API**（免費）  
✅ **DeepL API Pro**（付費，品質最好）  

---

## 📊 API 使用統計

程式執行完畢後會顯示統計：

```
============================================================
翻譯 API 使用統計
============================================================
gemini          成功:   50 | 失敗:    5 | 成功率: 90.9%
deepl           成功:  100 | 失敗:    0 | 成功率: 100.0%
mymemory        成功:   20 | 失敗:    3 | 成功率: 87.0%
googletrans     成功:    3 | 失敗:    0 | 成功率: 100.0%
============================================================
```

這可以幫你了解：
- 哪個 API 最常用
- 是否需要增加備援
- API 額度是否足夠

---

## ❓ 常見問題

### Q1: 一定要填 API Key 嗎？

不一定。如果不填：
- 遊戲名稱：使用 Google 搜尋（較慢但免費）
- 描述翻譯：使用 MyMemory 或 googletrans

建議至少申請 **Gemini API**（免費且額度高）

### Q2: API 額度用完怎麼辦？

程式會自動降級：
- Gemini 用完 → 保持英文原名
- DeepL 用完 → 使用 MyMemory
- MyMemory 用完 → 使用 googletrans

### Q3: 翻譯速度會變慢嗎？

API 翻譯通常比 Google 搜尋快：
- Google 搜尋：2-3 秒/個（有延遲避免封鎖）
- Gemini API：0.5-1 秒/個
- DeepL API：0.3-0.5 秒/個

### Q4: 可以只用 Gemini 翻譯所有內容嗎？

可以，但不建議：
- Gemini 適合遊戲名稱（需要文化理解）
- DeepL 更適合描述（專業翻譯引擎）

### Q5: 如何知道哪個 API 在作用？

日誌會顯示：
```
[字典] Super Mario Bros → 超級瑪利歐兄弟
[Google搜尋] Contra... 完成
[Gemini] The Legend of Zelda → 薩爾達傳說
[DeepL] 翻譯成功
```

---

## 🔗 相關連結

- **Gemini API 文件**: https://ai.google.dev/docs
- **DeepL API 文件**: https://www.deepl.com/docs-api
- **MyMemory API 文件**: https://mymemory.translated.net/doc/

---

## 📞 支援

如有問題請在 GitHub Issues 回報：
- API 連線問題
- 翻譯品質問題
- 額度用完提示

祝你翻譯順利！🎮
