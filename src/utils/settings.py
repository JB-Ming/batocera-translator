# 設定檔管理模組
"""
提供設定檔儲存與載入功能。
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field

from .file_utils import get_settings_path


@dataclass
class AppSettings:
    """應用程式設定"""
    # 路徑設定
    last_roms_path: str = ""
    last_language: str = "zh-TW"
    
    # 翻譯設定
    translate_name: bool = True
    translate_desc: bool = True
    skip_translated: bool = True
    include_platform_in_search: bool = False
    use_api_fallback: bool = True
    auto_keep_original: bool = True
    
    # 寫回設定
    write_back: bool = True
    auto_backup: bool = True
    display_format: str = "translated"  # translated, trans_orig, orig_trans, original
    name_strategy: str = "dict"         # skip, dict, xml, overwrite
    desc_strategy: str = "dict"
    
    # 字典設定
    merge_strategy: str = "merge"  # merge, fill_empty, overwrite, skip
    
    # API 設定
    translate_api: str = "googletrans"  # googletrans, google_cloud, deepl, azure
    api_key: str = ""
    request_delay: int = 2000  # ms
    
    # 視窗設定
    window_width: int = 900
    window_height: int = 700
    window_x: int = -1
    window_y: int = -1
    
    # 進階設定
    log_level: str = "INFO"
    max_log_files: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """從字典建立"""
        # 只取存在的欄位
        valid_fields = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
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
                # 設定檔損毀，使用預設值
                self._settings = AppSettings()
        else:
            # 建立預設設定
            self._settings = AppSettings()
        
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
            json.dump(self._settings.to_dict(), f, ensure_ascii=False, indent=2)
    
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
