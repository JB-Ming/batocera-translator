# 工具模組
"""
工具函式模組：
- logger: 日誌管理
- file_utils: 檔案操作
- xml_utils: XML 解析
- name_cleaner: 檔名清理
- cache: 全局快取管理
"""

from .logger import Logger, LogLevel
from .file_utils import ensure_dir, safe_copy, get_file_hash
from .xml_utils import parse_gamelist, GameInfo
from .name_cleaner import clean_game_name, get_game_key
from .cache import GlobalCache, get_global_cache

__all__ = [
    'Logger', 'LogLevel',
    'ensure_dir', 'safe_copy', 'get_file_hash',
    'parse_gamelist', 'GameInfo',
    'clean_game_name',
    'get_game_key',
    'GlobalCache', 'get_global_cache'
]
