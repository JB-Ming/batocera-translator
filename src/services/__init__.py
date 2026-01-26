# 服務模組
"""
外部服務整合模組：
- wikipedia: 維基百科 API
- search: 網路搜尋
- translate: 翻譯 API
- gemini: Gemini AI API
- gemini_batch: Gemini AI 批次翻譯 API
"""

from .wikipedia import WikipediaService
from .search import SearchService
from .translate import TranslateService
from .gemini import GeminiService
from .gemini_batch import GeminiBatchService, BatchTranslationResult

__all__ = [
    'WikipediaService',
    'SearchService',
    'TranslateService',
    'GeminiService',
    'GeminiBatchService',
    'BatchTranslationResult'
]
