# 貢獻指南

感謝您對 Batocera 翻譯工具的關注！我們歡迎各種形式的貢獻。

## 如何貢獻

### 1. 貢獻翻譯（最簡單）

**語系包翻譯：**
- 編輯 `translations/translations_{平台}.json` 檔案
- 加入新的翻譯對照
- 確保 JSON 格式正確
- 提交 Pull Request

**描述翻譯：**
- 編輯 `translations/descriptions_{平台}.json` 檔案
- 加入常見描述的翻譯
- 確保繁體中文翻譯品質

---

### 2. 回報問題

在 GitHub Issues 回報問題時，請包含：

- **問題描述**：清楚說明遇到的問題
- **重現步驟**：如何重現此問題
- **預期結果**：應該發生什麼
- **實際結果**：實際發生什麼
- **環境資訊**：
  - 作業系統版本
  - Python 版本
  - 程式版本

**範例：**
```
### 問題描述
翻譯 NES 平台時程式崩潰

### 重現步驟
1. 開啟 GUI
2. 選擇 roms 目錄：D:\roms
3. 點擊「開始翻譯」
4. 處理到第 5 個遊戲時崩潰

### 預期結果
順利完成所有遊戲的翻譯

### 實際結果
程式崩潰，顯示錯誤訊息...

### 環境
- Windows 11 64-bit
- Python 3.10.5
- 程式版本 1.0
```

---

### 3. 提交程式碼

**開發環境設定：**

```bash
# 1. Fork 並 Clone 專案
git clone https://github.com/你的帳號/batocera-translator.git
cd batocera-translator

# 2. 建立虛擬環境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. 安裝依賴
pip install -r requirements-gui.txt

# 4. 建立新分支
git checkout -b feature/你的功能名稱
```

**程式碼規範：**

- 使用 UTF-8 編碼
- 遵循 PEP 8 風格指南
- 加入適當的註解和文件字串
- 函數需要型別提示（Type Hints）
- 複雜邏輯加入說明

**範例：**
```python
def translate_name(self, game_name: str, platform: str) -> str:
    """
    翻譯遊戲名稱
    
    Args:
        game_name: 遊戲英文名稱
        platform: 平台代碼（如 'nes'）
        
    Returns:
        翻譯後的中文名稱
    """
    # 實作...
```

**提交訊息格式：**

```
類型: 簡短描述（50 字元內）

詳細說明（如果需要）

類型可以是：
- feat: 新功能
- fix: 修正錯誤
- docs: 文件更新
- style: 格式調整（不影響程式碼運作）
- refactor: 重構程式碼
- test: 加入測試
- chore: 雜項（更新依賴等）
```

**範例：**
```
feat: 加入自動偵測平台功能

新增函數 auto_detect_platform() 可以根據資料夾名稱
自動識別遊戲平台，無需手動指定。
```

**Pull Request 流程：**

1. 確保程式碼通過測試
2. 更新相關文件
3. 提交 Pull Request
4. 填寫 PR 說明範本
5. 等待審核

---

### 4. 改善文件

文件同樣重要！歡迎協助：

- 修正錯字
- 改善說明
- 加入更多範例
- 翻譯成其他語言

---

## 語系包貢獻指南

### 建立新平台語系包

```bash
# 1. 建立 JSON 檔案
touch translations/translations_新平台.json
touch translations/descriptions_新平台.json

# 2. 加入翻譯對照
{
  "Game Name 1": "遊戲名稱1",
  "Game Name 2": "遊戲名稱2"
}

# 3. 測試
python translator.py --roms-path test_roms --dry-run
```

### 翻譯品質標準

**好的翻譯：**
- ✅ 使用台灣慣用譯名
- ✅ 避免直譯
- ✅ 簡潔易懂
- ✅ 符合遊戲內容

**避免：**
- ❌ 機器翻譯未經校對
- ❌ 大陸用語（除非該遊戲官方譯名）
- ❌ 過度冗長
- ❌ 不常見的譯名

**範例：**
```json
{
  "Street Fighter II": "快打旋風II",  // ✅ 台灣譯名
  "Street Fighter II": "街頭霸王II",  // ❌ 大陸譯名
  
  "Final Fantasy": "太空戰士",        // ✅ 台灣譯名
  "Final Fantasy": "最終幻想",        // ❌ 直譯
}
```

---

## 測試

**執行測試：**

```bash
# 執行所有測試
python -m unittest discover tests

# 執行特定測試
python -m unittest tests.test_translator
```

**加入新測試：**

在 `tests/` 目錄建立測試檔案：

```python
import unittest
from translator import GamelistTranslator

class TestNewFeature(unittest.TestCase):
    def test_something(self):
        translator = GamelistTranslator()
        result = translator.some_function()
        self.assertEqual(result, expected_value)
```

---

## 社群規範

### 行為準則

- 友善和尊重所有貢獻者
- 接受建設性批評
- 專注於對專案最好的方案
- 展現同理心

### 溝通方式

- 使用繁體中文或英文
- 清楚表達意見
- 保持專業和禮貌
- 避免爭論，尋求共識

---

## 版本發佈

維護者會定期發佈新版本：

1. 更新版本號（`gui.py` 中的 `VERSION`）
2. 更新 CHANGELOG
3. 建立 Git Tag
4. 編譯 .exe 執行檔
5. 發佈到 GitHub Releases

---

## 授權

所有貢獻將採用 MIT License。

提交程式碼即表示您同意：
- 您擁有貢獻內容的版權
- 願意以 MIT License 授權

---

## 聯絡方式

- **GitHub Issues**：回報問題和建議
- **Pull Requests**：提交程式碼
- **Discussions**：一般討論

---

感謝您的貢獻！🎉
