# 主視窗模組
"""
Batocera Gamelist 翻譯工具的主視窗。
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QGroupBox, QCheckBox, QProgressBar, QFileDialog,
    QMessageBox, QStatusBar, QMenuBar, QMenu, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from pathlib import Path
from typing import Optional, List

from .progress_panel import ProgressPanel
from .log_panel import LogPanel
from .settings_dialog import SettingsDialog
from .preview_dialog import PreviewDialog
from .platform_selector import PlatformSelector
from ..utils.file_utils import get_dictionaries_dir
from ..utils.settings import SettingsManager, AppSettings


class TranslationWorker(QThread):
    """翻譯工作執行緒"""
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(dict)           # result summary
    error = pyqtSignal(str)               # error message
    log = pyqtSignal(str, str, str)       # level, module, message

    def __init__(self, roms_path: str, language: str, platforms: List[str], settings: dict):
        super().__init__()
        self.roms_path = roms_path
        self.language = language
        self.platforms = platforms
        self.settings = settings
        self._is_cancelled = False

    def run(self):
        """執行翻譯"""
        try:
            import time
            from concurrent.futures import ThreadPoolExecutor, as_completed
            from threading import Lock
            from ..core import Scanner, DictionaryManager, TranslationEngine, XmlWriter
            from ..services import WikipediaService, SearchService, TranslateService
            from ..utils import parse_gamelist, get_game_key
            from ..core.dictionary import GameEntry

            # 初始化模組
            scanner = Scanner(self.roms_path)
            dict_manager = DictionaryManager()
            translator = TranslationEngine(self.language)
            writer = XmlWriter()

            # 設定翻譯服務（將毫秒轉換為秒）
            delay_seconds = self.settings.get('request_delay', 500) / 1000.0
            wiki_service = WikipediaService(request_delay=delay_seconds)
            search_service = SearchService(request_delay=delay_seconds * 2)
            translate_service = TranslateService(request_delay=delay_seconds)

            translator.set_wiki_service(wiki_service)
            translator.set_search_service(search_service)
            translator.set_translate_api(translate_service)

            # 掃描平台
            self.log.emit("INFO", "Scanner", "開始掃描 ROM 資料夾...")
            platforms = scanner.scan()

            # 過濾平台
            if self.platforms:
                platforms = [p for p in platforms if p.name in self.platforms]
            else:
                platforms = scanner.get_platforms_with_gamelist()

            total_platforms = len(platforms)

            if total_platforms == 0:
                self.error.emit("找不到任何有 gamelist.xml 的平台")
                return

            result = {
                'platforms': 0,
                'games': 0,
                'translated': 0,
                'skipped': 0,
                'failed': 0,
            }

            for idx, platform in enumerate(platforms):
                if self._is_cancelled:
                    break

                self.log.emit("INFO", "Scanner", f"處理平台: {platform.name}")
                self.progress.emit(idx, total_platforms,
                                   f"處理平台: {platform.name}")

                # 複製到暫存區
                cache_path = scanner.copy_gamelist_to_cache(platform)

                # 解析遊戲清單
                games = parse_gamelist(cache_path)

                # 載入字典
                dictionary = dict_manager.load_dictionary(
                    self.language, platform.name)

                # 設定自動儲存頻率與多執行緒
                auto_save_interval = self.settings.get(
                    'auto_save_interval', 10)
                max_workers = self.settings.get('max_workers', 1)
                batch_size = self.settings.get('batch_size', 50)
                games_processed = 0

                # 執行緒鎖（保護字典更新）
                dict_lock = Lock()

                def translate_single_game(game):
                    """翻譯單個遊戲（執行緒安全）"""
                    import threading
                    thread_id = threading.current_thread().name
                    # 簡化執行緒名稱顯示（ThreadPoolExecutor-0_0 -> T0）
                    thread_num = thread_id.split(
                        '_')[-1] if '_' in thread_id else thread_id[-1]

                    # 顯示正在處理的遊戲（包含執行緒資訊）
                    display_name = game.name[:30] if len(
                        game.name) > 30 else game.name
                    self.progress.emit(
                        games_processed, len(games),
                        f"[執行緒-{thread_num}] {display_name}...")

                    # 建立或取得字典項目
                    game_key = get_game_key(game.path)

                    with dict_lock:
                        if game_key not in dictionary:
                            entry = GameEntry(
                                key=game_key,
                                original_name=game.name,
                                original_desc=game.desc
                            )
                            dictionary[game_key] = entry
                        else:
                            entry = dictionary[game_key]
                            # 更新原始資料（可能有變更）
                            entry.original_name = game.name
                            entry.original_desc = game.desc

                    # 翻譯（不需要鎖，每個執行緒獨立翻譯）
                    output = translator.translate_game(
                        entry,
                        translate_name=self.settings.get(
                            'translate_name', True),
                        translate_desc=self.settings.get(
                            'translate_desc', True),
                        skip_translated=self.settings.get(
                            'skip_translated', True)
                    )

                    # 更新字典（需要鎖）
                    with dict_lock:
                        if output.name:
                            entry.name = output.name
                            entry.name_source = output.name_source
                            entry.name_translated_at = time.strftime(
                                '%Y-%m-%dT%H:%M:%S')
                        if output.desc:
                            entry.desc = output.desc
                            entry.desc_source = output.desc_source
                            entry.desc_translated_at = time.strftime(
                                '%Y-%m-%dT%H:%M:%S')

                        # 更新原文 hash
                        entry.update_hashes()

                    # 返回結果（包含執行緒資訊用於日誌）
                    return (output.result.value, thread_num, game.name)

                # 使用執行緒池翻譯
                if max_workers > 1:
                    self.log.emit("INFO", "Translator",
                                  f"🔥 啟用多執行緒：{max_workers} 個 worker，批次大小：{batch_size}")

                    # 記錄使用的執行緒
                    active_threads = set()

                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # 批次提交任務
                        for i in range(0, len(games), batch_size):
                            if self._is_cancelled:
                                break

                            batch = games[i:i + batch_size]
                            futures = {executor.submit(
                                translate_single_game, game): game for game in batch}

                            for future in as_completed(futures):
                                if self._is_cancelled:
                                    break

                                try:
                                    status, thread_num, game_name = future.result()

                                    # 記錄執行緒使用情況
                                    active_threads.add(thread_num)

                                    # 每成功處理一個遊戲，記錄日誌（顯示執行緒）
                                    if status == 'success':
                                        result['translated'] += 1
                                        self.log.emit("SUCCESS", "Thread",
                                                      f"[T{thread_num}] ✓ {game_name[:40]}")
                                    elif status == 'skipped':
                                        result['skipped'] += 1
                                    else:
                                        result['failed'] += 1

                                    result['games'] += 1
                                    games_processed += 1

                                    # 每10個遊戲顯示多執行緒狀態
                                    if games_processed % 10 == 0 and len(active_threads) > 1:
                                        self.log.emit("INFO", "Threads",
                                                      f"✓ 多執行緒運作中：已使用 {len(active_threads)} 個執行緒")

                                    # 自動儲存
                                    if games_processed % auto_save_interval == 0:
                                        dict_manager.save_dictionary(
                                            self.language, platform.name, dictionary)
                                        self.log.emit(
                                            "INFO", "Dictionary", f"自動儲存進度 ({games_processed}/{len(games)})")

                                except Exception as e:
                                    self.log.emit(
                                        "ERROR", "Translator", f"翻譯失敗: {str(e)}")
                                    result['failed'] += 1

                    # 多執行緒總結
                    if len(active_threads) > 0:
                        self.log.emit("SUCCESS", "Threads",
                                      f"✓ 多執行緒完成：共使用了 {len(active_threads)} 個不同的執行緒")
                else:
                    # 單執行緒模式（原有邏輯）
                    self.log.emit("INFO", "Translator", "使用單執行緒模式")
                    for game in games:
                        if self._is_cancelled:
                            break

                        status, thread_num, game_name = translate_single_game(
                            game)
                        result['games'] += 1
                        games_processed += 1

                        if status == 'success':
                            result['translated'] += 1
                        elif status == 'skipped':
                            result['skipped'] += 1
                        else:
                            result['failed'] += 1

                        # 自動儲存（避免資料遺失）
                        if games_processed % auto_save_interval == 0:
                            dict_manager.save_dictionary(
                                self.language, platform.name, dictionary)
                            self.log.emit(
                                "INFO", "Dictionary", f"自動儲存進度 ({games_processed}/{len(games)})")

                # 最終儲存
                dict_manager.save_dictionary(
                    self.language, platform.name, dictionary)

                # 寫回 XML（如果設定允許）
                if self.settings.get('write_back', True) and platform.gamelist_path:
                    writer.write_translations(
                        platform.gamelist_path,
                        dictionary,
                        platform.name,
                        auto_backup=self.settings.get('auto_backup', True)
                    )

                result['platforms'] += 1

            # 翻譯完成，將快取批次寫入資料庫
            from ..utils.cache import get_global_cache
            cache = get_global_cache()
            cached_count = cache.flush_to_db()
            if cached_count > 0:
                self.log.emit("SUCCESS", "Cache",
                              f"✓ 快取持久化完成：{cached_count} 項")

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        """取消翻譯"""
        self._is_cancelled = True


class StageWorker(QThread):
    """階段工作執行緒基底類別"""
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(dict)           # result summary
    error = pyqtSignal(str)               # error message
    log = pyqtSignal(str, str, str)       # level, module, message

    def __init__(self):
        super().__init__()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True


class ScanWorker(StageWorker):
    """階段一：掃描取回 Worker"""

    def __init__(self, roms_path: str, selected_platforms: List[str] = None):
        super().__init__()
        self.roms_path = roms_path
        self.selected_platforms = selected_platforms or []  # 空清單表示全部

    def run(self):
        try:
            from ..core import Scanner

            self.log.emit("INFO", "Stage1", "開始階段一：掃描與取回...")
            self.progress.emit(0, 100, "正在掃描 ROM 資料夾...")

            scanner = Scanner(self.roms_path)
            platforms = scanner.scan()

            self.log.emit("INFO", "Stage1", f"發現 {len(platforms)} 個資料夾")
            self.progress.emit(30, 100, f"發現 {len(platforms)} 個資料夾")

            platforms_with_gamelist = scanner.get_platforms_with_gamelist()

            # 遞取選中的平台
            if self.selected_platforms:
                platforms_with_gamelist = [
                    p for p in platforms_with_gamelist
                    if p.name in self.selected_platforms
                ]
                self.log.emit("INFO", "Stage1",
                              f"選中 {len(platforms_with_gamelist)} 個平台進行處理")

            self.log.emit("INFO", "Stage1",
                          f"有 gamelist.xml 的平台: {len(platforms_with_gamelist)}")
            self.progress.emit(50, 100, "正在複製 gamelist.xml 到暫存區...")

            # 複製到暫存區
            copied = []
            total = len(platforms_with_gamelist)
            for i, platform in enumerate(platforms_with_gamelist):
                if self._is_cancelled:
                    break

                scanner.copy_gamelist_to_cache(platform)
                copied.append(platform.name)

                progress = 50 + int((i + 1) / total * 50) if total > 0 else 100
                self.progress.emit(
                    progress, 100, f"複製: {platform.name} ({i+1}/{total})")
                self.log.emit("INFO", "Stage1", f"  複製: {platform.name}")

            self.progress.emit(100, 100, "階段一完成！")
            self.log.emit("SUCCESS", "Stage1",
                          f"階段一完成！複製 {len(copied)} 個 gamelist.xml 到暫存區")

            self.finished.emit({'copied': len(copied)})

        except Exception as e:
            self.error.emit(str(e))


class DictionaryWorker(StageWorker):
    """階段二：產生字典 Worker"""

    def __init__(self, language: str, selected_platforms: List[str] = None):
        super().__init__()
        self.language = language
        self.selected_platforms = selected_platforms or []  # 空清單表示全部

    def run(self):
        try:
            from ..core import DictionaryManager
            from ..utils import parse_gamelist, get_game_key
            from ..core.dictionary import GameEntry

            self.log.emit("INFO", "Stage2", "開始階段二：產生字典檔...")
            self.progress.emit(0, 100, "正在掃描暫存區...")

            gamelists_dir = Path('./gamelists_local')
            if not gamelists_dir.exists():
                self.error.emit("請先執行階段一（掃描取回）")
                return

            dict_manager = DictionaryManager()

            # 收集所有平台
            platform_dirs = [d for d in gamelists_dir.iterdir(
            ) if d.is_dir() and (d / 'gamelist.xml').exists()]

            # 過濾選中的平台
            if self.selected_platforms:
                platform_dirs = [
                    d for d in platform_dirs if d.name in self.selected_platforms]
                self.log.emit("INFO", "Stage2",
                              f"選中 {len(platform_dirs)} 個平台進行處理")

            total_platforms = len(platform_dirs)
            total_games = 0

            for i, platform_dir in enumerate(platform_dirs):
                if self._is_cancelled:
                    break

                platform_name = platform_dir.name
                gamelist_path = platform_dir / 'gamelist.xml'

                self.progress.emit(int((i / total_platforms) * 100)
                                   if total_platforms > 0 else 100, 100, f"處理平台: {platform_name}")

                games = parse_gamelist(gamelist_path)
                dictionary = dict_manager.load_dictionary(
                    self.language, platform_name)

                for game in games:
                    key = get_game_key(game.path)
                    if key not in dictionary:
                        entry = GameEntry(
                            key=key,
                            original_name=game.name,
                            original_desc=game.desc
                        )
                        dictionary[key] = entry

                dict_manager.save_dictionary(
                    self.language, platform_name, dictionary)

                self.log.emit("INFO", "Stage2",
                              f"  {platform_name}: {len(dictionary)} 個遊戲")
                total_games += len(dictionary)

            self.progress.emit(100, 100, "階段二完成！")
            self.log.emit("SUCCESS", "Stage2",
                          f"階段二完成！{total_platforms} 個平台, {total_games} 個遊戲")

            self.finished.emit(
                {'platforms': total_platforms, 'games': total_games})

        except Exception as e:
            self.error.emit(str(e))


class TranslateWorker(StageWorker):
    """階段三：翻譯 Worker"""

    def __init__(self, language: str, translate_name: bool, translate_desc: bool, skip_translated: bool, selected_platforms: List[str] = None, gemini_api_key: str = "", request_delay: int = 500):
        super().__init__()
        self.language = language
        self.translate_name = translate_name
        self.translate_desc = translate_desc
        self.skip_translated = skip_translated
        self.selected_platforms = selected_platforms or []  # 空清單表示全部
        self.gemini_api_key = gemini_api_key
        self.request_delay = request_delay  # API 請求間隔（毫秒）

    def run(self):
        try:
            from ..core import DictionaryManager, TranslationEngine
            from ..services import WikipediaService, SearchService, TranslateService

            self.log.emit("INFO", "Stage3", "開始階段三：翻譯...")
            self.progress.emit(0, 100, "正在初始化翻譯服務...")

            dict_manager = DictionaryManager()
            lang_dir = get_dictionaries_dir() / self.language

            if not lang_dir.exists():
                self.error.emit("請先執行階段二（產生字典）")
                return

            platforms = [f.stem for f in lang_dir.glob('*.json')]

            # 過濾選中的平台
            if self.selected_platforms:
                platforms = [
                    p for p in platforms if p in self.selected_platforms]
                self.log.emit("INFO", "Stage3", f"選中 {len(platforms)} 個平台進行翻譯")

            # 按遊戲數量排序（從少到多），優先翻譯遊戲少的平台
            platform_sizes = {}
            for platform in platforms:
                dictionary = dict_manager.load_dictionary(
                    self.language, platform)
                platform_sizes[platform] = len(dictionary)

            # 排序：遊戲數量少的優先
            platforms = sorted(
                platforms, key=lambda p: platform_sizes.get(p, 0))
            self.log.emit("INFO", "Stage3",
                          f"平台處理順序（按遊戲數量）: {', '.join([f'{p}({platform_sizes[p]})' for p in platforms[:5]])}{'...' if len(platforms) > 5 else ''}")

            # 初始化翻譯引擎
            translator = TranslationEngine(target_language=self.language)
            # 將毫秒轉換為秒
            delay_seconds = self.request_delay / 1000.0
            translator.set_wiki_service(
                WikipediaService(request_delay=delay_seconds))
            translator.set_search_service(SearchService(
                request_delay=delay_seconds * 2))  # 搜尋服務延遲加倍
            translator.set_translate_api(
                TranslateService(request_delay=delay_seconds))

            # 如果有 Gemini API Key，初始化 Gemini 服務
            if self.gemini_api_key:
                try:
                    from ..services.gemini import GeminiService
                    gemini = GeminiService(self.gemini_api_key)
                    translator.set_gemini_service(gemini)
                    self.log.emit("INFO", "Stage3", "Gemini AI 服務已啟用")
                except Exception as e:
                    self.log.emit("WARNING", "Stage3", f"Gemini 服務初始化失敗: {e}")

            self.progress.emit(5, 100, "翻譯服務初始化完成")

            total_translated = 0
            total_entries = sum(platform_sizes.values())  # 使用已計算的數量
            processed_entries = 0

            self.log.emit("INFO", "Stage3",
                          f"共 {len(platforms)} 個平台, {total_entries} 個遊戲待處理")

            import time
            start_time = time.time()

            # 讀取性能設定
            from ..utils.settings import SettingsManager
            settings_mgr = SettingsManager()
            settings = settings_mgr.load()
            max_workers = settings.max_workers

            # 決定是否使用多執行緒
            use_multithreading = max_workers > 1
            if use_multithreading:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                from threading import Lock
                self.log.emit("INFO", "Stage3",
                              f"🔥 啟用多執行緒：{max_workers} 個 worker")

            for platform in platforms:
                if self._is_cancelled:
                    break

                dictionary = dict_manager.load_dictionary(
                    self.language, platform)
                platform_translated = 0

                entries_list = list(dictionary.values())

                if use_multithreading and len(entries_list) > 5:
                    # 多執行緒模式
                    dict_lock = Lock()
                    active_threads = set()

                    def translate_entry(entry, idx):
                        """翻譯單個條目（執行緒安全）"""
                        import threading
                        thread_id = threading.current_thread().name
                        thread_num = thread_id.split(
                            '_')[-1] if '_' in thread_id else thread_id[-1]

                        nonlocal processed_entries

                        # 更新進度（顯示執行緒資訊）
                        with dict_lock:
                            processed_entries += 1
                            progress = 5 + \
                                int((processed_entries / total_entries)
                                    * 90) if total_entries > 0 else 100

                        # 計算 ETA
                        elapsed = time.time() - start_time
                        if processed_entries > 0:
                            avg_time_per_entry = elapsed / processed_entries
                            remaining_entries = total_entries - processed_entries
                            eta_seconds = int(
                                avg_time_per_entry * remaining_entries)
                            if eta_seconds > 3600:
                                eta_str = f"約 {eta_seconds // 3600} 小時 {(eta_seconds % 3600) // 60} 分鐘"
                            elif eta_seconds > 60:
                                eta_str = f"約 {eta_seconds // 60} 分鐘"
                            else:
                                eta_str = f"約 {eta_seconds} 秒"
                        else:
                            eta_str = "計算中..."

                        display_name = entry.original_name[:25] if len(
                            entry.original_name) > 25 else entry.original_name
                        self.progress.emit(progress, 100,
                                           f"[T{thread_num}] [{platform}] {display_name}... ({processed_entries}/{total_entries}, 剩餘 {eta_str})")

                        # 檢查是否需要強制重新翻譯
                        force_retranslate = entry.needs_retranslate
                        actual_skip_translated = self.skip_translated and not force_retranslate

                        # 如果是重翻，記錄日誌
                        if force_retranslate:
                            self.log.emit("INFO", "Stage3",
                                          f"[T{thread_num}] 🔄 重翻：{entry.original_name}")

                        # 翻譯
                        output = translator.translate_game(
                            entry,
                            translate_name=self.translate_name,
                            translate_desc=self.translate_desc,
                            skip_translated=actual_skip_translated
                        )

                        # 更新結果
                        translated = False
                        with dict_lock:
                            if output.name:
                                entry.name = output.name
                                entry.name_source = output.name_source
                                entry.name_translated_at = time.strftime(
                                    '%Y-%m-%dT%H:%M:%S')
                                translated = True
                                if force_retranslate:
                                    self.log.emit("SUCCESS", "Stage3",
                                                  f"[T{thread_num}] ✓ 重翻名稱：{entry.original_name} → {output.name}")
                            if output.desc:
                                entry.desc = output.desc
                                entry.desc_source = output.desc_source
                                entry.desc_translated_at = time.strftime(
                                    '%Y-%m-%dT%H:%M:%S')
                                translated = True
                                if force_retranslate:
                                    desc_preview = output.desc[:50] + "..." if len(
                                        output.desc) > 50 else output.desc
                                    self.log.emit("SUCCESS", "Stage3",
                                                  f"[T{thread_num}] ✓ 重翻描述：{entry.original_name} - {desc_preview}")

                            # 翻譯完成後清除重翻標記
                            if force_retranslate and (output.name or output.desc):
                                entry.needs_retranslate = False

                            # 更新原文 hash
                            entry.update_hashes()

                        if translated:
                            self.log.emit("INFO", "Stage3",
                                          f"[T{thread_num}] ✓ {entry.original_name} → {output.name} ({output.name_source})")

                        return (translated, thread_num)

                    # 使用執行緒池處理
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = {executor.submit(translate_entry, entry, idx): entry
                                   for idx, entry in enumerate(entries_list)}

                        for future in as_completed(futures):
                            if self._is_cancelled:
                                break
                            try:
                                translated, thread_num = future.result()
                                active_threads.add(thread_num)
                                if translated:
                                    platform_translated += 1
                            except Exception as e:
                                import traceback
                                error_details = traceback.format_exc()
                                self.log.emit("ERROR", "Stage3",
                                              f"翻譯失敗: {str(e)}")
                                self.log.emit("ERROR", "Stage3",
                                              f"詳細錯誤:\n{error_details}")

                    # 顯示多執行緒總結
                    if len(active_threads) > 0:
                        self.log.emit("SUCCESS", "Stage3",
                                      f"[{platform}] 多執行緒完成：使用了 {len(active_threads)} 個執行緒，翻譯 {platform_translated} 個遊戲")
                else:
                    # 單執行緒模式（遊戲數量少或max_workers=1）
                    for entry in entries_list:
                        if self._is_cancelled:
                            break

                        processed_entries += 1
                        progress = 5 + \
                            int((processed_entries / total_entries)
                                * 90) if total_entries > 0 else 100

                        # 計算預估剩餘時間
                        elapsed = time.time() - start_time
                        if processed_entries > 0:
                            avg_time_per_entry = elapsed / processed_entries
                            remaining_entries = total_entries - processed_entries
                            eta_seconds = int(
                                avg_time_per_entry * remaining_entries)

                            if eta_seconds > 3600:
                                eta_str = f"約 {eta_seconds // 3600} 小時 {(eta_seconds % 3600) // 60} 分鐘"
                            elif eta_seconds > 60:
                                eta_str = f"約 {eta_seconds // 60} 分鐘"
                            else:
                                eta_str = f"約 {eta_seconds} 秒"
                        else:
                            eta_str = "計算中..."

                        self.progress.emit(
                            progress, 100, f"[{platform}] {entry.original_name[:25]}... ({processed_entries}/{total_entries}, 剩餘 {eta_str})")

                        # 檢查是否需要強制重新翻譯
                        force_retranslate = entry.needs_retranslate
                        actual_skip_translated = self.skip_translated and not force_retranslate

                        output = translator.translate_game(
                            entry,
                            translate_name=self.translate_name,
                            translate_desc=self.translate_desc,
                            skip_translated=actual_skip_translated
                        )

                        if output.name:
                            entry.name = output.name
                            entry.name_source = output.name_source
                            entry.name_translated_at = time.strftime(
                                '%Y-%m-%dT%H:%M:%S')
                            platform_translated += 1
                            self.log.emit(
                                "INFO", "Stage3", f"  ✓ {entry.original_name} → {output.name} ({output.name_source})")
                        if output.desc:
                            entry.desc = output.desc
                            entry.desc_source = output.desc_source
                            entry.desc_translated_at = time.strftime(
                                '%Y-%m-%dT%H:%M:%S')

                        # 翻譯完成後清除重翻標記
                        if force_retranslate and (output.name or output.desc):
                            entry.needs_retranslate = False

                        # 更新原文 hash（用於偵測原文變更）
                        entry.update_hashes()

                dict_manager.save_dictionary(
                    self.language, platform, dictionary)
                self.log.emit("INFO", "Stage3",
                              f"  {platform}: 翻譯 {platform_translated} 個")
                total_translated += platform_translated

            # 翻譯完成，將快取批次寫入資料庫
            from ..utils.cache import get_global_cache
            cache = get_global_cache()
            cached_count = cache.flush_to_db()
            if cached_count > 0:
                self.log.emit("SUCCESS", "Cache",
                              f"✓ 快取持久化完成：{cached_count} 項")

            self.progress.emit(100, 100, "階段三完成！")
            self.log.emit("SUCCESS", "Stage3",
                          f"階段三完成！翻譯 {total_translated} 個遊戲")

            self.finished.emit({'translated': total_translated})

        except Exception as e:
            self.error.emit(str(e))


class WritebackWorker(StageWorker):
    """階段四：寫回 Worker"""

    def __init__(self, language: str, auto_backup: bool, selected_platforms: List[str] = None):
        super().__init__()
        self.language = language
        self.auto_backup = auto_backup
        self.selected_platforms = selected_platforms or []  # 空清單表示全部

    def run(self):
        try:
            from ..core import DictionaryManager, XmlWriter
            from ..core.writer import DisplayFormat

            self.log.emit("INFO", "Stage4", "開始階段四：寫回 XML...")
            self.progress.emit(0, 100, "正在準備寫回...")

            dict_manager = DictionaryManager()
            writer = XmlWriter()

            gamelists_dir = Path('./gamelists_local')
            if not gamelists_dir.exists():
                self.error.emit("請先執行階段一（掃描取回）")
                return

            platform_dirs = [d for d in gamelists_dir.iterdir(
            ) if d.is_dir() and (d / 'gamelist.xml').exists()]

            # 過濾選中的平台
            if self.selected_platforms:
                platform_dirs = [
                    d for d in platform_dirs if d.name in self.selected_platforms]
                self.log.emit("INFO", "Stage4",
                              f"選中 {len(platform_dirs)} 個平台進行寫回")

            total = len(platform_dirs)
            total_updated = 0

            for i, platform_dir in enumerate(platform_dirs):
                if self._is_cancelled:
                    break

                platform_name = platform_dir.name
                gamelist_path = platform_dir / 'gamelist.xml'

                progress = int((i / total) * 100) if total > 0 else 100
                self.progress.emit(progress, 100, f"寫回: {platform_name}")

                dictionary = dict_manager.load_dictionary(
                    self.language, platform_name)

                if dictionary:
                    result = writer.write_translations(
                        xml_path=gamelist_path,
                        dictionary=dictionary,
                        platform=platform_name,
                        display_format=DisplayFormat.TRANSLATED_ONLY,
                        auto_backup=self.auto_backup
                    )

                    self.log.emit("INFO", "Stage4",
                                  f"  {platform_name}: 更新 {result.updated} 個")
                    total_updated += result.updated

            self.progress.emit(100, 100, "階段四完成！")
            self.log.emit("SUCCESS", "Stage4", f"階段四完成！更新 {total_updated} 個遊戲")

            self.finished.emit({'updated': total_updated})

        except Exception as e:
            self.error.emit(str(e))


class GeminiBatchWorker(StageWorker):
    """Gemini 批次翻譯 Worker"""

    def __init__(self, language: str, selected_platforms: List[str] = None,
                 gemini_api_key: str = "", batch_size: int = 80,
                 translate_name: bool = True):
        super().__init__()
        self.language = language
        self.selected_platforms = selected_platforms or []
        self.gemini_api_key = gemini_api_key
        self.batch_size = batch_size
        self.translate_name = translate_name

    def run(self):
        try:
            import time
            from ..core import DictionaryManager
            from ..services.gemini_batch import GeminiBatchService
            from ..core.dictionary import TranslationSource

            self.log.emit("INFO", "GeminiBatch", "開始 Gemini 批次翻譯...")
            self.progress.emit(0, 100, "正在初始化...")

            # 檢查 API Key
            if not self.gemini_api_key:
                self.error.emit("請先設定 Gemini API Key")
                return

            # 初始化服務
            dict_manager = DictionaryManager()
            lang_dir = get_dictionaries_dir() / self.language

            if not lang_dir.exists():
                self.error.emit("請先執行階段二（產生字典）")
                return

            # 初始化 Gemini 批次服務
            try:
                gemini_batch = GeminiBatchService(
                    api_key=self.gemini_api_key,
                    batch_size=self.batch_size,
                    request_delay=1.0  # 批次模式可以稍微放寬間隔
                )
            except Exception as e:
                self.error.emit(f"Gemini 服務初始化失敗: {e}")
                return

            # 取得平台列表
            platforms = [f.stem for f in lang_dir.glob('*.json')]
            if self.selected_platforms:
                platforms = [
                    p for p in platforms if p in self.selected_platforms]

            self.log.emit("INFO", "GeminiBatch", f"將處理 {len(platforms)} 個平台")

            # 計算總遊戲數
            total_games = 0
            platform_games = {}  # {platform: [(key, entry), ...]}

            for platform in platforms:
                dictionary = dict_manager.load_dictionary(
                    self.language, platform)
                games_to_translate = []
                for key, entry in dictionary.items():
                    # 只處理需要翻譯名稱的項目
                    if self.translate_name and not entry.name:
                        games_to_translate.append((key, entry))
                    # 或者標記為需要重翻的
                    elif entry.needs_retranslate:
                        games_to_translate.append((key, entry))

                if games_to_translate:
                    platform_games[platform] = games_to_translate
                    total_games += len(games_to_translate)

            if total_games == 0:
                self.log.emit("INFO", "GeminiBatch", "沒有需要翻譯的遊戲")
                self.progress.emit(100, 100, "完成！沒有需要翻譯的項目")
                self.finished.emit({
                    'total': 0,
                    'translated': 0,
                    'failed': 0
                })
                return

            self.log.emit("INFO", "GeminiBatch",
                          f"共 {total_games} 個遊戲待翻譯，批次大小 {self.batch_size}")
            self.progress.emit(5, 100, f"準備處理 {len(platform_games)} 個平台...")

            # 按平台分別翻譯（這樣可以傳入平台名稱提升準確度）
            start_time = time.time()
            total_translated = 0
            total_failed = 0
            processed_games = 0
            failed_entries = []

            for platform_idx, (platform, games) in enumerate(platform_games.items()):
                if self._is_cancelled:
                    break

                self.log.emit("INFO", "GeminiBatch",
                              f"[{platform_idx + 1}/{len(platform_games)}] 處理平台: {platform} ({len(games)} 個遊戲)")

                # 取得遊戲名稱列表
                game_names = [entry.original_name for _, entry in games]

                # 建立名稱到 (key, entry) 的對照表
                name_to_info = {}
                for key, entry in games:
                    if entry.original_name not in name_to_info:
                        name_to_info[entry.original_name] = []
                    name_to_info[entry.original_name].append((key, entry))

                # 去重複
                unique_names = list(name_to_info.keys())

                # 定義進度回呼
                def progress_callback(current, total, message):
                    overall_progress = 5 + int(
                        ((processed_games + current) / total_games) * 90
                    ) if total_games > 0 else 100
                    self.progress.emit(overall_progress, 100,
                                       f"[{platform}] {message}")

                # 執行批次翻譯（傳入平台名稱）
                result = gemini_batch.translate_all(
                    unique_names,
                    self.language,
                    platform=platform,  # 傳入平台名稱
                    progress_callback=progress_callback
                )

                # 載入字典準備更新
                dictionary = dict_manager.load_dictionary(
                    self.language, platform)

                # 更新成功的翻譯
                for name, translation in result.translations.items():
                    if name in name_to_info:
                        for key, entry in name_to_info[name]:
                            if key in dictionary:
                                dict_entry = dictionary[key]
                                dict_entry.name = translation
                                dict_entry.name_source = "gemini_batch"
                                dict_entry.name_translated_at = time.strftime(
                                    '%Y-%m-%dT%H:%M:%S')
                                dict_entry.needs_retranslate = False
                                dict_entry.update_hashes()
                                total_translated += 1
                                self.log.emit("SUCCESS", "GeminiBatch",
                                              f"✓ [{platform}] {entry.original_name} → {translation}")

                # 標記失敗的項目
                for name in result.failed:
                    if name in name_to_info:
                        for key, entry in name_to_info[name]:
                            if key in dictionary:
                                dictionary[key].needs_retranslate = True
                                failed_entries.append(
                                    f"{platform}/{entry.original_name}")
                                total_failed += 1

                # 儲存字典
                dict_manager.save_dictionary(
                    self.language, platform, dictionary)

                processed_games += len(games)
                self.log.emit("INFO", "GeminiBatch",
                              f"[{platform}] 完成：成功 {result.success_count}，失敗 {len(result.failed)}")

            elapsed = time.time() - start_time
            self.log.emit("INFO", "GeminiBatch",
                          f"批次翻譯完成，耗時 {elapsed:.1f} 秒")

            # 將快取寫入資料庫
            from ..utils.cache import get_global_cache
            cache = get_global_cache()
            cached_count = cache.flush_to_db()
            if cached_count > 0:
                self.log.emit("SUCCESS", "Cache",
                              f"✓ 快取持久化完成：{cached_count} 項")

            # 完成
            self.progress.emit(100, 100, "Gemini 批次翻譯完成！")

            summary = (
                f"翻譯成功：{total_translated} 個\n"
                f"翻譯失敗：{total_failed} 個（已標記重翻）"
            )
            self.log.emit("SUCCESS", "GeminiBatch", summary)

            if failed_entries and len(failed_entries) <= 10:
                self.log.emit("WARNING", "GeminiBatch",
                              f"失敗項目：\n  " + "\n  ".join(failed_entries))
            elif failed_entries:
                self.log.emit("WARNING", "GeminiBatch",
                              f"失敗項目共 {len(failed_entries)} 個，前 10 個：\n  " +
                              "\n  ".join(failed_entries[:10]))

            self.finished.emit({
                'total': total_games,
                'translated': total_translated,
                'failed': total_failed
            })

        except Exception as e:
            import traceback
            self.log.emit("ERROR", "GeminiBatch", f"錯誤: {e}")
            self.log.emit("ERROR", "GeminiBatch", traceback.format_exc())
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """
    主視窗

    包含：
    - 路徑設定區域
    - 語系選擇
    - 平台選擇
    - 開始/取消按鈕
    - 進度顯示
    - 日誌面板
    """

    def __init__(self):
        super().__init__()
        self.worker: Optional[TranslationWorker] = None

        # 載入設定
        self.settings_manager = SettingsManager()
        self.app_settings = self.settings_manager.load()
        self.settings = self._settings_to_dict()

        self._init_ui()
        self._load_settings_to_ui()

    def _settings_to_dict(self) -> dict:
        """將 AppSettings 轉換為 dict 供舊程式碼使用"""
        return {
            'translate_name': self.app_settings.translate_name,
            'translate_desc': self.app_settings.translate_desc,
            'skip_translated': self.app_settings.skip_translated,
            'write_back': self.app_settings.write_back,
            'auto_backup': self.app_settings.auto_backup,
            'translate_api': self.app_settings.translate_api,
            'api_key': self.app_settings.get_api_key(),  # 使用含優先順序的方法
            'gemini_api_key': self.app_settings.get_gemini_api_key(),  # 使用含優先順序的方法
            'use_gemini_batch': self.app_settings.use_gemini_batch,
            'gemini_batch_size': self.app_settings.gemini_batch_size,
            'request_delay': self.app_settings.request_delay,
            'max_workers': self.app_settings.max_workers,
            'batch_size': self.app_settings.batch_size,
            'auto_save_interval': self.app_settings.auto_save_interval,
        }

    def _default_settings(self) -> dict:
        """預設設定"""
        return {
            'translate_name': True,
            'translate_desc': False,
            'skip_translated': True,
            'write_back': True,
            'auto_backup': True,
            'translate_api': 'googletrans',
            'api_key': '',
            'gemini_api_key': '',
        }

    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("Batocera Gamelist 翻譯工具 v1.1")
        self.setMinimumSize(900, 700)

        # 設定視窗圖示
        icon_path = Path(__file__).parent.parent.parent / \
            'assets' / 'app_icon.ico'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # 建立選單
        self._create_menu()

        # 主要佈局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 路徑設定區域
        path_group = QGroupBox("路徑設定")
        path_layout = QHBoxLayout(path_group)

        path_layout.addWidget(QLabel("ROM 目錄:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("選擇你的 Batocera ROM 目錄...")
        path_layout.addWidget(self.path_input, stretch=1)

        browse_btn = QPushButton("瀏覽...")
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_btn)

        # 路徑變更時自動掃描
        self.path_input.textChanged.connect(self._on_path_changed)

        main_layout.addWidget(path_group)

        # 平台選擇區域
        self.platform_selector = PlatformSelector()
        self.platform_selector.selection_changed.connect(
            self._on_platform_selection_changed)
        main_layout.addWidget(self.platform_selector)

        # 儲存選擇的平台
        self.selected_platforms: List[str] = []

        # 語系與選項
        options_layout = QHBoxLayout()

        # 語系選擇
        lang_group = QGroupBox("目標語系")
        lang_layout = QHBoxLayout(lang_group)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "繁體中文 (zh-TW)",
            "簡體中文 (zh-CN)",
            "日文 (ja)",
            "韓文 (ko)",
        ])
        lang_layout.addWidget(self.lang_combo)
        options_layout.addWidget(lang_group)

        # 翻譯選項
        translate_group = QGroupBox("翻譯選項")
        translate_layout = QVBoxLayout(translate_group)

        self.name_checkbox = QCheckBox("翻譯遊戲名稱")
        self.name_checkbox.setChecked(True)
        translate_layout.addWidget(self.name_checkbox)

        self.desc_checkbox = QCheckBox("翻譯遊戲描述")
        self.desc_checkbox.setChecked(False)
        translate_layout.addWidget(self.desc_checkbox)

        self.skip_checkbox = QCheckBox("跳過已翻譯項目（取消勾選=強制重翻）")
        self.skip_checkbox.setChecked(True)
        translate_layout.addWidget(self.skip_checkbox)

        options_layout.addWidget(translate_group)

        # 寫入選項
        write_group = QGroupBox("寫入選項")
        write_layout = QVBoxLayout(write_group)

        self.writeback_checkbox = QCheckBox("寫回 gamelist.xml")
        self.writeback_checkbox.setChecked(True)
        write_layout.addWidget(self.writeback_checkbox)

        self.backup_checkbox = QCheckBox("自動備份")
        self.backup_checkbox.setChecked(True)
        write_layout.addWidget(self.backup_checkbox)

        options_layout.addWidget(write_group)

        main_layout.addLayout(options_layout)

        # 階段按鈕區域
        stage_group = QGroupBox("執行階段")
        stage_layout = QHBoxLayout(stage_group)

        self.scan_btn = QPushButton("①掃描取回")
        self.scan_btn.setToolTip("階段一：掃描 ROM 資料夾，複製 gamelist.xml 到暫存區")
        self.scan_btn.clicked.connect(self._run_stage_scan)
        stage_layout.addWidget(self.scan_btn)

        self.dict_btn = QPushButton("②產生字典")
        self.dict_btn.setToolTip("階段二：解析 gamelist.xml，產生字典檔")
        self.dict_btn.clicked.connect(self._run_stage_dictionary)
        stage_layout.addWidget(self.dict_btn)

        self.translate_btn = QPushButton("③翻譯")
        self.translate_btn.setToolTip("階段三：翻譯遊戲名稱與描述（一筆一筆翻譯）")
        self.translate_btn.clicked.connect(self._run_stage_translate)
        stage_layout.addWidget(self.translate_btn)

        self.gemini_batch_btn = QPushButton("③ Gemini批次")
        self.gemini_batch_btn.setToolTip(
            "使用 Gemini AI 批次翻譯遊戲名稱\n"
            "• 一次翻譯多個遊戲，效率高\n"
            "• 需要在設定中填入 Gemini API Key\n"
            "• 翻譯失敗的項目會標記「需要重翻」"
        )
        self.gemini_batch_btn.clicked.connect(self._run_gemini_batch)
        stage_layout.addWidget(self.gemini_batch_btn)

        self.writeback_btn = QPushButton("④寫回")
        self.writeback_btn.setToolTip("階段四：將翻譯結果寫回 gamelist.xml")
        self.writeback_btn.clicked.connect(self._run_stage_writeback)
        stage_layout.addWidget(self.writeback_btn)

        main_layout.addWidget(stage_group)

        # 主按鈕區域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.preview_btn = QPushButton("預覽模式")
        self.preview_btn.clicked.connect(self._show_preview)
        btn_layout.addWidget(self.preview_btn)

        self.settings_btn = QPushButton("設定")
        self.settings_btn.clicked.connect(self._show_settings)
        btn_layout.addWidget(self.settings_btn)

        self.start_btn = QPushButton("一鍵全部")
        self.start_btn.setMinimumWidth(120)
        self.start_btn.setToolTip("依序執行所有四個階段")
        self.start_btn.clicked.connect(self._start_translation)
        btn_layout.addWidget(self.start_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_translation)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

        # 分割面板（進度 + 日誌）
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 進度面板
        self.progress_panel = ProgressPanel()
        splitter.addWidget(self.progress_panel)

        # 日誌面板
        self.log_panel = LogPanel()
        splitter.addWidget(self.log_panel)

        splitter.setSizes([200, 300])
        main_layout.addWidget(splitter, stretch=1)

        # 狀態列
        self.statusBar().showMessage("就緒")

    def _create_menu(self):
        """建立選單"""
        menubar = self.menuBar()

        # 檔案選單
        file_menu = menubar.addMenu("檔案(&F)")

        import_action = QAction("匯入語系包...", self)
        import_action.triggered.connect(self._import_language_pack)
        file_menu.addAction(import_action)

        export_action = QAction("匯出字典...", self)
        export_action.triggered.connect(self._export_dictionary)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("結束(&X)", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 工具選單
        tools_menu = menubar.addMenu("工具(&T)")

        dict_editor_action = QAction("字典編輯器...", self)
        dict_editor_action.triggered.connect(self._show_dictionary_editor)
        tools_menu.addAction(dict_editor_action)

        tools_menu.addSeparator()

        settings_action = QAction("設定...", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)

        # 說明選單
        help_menu = menubar.addMenu("說明(&H)")

        about_action = QAction("關於", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _load_settings_to_ui(self):
        """將設定載入到 UI 元件"""
        # ROM 路徑
        if self.app_settings.last_roms_path:
            self.path_input.setText(self.app_settings.last_roms_path)

        # 語系選擇
        lang_map = {
            'zh-TW': 0,
            'zh-CN': 1,
            'ja': 2,
            'ko': 3,
        }
        lang_index = lang_map.get(self.app_settings.last_language, 0)
        self.lang_combo.setCurrentIndex(lang_index)

        # 翻譯選項
        self.name_checkbox.setChecked(self.app_settings.translate_name)
        self.desc_checkbox.setChecked(self.app_settings.translate_desc)
        self.skip_checkbox.setChecked(self.app_settings.skip_translated)

        # 寫入選項
        self.writeback_checkbox.setChecked(self.app_settings.write_back)
        self.backup_checkbox.setChecked(self.app_settings.auto_backup)

    def _save_settings(self):
        """從 UI 元件儲存設定"""
        # ROM 路徑
        self.app_settings.last_roms_path = self.path_input.text().strip()

        # 語系選擇
        self.app_settings.last_language = self._get_selected_language()

        # 翻譯選項
        self.app_settings.translate_name = self.name_checkbox.isChecked()
        self.app_settings.translate_desc = self.desc_checkbox.isChecked()
        self.app_settings.skip_translated = self.skip_checkbox.isChecked()

        # 寫入選項
        self.app_settings.write_back = self.writeback_checkbox.isChecked()
        self.app_settings.auto_backup = self.backup_checkbox.isChecked()

        # 儲存到檔案
        self.settings_manager.save(self.app_settings)

    def closeEvent(self, event):
        """視窗關閉時顯示確認對話框"""
        # 檢查是否有任務正在執行
        has_running_task = hasattr(
            self, 'stage_worker') and self.stage_worker and self.stage_worker.isRunning()

        if has_running_task:
            reply = QMessageBox.question(
                self,
                "確認關閉",
                "目前有翻譯任務正在執行中！\n\n確定要關閉程式嗎？（進度將會遺失）",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        else:
            reply = QMessageBox.question(
                self,
                "確認關閉",
                "確定要關閉 Batocera 翻譯工具嗎？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

        if reply == QMessageBox.StandardButton.Yes:
            # 如果有正在執行的任務，先取消
            if has_running_task:
                self.stage_worker.cancel()
                self.stage_worker.wait(1000)  # 等待最多1秒

            self._save_settings()
            event.accept()
        else:
            event.ignore()

    def _browse_path(self):
        """開啟資料夾選擇對話框"""
        path = QFileDialog.getExistingDirectory(self, "選擇 ROM 目錄")
        if path:
            self.path_input.setText(path)

    def _on_path_changed(self, path: str):
        """ROM 路徑變更時自動掃描平台"""
        path = path.strip()
        if not path:
            self.platform_selector.clear()
            return

        roms_path = Path(path)
        if not roms_path.exists():
            self.platform_selector.clear()
            return

        try:
            # 掃描資料夾
            platforms = []
            has_gamelist = set()

            for item in roms_path.iterdir():
                if item.is_dir():
                    platform_name = item.name
                    platforms.append(platform_name)

                    # 檢查是否有 gamelist.xml
                    gamelist_path = item / 'gamelist.xml'
                    if gamelist_path.exists():
                        has_gamelist.add(platform_name)

            self.platform_selector.set_platforms(platforms, has_gamelist)

        except Exception as e:
            self.log_panel.add_log("ERROR", "Main", f"掃描平台失敗: {e}")
            self.platform_selector.clear()

    def _on_platform_selection_changed(self, selected: List[str]):
        """平台選擇變更"""
        self.selected_platforms = selected
        count = len(selected)
        self.statusBar().showMessage(f"已選擇 {count} 個平台")

    def _get_selected_language(self) -> str:
        """取得選擇的語系代碼"""
        lang_map = {
            0: 'zh-TW',
            1: 'zh-CN',
            2: 'ja',
            3: 'ko',
        }
        return lang_map.get(self.lang_combo.currentIndex(), 'zh-TW')

    def _start_translation(self):
        """開始翻譯"""
        roms_path = self.path_input.text().strip()
        if not roms_path:
            QMessageBox.warning(self, "錯誤", "請先選擇 ROM 目錄")
            return

        if not Path(roms_path).exists():
            QMessageBox.warning(self, "錯誤", "指定的目錄不存在")
            return

        # 取得設定
        settings = {
            'translate_name': self.name_checkbox.isChecked(),
            'translate_desc': self.desc_checkbox.isChecked(),
            'skip_translated': self.skip_checkbox.isChecked(),
            'write_back': self.writeback_checkbox.isChecked(),
            'auto_backup': self.backup_checkbox.isChecked(),
        }
        settings.update(self.settings)

        language = self._get_selected_language()

        # 建立工作執行緒
        self.worker = TranslationWorker(roms_path, language, [], settings)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.log.connect(self._on_log)

        # 更新 UI 狀態
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.statusBar().showMessage("翻譯進行中...")

        # 清除舊日誌
        self.log_panel.clear()

        # 開始執行
        self.worker.start()

    def _cancel_translation(self):
        """取消翻譯"""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.statusBar().showMessage("正在取消...")

    def _on_progress(self, current: int, total: int, message: str):
        """進度更新"""
        self.progress_panel.update_progress(current, total, message)

    def _on_finished(self, result: dict):
        """翻譯完成"""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        summary = (f"翻譯完成！\n"
                   f"處理平台: {result['platforms']}\n"
                   f"處理遊戲: {result['games']}\n"
                   f"成功翻譯: {result['translated']}\n"
                   f"已跳過: {result['skipped']}\n"
                   f"失敗: {result['failed']}")

        self.statusBar().showMessage("翻譯完成")
        self.log_panel.add_log("SUCCESS", "Main", summary)
        QMessageBox.information(self, "完成", summary)

    def _on_error(self, error: str):
        """錯誤處理"""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.statusBar().showMessage("發生錯誤")
        self.log_panel.add_log("ERROR", "Main", error)
        QMessageBox.critical(self, "錯誤", error)

    def _on_log(self, level: str, module: str, message: str):
        """日誌更新"""
        self.log_panel.add_log(level, module, message)

    def _show_preview(self):
        """顯示預覽對話框"""
        dialog = PreviewDialog(self)
        dialog.exec()

    def _show_settings(self):
        """顯示設定對話框"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.settings = dialog.get_settings()
            # 同步設定回 app_settings
            self.app_settings.gemini_api_key = self.settings.get(
                'gemini_api_key', '')
            self.app_settings.translate_api = self.settings.get(
                'translate_api', 'googletrans')
            self.app_settings.api_key = self.settings.get('api_key', '')
            # Gemini 批次翻譯設定
            self.app_settings.use_gemini_batch = self.settings.get(
                'use_gemini_batch', False)
            self.app_settings.gemini_batch_size = self.settings.get(
                'gemini_batch_size', 20)
            # 同步效能設定
            self.app_settings.request_delay = self.settings.get(
                'request_delay', 500)
            self.app_settings.max_workers = self.settings.get('max_workers', 3)
            self.app_settings.batch_size = self.settings.get('batch_size', 20)
            self.app_settings.auto_save_interval = self.settings.get(
                'auto_save_interval', 10)
            self.settings_manager.save(self.app_settings)

    def _import_language_pack(self):
        """匯入語系包"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇語系包", "", "JSON 檔案 (*.json)"
        )
        if file_path:
            self.log_panel.add_log("INFO", "Main", f"匯入語系包: {file_path}")
            # TODO: 實作匯入邏輯

    def _export_dictionary(self):
        """匯出字典"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "匯出字典", "", "JSON 檔案 (*.json)"
        )
        if file_path:
            self.log_panel.add_log("INFO", "Main", f"匯出字典: {file_path}")
            # TODO: 實作匯出邏輯

    def _show_about(self):
        """顯示關於對話框"""
        QMessageBox.about(
            self,
            "關於 Batocera Gamelist 翻譯工具",
            "<b>Batocera Gamelist 翻譯工具 v1.1</b><br><br>"
            "專為 Batocera 復古遊戲模擬器設計的多語系翻譯工具。<br><br>"
            "讓你的復古遊戲收藏說中文！<br><br>"
            "© 2025 MIT License"
        )

    def _run_stage_scan(self):
        """階段一：掃描取回（非同步）"""
        roms_path = self.path_input.text().strip()
        if not roms_path:
            QMessageBox.warning(self, "錯誤", "請先選擇 ROM 目錄")
            return

        if not Path(roms_path).exists():
            QMessageBox.warning(self, "錯誤", "指定的目錄不存在")
            return

        self._disable_stage_buttons()
        self.log_panel.clear()
        self.progress_panel.reset()

        # 取得選中的平台
        selected = self.selected_platforms if self.selected_platforms else []

        self.stage_worker = ScanWorker(roms_path, selected)
        self.stage_worker.progress.connect(self._on_stage_progress)
        self.stage_worker.log.connect(self._on_stage_log)
        self.stage_worker.finished.connect(lambda r: self._on_stage_finished(
            "階段一", f"複製 {r['copied']} 個 gamelist.xml"))
        self.stage_worker.error.connect(self._on_stage_error)
        self.stage_worker.start()

    def _run_stage_dictionary(self):
        """階段二：產生字典（非同步）"""
        gamelists_dir = Path('./gamelists_local')
        if not gamelists_dir.exists():
            QMessageBox.warning(self, "錯誤", "請先執行階段一（掃描取回）")
            return

        self._disable_stage_buttons()
        self.progress_panel.reset()

        language = self._get_selected_language()
        # 取得選中的平台
        selected = self.selected_platforms if self.selected_platforms else []

        self.stage_worker = DictionaryWorker(language, selected)
        self.stage_worker.progress.connect(self._on_stage_progress)
        self.stage_worker.log.connect(self._on_stage_log)
        self.stage_worker.finished.connect(lambda r: self._on_stage_finished(
            "階段二", f"{r['platforms']} 個平台, {r['games']} 個遊戲"))
        self.stage_worker.error.connect(self._on_stage_error)
        self.stage_worker.start()

    def _run_stage_translate(self):
        """階段三：翻譯（非同步）"""
        lang_dir = get_dictionaries_dir() / self._get_selected_language()
        if not lang_dir.exists():
            QMessageBox.warning(self, "錯誤", "請先執行階段二（產生字典）")
            return

        self._disable_stage_buttons()
        self.progress_panel.reset()

        language = self._get_selected_language()
        # 取得選中的平台
        selected = self.selected_platforms if self.selected_platforms else []

        self.stage_worker = TranslateWorker(
            language,
            self.name_checkbox.isChecked(),
            self.desc_checkbox.isChecked(),
            self.skip_checkbox.isChecked(),
            selected,
            self.settings.get('gemini_api_key', ''),
            self.settings.get('request_delay', 500)
        )
        self.stage_worker.progress.connect(self._on_stage_progress)
        self.stage_worker.log.connect(self._on_stage_log)
        self.stage_worker.finished.connect(
            lambda r: self._on_stage_finished("階段三", f"翻譯 {r['translated']} 個遊戲"))
        self.stage_worker.error.connect(self._on_stage_error)
        self.stage_worker.start()

    def _run_gemini_batch(self):
        """Gemini 批次翻譯"""
        lang_dir = get_dictionaries_dir() / self._get_selected_language()
        if not lang_dir.exists():
            QMessageBox.warning(self, "錯誤", "請先執行階段二（產生字典）")
            return

        # 檢查 Gemini API Key
        gemini_key = self.settings.get('gemini_api_key', '')
        if not gemini_key:
            reply = QMessageBox.question(
                self,
                "缺少 API Key",
                "尚未設定 Gemini API Key。\n\n"
                "Gemini 批次翻譯需要 API Key 才能運作。\n"
                "要開啟設定視窗嗎？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._show_settings()
            return

        # 取得批次大小設定
        batch_size = self.settings.get('gemini_batch_size', 20)

        self._disable_stage_buttons()
        self.progress_panel.reset()

        language = self._get_selected_language()
        selected = self.selected_platforms if self.selected_platforms else []

        self.stage_worker = GeminiBatchWorker(
            language=language,
            selected_platforms=selected,
            gemini_api_key=gemini_key,
            batch_size=batch_size,
            translate_name=self.name_checkbox.isChecked()
        )
        self.stage_worker.progress.connect(self._on_stage_progress)
        self.stage_worker.log.connect(self._on_stage_log)
        self.stage_worker.finished.connect(
            lambda r: self._on_stage_finished(
                "Gemini 批次翻譯",
                f"翻譯 {r['translated']} 個遊戲\n"
                f"失敗 {r['failed']} 個（已標記重翻）\n\n"
                "失敗的項目可使用「③翻譯」按鈕重新處理"
            )
        )
        self.stage_worker.error.connect(self._on_stage_error)
        self.stage_worker.start()

    def _run_stage_writeback(self):
        """階段四：寫回（非同步）"""
        gamelists_dir = Path('./gamelists_local')
        if not gamelists_dir.exists():
            QMessageBox.warning(self, "錯誤", "請先執行階段一（掃描取回）")
            return

        self._disable_stage_buttons()
        self.progress_panel.reset()

        language = self._get_selected_language()
        # 取得選中的平台
        selected = self.selected_platforms if self.selected_platforms else []

        self.stage_worker = WritebackWorker(
            language, self.backup_checkbox.isChecked(), selected)
        self.stage_worker.progress.connect(self._on_stage_progress)
        self.stage_worker.log.connect(self._on_stage_log)
        self.stage_worker.finished.connect(lambda r: self._on_stage_finished(
            "階段四", f"更新 {r['updated']} 個遊戲\n\n結果已寫入 gamelists_local/ 目錄"))
        self.stage_worker.error.connect(self._on_stage_error)
        self.stage_worker.start()

    def _disable_stage_buttons(self):
        """停用所有階段按鈕"""
        self.scan_btn.setEnabled(False)
        self.dict_btn.setEnabled(False)
        self.translate_btn.setEnabled(False)
        self.gemini_batch_btn.setEnabled(False)
        self.writeback_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.statusBar().showMessage("執行中...")

    def _enable_stage_buttons(self):
        """啟用所有階段按鈕"""
        self.scan_btn.setEnabled(True)
        self.dict_btn.setEnabled(True)
        self.translate_btn.setEnabled(True)
        self.gemini_batch_btn.setEnabled(True)
        self.writeback_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.statusBar().showMessage("就緒")

    def _on_stage_progress(self, current: int, total: int, message: str):
        """階段進度更新"""
        self.progress_panel.update_progress(current, total, message)

    def _on_stage_log(self, level: str, module: str, message: str):
        """階段日誌更新"""
        self.log_panel.add_log(level, module, message)

    def _on_stage_finished(self, stage_name: str, result_msg: str):
        """階段完成"""
        self._enable_stage_buttons()
        QMessageBox.information(self, "完成", f"{stage_name}完成！\n{result_msg}")

    def _on_stage_error(self, error: str):
        """階段錯誤"""
        self._enable_stage_buttons()
        self.log_panel.add_log("ERROR", "Stage", f"錯誤: {error}")
        QMessageBox.critical(self, "錯誤", error)

    def _show_dictionary_editor(self):
        """開啟字典編輯器"""
        from .dictionary_editor import DictionaryEditorDialog

        language = self._get_selected_language()
        dialog = DictionaryEditorDialog(language, self)
        dialog.exec()
