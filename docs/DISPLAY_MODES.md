# 顯示模式說明

## 四種顯示模式

Batocera 翻譯工具提供四種不同的顯示模式，讓您自由選擇遊戲名稱的呈現方式。

---

## 1. 僅中文 (chinese_only)

**說明：** 只顯示中文譯名

**範例：**
```
原始名稱: Super Mario Bros (USA)
翻譯後:   超級瑪利歐兄弟
```

**適用場景：**
- 介面簡潔
- 完全中文化
- 螢幕空間有限

---

## 2. 中文 (英文) - chinese_english

**說明：** 主要顯示中文，英文放在括號內

**範例：**
```
原始名稱: Super Mario Bros (USA)
翻譯後:   超級瑪利歐兄弟 (Super Mario Bros)
```

**適用場景：**
- 優先看中文
- 保留英文以便搜尋
- 兼顧辨識度

---

## 3. 英文 (中文) - english_chinese

**說明：** 主要顯示英文，中文放在括號內

**範例：**
```
原始名稱: Super Mario Bros (USA)
翻譯後:   Super Mario Bros (超級瑪利歐兄弟)
```

**適用場景：**
- 保持原始風格
- 學習中文譯名
- 與國際版本對照

---

## 4. 僅英文 (english_only)

**說明：** 保持原始英文，不進行翻譯

**範例：**
```
原始名稱: Super Mario Bros (USA)
翻譯後:   Super Mario Bros
```

**適用場景：**
- 不需要翻譯
- 只清理區域標記
- 保持原汁原味

---

## 如何選擇？

| 優先需求 | 推薦模式 |
|---------|---------|
| 完全中文化 | 僅中文 |
| 中英對照（主中文） | 中文 (英文) |
| 中英對照（主英文） | 英文 (中文) |
| 保持原樣 | 僅英文 |

---

## 設定方式

### GUI 介面
在「翻譯設定」區域選擇對應的單選按鈕

### 命令列
```bash
python translator.py --roms-path /path/to/roms --mode chinese_only
```

### 程式碼
```python
translator = GamelistTranslator(display_mode="chinese_english")
```

---

## 名稱長度限制

所有模式都支援最大長度限制（預設 100 字元）。超過長度時會自動截斷並加上 "..."。

**範例：**
```python
translator = GamelistTranslator(
    display_mode="chinese_english",
    max_name_length=50  # 限制在 50 字元
)
```
