# 網路搜尋服務
"""
封裝網路搜尋功能，用於查找遊戲譯名。
"""
import re
import time
import requests
from typing import Optional
from urllib.parse import quote

from ..utils.cache import get_global_cache


class SearchService:
    """
    網路搜尋服務

    功能：
    - 使用 DuckDuckGo API 搜尋遊戲譯名
    - 解析搜尋結果提取譯名
    - 全局快取支援
    """

    def __init__(self, request_delay: float = 2.0):
        """
        初始化搜尋服務

        Args:
            request_delay: 請求間隔時間（秒）
        """
        self.request_delay = request_delay
        self._last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BatoceraTranslator/1.0'
        })
        # 連接池優化
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # 全局快取
        self.cache = get_global_cache()

    def _rate_limit(self) -> None:
        """速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()

    def search(self, query: str, language: str = 'zh-TW',
               include_platform: bool = True,
               platform_name: str = '') -> Optional[str]:
        """
        搜尋遊戲譯名

        Args:
            query: 搜尋關鍵字（通常是英文遊戲名稱）
            language: 目標語系
            include_platform: 是否在搜尋關鍵字中包含平台名稱
            platform_name: 平台名稱

        Returns:
            找到的譯名，找不到返回 None
        """
        # 檢查快取
        cache_key = f"{query}|{platform_name if include_platform else ''}"
        cached = self.cache.get('search', cache_key, language)
        if cached:
            return cached

        self._rate_limit()

        # 組合搜尋關鍵字
        search_terms = [query]
        if include_platform and platform_name:
            search_terms.append(platform_name)

        # 加入語系關鍵字
        lang_keywords = {
            'zh-TW': '遊戲 中文',
            'zh-CN': '游戏 中文',
            'ja': 'ゲーム',
            'ko': '게임',
        }
        if language in lang_keywords:
            search_terms.append(lang_keywords[language])

        search_query = ' '.join(search_terms)

        # 使用 DuckDuckGo Instant Answer API
        url = 'https://api.duckduckgo.com/'
        params = {
            'q': search_query,
            'format': 'json',
            'no_redirect': 1,
            'no_html': 1,
        }

        try:
            response = self.session.get(url, params=params, timeout=3)
            response.raise_for_status()
            data = response.json()

            # 嘗試從摘要中提取譯名
            abstract = data.get('Abstract', '')
            heading = data.get('Heading', '')

            if heading:
                # 提取可能的譯名
                translated = self._extract_translated_name(
                    heading, query, language)
                if translated:
                    return translated

            if abstract:
                translated = self._extract_translated_name(
                    abstract, query, language)
                if translated:
                    # 寫入快取
                    self.cache.set('search', cache_key, language, translated)
                    return translated

            # 寫入空結果快取（避免重複查詢）
            self.cache.set('search', cache_key, language, None)
            return None

        except requests.RequestException:
            # 錯誤時也快取空結果
            self.cache.set('search', cache_key, language, None)
            return None

    def _extract_translated_name(self, text: str, original: str,
                                 language: str) -> Optional[str]:
        """
        從文字中提取譯名

        Args:
            text: 要搜尋的文字
            original: 原始名稱
            language: 目標語系

        Returns:
            提取的譯名
        """
        # 根據語系使用不同的正則模式
        patterns = {
            'zh-TW': r'《([^》]+)》|「([^」]+)」',
            'zh-CN': r'《([^》]+)》|「([^」]+)」',
            'ja': r'『([^』]+)』|「([^」]+)」',
            'ko': r'「([^」]+)」|《([^》]+)》',
        }

        pattern = patterns.get(language, r'《([^》]+)》')
        matches = re.findall(pattern, text)

        for match in matches:
            # match 可能是 tuple，取非空的部分
            name = match[0] if match[0] else match[1] if len(match) > 1 else ''
            if name and name.lower() != original.lower():
                return name

        return None

    def search_巴哈姆特(self, query: str) -> Optional[str]:
        """
        搜尋巴哈姆特（台灣遊戲資料庫）

        **注意：** 這是預留的方法，實際實作需要處理網頁爬蟲
        目前僅作為介面定義

        Args:
            query: 搜尋關鍵字

        Returns:
            找到的譯名
        """
        # TODO: 實作巴哈姆特搜尋
        return None
