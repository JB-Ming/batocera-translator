# 服務模組
"""
外部服務整合模組：
- wikipedia: 維基百科 API
- search: 網路搜尋
- translate: 翻譯 API
- gemini: Gemini AI API
"""

from .wikipedia import WikipediaService
from .search import SearchService
from .translate import TranslateService
from .gemini import GeminiService

__all__ = ['WikipediaService', 'SearchService', 'TranslateService', 'GeminiService']
