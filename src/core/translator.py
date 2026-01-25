# 翻譯引擎模組
"""
負責遊戲名稱與描述的翻譯邏輯。
"""
import re
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from .dictionary import GameEntry, TranslationSource


class TranslationResult(Enum):
    """翻譯結果狀態"""
    SUCCESS = "success"         # 翻譯成功
    KEEP_ORIGINAL = "keep"      # 保留原文
    SKIPPED = "skipped"         # 已跳過（已有翻譯）
    FAILED = "failed"           # 翻譯失敗


@dataclass
class TranslationOutput:
    """翻譯輸出"""
    result: TranslationResult
    name: str = ""
    name_source: str = ""
    desc: str = ""
    desc_source: str = ""
    error_message: str = ""


# 繁簡轉換器（延遲初始化）
_opencc_converter = None


def get_opencc_converter():
    """取得 OpenCC 轉換器（簡體轉繁體）"""
    global _opencc_converter
    if _opencc_converter is None:
        try:
            from opencc import OpenCC
            _opencc_converter = OpenCC('s2twp')  # 簡體轉繁體（台灣用語）
        except ImportError:
            _opencc_converter = None
    return _opencc_converter


def to_traditional_chinese(text: str) -> str:
    """將簡體中文轉換為繁體中文"""
    if not text:
        return text
    converter = get_opencc_converter()
    if converter:
        return converter.convert(text)
    return text


class TranslationEngine:
    """
    翻譯引擎

    翻譯查找優先順序：
    1. 本地字典
    2. 維基百科 API
    3. 其他網站搜尋（Google）
    4. 翻譯 API 直譯
    5. 保留原文
    """

    # 應保留原文的模式（品牌+數字、純英文數字組合等）
    KEEP_ORIGINAL_PATTERNS = [
        r'^(FIFA|NBA|NFL|NHL|MLB|F1|WWE|UFC|PGA|WRC)\s*\d+',  # 運動遊戲系列
        r'^(F-Zero|R-Type|G-Darius)',  # 經典保留原名的遊戲
        r'^\d+$',  # 純數字
        r'^[A-Z]-\d+$',  # 字母-數字組合
    ]

    def __init__(self, target_language: str = 'zh-TW'):
        """
        初始化翻譯引擎

        Args:
            target_language: 目標語系
        """
        self.target_language = target_language
        self._wiki_service = None
        self._gemini_service = None
        self._search_service = None
        self._translate_api = None

    def set_wiki_service(self, service) -> None:
        """設定維基百科服務"""
        self._wiki_service = service

    def set_gemini_service(self, service) -> None:
        """設定 Gemini AI 服務"""
        self._gemini_service = service

    def set_search_service(self, service) -> None:
        """設定網路搜尋服務"""
        self._search_service = service

    def set_translate_api(self, api) -> None:
        """設定翻譯 API"""
        self._translate_api = api

    def clean_filename(self, filename: str) -> str:
        """
        清理檔名，移除版本號、區域碼等雜訊

        Args:
            filename: 原始檔名

        Returns:
            清理後的遊戲名稱
        """
        # 移除副檔名
        name = re.sub(r'\.[a-zA-Z0-9]+$', '', filename)

        # 移除括號內容（區域碼、版本號等）
        name = re.sub(r'\s*\([^)]*\)', '', name)
        name = re.sub(r'\s*\[[^\]]*\]', '', name)

        # 移除常見版本標記
        name = re.sub(r'\s*(Rev\s*\d+|v\d+\.?\d*|Ver\.?\s*\d+)',
                      '', name, flags=re.IGNORECASE)

        # 清理多餘空白
        name = re.sub(r'\s+', ' ', name).strip()

        return name

    def should_keep_original(self, text: str, translated: str = "") -> bool:
        """
        判定是否應保留原文

        Args:
            text: 原始文字
            translated: 翻譯結果（可選）

        Returns:
            是否應保留原文
        """
        # 檢查是否符合保留原文的模式
        for pattern in self.KEEP_ORIGINAL_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True

        # 翻譯結果與原文相同
        if translated and translated.lower() == text.lower():
            return True

        return False

    def translate_game(self, entry: GameEntry,
                       translate_name: bool = True,
                       translate_desc: bool = True,
                       skip_translated: bool = True,
                       progress_callback: Optional[Callable] = None) -> TranslationOutput:
        """
        翻譯單一遊戲

        Args:
            entry: 遊戲字典項目
            translate_name: 是否翻譯名稱
            translate_desc: 是否翻譯描述
            skip_translated: 是否跳過已翻譯的項目
            progress_callback: 進度回呼函式

        Returns:
            翻譯輸出結果
        """
        output = TranslationOutput(result=TranslationResult.SUCCESS)

        # 檢查是否標記為需要重新翻譯
        force_retranslate = entry.needs_retranslate

        # 如果需要重翻，清空舊的翻譯結果（重新開始）
        if force_retranslate:
            print(f"[重翻] 清空舊翻譯：{entry.original_name}")
            print(f"  - 舊 name: {entry.name}")
            print(
                f"  - 舊 desc: {entry.desc[:50]}..." if entry.desc else "  - 舊 desc: (空)")
            # 清空翻譯結果，重新翻譯
            entry.name = ""
            entry.name_source = ""
            entry.desc = ""
            entry.desc_source = ""

        # 如果需要重翻，清除維基百科快取
        if force_retranslate and self._wiki_service:
            clean_name = self.clean_filename(entry.original_name)
            # 清除名稱和描述的快取
            self._wiki_service.clear_cache(clean_name)
            if entry.name:
                self._wiki_service.clear_cache(entry.name)

        # 檢查是否需要跳過（除非標記為需要重翻）
        if skip_translated and not force_retranslate:
            name_done = not translate_name or entry.has_name_translation()
            desc_done = not translate_desc or entry.has_desc_translation()
            if name_done and desc_done:
                return TranslationOutput(result=TranslationResult.SKIPPED)

        # 翻譯名稱
        if translate_name and (not entry.has_name_translation() or force_retranslate):
            clean_name = self.clean_filename(entry.original_name)

            # 檢查是否應保留原文
            if self.should_keep_original(clean_name):
                output.name = clean_name
                output.name_source = TranslationSource.KEEP.value
            else:
                # 依優先順序嘗試翻譯
                translated_name, source = self._translate_name(clean_name)
                output.name = translated_name or clean_name
                output.name_source = source

                # 再次檢查翻譯結果
                if self.should_keep_original(clean_name, translated_name):
                    output.name = clean_name
                    output.name_source = TranslationSource.KEEP.value

        # 翻譯描述
        if translate_desc and (not entry.has_desc_translation() or force_retranslate):
            # 檢查是否有有效的原始描述（非空字串）
            if entry.original_desc and entry.original_desc.strip():
                # 有原始描述，直接翻譯
                translated_desc, source = self._translate_description(
                    entry.original_desc)
                output.desc = translated_desc or ""
                output.desc_source = source
            else:
                # 沒有原始描述或描述為空，使用遊戲名稱搜尋描述
                clean_name = self.clean_filename(entry.original_name)
                # 重翻時優先使用英文原名，避免中文名稱搜到錯誤結果（如「外星人」會搜到 E.T. 電影）
                if force_retranslate:
                    search_name = clean_name  # 使用英文原名
                    # 調試：記錄重翻搜尋
                    print(
                        f"[重翻] 使用英文原名搜尋描述：'{search_name}' (原中文名：'{entry.name}')")
                else:
                    # 正常翻譯：優先使用已翻譯的名稱，搜尋結果更準確
                    search_name = entry.name if entry.has_name_translation() else clean_name

                fetched_desc, source = self._fetch_description_by_name(
                    search_name)
                if fetched_desc:
                    output.desc = fetched_desc
                    output.desc_source = source
                    if force_retranslate:
                        # 調試：顯示搜尋結果預覽
                        desc_preview = fetched_desc[:100] if len(
                            fetched_desc) > 100 else fetched_desc
                        print(f"[重翻] 找到描述：{desc_preview}")
                else:
                    # 沒找到描述
                    if force_retranslate:
                        print(f"[重翻] 未找到描述：'{search_name}'，保持空白")
                    # 重翻時保持空白，正常翻譯時也不填入舊值
                    output.desc = ""
                    output.desc_source = ""

        # 如果成功翻譯，清除重翻標記
        if force_retranslate:
            if output.name or output.desc:
                entry.needs_retranslate = False
            # 如果重翻但沒有新結果，保持標記不變（讓用戶可以再次嘗試）

        # 套用繁簡轉換（確保輸出為繁體中文）
        if self.target_language == 'zh-TW':
            if output.name and output.name != clean_name:  # 只轉換翻譯結果
                output.name = to_traditional_chinese(output.name)
            if output.desc:
                output.desc = to_traditional_chinese(output.desc)

        return output

    def _translate_name(self, name: str) -> Tuple[str, str]:
        """
        翻譯遊戲名稱

        查找順序：維基百科 → Gemini AI → 網路搜尋 → API 直譯

        順序設計說明：
        1. 維基百科：免費且最準確（官方譯名），優先使用
        2. Gemini AI：AI 翻譯品質高，但需要 API key（如果沒設定會自動跳過）
        3. 網路搜尋：免費但結果不穩定，作為備選
        4. API 直譯：保底方案，確保總能翻譯

        重要特性：
        - 找到有效結果後立即返回（避免浪費 API 額度）
        - 如果服務未初始化（如 Gemini 沒有 key），會自動跳過
        - 每個服務獨立處理，互不影響

        Returns:
            (翻譯結果, 來源標記)
        """
        # 1. 維基百科搜尋（最準確，免費）
        if self._wiki_service:
            result = self._wiki_service.search(name, self.target_language)
            if result and result != name:  # 確保有效翻譯
                return result, TranslationSource.WIKI.value

        # 2. Gemini AI 翻譯（高品質，需要 key）
        # 注意：如果沒設定 API key，這個服務不會被初始化，會自動跳過
        if self._gemini_service:
            result = self._gemini_service.translate_game_name(
                name, self.target_language)
            if result and result != name:
                return result, "gemini"

        # 3. 網路搜尋（免費，備選方案）
        if self._search_service:
            result = self._search_service.search(name, self.target_language)
            if result and result != name:
                return result, TranslationSource.SEARCH.value

        # 4. API 直譯（保底方案，免費）
        if self._translate_api:
            result = self._translate_api.translate(name, self.target_language)
            if result and result != name:
                return result, TranslationSource.API.value

        # 所有方法都失敗，保留原文
        return name, TranslationSource.KEEP.value
        result = self._search_service.search(name, self.target_language)
        if result:
            return result, TranslationSource.SEARCH.value

        # 4. API 直譯
        if self._translate_api:
            result = self._translate_api.translate(name, self.target_language)
            if result:
                return result, TranslationSource.API.value

        # 找不到翻譯，保留原文
        return name, TranslationSource.KEEP.value

    def _translate_description(self, desc: str) -> Tuple[str, str]:
        """
        翻譯遊戲描述

        描述通常較長，直接使用翻譯 API

        Returns:
            (翻譯結果, 來源標記)
        """
        # 1. 維基百科（可能有遊戲介紹）
        if self._wiki_service:
            result = self._wiki_service.get_description(
                desc[:50], self.target_language)
            if result:
                return result, TranslationSource.WIKI.value

        # 2. API 直譯
        if self._translate_api:
            result = self._translate_api.translate(desc, self.target_language)
            if result:
                return result, TranslationSource.API.value

        return "", ""

    def _fetch_description_by_name(self, game_name: str) -> Tuple[str, str]:
        """
        使用遊戲名稱搜尋描述（當原始描述為空時使用）

        Args:
            game_name: 遊戲名稱

        Returns:
            (描述文字, 來源標記)
        """
        # 1. 維基百科搜尋描述
        if self._wiki_service:
            result = self._wiki_service.get_description(
                game_name, self.target_language)
            if result:
                return result, TranslationSource.WIKI.value

        # 2. Gemini AI 取得描述（如果有配置）
        if self._gemini_service and hasattr(self._gemini_service, 'get_game_description'):
            result = self._gemini_service.get_game_description(
                game_name, self.target_language)
            if result:
                return result, "gemini"

        return "", ""
