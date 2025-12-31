# 日誌面板模組
"""
日誌顯示面板。
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QComboBox, QLineEdit, QPushButton,
    QGroupBox, QFileDialog, QLabel
)
from PyQt6.QtGui import QColor, QTextCharFormat, QFont
from PyQt6.QtCore import Qt


class LogPanel(QWidget):
    """
    日誌面板
    
    功能：
    - 即時顯示日誌
    - 級別篩選
    - 搜尋功能
    - 匯出功能
    """
    
    # 日誌級別顏色
    LEVEL_COLORS = {
        'DEBUG': QColor(150, 150, 150),   # 灰
        'INFO': QColor(255, 255, 255),    # 白
        'SUCCESS': QColor(100, 200, 100), # 綠
        'WARN': QColor(255, 200, 100),    # 黃
        'ERROR': QColor(255, 100, 100),   # 紅
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logs = []
        self._auto_scroll = True
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("日誌")
        group_layout = QVBoxLayout(group)
        
        # 工具列
        toolbar = QHBoxLayout()
        
        # 級別篩選
        toolbar.addWidget(QLabel("級別:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["全部", "DEBUG", "INFO", "SUCCESS", "WARN", "ERROR"])
        self.level_combo.currentTextChanged.connect(self._filter_logs)
        toolbar.addWidget(self.level_combo)
        
        # 搜尋
        toolbar.addWidget(QLabel("搜尋:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("輸入關鍵字...")
        self.search_input.textChanged.connect(self._filter_logs)
        toolbar.addWidget(self.search_input, stretch=1)
        
        # 按鈕
        self.scroll_btn = QPushButton("暫停捲動")
        self.scroll_btn.setCheckable(True)
        self.scroll_btn.toggled.connect(self._toggle_scroll)
        toolbar.addWidget(self.scroll_btn)
        
        export_btn = QPushButton("匯出")
        export_btn.clicked.connect(self._export_logs)
        toolbar.addWidget(export_btn)
        
        clear_btn = QPushButton("清除")
        clear_btn.clicked.connect(self.clear)
        toolbar.addWidget(clear_btn)
        
        group_layout.addLayout(toolbar)
        
        # 日誌顯示區
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
            }
        """)
        group_layout.addWidget(self.log_text)
        
        layout.addWidget(group)
    
    def add_log(self, level: str, module: str, message: str):
        """新增日誌"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'module': module,
            'message': message
        }
        self._logs.append(log_entry)
        
        # 檢查篩選條件
        if self._should_show(log_entry):
            self._append_log_text(log_entry)
    
    def _should_show(self, log_entry: dict) -> bool:
        """檢查日誌是否應顯示"""
        # 級別篩選
        level_filter = self.level_combo.currentText()
        if level_filter != "全部" and log_entry['level'] != level_filter:
            return False
        
        # 關鍵字篩選
        search_text = self.search_input.text().lower()
        if search_text:
            full_text = f"{log_entry['module']} {log_entry['message']}".lower()
            if search_text not in full_text:
                return False
        
        return True
    
    def _append_log_text(self, log_entry: dict):
        """附加日誌到顯示區"""
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        # 設定顏色
        fmt = QTextCharFormat()
        color = self.LEVEL_COLORS.get(log_entry['level'], QColor(255, 255, 255))
        fmt.setForeground(color)
        
        # 格式化日誌
        text = f"[{log_entry['timestamp']}] [{log_entry['level']:7}] [{log_entry['module']:10}] {log_entry['message']}\n"
        
        cursor.insertText(text, fmt)
        
        # 自動捲動
        if self._auto_scroll:
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )
    
    def _filter_logs(self):
        """重新篩選並顯示日誌"""
        self.log_text.clear()
        for log_entry in self._logs:
            if self._should_show(log_entry):
                self._append_log_text(log_entry)
    
    def _toggle_scroll(self, checked: bool):
        """切換自動捲動"""
        self._auto_scroll = not checked
        self.scroll_btn.setText("繼續捲動" if checked else "暫停捲動")
    
    def _export_logs(self):
        """匯出日誌"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "匯出日誌", 
            f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "文字檔案 (*.txt)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                for log_entry in self._logs:
                    text = f"[{log_entry['timestamp']}] [{log_entry['level']:7}] [{log_entry['module']:10}] {log_entry['message']}\n"
                    f.write(text)
    
    def clear(self):
        """清除日誌"""
        self._logs.clear()
        self.log_text.clear()
