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
            from ..core import Scanner, DictionaryManager, TranslationEngine, XmlWriter
            from ..services import WikipediaService, SearchService, TranslateService
            from ..utils import parse_gamelist, get_game_key
            from ..core.dictionary import GameEntry
            
            # 初始化模組
            scanner = Scanner(self.roms_path)
            dict_manager = DictionaryManager()
            translator = TranslationEngine(self.language)
            writer = XmlWriter()
            
            # 設定翻譯服務
            wiki_service = WikipediaService()
            search_service = SearchService()
            translate_service = TranslateService()
            
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
                self.progress.emit(idx, total_platforms, f"處理平台: {platform.name}")
                
                # 複製到暫存區
                cache_path = scanner.copy_gamelist_to_cache(platform)
                
                # 解析遊戲清單
                games = parse_gamelist(cache_path)
                
                # 載入字典
                dictionary = dict_manager.load_dictionary(self.language, platform.name)
                
                # 翻譯每個遊戲
                for game in games:
                    if self._is_cancelled:
                        break
                    
                    # 建立或取得字典項目
                    game_key = get_game_key(game.path)
                    if game_key not in dictionary:
                        entry = GameEntry(
                            key=game_key,
                            original_name=game.name,
                            original_desc=game.desc
                        )
                        dictionary[game_key] = entry
                    else:
                        entry = dictionary[game_key]
                    
                    # 翻譯
                    output = translator.translate_game(
                        entry,
                        translate_name=self.settings.get('translate_name', True),
                        translate_desc=self.settings.get('translate_desc', True),
                        skip_translated=self.settings.get('skip_translated', True)
                    )
                    
                    # 更新字典
                    if output.name:
                        entry.name = output.name
                        entry.name_source = output.name_source
                    if output.desc:
                        entry.desc = output.desc
                        entry.desc_source = output.desc_source
                    
                    result['games'] += 1
                    if output.result.value == 'success':
                        result['translated'] += 1
                    elif output.result.value == 'skipped':
                        result['skipped'] += 1
                    else:
                        result['failed'] += 1
                
                # 儲存字典
                dict_manager.save_dictionary(self.language, platform.name, dictionary)
                
                # 寫回 XML（如果設定允許）
                if self.settings.get('write_back', True) and platform.gamelist_path:
                    writer.write_translations(
                        platform.gamelist_path,
                        dictionary,
                        platform.name,
                        auto_backup=self.settings.get('auto_backup', True)
                    )
                
                result['platforms'] += 1
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def cancel(self):
        """取消翻譯"""
        self._is_cancelled = True


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
        self.settings = self._default_settings()
        self._init_ui()
        
    def _default_settings(self) -> dict:
        """預設設定"""
        return {
            'translate_name': True,
            'translate_desc': True,
            'skip_translated': True,
            'write_back': True,
            'auto_backup': True,
            'translate_api': 'googletrans',
            'api_key': '',
        }
    
    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("Batocera Gamelist 翻譯工具 v1.0")
        self.setMinimumSize(900, 700)
        
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
        
        main_layout.addWidget(path_group)
        
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
        self.desc_checkbox.setChecked(True)
        translate_layout.addWidget(self.desc_checkbox)
        
        self.skip_checkbox = QCheckBox("跳過已翻譯項目")
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
        
        # 按鈕區域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.preview_btn = QPushButton("預覽模式")
        self.preview_btn.clicked.connect(self._show_preview)
        btn_layout.addWidget(self.preview_btn)
        
        self.settings_btn = QPushButton("設定")
        self.settings_btn.clicked.connect(self._show_settings)
        btn_layout.addWidget(self.settings_btn)
        
        self.start_btn = QPushButton("開始翻譯")
        self.start_btn.setMinimumWidth(120)
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
        
        settings_action = QAction("設定...", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # 說明選單
        help_menu = menubar.addMenu("說明(&H)")
        
        about_action = QAction("關於", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _browse_path(self):
        """開啟資料夾選擇對話框"""
        path = QFileDialog.getExistingDirectory(self, "選擇 ROM 目錄")
        if path:
            self.path_input.setText(path)
    
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
            "<b>Batocera Gamelist 翻譯工具 v1.0</b><br><br>"
            "專為 Batocera 復古遊戲模擬器設計的多語系翻譯工具。<br><br>"
            "讓你的復古遊戲收藏說中文！<br><br>"
            "© 2025 MIT License"
        )
