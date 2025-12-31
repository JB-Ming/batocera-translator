# 設定對話框模組
"""
翻譯設定對話框。
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QWidget, QFormLayout, QSpinBox
)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    """
    設定對話框
    
    包含：
    - 字典檔設定
    - 翻譯設定
    - 寫回設定
    - API 設定
    """
    
    def __init__(self, current_settings: dict, parent=None):
        super().__init__(parent)
        self.settings = current_settings.copy()
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("設定")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 分頁標籤
        tabs = QTabWidget()
        
        # 字典檔設定
        dict_tab = self._create_dict_tab()
        tabs.addTab(dict_tab, "字典檔")
        
        # 翻譯設定
        translate_tab = self._create_translate_tab()
        tabs.addTab(translate_tab, "翻譯")
        
        # 寫回設定
        write_tab = self._create_write_tab()
        tabs.addTab(write_tab, "寫回")
        
        # API 設定
        api_tab = self._create_api_tab()
        tabs.addTab(api_tab, "API")
        
        layout.addWidget(tabs)
        
        # 按鈕
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("確定")
        ok_btn.clicked.connect(self._save_and_close)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_dict_tab(self) -> QWidget:
        """建立字典檔設定分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 衝突處理
        group = QGroupBox("字典檔衝突處理")
        form = QFormLayout(group)
        
        self.merge_combo = QComboBox()
        self.merge_combo.addItems([
            "合併（保留已翻譯，加入新項目）",
            "僅補空白（只填入空白欄位）",
            "覆寫（完全取代）",
            "跳過（不處理）"
        ])
        form.addRow("處理策略:", self.merge_combo)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return widget
    
    def _create_translate_tab(self) -> QWidget:
        """建立翻譯設定分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 搜尋設定
        search_group = QGroupBox("搜尋設定")
        search_layout = QVBoxLayout(search_group)
        
        self.include_platform_check = QCheckBox("搜尋時包含平台名稱")
        search_layout.addWidget(self.include_platform_check)
        
        self.use_api_fallback_check = QCheckBox("搜尋失敗時使用 API 直譯")
        self.use_api_fallback_check.setChecked(True)
        search_layout.addWidget(self.use_api_fallback_check)
        
        self.auto_keep_original_check = QCheckBox("自動偵測保留原文")
        self.auto_keep_original_check.setChecked(True)
        search_layout.addWidget(self.auto_keep_original_check)
        
        layout.addWidget(search_group)
        
        # 已翻譯項目處理
        translated_group = QGroupBox("已翻譯項目處理")
        translated_layout = QVBoxLayout(translated_group)
        
        self.translated_combo = QComboBox()
        self.translated_combo.addItems([
            "跳過已翻譯",
            "僅重新翻譯 API 直譯項目",
            "全部重新翻譯"
        ])
        translated_layout.addWidget(self.translated_combo)
        
        layout.addWidget(translated_group)
        layout.addStretch()
        
        return widget
    
    def _create_write_tab(self) -> QWidget:
        """建立寫回設定分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 處理策略
        strategy_group = QGroupBox("處理策略")
        strategy_layout = QVBoxLayout(strategy_group)
        
        self.name_strategy_combo = QComboBox()
        self.name_strategy_combo.addItems([
            "跳過已翻譯",
            "字典優先",
            "XML 優先",
            "全部覆寫"
        ])
        strategy_layout.addWidget(QLabel("name 處理:"))
        strategy_layout.addWidget(self.name_strategy_combo)
        
        self.desc_strategy_combo = QComboBox()
        self.desc_strategy_combo.addItems([
            "跳過已翻譯",
            "字典優先",
            "XML 優先",
            "全部覆寫"
        ])
        strategy_layout.addWidget(QLabel("desc 處理:"))
        strategy_layout.addWidget(self.desc_strategy_combo)
        
        layout.addWidget(strategy_group)
        
        # 顯示格式
        format_group = QGroupBox("顯示格式")
        format_layout = QVBoxLayout(format_group)
        
        self.display_format_combo = QComboBox()
        self.display_format_combo.addItems([
            "僅中文",
            "中文(英文)",
            "英文(中文)",
            "僅保留原文"
        ])
        format_layout.addWidget(self.display_format_combo)
        
        layout.addWidget(format_group)
        layout.addStretch()
        
        return widget
    
    def _create_api_tab(self) -> QWidget:
        """建立 API 設定分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API 選擇
        api_group = QGroupBox("翻譯 API")
        form = QFormLayout(api_group)
        
        self.api_combo = QComboBox()
        self.api_combo.addItems([
            "googletrans（免費）",
            "Google Cloud Translation",
            "DeepL",
            "Azure Translator"
        ])
        form.addRow("API 類型:", self.api_combo)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("付費 API 需要填寫金鑰")
        form.addRow("API Key:", self.api_key_input)
        
        layout.addWidget(api_group)
        
        # 速率限制
        rate_group = QGroupBox("速率限制")
        rate_form = QFormLayout(rate_group)
        
        self.request_delay_spin = QSpinBox()
        self.request_delay_spin.setRange(500, 10000)
        self.request_delay_spin.setSingleStep(500)
        self.request_delay_spin.setValue(2000)
        self.request_delay_spin.setSuffix(" ms")
        rate_form.addRow("請求間隔:", self.request_delay_spin)
        
        layout.addWidget(rate_group)
        layout.addStretch()
        
        return widget
    
    def _load_settings(self):
        """載入設定到 UI"""
        api_map = {
            'googletrans': 0,
            'google_cloud': 1,
            'deepl': 2,
            'azure': 3,
        }
        api_type = self.settings.get('translate_api', 'googletrans')
        self.api_combo.setCurrentIndex(api_map.get(api_type, 0))
        self.api_key_input.setText(self.settings.get('api_key', ''))
    
    def _save_and_close(self):
        """儲存設定並關閉"""
        api_map = ['googletrans', 'google_cloud', 'deepl', 'azure']
        self.settings['translate_api'] = api_map[self.api_combo.currentIndex()]
        self.settings['api_key'] = self.api_key_input.text()
        self.settings['request_delay'] = self.request_delay_spin.value()
        self.accept()
    
    def get_settings(self) -> dict:
        """取得設定"""
        return self.settings
