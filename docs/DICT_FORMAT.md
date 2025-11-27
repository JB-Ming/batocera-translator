# 語系包格式說明

## 簡介

語系包是 JSON 格式的字典檔，用於儲存遊戲名稱和描述的翻譯對照。

## 檔案命名規則

- 遊戲名稱翻譯：`translations_{平台}.json`
- 描述翻譯：`descriptions_{平台}.json`

## 格式範例

### translations_nes.json（遊戲名稱）

```json
{
  "Super Mario Bros": "超級瑪利歐兄弟",
  "The Legend of Zelda": "薩爾達傳說",
  "Contra": "魂斗羅",
  "Mega Man": "洛克人"
}
```

### descriptions_nes.json（遊戲描述）

```json
{
  "A classic platformer game": "經典的平台跳躍遊戲",
  "Run and gun action game": "橫向卷軸射擊遊戲",
  "Adventure game with puzzles": "帶有解謎元素的冒險遊戲"
}
```

## 平台代碼列表

| 代碼 | 平台名稱 |
|------|---------|
| nes | FC 紅白機 |
| snes | 超級任天堂 |
| megadrive | MD Mega Drive |
| gba | GBA Game Boy Advance |
| ps1 | PS1 PlayStation |
| arcade | 街機 |

完整列表請參考 `translator.py` 中的 `PLATFORM_NAMES`。

## 貢獻語系包

1. 編輯或建立對應平台的 JSON 檔案
2. 確保 JSON 格式正確（可用線上工具驗證）
3. 使用繁體中文翻譯
4. 提交 Pull Request 到 GitHub

## 注意事項

- JSON 檔案必須使用 UTF-8 編碼
- KEY（英文名稱）必須是清理過的名稱（無區域標記）
- VALUE（中文翻譯）應使用台灣慣用譯名
- 避免使用特殊字元或 emoji
