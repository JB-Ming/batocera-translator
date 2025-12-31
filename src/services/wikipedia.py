# 維基百科 API 服務
"""
封裝維基百科 API，用於搜尋遊戲名稱的正式譯名。
"""
import re
import time
import requests
from typing import Optional, Dict, Any
from urllib.parse import quote


class WikipediaService:
    """
    維基百科 API 服務
    
    功能：
    - 搜尋遊戲名稱的維基百科頁面
    - 取得頁面標題（通常是正式譯名）
    - 取得頁面摘要（遊戲描述）
    """
    
    # 語系對應的維基百科網域
    WIKI_DOMAINS = {
        'zh-TW': 'zh.wikipedia.org',
        'zh-CN': 'zh.wikipedia.org',
        'ja': 'ja.wikipedia.org',
        'ko': 'ko.wikipedia.org',
        'en': 'en.wikipedia.org',
    }
    
    # 語系對應的維基百科變體
    WIKI_VARIANTS = {
        'zh-TW': 'zh-tw',
        'zh-CN': 'zh-cn',
    }
    
    def __init__(self, request_delay: float = 1.0):
        """
        初始化維基百科服務
        
        Args:
            request_delay: 請求間隔時間（秒），避免被封鎖
        """
        self.request_delay = request_delay
        self._last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BatoceraTranslator/1.0 (https://github.com/example/batocera-translator)'
        })
    
    def _rate_limit(self) -> None:
        """速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()
    
    def _get_api_url(self, language: str) -> str:
        """取得 API URL"""
        domain = self.WIKI_DOMAINS.get(language, 'en.wikipedia.org')
        return f"https://{domain}/w/api.php"
    
    def search(self, query: str, language: str = 'zh-TW') -> Optional[str]:
        """
        搜尋遊戲名稱的維基百科譯名
        
        Args:
            query: 搜尋關鍵字（通常是英文遊戲名稱）
            language: 目標語系
            
        Returns:
            找到的譯名，找不到返回 None
        """
        self._rate_limit()
        
        api_url = self._get_api_url(language)
        
        # 搜尋 API 參數
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': f'{query} video game',
            'srlimit': 3,
        }
        
        # 加入語系變體
        variant = self.WIKI_VARIANTS.get(language)
        if variant:
            params['variant'] = variant
        
        try:
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 取得搜尋結果
            search_results = data.get('query', {}).get('search', [])
            if not search_results:
                return None
            
            # 取得第一個結果的標題
            title = search_results[0].get('title', '')
            
            # 過濾非遊戲結果
            if self._is_game_page(title, query):
                return title
            
            return None
            
        except requests.RequestException:
            return None
    
    def get_page_info(self, title: str, language: str = 'zh-TW') -> Optional[Dict[str, str]]:
        """
        取得頁面資訊
        
        Args:
            title: 頁面標題
            language: 語系
            
        Returns:
            包含 title 和 extract 的字典
        """
        self._rate_limit()
        
        api_url = self._get_api_url(language)
        
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'exsectionformat': 'plain',
        }
        
        variant = self.WIKI_VARIANTS.get(language)
        if variant:
            params['variant'] = variant
        
        try:
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page in pages.items():
                if page_id == '-1':
                    return None
                return {
                    'title': page.get('title', ''),
                    'extract': page.get('extract', '')
                }
            
            return None
            
        except requests.RequestException:
            return None
    
    def get_description(self, query: str, language: str = 'zh-TW') -> Optional[str]:
        """
        取得遊戲描述
        
        Args:
            query: 搜尋關鍵字
            language: 語系
            
        Returns:
            遊戲描述文字
        """
        title = self.search(query, language)
        if not title:
            return None
            
        page_info = self.get_page_info(title, language)
        if page_info:
            return page_info.get('extract', '')
        
        return None
    
    def _is_game_page(self, title: str, query: str) -> bool:
        """
        判斷是否為遊戲頁面
        
        簡單的判斷邏輯，避免選到同名的電影、書籍等
        """
        # 排除明顯非遊戲的頁面
        exclude_patterns = [
            r'電影',
            r'電視',
            r'動畫',
            r'漫畫',
            r'小說',
            r'專輯',
            r'歌曲',
            r'列表',           # 排除列表頁面
            r'游戏列表',       # 排除遊戲列表頁面
            r'遊戲列表',       # 繁體
            r'List of',        # 英文列表
            r'索引',
            r'年表',
            r'人物',
            r'角色',
            r'配音',
            r'Category',
            r'Template',
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return False
        
        # 檢查標題是否與查詢有關聯（至少包含查詢的一部分）
        query_words = query.lower().split()
        title_lower = title.lower()
        
        # 如果查詢詞完全不在標題中，可能是錯誤的結果
        has_match = False
        for word in query_words:
            if len(word) > 2 and word in title_lower:
                has_match = True
                break
        
        # 如果沒有匹配且標題很不相關，返回 False
        if not has_match and len(query) > 5:
            # 計算相似度（簡單方法：共同字母）
            query_set = set(query.lower().replace(' ', ''))
            title_set = set(title_lower.replace(' ', ''))
            common = len(query_set & title_set)
            similarity = common / max(len(query_set), 1)
            
            if similarity < 0.3:  # 相似度太低
                return False
        
        return True

