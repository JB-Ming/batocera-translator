# Gemini AI 翻譯服務
"""
使用 Google Gemini API 進行遊戲名稱翻譯。
提供比維基百科更精準的翻譯結果。
"""
import time
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


class GeminiService:
    """
    Gemini AI 翻譯服務

    功能：
    - 使用 Gemini Pro 模型翻譯遊戲名稱
    - 支援多語系翻譯
    - 帶有速率限制
    """

    # 語系名稱對照
    LANGUAGE_NAMES = {
        'zh-TW': '繁體中文',
        'zh-CN': '簡體中文',
        'ja': '日文',
        'ko': '韓文',
        'en': '英文',
    }

    def __init__(self, api_key: str, request_delay: float = 1.0):
        """
        初始化 Gemini 服務

        Args:
            api_key: Google AI API Key
            request_delay: 請求間隔時間（秒），避免超過速率限制
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "請安裝 google-generativeai: pip install google-generativeai")

        from ..utils.cache import get_global_cache

        self.api_key = api_key
        self.request_delay = request_delay
        self._last_request_time = 0
        self._model = None
        self._initialized = False
        # 全局快取
        self.cache = get_global_cache()

    def _ensure_initialized(self) -> bool:
        """確保 API 已初始化"""
        if self._initialized:
            return True

        try:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel('gemini-2.0-flash')
            self._initialized = True
            return True
        except Exception as e:
            print(f"Gemini 初始化失敗: {e}")
            return False

    def _rate_limit(self) -> None:
        """速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()

    def translate_game_name(self, game_name: str, language: str = 'zh-TW') -> Optional[str]:
        """
        翻譯遊戲名稱

        Args:
            game_name: 英文遊戲名稱
            language: 目標語系

        Returns:
            翻譯後的遊戲名稱，失敗返回 None
        """
        # 檢查快取
        cached = self.cache.get('gemini', game_name, language)
        if cached:
            return cached

        if not self._ensure_initialized():
            return None

        self._rate_limit()

        lang_name = self.LANGUAGE_NAMES.get(language, '中文')

        prompt = f"""你是遊戲翻譯專家。請提供遊戲《{game_name}》的官方{lang_name}名稱。

    規則：
    1. 只回答遊戲的官方{lang_name}譯名
    2. 如果有多個官方譯名，回答最常用的那個
    3. 如果沒有官方譯名，提供最廣為接受的{lang_name}翻譯
    4. 只回答名稱，不要加任何解釋或標點符號
    5. 如果完全不知道這款遊戲，請保留空白，不要填任何字元，不要填 UNKNOWN 或亂填。

    遊戲名稱：{game_name}
    {lang_name}名稱："""

        try:
            response = self._model.generate_content(prompt)
            result = response.text.strip()

            # 過濾無效回應
            if not result or result == 'UNKNOWN' or len(result) > 100:
                return None

            # 移除可能的引號
            result = result.strip('"\'「」『』')

            # 檢測 AI 的「說明性」無效回應
            # 這些是 AI 找不到翻譯時給出的解釋性文字，不是有效的翻譯結果
            invalid_patterns = [
                '沒有資料',
                '沒有官方',
                '無法找到',
                '找不到',
                '無官方譯名',
                '沒有繁體中文譯名',
                '沒有中文譯名',
                '無繁體中文',
                '無中文譯名',
                '不確定',
                '無法確定',
                '未知',
                '無譯名',
                '暫無',
                '目前沒有',
                '尚無',
                '此遊戲',
                '此合輯',
                '該遊戲',
                '該合輯',
                '抱歉',
                '對不起',
            ]

            for pattern in invalid_patterns:
                if pattern in result:
                    return None

            # 寫入快取
            if result:
                self.cache.set('gemini', game_name, language, result)

            return result

        except Exception as e:
            print(f"Gemini 翻譯失敗 ({game_name}): {e}")
            return None

    def translate_description(self, description: str, language: str = 'zh-TW') -> Optional[str]:
        """
        翻譯遊戲描述

        Args:
            description: 英文描述
            language: 目標語系

        Returns:
            翻譯後的描述，失敗返回 None
        """
        # 檢查快取
        cached = self.cache.get(
            'gemini_desc', description[:100], language)  # 用前100字當key
        if cached:
            return cached

        if not self._ensure_initialized():
            return None

        self._rate_limit()

        lang_name = self.LANGUAGE_NAMES.get(language, '中文')

        # 限制描述長度避免 token 過多
        if len(description) > 500:
            description = description[:500] + '...'

        prompt = f"""請將以下遊戲描述翻譯成{lang_name}，保持原意並使用流暢的{lang_name}表達：

{description}

{lang_name}翻譯："""

        try:
            response = self._model.generate_content(prompt)
            result = response.text.strip()

            if not result or len(result) < 5:
                return None

            # 寫入快取
            if result:
                self.cache.set(
                    'gemini_desc', description[:100], language, result)

            return result

        except Exception as e:
            print(f"Gemini 描述翻譯失敗: {e}")
            return None

    @staticmethod
    def is_available() -> bool:
        """檢查 Gemini 是否可用"""
        return GEMINI_AVAILABLE

    def test_connection(self) -> tuple[bool, str]:
        """
        測試 API 連線

        Returns:
            (成功, 訊息)
        """
        if not GEMINI_AVAILABLE:
            return False, "請先安裝 google-generativeai 套件"

        if not self.api_key:
            return False, "API Key 未設定"

        try:
            if not self._ensure_initialized():
                return False, "初始化失敗"

            # 測試請求
            response = self._model.generate_content("回答 OK")
            if response.text:
                return True, "連線成功"
            return False, "無回應"

        except Exception as e:
            return False, f"連線失敗: {str(e)}"
