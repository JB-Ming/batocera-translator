# 進度面板模組
"""
翻譯進度顯示面板。
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QProgressBar, QGroupBox
)
from PyQt6.QtCore import Qt


class ProgressPanel(QWidget):
    """
    進度面板
    
    顯示：
    - 總進度條
    - 當前動作
    - 統計資訊
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("進度")
        group_layout = QVBoxLayout(group)
        
        # 當前動作
        self.action_label = QLabel("等待開始...")
        group_layout.addWidget(self.action_label)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        group_layout.addWidget(self.progress_bar)
        
        # 統計資訊
        stats_layout = QHBoxLayout()
        
        self.platform_label = QLabel("平台: 0/0")
        stats_layout.addWidget(self.platform_label)
        
        self.game_label = QLabel("遊戲: 0")
        stats_layout.addWidget(self.game_label)
        
        self.translated_label = QLabel("已翻譯: 0")
        stats_layout.addWidget(self.translated_label)
        
        self.skipped_label = QLabel("跳過: 0")
        stats_layout.addWidget(self.skipped_label)
        
        stats_layout.addStretch()
        group_layout.addLayout(stats_layout)
        
        layout.addWidget(group)
    
    def update_progress(self, current: int, total: int, message: str):
        """更新進度"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.platform_label.setText(f"平台: {current}/{total}")
        
        self.action_label.setText(message)
    
    def update_stats(self, games: int, translated: int, skipped: int):
        """更新統計"""
        self.game_label.setText(f"遊戲: {games}")
        self.translated_label.setText(f"已翻譯: {translated}")
        self.skipped_label.setText(f"跳過: {skipped}")
    
    def reset(self):
        """重置"""
        self.progress_bar.setValue(0)
        self.action_label.setText("等待開始...")
        self.platform_label.setText("平台: 0/0")
        self.game_label.setText("遊戲: 0")
        self.translated_label.setText("已翻譯: 0")
        self.skipped_label.setText("跳過: 0")
