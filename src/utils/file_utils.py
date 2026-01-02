# 檔案操作工具
"""
提供檔案操作相關的工具函式。
"""
import os
import sys
import shutil
import hashlib
from pathlib import Path
from typing import Optional


# 應用程式名稱（用於使用者資料目錄）
APP_NAME = "BatoceraTranslator"


def get_app_data_dir() -> Path:
    """
    取得應用程式使用者資料目錄
    
    使用者資料（字典檔、備份、設定）會存放在此目錄，
    避免程式更新或重新打包時遺失用戶資料。
    
    Windows: %LOCALAPPDATA%/BatoceraTranslator
    Linux/Mac: ~/.local/share/BatoceraTranslator
    
    Returns:
        使用者資料目錄路徑
    """
    if sys.platform == 'win32':
        # Windows: 使用 LOCALAPPDATA
        base = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')))
    else:
        # Linux/Mac: 使用 XDG_DATA_HOME 或 ~/.local/share
        base = Path(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')))
    
    app_dir = base / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_dictionaries_dir() -> Path:
    """取得字典檔目錄"""
    return ensure_dir(get_app_data_dir() / 'dictionaries')


def get_backups_dir() -> Path:
    """取得備份目錄"""
    return ensure_dir(get_app_data_dir() / 'backups')


def get_language_packs_dir() -> Path:
    """
    取得語系包目錄（專案目錄下的 language_packs）
    
    此目錄用於版控分享，與使用者資料目錄中的字典檔並存。
    翻譯完成後，字典會同時儲存到這裡，方便透過 Git 分享給其他使用者。
    
    Returns:
        語系包目錄路徑（專案目錄/language_packs）
    """
    # 取得程式執行的根目錄
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包後的執行檔目錄
        app_root = Path(sys.executable).parent
    else:
        # 開發模式：從 src/utils/file_utils.py 往上三層到專案根目錄
        app_root = Path(__file__).parent.parent.parent
    
    return ensure_dir(app_root / 'language_packs')


def get_settings_path() -> Path:
    """取得設定檔路徑"""
    return get_app_data_dir() / 'settings.json'


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
