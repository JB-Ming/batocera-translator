# 日誌管理模組
"""
提供日誌記錄功能，支援多輸出（控制台 + 檔案 + UI）。
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, List
from enum import Enum
from dataclasses import dataclass


class LogLevel(Enum):
    """日誌級別"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


@dataclass
class LogEntry:
    """日誌項目"""
    timestamp: datetime
    level: LogLevel
    module: str
    message: str
    
    def format(self) -> str:
        """格式化日誌"""
        time_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return f"[{time_str}] [{self.level.value}] [{self.module}] {self.message}"


class Logger:
    """
    日誌管理器
    
    功能：
    - 多級別日誌（DEBUG/INFO/WARN/ERROR/SUCCESS）
    - 多輸出目標（控制台/檔案/UI 回呼）
    - 日誌檔案自動輪轉
    """
    
    def __init__(self, 
                 logs_path: str = './logs',
                 file_logging: bool = True,
                 console_logging: bool = True,
                 min_level: LogLevel = LogLevel.INFO):
        """
        初始化日誌管理器
        
        Args:
            logs_path: 日誌檔案目錄
            file_logging: 是否寫入檔案
            console_logging: 是否輸出到控制台
            min_level: 最小日誌級別
        """
        self.logs_path = Path(logs_path)
        self.file_logging = file_logging
        self.console_logging = console_logging
        self.min_level = min_level
        
        self._log_file: Optional[Path] = None
        self._ui_callback: Optional[Callable[[LogEntry], None]] = None
        self._entries: List[LogEntry] = []
        
        # 初始化日誌檔案
        if file_logging:
            self._init_log_file()
    
    def _init_log_file(self) -> None:
        """初始化日誌檔案"""
        self.logs_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._log_file = self.logs_path / f"translator_{timestamp}.log"
    
    def set_ui_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """設定 UI 回呼函式"""
        self._ui_callback = callback
    
    def _should_log(self, level: LogLevel) -> bool:
        """判斷是否應記錄此級別"""
        level_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.SUCCESS, LogLevel.WARN, LogLevel.ERROR]
        return level_order.index(level) >= level_order.index(self.min_level)
    
    def _log(self, level: LogLevel, module: str, message: str) -> None:
        """內部日誌記錄方法"""
        if not self._should_log(level):
            return
            
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            module=module,
            message=message
        )
        
        self._entries.append(entry)
        formatted = entry.format()
        
        # 控制台輸出
        if self.console_logging:
            print(formatted)
        
        # 檔案輸出
        if self.file_logging and self._log_file:
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(formatted + '\n')
        
        # UI 回呼
        if self._ui_callback:
            self._ui_callback(entry)
    
    def debug(self, module: str, message: str) -> None:
        """記錄 DEBUG 日誌"""
        self._log(LogLevel.DEBUG, module, message)
    
    def info(self, module: str, message: str) -> None:
        """記錄 INFO 日誌"""
        self._log(LogLevel.INFO, module, message)
    
    def warn(self, module: str, message: str) -> None:
        """記錄 WARN 日誌"""
        self._log(LogLevel.WARN, module, message)
    
    def error(self, module: str, message: str) -> None:
        """記錄 ERROR 日誌"""
        self._log(LogLevel.ERROR, module, message)
    
    def success(self, module: str, message: str) -> None:
        """記錄 SUCCESS 日誌"""
        self._log(LogLevel.SUCCESS, module, message)
    
    def get_entries(self, level: Optional[LogLevel] = None) -> List[LogEntry]:
        """取得日誌項目"""
        if level:
            return [e for e in self._entries if e.level == level]
        return self._entries.copy()
    
    def get_log_file_path(self) -> Optional[Path]:
        """取得日誌檔案路徑"""
        return self._log_file
    
    def export_log(self, path: Path) -> None:
        """匯出日誌到指定路徑"""
        with open(path, 'w', encoding='utf-8') as f:
            for entry in self._entries:
                f.write(entry.format() + '\n')
    
    def clear(self) -> None:
        """清除記憶體中的日誌"""
        self._entries.clear()
    
    def get_summary(self) -> dict:
        """取得執行摘要"""
        summary = {
            'total': len(self._entries),
            'debug': 0,
            'info': 0,
            'success': 0,
            'warn': 0,
            'error': 0,
        }
        
        for entry in self._entries:
            summary[entry.level.value.lower()] += 1
        
        return summary
