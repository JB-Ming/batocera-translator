# XML 寫回模組
"""
負責將翻譯結果寫回 gamelist.xml。
"""
import xml.etree.ElementTree as ET
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .dictionary import GameEntry
from ..utils import get_game_key


class DisplayFormat(Enum):
    """顯示格式"""
    TRANSLATED_ONLY = "translated"      # 僅顯示翻譯
    TRANSLATED_ORIGINAL = "trans_orig"  # 翻譯(原文)
    ORIGINAL_TRANSLATED = "orig_trans"  # 原文(翻譯)
    ORIGINAL_ONLY = "original"          # 僅保留原文


class WriteStrategy(Enum):
    """寫回策略"""
    SKIP_TRANSLATED = "skip"      # 跳過 XML 中已翻譯的
    DICT_PRIORITY = "dict"        # 字典優先
    XML_PRIORITY = "xml"          # XML 優先
    OVERWRITE_ALL = "overwrite"   # 全部覆寫


@dataclass
class WriteResult:
    """寫回結果"""
    total: int = 0          # 總遊戲數
    updated: int = 0        # 已更新
    skipped: int = 0        # 已跳過
    failed: int = 0         # 失敗
    backup_path: str = ""   # 備份路徑


class XmlWriter:
    """
    XML 寫回器
    
    功能：
    - 讀取 gamelist.xml
    - 依據字典檔更新遊戲名稱與描述
    - 支援多種顯示格式
    - 自動備份原始檔案
    """
    
    def __init__(self, backup_path: str = './backups'):
        """
        初始化寫回器
        
        Args:
            backup_path: 備份資料夾路徑
        """
        self.backup_path = Path(backup_path)
        
    def _format_text(self, translated: str, original: str, 
                     display_format: DisplayFormat) -> str:
        """
        依顯示格式組合文字
        
        Args:
            translated: 翻譯文字
            original: 原始文字
            display_format: 顯示格式
            
        Returns:
            組合後的文字
        """
        if not translated:
            return original
            
        if display_format == DisplayFormat.TRANSLATED_ONLY:
            return translated
        elif display_format == DisplayFormat.TRANSLATED_ORIGINAL:
            return f"{translated} ({original})"
        elif display_format == DisplayFormat.ORIGINAL_TRANSLATED:
            return f"{original} ({translated})"
        else:  # ORIGINAL_ONLY
            return original
    
    def backup_file(self, source_path: Path, platform: str) -> Path:
        """
        備份檔案
        
        Args:
            source_path: 來源檔案路徑
            platform: 平台名稱
            
        Returns:
            備份檔案路徑
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backup_path / platform
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_file = backup_dir / f"gamelist_{timestamp}.xml"
        shutil.copy2(source_path, backup_file)
        
        return backup_file
    
    def write_translations(self, 
                           xml_path: Path,
                           dictionary: Dict[str, GameEntry],
                           platform: str,
                           display_format: DisplayFormat = DisplayFormat.TRANSLATED_ONLY,
                           strategy: WriteStrategy = WriteStrategy.DICT_PRIORITY,
                           auto_backup: bool = True,
                           preview_only: bool = False) -> WriteResult:
        """
        將翻譯寫回 XML
        
        Args:
            xml_path: gamelist.xml 路徑
            dictionary: 翻譯字典
            platform: 平台名稱
            display_format: 顯示格式
            strategy: 寫回策略
            auto_backup: 是否自動備份
            preview_only: 僅預覽不寫入
            
        Returns:
            寫回結果
        """
        result = WriteResult()
        
        # 備份
        if auto_backup and not preview_only:
            result.backup_path = str(self.backup_file(xml_path, platform))
        
        # 解析 XML
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            result.failed = 1
            return result
        
        # 遍歷所有遊戲
        for game in root.findall('game'):
            result.total += 1
            
            # 取得遊戲路徑作為 Key
            path_elem = game.find('path')
            if path_elem is None or not path_elem.text:
                result.skipped += 1
                continue
                
            # 用 get_game_key 生成與字典一致的 KEY
            game_key = get_game_key(path_elem.text)
            
            # 查找字典
            if game_key not in dictionary:
                result.skipped += 1
                continue
                
            entry = dictionary[game_key]
            
            # 處理名稱
            name_elem = game.find('name')
            if name_elem is not None and entry.name:
                original = name_elem.text or ""
                
                # 判斷是否需要更新
                should_update = True
                if strategy == WriteStrategy.SKIP_TRANSLATED:
                    # 檢查是否已有非英文字元（可能已翻譯）
                    if self._has_non_ascii(original):
                        should_update = False
                elif strategy == WriteStrategy.XML_PRIORITY:
                    if original and original != entry.original_name:
                        should_update = False
                
                if should_update:
                    name_elem.text = self._format_text(
                        entry.name, entry.original_name, display_format
                    )
            
            # 處理描述
            desc_elem = game.find('desc')
            if desc_elem is not None and entry.desc:
                original_desc = desc_elem.text or ""
                
                should_update_desc = True
                if strategy == WriteStrategy.SKIP_TRANSLATED:
                    if self._has_non_ascii(original_desc):
                        should_update_desc = False
                
                if should_update_desc:
                    desc_elem.text = entry.desc
            
            result.updated += 1
        
        # 寫入檔案（保留原始格式）
        if not preview_only:
            self._write_preserving_format(xml_path, tree)
        
        return result
    
    def _write_preserving_format(self, xml_path: Path, tree: ET.ElementTree) -> None:
        """
        寫入 XML 並盡量保留原始格式
        
        使用 xml.etree.ElementTree 的 indent 功能來保持格式
        """
        import xml.etree.ElementTree as ET
        
        # 嘗試使用 Python 3.9+ 的 indent 功能
        try:
            ET.indent(tree.getroot(), space="\t", level=0)
        except AttributeError:
            # Python 3.8 及更早版本沒有 indent，手動處理
            self._indent_xml(tree.getroot())
        
        # 寫入時使用 UTF-8 編碼
        tree.write(xml_path, encoding='utf-8', xml_declaration=True)
    
    def _indent_xml(self, elem, level=0):
        """
        手動為 XML 元素添加縮排（相容舊版 Python）
        """
        indent = "\n" + "\t" * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent
    
    def _has_non_ascii(self, text: str) -> bool:
        """檢查文字是否包含非 ASCII 字元（可能是已翻譯的內容）"""
        if not text:
            return False
        return not all(ord(c) < 128 for c in text)
    
    def preview_changes(self, 
                        xml_path: Path,
                        dictionary: Dict[str, GameEntry],
                        display_format: DisplayFormat = DisplayFormat.TRANSLATED_ONLY) -> List[dict]:
        """
        預覽變更內容
        
        Args:
            xml_path: gamelist.xml 路徑
            dictionary: 翻譯字典
            display_format: 顯示格式
            
        Returns:
            變更清單
        """
        changes = []
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError:
            return changes
        
        for game in root.findall('game'):
            path_elem = game.find('path')
            if path_elem is None or not path_elem.text:
                continue
                
            # 用 get_game_key 生成與字典一致的 KEY
            game_key = get_game_key(path_elem.text)
            if game_key not in dictionary:
                continue
                
            entry = dictionary[game_key]
            name_elem = game.find('name')
            
            if name_elem is not None and entry.name:
                original = name_elem.text or ""
                new_value = self._format_text(entry.name, entry.original_name, display_format)
                
                if original != new_value:
                    changes.append({
                        'key': game_key,
                        'field': 'name',
                        'before': original,
                        'after': new_value,
                        'source': entry.name_source
                    })
            
            desc_elem = game.find('desc')
            if desc_elem is not None and entry.desc:
                original_desc = desc_elem.text or ""
                if original_desc != entry.desc:
                    changes.append({
                        'key': game_key,
                        'field': 'desc',
                        'before': original_desc[:100] + '...' if len(original_desc) > 100 else original_desc,
                        'after': entry.desc[:100] + '...' if len(entry.desc) > 100 else entry.desc,
                        'source': entry.desc_source
                    })
        
        return changes
