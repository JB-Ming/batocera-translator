# 字典檔管理模組
"""
負責管理翻譯字典檔的讀取、寫入、合併等操作。
"""
import json
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.file_utils import get_dictionaries_dir, get_language_packs_dir


class TranslationSource(Enum):
    """翻譯來源標記"""
    WIKI = "wiki"       # 維基百科
    SEARCH = "search"   # 網路搜尋
    API = "api"         # API 直譯
    KEEP = "keep"       # 保留原文
    MANUAL = "manual"   # 手動填入
    PACK = "pack"       # 語系包匯入


class MergeStrategy(Enum):
    """字典檔合併策略"""
    MERGE = "merge"           # 合併（保留已翻譯，加入新項目）
    FILL_EMPTY = "fill_empty" # 僅補空白
    OVERWRITE = "overwrite"   # 完全覆寫
    SKIP = "skip"             # 跳過


@dataclass
class GameEntry:
    """遊戲字典項目"""
    # === 基本欄位 ===
    key: str                          # 遊戲識別 Key（通常是檔名或路徑）
    original_name: str                # 原始名稱
    name: str = ""                    # 翻譯後名稱
    name_source: str = ""             # 名稱翻譯來源
    original_desc: str = ""           # 原始描述
    desc: str = ""                    # 翻譯後描述
    desc_source: str = ""             # 描述翻譯來源
    
    # === 追蹤欄位 ===
    needs_retranslate: bool = False   # 是否需要重新翻譯（手動標記翻譯品質不佳）
    name_translated_at: str = ""      # 名稱翻譯時間 (ISO8601 格式)
    desc_translated_at: str = ""      # 描述翻譯時間 (ISO8601 格式)
    
    # === 原文變更偵測 ===
    original_name_hash: str = ""      # 原文名稱的 hash，用於偵測原文是否變更
    original_desc_hash: str = ""      # 原文描述的 hash，用於偵測原文是否變更
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameEntry':
        """從字典建立"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def has_name_translation(self) -> bool:
        """是否有名稱翻譯"""
        return bool(self.name and self.name_source)
    
    def has_desc_translation(self) -> bool:
        """是否有描述翻譯"""
        return bool(self.desc and self.desc_source)
    
    def compute_original_hash(self, text: str) -> str:
        """計算原文 hash（用於變更偵測）"""
        import hashlib
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
    
    def check_original_changed(self) -> bool:
        """
        檢查原文是否已變更
        
        Returns:
            True 表示原文已變更，需要重新翻譯
        """
        if self.original_name and self.original_name_hash:
            current_hash = self.compute_original_hash(self.original_name)
            if current_hash != self.original_name_hash:
                return True
        if self.original_desc and self.original_desc_hash:
            current_hash = self.compute_original_hash(self.original_desc)
            if current_hash != self.original_desc_hash:
                return True
        return False
    
    def update_hashes(self) -> None:
        """更新原文 hash（翻譯完成後呼叫）"""
        if self.original_name:
            self.original_name_hash = self.compute_original_hash(self.original_name)
        if self.original_desc:
            self.original_desc_hash = self.compute_original_hash(self.original_desc)


class DictionaryManager:
    """
    字典檔管理器
    
    功能：
    - 讀取/寫入字典檔（JSON 格式）
    - 字典檔合併（支援多種策略）
    - 語系包匯入/匯出
    
    字典檔存放於使用者資料目錄（%LOCALAPPDATA%/BatoceraTranslator/dictionaries），
    確保程式更新時不會遺失翻譯資料。
    """
    
    def __init__(self, dictionaries_path: Optional[Path] = None):
        """
        初始化字典管理器
        
        Args:
            dictionaries_path: 字典檔根目錄，None 使用預設的使用者資料目錄
        """
        self.dictionaries_path = dictionaries_path or get_dictionaries_dir()
        
    def _get_dict_path(self, language: str, platform: str) -> Path:
        """取得字典檔路徑"""
        return self.dictionaries_path / language / f"{platform}.json"
    
    def load_dictionary(self, language: str, platform: str) -> Dict[str, GameEntry]:
        """
        載入字典檔
        
        Args:
            language: 語系代碼（如 zh-TW）
            platform: 平台代碼（如 nes）
            
        Returns:
            遊戲 Key 到 GameEntry 的對應字典
        """
        dict_path = self._get_dict_path(language, platform)
        
        if not dict_path.exists():
            return {}
            
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return {key: GameEntry.from_dict(entry) for key, entry in data.items()}
    
    def save_dictionary(self, language: str, platform: str, 
                        dictionary: Dict[str, GameEntry]) -> None:
        """
        儲存字典檔
        
        字典會同時儲存到兩個位置：
        1. 使用者資料目錄（%LOCALAPPDATA%/BatoceraTranslator/dictionaries）：本機使用
        2. 專案目錄下的 language_packs：用於版控分享
        
        Args:
            language: 語系代碼
            platform: 平台代碼
            dictionary: 遊戲字典
        """
        # 轉換為可序列化的字典格式
        data = {key: entry.to_dict() for key, entry in dictionary.items()}
        
        # === 儲存到使用者資料目錄（本機字典） ===
        dict_path = self._get_dict_path(language, platform)
        dict_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dict_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # === 同時儲存到 language_packs 資料夾（版控分享） ===
        language_packs_dir = get_language_packs_dir()
        pack_path = language_packs_dir / language / f"{platform}.json"
        pack_path.parent.mkdir(parents=True, exist_ok=True)
        with open(pack_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def merge_dictionaries(self, base: Dict[str, GameEntry], 
                          incoming: Dict[str, GameEntry],
                          strategy: MergeStrategy = MergeStrategy.MERGE) -> Dict[str, GameEntry]:
        """
        合併兩個字典
        
        Args:
            base: 基礎字典
            incoming: 要合併進來的字典
            strategy: 合併策略
            
        Returns:
            合併後的字典
        """
        if strategy == MergeStrategy.SKIP:
            return base.copy()
            
        if strategy == MergeStrategy.OVERWRITE:
            return incoming.copy()
            
        result = base.copy()
        
        for key, entry in incoming.items():
            if key not in result:
                # 新項目直接加入
                result[key] = entry
            elif strategy == MergeStrategy.MERGE:
                # 合併模式：保留已翻譯的，補充空白的
                existing = result[key]
                if not existing.has_name_translation() and entry.has_name_translation():
                    existing.name = entry.name
                    existing.name_source = entry.name_source
                if not existing.has_desc_translation() and entry.has_desc_translation():
                    existing.desc = entry.desc
                    existing.desc_source = entry.desc_source
            elif strategy == MergeStrategy.FILL_EMPTY:
                # 僅補空白：只處理完全沒有翻譯的項目
                existing = result[key]
                if not existing.has_name_translation() and not existing.has_desc_translation():
                    result[key] = entry
                    
        return result
    
    def import_language_pack(self, language: str, platform: str, 
                            pack_data: Dict[str, Any]) -> int:
        """
        匯入語系包
        
        Args:
            language: 目標語系
            platform: 平台代碼
            pack_data: 語系包資料
            
        Returns:
            匯入的項目數量
        """
        # 載入現有字典
        existing = self.load_dictionary(language, platform)
        
        # 轉換語系包資料
        incoming = {}
        for key, entry_data in pack_data.items():
            entry = GameEntry.from_dict(entry_data)
            # 標記來源為語系包
            if entry.name_source:
                entry.name_source = TranslationSource.PACK.value
            if entry.desc_source:
                entry.desc_source = TranslationSource.PACK.value
            incoming[key] = entry
        
        # 合併（僅填入空白項目）
        merged = self.merge_dictionaries(existing, incoming, MergeStrategy.MERGE)
        
        # 儲存
        self.save_dictionary(language, platform, merged)
        
        # 計算新增項目數
        return len(merged) - len(existing)
    
    def export_dictionary(self, language: str, platform: str) -> Dict[str, Any]:
        """
        匯出字典為語系包格式
        
        Args:
            language: 語系代碼
            platform: 平台代碼
            
        Returns:
            語系包資料（可序列化為 JSON）
        """
        dictionary = self.load_dictionary(language, platform)
        return {key: entry.to_dict() for key, entry in dictionary.items()}
    
    def get_available_platforms(self, language: str) -> List[str]:
        """取得指定語系下所有可用的平台"""
        lang_dir = self.dictionaries_path / language
        if not lang_dir.exists():
            return []
        return [f.stem for f in lang_dir.glob('*.json')]
