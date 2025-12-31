# 檔名清理工具
"""
提供遊戲檔名清理相關的工具函式。
"""
import re
from typing import Tuple


def get_game_key(path: str) -> str:
    """
    從遊戲路徑生成字典 KEY
    
    處理項目：
    - 移除 ./ 前綴
    - 移除前導斜線
    - 移除副檔名
    
    Args:
        path: 遊戲路徑（如 ./Super Mario Bros.nes）
        
    Returns:
        字典 KEY（如 Super Mario Bros）
    """
    # 移除 ./ 前綴
    key = path.lstrip('./')
    # 移除前導斜線
    key = key.lstrip('/')
    # 移除副檔名
    if '.' in key:
        key = key.rsplit('.', 1)[0]
    return key


def clean_game_name(filename: str) -> str:
    """
    清理遊戲檔名，移除雜訊保留遊戲名稱
    
    處理項目：
    - 移除副檔名
    - 移除區域碼 (USA), (Japan), [J], [U] 等
    - 移除版本號 (Rev 1), (V1.0) 等
    - 移除開發碼 (Alpha), (Beta), (Proto) 等
    - 移除編號 (Disc 1), (Part 2) 等
    - 清理多餘空白
    
    Args:
        filename: 原始檔名
        
    Returns:
        清理後的遊戲名稱
    """
    name = filename
    
    # 移除副檔名
    name = re.sub(r'\.[a-zA-Z0-9]{2,4}$', '', name)
    
    # 移除小括號內容
    name = re.sub(r'\s*\([^)]*\)', '', name)
    
    # 移除中括號內容
    name = re.sub(r'\s*\[[^\]]*\]', '', name)
    
    # 移除常見後綴
    suffixes = [
        r'\s*-\s*Disc\s*\d+',
        r'\s*-\s*Part\s*\d+',
        r'\s*-\s*Volume\s*\d+',
        r'\s*Rev\s*\d+',
        r'\s*v\d+\.?\d*',
        r'\s*Ver\.?\s*\d+',
    ]
    for suffix in suffixes:
        name = re.sub(suffix, '', name, flags=re.IGNORECASE)
    
    # 清理多餘空白與連字號
    name = re.sub(r'\s+', ' ', name).strip()
    name = re.sub(r'^-\s*|\s*-$', '', name)
    
    return name


def extract_region(filename: str) -> Tuple[str, str]:
    """
    從檔名提取區域碼
    
    Args:
        filename: 原始檔名
        
    Returns:
        (區域碼, 清理後的名稱)
    """
    # 常見區域碼對應
    region_patterns = {
        r'\(USA\)|\[U\]|\(U\)': 'USA',
        r'\(Japan\)|\(JP\)|\[J\]|\(J\)': 'Japan',
        r'\(Europe\)|\(EU\)|\[E\]|\(E\)': 'Europe',
        r'\(World\)|\[W\]|\(W\)': 'World',
        r'\(Korea\)|\[K\]|\(K\)': 'Korea',
        r'\(Taiwan\)|\[T\]|\(T\)': 'Taiwan',
        r'\(China\)|\[C\]|\(C\)': 'China',
    }
    
    region = ''
    for pattern, code in region_patterns.items():
        if re.search(pattern, filename, re.IGNORECASE):
            region = code
            break
    
    clean_name = clean_game_name(filename)
    return region, clean_name


def normalize_name(name: str) -> str:
    """
    正規化遊戲名稱（用於比對）
    
    - 轉小寫
    - 移除標點符號
    - 移除冠詞（The, A, An）
    
    Args:
        name: 遊戲名稱
        
    Returns:
        正規化後的名稱
    """
    # 轉小寫
    normalized = name.lower()
    
    # 移除標點符號
    normalized = re.sub(r'[^\w\s]', '', normalized)
    
    # 移除開頭的冠詞
    normalized = re.sub(r'^(the|a|an)\s+', '', normalized)
    
    # 清理空白
    normalized = ' '.join(normalized.split())
    
    return normalized


def is_sequel(name: str) -> Tuple[bool, str, int]:
    """
    判斷是否為續作，提取系列名與編號
    
    Args:
        name: 遊戲名稱
        
    Returns:
        (是否續作, 系列名, 編號)
    """
    # 常見續作模式
    patterns = [
        r'^(.+?)\s+(\d+)$',           # Game Name 2
        r'^(.+?)\s+([IVXLC]+)$',      # Game Name II
        r'^(.+?)\s+(\d+):\s*.+$',     # Game Name 2: Subtitle
    ]
    
    for pattern in patterns:
        match = re.match(pattern, name, re.IGNORECASE)
        if match:
            series = match.group(1)
            number_str = match.group(2)
            
            # 轉換羅馬數字
            roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
                        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
            if number_str.upper() in roman_map:
                number = roman_map[number_str.upper()]
            else:
                try:
                    number = int(number_str)
                except ValueError:
                    continue
            
            return True, series.strip(), number
    
    return False, name, 1
