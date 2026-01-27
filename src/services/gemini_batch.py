# Gemini AI 批次翻譯服務
"""
使用 Google Gemini API 進行遊戲名稱批次翻譯。
一次翻譯多個遊戲名稱，大幅減少 API 呼叫次數。
"""
import json
import time
import re
import warnings
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

# 抑制 google-generativeai 的棄用警告
warnings.filterwarnings('ignore', message='.*google.generativeai.*')

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


@dataclass
class BatchTranslationResult:
    """批次翻譯結果"""
    translations: Dict[str, str]  # {原名: 翻譯結果}
    failed: List[str]             # 翻譯失敗的遊戲名稱
    total: int                    # 總數
    success_count: int            # 成功數


class GeminiBatchService:
    """
    Gemini AI 批次翻譯服務

    功能：
    - 使用 Gemini Pro 模型批次翻譯遊戲名稱
    - 一次處理多個遊戲，減少 API 呼叫
    - 支援多語系翻譯
    - JSON 格式輸出
    """

    # 語系名稱對照
    LANGUAGE_NAMES = {
        'zh-TW': '繁體中文',
        'zh-CN': '簡體中文',
        'ja': '日文',
        'ko': '韓文',
        'en': '英文',
    }

    # 預設批次大小
    DEFAULT_BATCH_SIZE = 30

    # 最大重試次數
    MAX_RETRIES = 3

    def __init__(self, api_key: str, batch_size: int = DEFAULT_BATCH_SIZE,
                 request_delay: float = 1.0):
        """
        初始化 Gemini 批次服務

        Args:
            api_key: Google AI API Key
            batch_size: 每批次處理的遊戲數量
            request_delay: 請求間隔時間（秒），避免超過速率限制
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "請安裝 google-generativeai: pip install google-generativeai")

        from ..utils.cache import get_global_cache

        self.api_key = api_key
        self.batch_size = batch_size
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
            # 使用 gemini-2.0-flash-lite，比 flash 更便宜
            self._model = genai.GenerativeModel(
                'gemini-2.0-flash-lite',
                generation_config=genai.GenerationConfig(
                    max_output_tokens=8192,
                ),
            )
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

    def _build_prompt(self, game_names: List[str], language: str,
                      platform: str = "") -> str:
        """
        建構批次翻譯的 prompt

        Args:
            game_names: 遊戲名稱列表
            language: 目標語系
            platform: 遊戲平台名稱（如 nes, snes, megadrive 等）

        Returns:
            完整的 prompt
        """
        lang_name = self.LANGUAGE_NAMES.get(language, '中文')

        # 建立編號清單
        numbered_list = "\n".join(
            [f"{i+1}. {name}" for i, name in enumerate(game_names)])

        # 平台提示（如果有提供）
        platform_hint = ""
        if platform:
            platform_hint = f"\n注意：這些遊戲來自「{platform}」平台，請根據平台特性來判斷遊戲譯名。"

        prompt = f"""你是遊戲翻譯專家。請將以下遊戲名稱翻譯成{lang_name}官方譯名。{platform_hint}

規則：
1. 回答格式必須是 JSON 陣列，每個項目包含 "id"（編號）和 "name"（翻譯結果）
2. 優先使用官方{lang_name}譯名，沒有官方譯名則提供最通用的翻譯
3. 遊戲名稱中的 (年份)(發行商) 等資訊是輔助判斷用，翻譯時不需要保留
4. 如果遊戲名稱是英文縮寫、專有名詞或品牌名，可以保留英文原名
5. 如果完全不知道該遊戲，仍請嘗試根據英文名稱的字面意思翻譯
6. 只有真的無法翻譯時，"name" 才設為 null
7. 不要加任何解釋文字，只要翻譯結果
8. 保持遊戲編號與輸入一致
9. 確保 JSON 格式正確，null 不要加引號

輸入遊戲列表：
{numbered_list}

請以 JSON 陣列格式回覆：
[
  {{"id": 1, "name": "翻譯結果1"}},
  {{"id": 2, "name": null}}
]

JSON 回覆："""

        return prompt

    def _parse_response(self, response_text: str, game_names: List[str]) -> Dict[str, str]:
        """
        解析 Gemini 回應

        Args:
            response_text: API 回應文字
            game_names: 原始遊戲名稱列表（用於對照）

        Returns:
            {原名: 翻譯結果} 的字典
        """
        results = {}

        try:
            # 嘗試找到 JSON 陣列
            # 移除可能的 markdown 程式碼區塊
            text = response_text.strip()
            if text.startswith("```"):
                # 移除 ```json 或 ``` 開頭和 ``` 結尾
                lines = text.split("\n")
                text = "\n".join(lines[1:-1]) if len(lines) > 2 else text

            # 尋找 JSON 陣列的開始和結束
            start_idx = text.find('[')
            end_idx = text.rfind(']')

            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx + 1]

                # 修復常見的 JSON 格式錯誤
                json_str = self._fix_json_errors(json_str)

                data = json.loads(json_str)

                # 解析每個項目
                for item in data:
                    if isinstance(item, dict):
                        idx = item.get('id')
                        name = item.get('name')

                        # 確保 id 有效且在範圍內
                        if idx is not None and 1 <= idx <= len(game_names):
                            original_name = game_names[idx - 1]
                            # 只有有效的翻譯才加入結果
                            if name and name != 'null' and name != original_name:
                                # 清理翻譯結果
                                cleaned = self._clean_translation(name)
                                if cleaned:
                                    results[original_name] = cleaned

        except json.JSONDecodeError as e:
            print(f"JSON 解析錯誤: {e}")
            print(f"原始回應: {response_text[:500]}...")
            # 嘗試逐行解析，盡量搶救部分結果
            results = self._parse_response_fallback(response_text, game_names)
        except Exception as e:
            print(f"解析回應時發生錯誤: {e}")

        return results

    def _fix_json_errors(self, json_str: str) -> str:
        """
        修復常見的 JSON 格式錯誤

        Args:
            json_str: 原始 JSON 字串

        Returns:
            修復後的 JSON 字串
        """
        # 修復 null" -> null (AI 常見錯誤)
        json_str = re.sub(r': null"', ': null', json_str)
        json_str = re.sub(r':null"', ':null', json_str)

        # 修復 true" -> true
        json_str = re.sub(r': true"', ': true', json_str)

        # 修復 false" -> false
        json_str = re.sub(r': false"', ': false', json_str)

        # 修復遺漏的逗號 (}{ -> },{)
        json_str = re.sub(r'\}\s*\{', '},{', json_str)

        # 修復多餘的逗號 (,] -> ])
        json_str = re.sub(r',\s*\]', ']', json_str)

        # 修復多餘的逗號 (,} -> })
        json_str = re.sub(r',\s*\}', '}', json_str)

        return json_str

    def _parse_response_fallback(self, response_text: str, game_names: List[str]) -> Dict[str, str]:
        """
        備用解析方法：逐行嘗試解析，盡量搶救部分結果

        Args:
            response_text: API 回應文字
            game_names: 原始遊戲名稱列表

        Returns:
            {原名: 翻譯結果} 的字典
        """
        results = {}

        # 使用正則表達式找出所有 {"id": X, "name": "Y"} 格式的項目
        pattern = r'\{"id"\s*:\s*(\d+)\s*,\s*"name"\s*:\s*"([^"]+)"\s*\}'
        matches = re.findall(pattern, response_text)

        for idx_str, name in matches:
            try:
                idx = int(idx_str)
                if 1 <= idx <= len(game_names):
                    original_name = game_names[idx - 1]
                    cleaned = self._clean_translation(name)
                    if cleaned and cleaned != original_name:
                        results[original_name] = cleaned
            except (ValueError, IndexError):
                continue

        if results:
            print(f"  備用解析搶救了 {len(results)} 筆結果")

        return results

    def _clean_translation(self, text: str) -> Optional[str]:
        """
        清理翻譯結果

        Args:
            text: 原始翻譯文字

        Returns:
            清理後的文字，若為無效回應則返回 None
        """
        if not text:
            return None

        # 移除可能的引號
        text = text.strip().strip('"\'「」『』《》')

        # 移除可能的編號前綴
        text = re.sub(r'^\d+\.\s*', '', text)

        # 檢查長度
        if len(text) < 1 or len(text) > 100:
            return None

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

        text_lower = text.lower()
        for pattern in invalid_patterns:
            if pattern in text_lower or pattern.lower() in text_lower:
                return None

        return text

    def translate_batch(self, game_names: List[str],
                        language: str = 'zh-TW',
                        platform: str = "") -> BatchTranslationResult:
        """
        批次翻譯遊戲名稱

        Args:
            game_names: 遊戲名稱列表
            language: 目標語系
            platform: 遊戲平台名稱（提升翻譯準確度）

        Returns:
            BatchTranslationResult 包含翻譯結果和失敗清單
        """
        if not game_names:
            return BatchTranslationResult(
                translations={},
                failed=[],
                total=0,
                success_count=0
            )

        # 先檢查快取
        translations = {}
        uncached_names = []

        for name in game_names:
            cached = self.cache.get('gemini', name, language)
            if cached:
                translations[name] = cached
            else:
                uncached_names.append(name)

        # 如果全部都有快取，直接返回
        if not uncached_names:
            return BatchTranslationResult(
                translations=translations,
                failed=[],
                total=len(game_names),
                success_count=len(translations)
            )

        # 確保 API 已初始化
        if not self._ensure_initialized():
            return BatchTranslationResult(
                translations=translations,
                failed=uncached_names,
                total=len(game_names),
                success_count=len(translations)
            )

        # 分批處理
        failed = []

        for i in range(0, len(uncached_names), self.batch_size):
            batch = uncached_names[i:i + self.batch_size]

            # 速率限制
            self._rate_limit()

            # 重試機制
            batch_result = None
            for retry in range(self.MAX_RETRIES):
                try:
                    prompt = self._build_prompt(batch, language, platform)
                    response = self._model.generate_content(prompt)

                    if response.text:
                        batch_result = self._parse_response(
                            response.text, batch)
                        break

                except Exception as e:
                    print(f"批次翻譯失敗 (嘗試 {retry + 1}/{self.MAX_RETRIES}): {e}")
                    if retry < self.MAX_RETRIES - 1:
                        time.sleep(2 ** retry)  # 指數退避

            # 處理結果
            if batch_result:
                for name, trans in batch_result.items():
                    translations[name] = trans
                    # 寫入快取
                    self.cache.set('gemini', name, language, trans)

                # 記錄失敗的項目
                for name in batch:
                    if name not in batch_result:
                        failed.append(name)
            else:
                # 整批失敗
                failed.extend(batch)

        return BatchTranslationResult(
            translations=translations,
            failed=failed,
            total=len(game_names),
            success_count=len(translations)
        )

    def translate_all(self, game_names: List[str],
                      language: str = 'zh-TW',
                      platform: str = "",
                      progress_callback=None,
                      cancel_check=None) -> BatchTranslationResult:
        """
        翻譯所有遊戲名稱（自動分批）

        Args:
            game_names: 遊戲名稱列表
            language: 目標語系
            platform: 遊戲平台名稱（提升翻譯準確度）
            progress_callback: 進度回呼函數 (current, total, message)
            cancel_check: 取消檢查函數，回傳 True 表示要取消

        Returns:
            BatchTranslationResult 包含翻譯結果和失敗清單
        """
        if not game_names:
            return BatchTranslationResult(
                translations={},
                failed=[],
                total=0,
                success_count=0
            )

        # 先檢查快取，過濾出需要翻譯的
        translations = {}
        uncached_names = []

        for name in game_names:
            cached = self.cache.get('gemini', name, language)
            if cached:
                translations[name] = cached
            else:
                uncached_names.append(name)

        if progress_callback:
            progress_callback(
                len(translations),
                len(game_names),
                f"快取命中 {len(translations)} 筆，待翻譯 {len(uncached_names)} 筆"
            )

        # 如果全部都有快取，直接返回
        if not uncached_names:
            return BatchTranslationResult(
                translations=translations,
                failed=[],
                total=len(game_names),
                success_count=len(translations)
            )

        # 確保 API 已初始化
        if not self._ensure_initialized():
            return BatchTranslationResult(
                translations=translations,
                failed=uncached_names,
                total=len(game_names),
                success_count=len(translations)
            )

        # 計算批次數
        total_batches = (len(uncached_names) +
                         self.batch_size - 1) // self.batch_size
        failed = []

        for batch_idx, i in enumerate(range(0, len(uncached_names), self.batch_size)):
            # 檢查是否取消
            if cancel_check and cancel_check():
                # 將未處理的加入失敗清單
                remaining = uncached_names[i:]
                failed.extend(remaining)
                break

            batch = uncached_names[i:i + self.batch_size]

            if progress_callback:
                progress_callback(
                    len(translations),
                    len(game_names),
                    f"批次 {batch_idx + 1}/{total_batches}：翻譯 {len(batch)} 個遊戲..."
                )

            # 速率限制
            self._rate_limit()

            # 重試機制
            batch_result = None
            for retry in range(self.MAX_RETRIES):
                # 在重試時也檢查取消
                if cancel_check and cancel_check():
                    break

                try:
                    prompt = self._build_prompt(batch, language, platform)
                    response = self._model.generate_content(prompt)

                    if response.text:
                        batch_result = self._parse_response(
                            response.text, batch)
                        break

                except Exception as e:
                    print(f"批次翻譯失敗 (嘗試 {retry + 1}/{self.MAX_RETRIES}): {e}")
                    if retry < self.MAX_RETRIES - 1:
                        # 在等待重試時分段檢查取消（每秒檢查一次）
                        wait_time = 2 ** retry
                        for _ in range(wait_time):
                            if cancel_check and cancel_check():
                                break
                            time.sleep(1)

            # 如果已取消，跳出批次迴圈
            if cancel_check and cancel_check():
                remaining = uncached_names[i + self.batch_size:]
                if remaining:
                    failed.extend(remaining)
                break

            # 處理結果
            if batch_result:
                for name, trans in batch_result.items():
                    translations[name] = trans
                    # 寫入快取
                    self.cache.set('gemini', name, language, trans)

                # 記錄失敗的項目
                for name in batch:
                    if name not in batch_result:
                        failed.append(name)
            else:
                # 整批失敗
                failed.extend(batch)

            if progress_callback:
                progress_callback(
                    len(translations),
                    len(game_names),
                    f"已完成 {len(translations)}/{len(game_names)}"
                )

        return BatchTranslationResult(
            translations=translations,
            failed=failed,
            total=len(game_names),
            success_count=len(translations)
        )

    @staticmethod
    def is_available() -> bool:
        """檢查 Gemini 是否可用"""
        return GEMINI_AVAILABLE

    def test_connection(self) -> Tuple[bool, str]:
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
