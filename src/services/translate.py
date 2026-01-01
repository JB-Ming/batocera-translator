# 翻譯 API 服務
"""
封裝各種翻譯 API，用於直接翻譯遊戲描述。
"""
import time
import re
from typing import Optional
from abc import ABC, abstractmethod
from enum import Enum


def clean_translation_text(text: Optional[str]) -> Optional[str]:
    """
    清理翻譯結果中的特殊字元
    
    移除或替換 API 返回時可能夾帶的不可見字元，如：
    - ZWSP (Zero-Width Space, U+200B)
    - ZWNJ (Zero-Width Non-Joiner, U+200C)
    - ZWJ (Zero-Width Joiner, U+200D)
    - Word Joiner (U+2060)
    - %ZWSP% 等編碼殘留
    
    Args:
        text: 原始翻譯文字
        
    Returns:
        清理後的文字
    """
    if not text:
        return text
    
    # 移除 %ZWSP% 等編碼殘留（可能是某些 API 的 bug）
    text = re.sub(r'%ZWSP%', '', text, flags=re.IGNORECASE)
    
    # 移除零寬度字元
    zero_width_chars = [
        '\u200b',  # Zero-Width Space
        '\u200c',  # Zero-Width Non-Joiner
        '\u200d',  # Zero-Width Joiner
        '\u2060',  # Word Joiner
        '\ufeff',  # Byte Order Mark
    ]
    for char in zero_width_chars:
        text = text.replace(char, '')
    
    # 清理多餘空格
    text = re.sub(r' +', ' ', text)
    text = text.strip()
    
    return text


class TranslateProvider(Enum):
    """翻譯服務提供者"""
    GOOGLETRANS = "googletrans"   # 免費 Google 翻譯
    GOOGLE_CLOUD = "google_cloud" # Google Cloud Translation API
    DEEPL = "deepl"               # DeepL API
    AZURE = "azure"               # Azure Translator


class BaseTranslateService(ABC):
    """翻譯服務基底類別"""
    
    @abstractmethod
    def translate(self, text: str, target_language: str, 
                  source_language: str = 'auto') -> Optional[str]:
        """翻譯文字"""
        pass


class GoogleTransService(BaseTranslateService):
    """
    免費 Google 翻譯服務（使用 googletrans 庫）
    
    注意：此服務不穩定，可能會被限制
    """
    
    # 語系代碼對應
    LANG_CODES = {
        'zh-TW': 'zh-tw',
        'zh-CN': 'zh-cn',
        'ja': 'ja',
        'ko': 'ko',
        'en': 'en',
    }
    
    def __init__(self, request_delay: float = 1.0):
        """
        初始化服務
        
        Args:
            request_delay: 請求間隔時間
        """
        self.request_delay = request_delay
        self._last_request_time = 0
        self._translator = None
        
    def _get_translator(self):
        """延遲初始化 googletrans"""
        if self._translator is None:
            try:
                from googletrans import Translator
                self._translator = Translator()
            except ImportError:
                raise ImportError("請先安裝 googletrans: pip install googletrans==4.0.0-rc1")
        return self._translator
    
    def _rate_limit(self) -> None:
        """速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()
    
    def translate(self, text: str, target_language: str,
                  source_language: str = 'auto') -> Optional[str]:
        """
        翻譯文字
        
        Args:
            text: 要翻譯的文字
            target_language: 目標語系
            source_language: 來源語系（auto 自動偵測）
            
        Returns:
            翻譯結果
        """
        if not text:
            return None
            
        self._rate_limit()
        
        target = self.LANG_CODES.get(target_language, target_language)
        source = 'auto' if source_language == 'auto' else self.LANG_CODES.get(source_language, source_language)
        
        try:
            translator = self._get_translator()
            result = translator.translate(text, dest=target, src=source)
            return clean_translation_text(result.text)
        except Exception:
            return None


class DeepLService(BaseTranslateService):
    """
    DeepL 翻譯服務
    
    需要 DeepL API Key（有免費額度）
    """
    
    LANG_CODES = {
        'zh-TW': 'ZH',
        'zh-CN': 'ZH',
        'ja': 'JA',
        'ko': 'KO',
        'en': 'EN',
    }
    
    API_URL = 'https://api-free.deepl.com/v2/translate'
    
    def __init__(self, api_key: str, request_delay: float = 0.5):
        """
        初始化 DeepL 服務
        
        Args:
            api_key: DeepL API Key
            request_delay: 請求間隔時間
        """
        self.api_key = api_key
        self.request_delay = request_delay
        self._last_request_time = 0
        
        try:
            import requests
            self.session = requests.Session()
        except ImportError:
            raise ImportError("請先安裝 requests: pip install requests")
    
    def _rate_limit(self) -> None:
        """速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()
    
    def translate(self, text: str, target_language: str,
                  source_language: str = 'auto') -> Optional[str]:
        """
        翻譯文字
        
        Args:
            text: 要翻譯的文字
            target_language: 目標語系
            source_language: 來源語系
            
        Returns:
            翻譯結果
        """
        if not text:
            return None
            
        self._rate_limit()
        
        target = self.LANG_CODES.get(target_language, 'EN')
        
        data = {
            'auth_key': self.api_key,
            'text': text,
            'target_lang': target,
        }
        
        if source_language != 'auto':
            source = self.LANG_CODES.get(source_language, '')
            if source:
                data['source_lang'] = source
        
        try:
            response = self.session.post(self.API_URL, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            translations = result.get('translations', [])
            if translations:
                return clean_translation_text(translations[0].get('text', ''))
            
            return None
            
        except Exception:
            return None


class TranslateService:
    """
    翻譯服務工廠
    
    統一的翻譯服務介面，可切換不同的翻譯提供者
    """
    
    def __init__(self, provider: TranslateProvider = TranslateProvider.GOOGLETRANS,
                 api_key: str = ''):
        """
        初始化翻譯服務
        
        Args:
            provider: 翻譯服務提供者
            api_key: API Key（部分服務需要）
        """
        self.provider = provider
        self.api_key = api_key
        self._service: Optional[BaseTranslateService] = None
        
    def _get_service(self) -> BaseTranslateService:
        """取得翻譯服務實例"""
        if self._service is None:
            if self.provider == TranslateProvider.GOOGLETRANS:
                self._service = GoogleTransService()
            elif self.provider == TranslateProvider.DEEPL:
                if not self.api_key:
                    raise ValueError("DeepL 服務需要 API Key")
                self._service = DeepLService(self.api_key)
            else:
                # 預設使用免費的 googletrans
                self._service = GoogleTransService()
        
        return self._service
    
    def translate(self, text: str, target_language: str,
                  source_language: str = 'auto') -> Optional[str]:
        """
        翻譯文字
        
        Args:
            text: 要翻譯的文字
            target_language: 目標語系
            source_language: 來源語系
            
        Returns:
            翻譯結果
        """
        service = self._get_service()
        return service.translate(text, target_language, source_language)
