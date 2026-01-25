# 效能優化設定指南

## ⚠️ 重要：設定檔位置

設定檔儲存在：
```
Windows: %LOCALAPPDATA%\BatoceraTranslator\settings.json
```

**修改程式碼的預設值不會影響已存在的設定檔！**

## 🎯 如何啟用優化設定

### 方法 1：透過 UI 設定（推薦）✅

1. 啟動程式
2. 點擊右上角「設定」按鈕
3. 找到「效能設定」區塊
4. 調整以下參數：

```
請求間隔：500 ms（預設可能是 2000 ms）
翻譯執行緒數：3（預設可能是 1）
批次處理大小：20（預設可能是 50）
```

5. 點擊「確定」儲存
6. 重新執行翻譯

### 方法 2：手動編輯設定檔

1. 按 `Win + R`，輸入 `%LOCALAPPDATA%\BatoceraTranslator`
2. 用記事本開啟 `settings.json`
3. 修改以下項目：

```json
{
  "request_delay": 500,
  "max_workers": 3,
  "batch_size": 20
}
```

4. 儲存檔案
5. 重新啟動程式

### 方法 3：刪除設定檔（使用新預設值）

1. 關閉程式
2. 刪除 `%LOCALAPPDATA%\BatoceraTranslator\settings.json`
3. 重新啟動程式（會使用新的預設值）

## 📊 驗證設定是否生效

查看日誌（程式底部），應該會看到：

```
[INFO] 使用 3 個執行緒進行翻譯
```

如果看到這行，表示多執行緒已啟用！

## 🔍 當前問題診斷

根據您的截圖，目前看到的是：
- 使用舊的 Stage3 流程
- **沒有看到「使用 N 個執行緒」的訊息**
- 速度仍然是 ~10 秒/遊戲

這表示：**設定檔仍在使用舊值（單執行緒 + 2000ms 延遲）**

## 💡 快速解決方案

**最簡單的方法**：

1. 關閉程式
2. 執行 PowerShell 命令：
```powershell
Remove-Item "$env:LOCALAPPDATA\BatoceraTranslator\settings.json"
```
3. 重新啟動程式
4. 再次執行翻譯

程式會使用新的預設值（3 執行緒 + 500ms 延遲）

## 📈 預期效果

設定生效後，應該會看到：

**優化前（當前）**:
```
平台: 19/100  速度: ~10 秒/遊戲
無多執行緒訊息
```

**優化後**:
```
[INFO] 使用 3 個執行緒進行翻譯
平台: 19/100  速度: ~2-4 秒/遊戲
```

**加速比**: 3-5 倍

## 🎛️ 進階調整

如果優化後仍然慢，可以進一步調整：

### 激進設定（最快但可能被限制）
```json
{
  "request_delay": 300,
  "max_workers": 4,
  "batch_size": 15
}
```

### 保守設定（穩定但較慢）
```json
{
  "request_delay": 1000,
  "max_workers": 2,
  "batch_size": 30
}
```

## ❓ 故障排除

### Q: 修改後仍然沒有變快？
A: 檢查日誌是否顯示「使用 N 個執行緒」

### Q: 出現很多錯誤？
A: 提高 `request_delay` 到 1000-2000

### Q: 程式閃退？
A: 降低 `max_workers` 到 2

## 📞 確認步驟

請執行以下步驟並回報結果：

1. 查看當前設定檔內容：
```powershell
Get-Content "$env:LOCALAPPDATA\BatoceraTranslator\settings.json" | ConvertFrom-Json | Select request_delay, max_workers, batch_size
```

2. 如果值不是 500, 3, 20，就是這個原因！

3. 刪除設定檔重新開始：
```powershell
Remove-Item "$env:LOCALAPPDATA\BatoceraTranslator\settings.json"
```

4. 重新執行程式並翻譯

5. 查看日誌是否出現「使用 3 個執行緒進行翻譯」
