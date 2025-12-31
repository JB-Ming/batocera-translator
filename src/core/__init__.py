# 核心功能模組
"""
核心模組包含：
- scanner: ROM 資料夾掃描
- dictionary: 字典檔管理
- translator: 翻譯引擎
- writer: XML 寫回
"""

from .scanner import Scanner
from .dictionary import DictionaryManager
from .translator import TranslationEngine
from .writer import XmlWriter

__all__ = ['Scanner', 'DictionaryManager', 'TranslationEngine', 'XmlWriter']
