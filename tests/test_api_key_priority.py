#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 API Key 優先順序邏輯
"""
from src.utils.settings import AppSettings
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_api_key_priority():
    """測試 API Key 優先順序"""
    print("=" * 60)
    print("測試 API Key 優先順序")
    print("=" * 60)

    # 先清除環境變數（確保測試乾淨）
    original_env = os.environ.get('GEMINI_API_KEY')

    # =====================================================
    # 測試 1: UI 設定有值，環境變數也有值 → 應使用 UI 設定
    # =====================================================
    print("\n【測試 1】UI 設定有值，環境變數也有值")
    os.environ['GEMINI_API_KEY'] = 'ENV_KEY_12345'

    settings = AppSettings(gemini_api_key='UI_KEY_ABCDE')
    result = settings.get_gemini_api_key()

    print(f"   UI 設定值:    'UI_KEY_ABCDE'")
    print(f"   環境變數值:   'ENV_KEY_12345'")
    print(f"   實際取得值:   '{result}'")

    if result == 'UI_KEY_ABCDE':
        print("   ✓ 正確！優先使用 UI 設定")
    else:
        print("   ✗ 錯誤！應該使用 UI 設定")

    # =====================================================
    # 測試 2: UI 設定為空，環境變數有值 → 應使用環境變數
    # =====================================================
    print("\n【測試 2】UI 設定為空，環境變數有值")
    os.environ['GEMINI_API_KEY'] = 'ENV_KEY_12345'

    settings = AppSettings(gemini_api_key='')  # UI 設定為空
    result = settings.get_gemini_api_key()

    print(f"   UI 設定值:    '' (空)")
    print(f"   環境變數值:   'ENV_KEY_12345'")
    print(f"   實際取得值:   '{result}'")

    if result == 'ENV_KEY_12345':
        print("   ✓ 正確！備用使用環境變數")
    else:
        print("   ✗ 錯誤！應該使用環境變數")

    # =====================================================
    # 測試 3: 兩者都為空 → 應返回空字串
    # =====================================================
    print("\n【測試 3】UI 設定為空，環境變數也為空")
    if 'GEMINI_API_KEY' in os.environ:
        del os.environ['GEMINI_API_KEY']

    settings = AppSettings(gemini_api_key='')
    result = settings.get_gemini_api_key()

    print(f"   UI 設定值:    '' (空)")
    print(f"   環境變數值:   (未設定)")
    print(f"   實際取得值:   '{result}'")

    if result == '':
        print("   ✓ 正確！返回空字串")
    else:
        print("   ✗ 錯誤！應該返回空字串")

    # =====================================================
    # 測試 4: 實際從 .env 檔案讀取
    # =====================================================
    print("\n【測試 4】從 .env 檔案讀取")

    # 重新載入 .env
    try:
        from dotenv import load_dotenv
        from pathlib import Path
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(env_path, override=True)
            env_key = os.environ.get('GEMINI_API_KEY', '')
            print(f"   .env 檔案存在")
            print(f"   GEMINI_API_KEY: '{env_key[:20]}...' (僅顯示前 20 字)")

            # 測試 UI 為空時是否會讀取 .env
            settings = AppSettings(gemini_api_key='')
            result = settings.get_gemini_api_key()

            if result == env_key:
                print("   ✓ 正確！成功從 .env 讀取")
            else:
                print(f"   ✗ 錯誤！預期 '{env_key[:10]}...' 但得到 '{result[:10]}...'")
        else:
            print("   .env 檔案不存在，跳過此測試")
    except ImportError:
        print("   python-dotenv 未安裝，跳過此測試")

    # 恢復原本的環境變數
    if original_env:
        os.environ['GEMINI_API_KEY'] = original_env
    elif 'GEMINI_API_KEY' in os.environ:
        del os.environ['GEMINI_API_KEY']

    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)


if __name__ == '__main__':
    test_api_key_priority()
