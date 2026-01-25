#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證設定是否正確載入並使用
"""
import json
from pathlib import Path
import os


def get_settings_path():
    """取得設定檔路徑"""
    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')))
    else:
        base = Path(os.environ.get('XDG_DATA_HOME',
                    os.path.expanduser('~/.local/share')))
    return base / 'BatoceraTranslator' / 'settings.json'


def main():
    settings_path = get_settings_path()

    print("=" * 60)
    print("Batocera Translator 設定驗證工具")
    print("=" * 60)
    print()

    if not settings_path.exists():
        print(f"❌ 設定檔不存在: {settings_path}")
        print("   請先啟動程式以產生設定檔")
        return

    print(f"✓ 設定檔位置: {settings_path}")
    print()

    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        print("📋 效能相關設定:")
        print("-" * 60)

        # 檢查關鍵設定
        checks = [
            ('request_delay', 500, '請求間隔 (ms)', 'API 請求之間的延遲'),
            ('max_workers', 3, '執行緒數', '並行翻譯的執行緒數量'),
            ('batch_size', 20, '批次大小', '每批次處理的遊戲數量'),
            ('auto_save_interval', 10, '自動儲存間隔', '每 N 個遊戲自動儲存'),
        ]

        all_good = True
        for key, recommended, name, desc in checks:
            value = settings.get(key, 'N/A')
            status = '✓' if value == recommended else '⚠️'

            if value != recommended:
                all_good = False

            print(f"{status} {name:20} = {value:6} (建議: {recommended:6}) - {desc}")

        print()
        print("📋 API 設定:")
        print("-" * 60)

        api_checks = [
            ('gemini_api_key', 'Gemini API Key',
             lambda x: '✓ 已設定' if x else '- 未設定（可選）'),
            ('translate_api', '翻譯 API', lambda x: x or 'googletrans'),
        ]

        for key, name, formatter in api_checks:
            value = settings.get(key, '')
            display = formatter(value)
            print(f"  {name:20} : {display}")

        print()
        print("=" * 60)

        if all_good:
            print("✅ 所有效能設定都符合建議值！")
            print()
            print("預期效能提升:")
            print("  • 翻譯速度: 從 ~12秒/遊戲 降到 ~2-4秒/遊戲")
            print("  • 加速比: 3-6 倍")
        else:
            print("⚠️ 部分設定未使用建議值")
            print()
            print("如何更新設定:")
            print("  方法 1: 在程式中點擊「設定」按鈕進行調整")
            print("  方法 2: 直接編輯設定檔")
            print("  方法 3: 刪除設定檔後重新啟動程式（使用新預設值）")

        print("=" * 60)

        # 檢查程式碼是否會使用這些設定
        print()
        print("🔍 驗證程式碼使用情況:")
        print("-" * 60)

        main_window_path = Path(__file__).parent / \
            'src' / 'ui' / 'main_window.py'
        if main_window_path.exists():
            with open(main_window_path, 'r', encoding='utf-8') as f:
                code = f.read()

            usage_checks = [
                ("settings.get('request_delay'", "✓ request_delay 會被讀取"),
                ("settings.get('max_workers'", "✓ max_workers 會被讀取"),
                ("settings.get('batch_size'", "✓ batch_size 會被讀取"),
                ("request_delay=delay_seconds", "✓ request_delay 會傳入服務"),
                ("self.request_delay / 1000", "✓ request_delay 會被轉換並使用"),
            ]

            for check, msg in usage_checks:
                if check in code:
                    print(f"  {msg}")
                else:
                    print(f"  ❌ 找不到: {check}")

        print("=" * 60)

    except json.JSONDecodeError as e:
        print(f"❌ 設定檔格式錯誤: {e}")
    except Exception as e:
        print(f"❌ 錯誤: {e}")


if __name__ == '__main__':
    main()
