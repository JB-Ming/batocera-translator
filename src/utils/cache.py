# 全局快取管理器
"""
提供持久化快取功能，使用 SQLite 儲存翻譯結果。
避免重複查詢相同內容，大幅提升效能。
"""
import sqlite3
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from threading import Lock

from .file_utils import get_app_data_dir


class GlobalCache:
    """
    全局快取管理器

    功能：
    - SQLite 持久化快取
    - 多執行緒安全
    - 自動過期清理
    - LRU 記憶體快取

    快取鍵格式：service|query|language
    例如：wikipedia|Super Mario Bros|zh-TW
    """

    def __init__(self, cache_file: Optional[Path] = None,
                 max_age_days: int = 30,
                 memory_cache_size: int = 1000):
        """
        初始化快取管理器

        Args:
            cache_file: 快取檔案路徑，None 使用預設位置
            max_age_days: 快取過期天數
            memory_cache_size: 記憶體快取大小
        """
        if cache_file is None:
            cache_dir = get_app_data_dir() / 'cache'
            cache_dir.mkdir(exist_ok=True)
            cache_file = cache_dir / 'translation_cache.db'

        self.cache_file = cache_file
        self.max_age_days = max_age_days
        self.memory_cache_size = memory_cache_size

        # 記憶體快取（LRU）
        self._memory_cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self._lock = Lock()

        # 初始化資料庫
        self._init_db()

    def _init_db(self):
        """初始化資料庫結構"""
        with sqlite3.connect(self.cache_file) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    service TEXT NOT NULL,
                    query TEXT NOT NULL,
                    language TEXT NOT NULL,
                    result TEXT,
                    created_at INTEGER NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
            ''')

            # 建立索引加速查詢
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_service_query 
                ON cache(service, query, language)
            ''')

            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON cache(created_at)
            ''')

            conn.commit()

    def _make_key(self, service: str, query: str, language: str) -> str:
        """生成快取鍵"""
        return f"{service}|{query}|{language}"

    def get(self, service: str, query: str, language: str) -> Optional[str]:
        """
        取得快取結果

        Args:
            service: 服務名稱（wikipedia, gemini, search, translate）
            query: 查詢內容
            language: 目標語系

        Returns:
            快取的結果，找不到返回 None
        """
        key = self._make_key(service, query, language)

        # 先查記憶體快取
        with self._lock:
            if key in self._memory_cache:
                value, timestamp = self._memory_cache[key]
                # 檢查是否過期
                if time.time() - timestamp < self.max_age_days * 86400:
                    return value
                else:
                    # 過期，從記憶體移除
                    del self._memory_cache[key]

        # 查詢資料庫
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.execute('''
                    SELECT result, created_at FROM cache 
                    WHERE key = ?
                ''', (key,))

                row = cursor.fetchone()
                if row:
                    result, created_at = row

                    # 檢查是否過期
                    age_days = (time.time() - created_at) / 86400
                    if age_days < self.max_age_days:
                        # 更新命中次數
                        conn.execute('''
                            UPDATE cache SET hit_count = hit_count + 1 
                            WHERE key = ?
                        ''', (key,))
                        conn.commit()

                        # 加入記憶體快取
                        with self._lock:
                            self._add_to_memory_cache(key, result, created_at)

                        return result
                    else:
                        # 過期，刪除
                        conn.execute('DELETE FROM cache WHERE key = ?', (key,))
                        conn.commit()

        except sqlite3.Error as e:
            print(f"快取讀取錯誤: {e}")

        return None

    def set(self, service: str, query: str, language: str, result: str):
        """
        設定快取結果

        Args:
            service: 服務名稱
            query: 查詢內容
            language: 目標語系
            result: 翻譯結果
        """
        if not result:  # 不快取空結果
            return

        key = self._make_key(service, query, language)
        timestamp = int(time.time())

        # 寫入資料庫
        try:
            with sqlite3.connect(self.cache_file) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache 
                    (key, service, query, language, result, created_at, hit_count)
                    VALUES (?, ?, ?, ?, ?, ?, COALESCE(
                        (SELECT hit_count FROM cache WHERE key = ?), 0
                    ))
                ''', (key, service, query, language, result, timestamp, key))
                conn.commit()

        except sqlite3.Error as e:
            print(f"快取寫入錯誤: {e}")

        # 加入記憶體快取
        with self._lock:
            self._add_to_memory_cache(key, result, timestamp)

    def _add_to_memory_cache(self, key: str, value: str, timestamp: float):
        """加入記憶體快取（LRU）"""
        # 如果超過大小限制，移除最舊的
        if len(self._memory_cache) >= self.memory_cache_size:
            # 找出最舊的項目
            oldest_key = min(self._memory_cache.items(),
                             key=lambda x: x[1][1])[0]
            del self._memory_cache[oldest_key]

        self._memory_cache[key] = (value, timestamp)

    def clear_expired(self):
        """清理過期快取"""
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cutoff = int(time.time() - self.max_age_days * 86400)
                conn.execute(
                    'DELETE FROM cache WHERE created_at < ?', (cutoff,))
                deleted = conn.total_changes
                conn.commit()
                return deleted

        except sqlite3.Error as e:
            print(f"快取清理錯誤: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """取得快取統計資訊"""
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(hit_count) as total_hits,
                        COUNT(DISTINCT service) as services,
                        COUNT(DISTINCT language) as languages
                    FROM cache
                ''')
                row = cursor.fetchone()

                stats = {
                    'total_entries': row[0],
                    'total_hits': row[1] or 0,
                    'services': row[2],
                    'languages': row[3],
                    'memory_cache_size': len(self._memory_cache),
                    'db_size_mb': self.cache_file.stat().st_size / 1024 / 1024
                }

                # 各服務統計
                cursor = conn.execute('''
                    SELECT service, COUNT(*), SUM(hit_count)
                    FROM cache GROUP BY service
                ''')
                stats['by_service'] = {
                    row[0]: {'count': row[1], 'hits': row[2] or 0}
                    for row in cursor.fetchall()
                }

                return stats

        except sqlite3.Error as e:
            print(f"統計資訊錯誤: {e}")
            return {}

    def clear_all(self):
        """清空所有快取"""
        try:
            with sqlite3.connect(self.cache_file) as conn:
                conn.execute('DELETE FROM cache')
                conn.commit()

            with self._lock:
                self._memory_cache.clear()

        except sqlite3.Error as e:
            print(f"清空快取錯誤: {e}")


# 全局單例
_global_cache: Optional[GlobalCache] = None
_cache_lock = Lock()


def get_global_cache() -> GlobalCache:
    """取得全局快取實例（單例模式）"""
    global _global_cache

    if _global_cache is None:
        with _cache_lock:
            if _global_cache is None:
                _global_cache = GlobalCache()

    return _global_cache
