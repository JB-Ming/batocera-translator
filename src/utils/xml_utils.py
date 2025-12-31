# XML 解析工具
"""
提供 gamelist.xml 解析相關的工具函式。
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class GameInfo:
    """遊戲資訊"""
    path: str             # 遊戲路徑（作為唯一識別 Key）
    name: str             # 遊戲名稱
    desc: str = ""        # 遊戲描述
    image: str = ""       # 圖片路徑
    rating: float = 0.0   # 評分
    releasedate: str = "" # 發行日期
    developer: str = ""   # 開發商
    publisher: str = ""   # 發行商
    genre: str = ""       # 類型
    players: str = ""     # 玩家數
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'path': self.path,
            'name': self.name,
            'desc': self.desc,
            'image': self.image,
            'rating': self.rating,
            'releasedate': self.releasedate,
            'developer': self.developer,
            'publisher': self.publisher,
            'genre': self.genre,
            'players': self.players,
        }


def parse_gamelist(xml_path: Path) -> List[GameInfo]:
    """
    解析 gamelist.xml
    
    Args:
        xml_path: XML 檔案路徑
        
    Returns:
        遊戲資訊清單
    """
    games = []
    
    if not xml_path.exists():
        return games
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        for game_elem in root.findall('game'):
            # 取得路徑（必要欄位）
            path_elem = game_elem.find('path')
            if path_elem is None or not path_elem.text:
                continue
            
            # 取得名稱（必要欄位）
            name_elem = game_elem.find('name')
            if name_elem is None or not name_elem.text:
                continue
            
            # 取得其他欄位
            game = GameInfo(
                path=path_elem.text,
                name=name_elem.text,
                desc=_get_element_text(game_elem, 'desc'),
                image=_get_element_text(game_elem, 'image'),
                rating=_get_element_float(game_elem, 'rating'),
                releasedate=_get_element_text(game_elem, 'releasedate'),
                developer=_get_element_text(game_elem, 'developer'),
                publisher=_get_element_text(game_elem, 'publisher'),
                genre=_get_element_text(game_elem, 'genre'),
                players=_get_element_text(game_elem, 'players'),
            )
            
            games.append(game)
            
    except ET.ParseError:
        pass
    
    return games


def _get_element_text(parent: ET.Element, tag: str) -> str:
    """取得子元素文字"""
    elem = parent.find(tag)
    return elem.text if elem is not None and elem.text else ""


def _get_element_float(parent: ET.Element, tag: str) -> float:
    """取得子元素浮點數"""
    text = _get_element_text(parent, tag)
    try:
        return float(text) if text else 0.0
    except ValueError:
        return 0.0


def get_game_count(xml_path: Path) -> int:
    """
    取得遊戲數量
    
    Args:
        xml_path: XML 檔案路徑
        
    Returns:
        遊戲數量
    """
    if not xml_path.exists():
        return 0
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        return len(root.findall('game'))
    except ET.ParseError:
        return 0


def validate_gamelist(xml_path: Path) -> tuple[bool, str]:
    """
    驗證 gamelist.xml 格式
    
    Args:
        xml_path: XML 檔案路徑
        
    Returns:
        (是否有效, 錯誤訊息)
    """
    if not xml_path.exists():
        return False, "檔案不存在"
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        if root.tag != 'gameList':
            return False, f"根元素應為 gameList，但找到 {root.tag}"
        
        games = root.findall('game')
        if not games:
            return True, "警告：沒有找到任何遊戲"
        
        return True, ""
        
    except ET.ParseError as e:
        return False, f"XML 解析錯誤：{str(e)}"
