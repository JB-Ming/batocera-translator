# 檔案操作工具
"""
提供檔案操作相關的工具函式。
"""
import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional


def ensure_dir(path: Path) -> Path:
    """
    確保目錄存在，不存在則建立
    
    Args:
        path: 目錄路徑
        
    Returns:
        目錄路徑
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_copy(src: Path, dst: Path, overwrite: bool = False) -> bool:
    """
    安全複製檔案
    
    Args:
        src: 來源檔案
        dst: 目標位置
        overwrite: 是否覆寫
        
    Returns:
        是否成功
    """
    if not src.exists():
        return False
        
    if dst.exists() and not overwrite:
        return False
    
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def get_file_hash(path: Path, algorithm: str = 'md5') -> Optional[str]:
    """
    計算檔案雜湊值
    
    Args:
        path: 檔案路徑
        algorithm: 雜湊演算法（md5/sha256）
        
    Returns:
        雜湊值
    """
    if not path.exists():
        return None
    
    hash_func = hashlib.new(algorithm)
    
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_dir_size(path: Path) -> int:
    """
    計算目錄大小
    
    Args:
        path: 目錄路徑
        
    Returns:
        總大小（byte）
    """
    total = 0
    for entry in path.rglob('*'):
        if entry.is_file():
            total += entry.stat().st_size
    return total


def clean_old_files(path: Path, pattern: str = '*', keep_count: int = 10) -> int:
    """
    清理舊檔案，保留最新的幾個
    
    Args:
        path: 目錄路徑
        pattern: 檔案模式
        keep_count: 保留數量
        
    Returns:
        刪除的檔案數量
    """
    if not path.exists():
        return 0
    
    files = sorted(path.glob(pattern), key=lambda f: f.stat().st_mtime, reverse=True)
    deleted = 0
    
    for f in files[keep_count:]:
        try:
            f.unlink()
            deleted += 1
        except Exception:
            pass
    
    return deleted
