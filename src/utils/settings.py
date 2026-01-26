# 設定檔管理模組
"""
提供設定檔儲存與載入功能。
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field

from .file_utils import get_settings_path

# 嘗試載入 .env 檔案（僅在開發環境，打包後的執行檔不會載入）
# 這是為了讓開發者可以在本機設定 API Key，而不需要每次都在 UI 輸入
# 打包後的執行檔不會包含 .env，使用者需要在 UI 設定中輸入 API Key
if not getattr(sys, 'frozen', False):
    # 開發模式：嘗試載入 .env
    try:
        from dotenv import load_dotenv
        _project_root = Path(__file__).parent.parent.parent
        _env_path = _project_root / '.env'
        if _env_path.exists():
            load_dotenv(_env_path)
    except ImportError:
        pass  # python-dotenv 未安裝，僅使用系統環境變數


@dataclass
class AppSettings:
    """
    應用程式設定

    設定檔會在以下情況自動建立：
    1. 程式首次啟動時，若設定檔不存在，會自動以預設值建立
    2. 位置: %LOCALAPPDATA%\\BatoceraTranslator\\settings.json

    設定檔會在以下情況自動儲存：
    1. 使用者在設定對話框按「確定」時
    2. 程式關閉時（closeEvent）
    """

    # ==================== 路徑設定 ====================
    last_roms_path: str = ""            # 上次開啟的 ROM 資料夾路徑
    last_language: str = "zh-TW"        # 上次選擇的目標語系

    # ==================== 翻譯設定 ====================
    translate_name: bool = True         # 是否翻譯遊戲名稱
    translate_desc: bool = False        # 是否翻譯遊戲描述（預設關閉，描述翻譯較慢）
    skip_translated: bool = True        # 是否跳過已翻譯的項目
    include_platform_in_search: bool = False  # 搜尋時是否包含平台名稱
    use_api_fallback: bool = True       # 搜尋失敗時是否使用 API 直譯
    auto_keep_original: bool = True     # 是否自動偵測並保留原文（如品牌名）

    # ==================== 寫回設定 ====================
    write_back: bool = True             # 是否將翻譯結果寫回 gamelist.xml
    auto_backup: bool = True            # 寫回前是否自動備份原檔
    # 顯示格式：translated/trans_orig/orig_trans/original
    display_format: str = "translated"
    name_strategy: str = "dict"         # name 處理策略：skip/dict/xml/overwrite
    desc_strategy: str = "dict"         # desc 處理策略：skip/dict/xml/overwrite

    # ==================== 字典設定 ====================
    merge_strategy: str = "merge"       # 字典合併策略：merge/fill_empty/overwrite/skip

    # ==================== API 設定 ====================
    translate_api: str = "googletrans"  # 翻譯 API：googletrans/google_cloud/deepl/azure
    api_key: str = ""                   # 付費翻譯 API 金鑰
    gemini_api_key: str = ""            # Gemini AI API Key（遊戲名稱翻譯用）
    request_delay: int = 500            # API 請求間隔（毫秒），避免被限制可調高至 1000-2000

    # ==================== Gemini 批次翻譯設定 ====================
    use_gemini_batch: bool = False      # 是否啟用 Gemini 批次翻譯模式
    gemini_batch_size: int = 80         # Gemini 每批次翻譯的遊戲數量（建議 50-80）

    # ==================== 視窗設定 ====================
    window_width: int = 900             # 視窗寬度
    window_height: int = 700            # 視窗高度
    window_x: int = -1                  # 視窗 X 座標（-1 表示置中）
    window_y: int = -1                  # 視窗 Y 座標（-1 表示置中）

    # ==================== 效能設定 ====================
    auto_save_interval: int = 10        # 每翻譯 N 個遊戲自動儲存一次進度
    max_workers: int = 3                # 翻譯執行緒數（建議 2-4，過高可能被 API 限制）
    batch_size: int = 20                # 一般批次處理大小（非 Gemini）

    # ==================== 進階設定 ====================
    log_level: str = "INFO"             # 日誌等級：DEBUG/INFO/WARNING/ERROR
    max_log_files: int = 10             # 最多保留的日誌檔案數量

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return asdict(self)

    def get_gemini_api_key(self) -> str:
        """
        取得 Gemini API Key（含優先順序處理）

        優先順序：
        1. UI 設定的值（如果不為空）
        2. 環境變數 GEMINI_API_KEY

        Returns:
            API Key 字串，若無則為空字串
        """
        # 優先使用 UI 設定的值
        if self.gemini_api_key:
            return self.gemini_api_key
        # 備用：環境變數
        return os.environ.get('GEMINI_API_KEY', '')

    def get_api_key(self) -> str:
        """
        取得翻譯 API Key（含優先順序處理）

        優先順序：
        1. UI 設定的值（如果不為空）
        2. 環境變數 GOOGLE_TRANSLATE_API_KEY

        Returns:
            API Key 字串，若無則為空字串
        """
        if self.api_key:
            return self.api_key
        return os.environ.get('GOOGLE_TRANSLATE_API_KEY', '')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """從字典建立"""
        # 只取存在的欄位
        valid_fields = {k: v for k,
                        v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)


class SettingsManager:
    """
    設定檔管理器

    功能：
    - 載入設定檔
    - 儲存設定檔
    - 自動建立預設設定

    設定檔存放於使用者資料目錄（%LOCALAPPDATA%/BatoceraTranslator），
    確保程式更新時不會遺失設定。
    """

    def __init__(self, settings_path: Optional[Path] = None):
        """
        初始化設定管理器

        Args:
            settings_path: 設定檔路徑，None 使用預設的使用者資料目錄
        """
        self.settings_path = settings_path or get_settings_path()
        self._settings: Optional[AppSettings] = None

    def load(self) -> AppSettings:
        """
        載入設定檔

        Returns:
            應用程式設定
        """
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._settings = AppSettings.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                # 設定檔損毀，使用預設值並重新建立
                self._settings = AppSettings()
                self.save()  # 自動建立新的設定檔
        else:
            # 設定檔不存在，建立預設設定並儲存
            self._settings = AppSettings()
            self.save()  # 自動建立設定檔

        return self._settings

    def save(self, settings: Optional[AppSettings] = None) -> None:
        """
        儲存設定檔

        Args:
            settings: 要儲存的設定，None 使用目前載入的設定
        """
        if settings:
            self._settings = settings

        if self._settings is None:
            return

        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(self._settings.to_dict(), f,
                      ensure_ascii=False, indent=2)

    def get(self) -> AppSettings:
        """取得設定"""
        if self._settings is None:
            self.load()
        return self._settings

    def reset(self) -> AppSettings:
        """重置為預設設定"""
        self._settings = AppSettings()
        self.save()
        return self._settings
