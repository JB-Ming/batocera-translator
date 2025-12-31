# 平台選擇模組
"""
提供遊戲機平台多選功能的 UI 元件。
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QScrollArea, QCheckBox, QPushButton, QLabel, QFrame,
    QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from typing import List, Set


class FlowLayout(QHBoxLayout):
    """
    簡易流式佈局：將項目水平排列，自動換行效果透過固定欄位數達成
    """
    pass


class PlatformSelector(QGroupBox):
    """
    平台選擇元件
    
    提供：
    - 可捲動的複選框列表（只顯示有 gamelist.xml 的平台）
    - 全選/取消全選按鈕
    - 選擇變更信號
    """
    
    # 選擇變更信號
    selection_changed = pyqtSignal(list)  # 選中的平台名稱清單
    
    def __init__(self, parent=None):
        super().__init__("平台選擇", parent)
        self.checkboxes: dict[str, QCheckBox] = {}  # 平台名稱 -> 複選框
        self._init_ui()
        
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # 頂部控制列
        control_layout = QHBoxLayout()
        
        self.status_label = QLabel("請先選擇 ROM 目錄")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        
        self.select_all_btn = QPushButton("全選")
        self.select_all_btn.setFixedWidth(70)
        self.select_all_btn.clicked.connect(self._select_all)
        self.select_all_btn.setEnabled(False)
        control_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("取消全選")
        self.deselect_all_btn.setFixedWidth(80)
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        self.deselect_all_btn.setEnabled(False)
        control_layout.addWidget(self.deselect_all_btn)
        
        self.invert_btn = QPushButton("反選")
        self.invert_btn.setFixedWidth(70)
        self.invert_btn.clicked.connect(self._invert_selection)
        self.invert_btn.setEnabled(False)
        control_layout.addWidget(self.invert_btn)
        
        layout.addLayout(control_layout)
        
        # 可捲動區域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(80)
        self.scroll_area.setMaximumHeight(120)
        self.scroll_area.setFrameShape(QFrame.Shape.StyledPanel)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
            }
        """)
        
        # 平台複選框容器（使用 Grid 佈局）
        self.platforms_widget = QWidget()
        self.platforms_widget.setStyleSheet("background-color: #2a2a2a;")
        self.grid_layout = QGridLayout(self.platforms_widget)
        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll_area.setWidget(self.platforms_widget)
        layout.addWidget(self.scroll_area)
    
    def set_platforms(self, platforms: List[str], has_gamelist: Set[str] = None):
        """
        設定可選擇的平台清單
        
        Args:
            platforms: 平台名稱清單（所有資料夾）
            has_gamelist: 有 gamelist.xml 的平台集合
        """
        if has_gamelist is None:
            has_gamelist = set()
            
        # 清除舊複選框
        self._clear_checkboxes()
        
        # 只顯示有 gamelist.xml 的平台
        valid_platforms = sorted([p for p in platforms if p in has_gamelist])
        
        if not valid_platforms:
            self.status_label.setText("未找到任何有 gamelist.xml 的資料夾")
            self.status_label.setStyleSheet("color: #ff6b6b; font-size: 12px;")
            self._disable_buttons()
            return
        
        # 計算欄數（根據平台數量動態調整，最多 6 欄）
        num_platforms = len(valid_platforms)
        if num_platforms <= 6:
            columns = num_platforms
        elif num_platforms <= 12:
            columns = 4
        elif num_platforms <= 24:
            columns = 5
        else:
            columns = 6
        
        # 建立複選框（Grid 佈局）
        for i, platform in enumerate(valid_platforms):
            row = i // columns
            col = i % columns
            
            checkbox = QCheckBox(platform)
            checkbox.setChecked(True)  # 預設全選
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #e0e0e0;
                    font-size: 12px;
                    padding: 2px 8px;
                    min-width: 100px;
                }
                QCheckBox:hover {
                    background-color: #3a3a3a;
                    border-radius: 3px;
                }
                QCheckBox::indicator {
                    width: 14px;
                    height: 14px;
                }
            """)
            checkbox.setToolTip(f"翻譯 {platform} 平台的遊戲")
            checkbox.stateChanged.connect(self._on_checkbox_changed)
            
            self.grid_layout.addWidget(checkbox, row, col)
            self.checkboxes[platform] = checkbox
        
        # 更新狀態
        self.status_label.setText(f"共 {num_platforms} 個平台")
        self.status_label.setStyleSheet("color: #8bc34a; font-size: 12px;")
        
        # 啟用控制按鈕
        self.select_all_btn.setEnabled(True)
        self.deselect_all_btn.setEnabled(True)
        self.invert_btn.setEnabled(True)
        
        # 發送選擇變更信號
        self._emit_selection()
    
    def _clear_checkboxes(self):
        """清除所有複選框"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.checkboxes.clear()
    
    def _disable_buttons(self):
        """停用控制按鈕"""
        self.select_all_btn.setEnabled(False)
        self.deselect_all_btn.setEnabled(False)
        self.invert_btn.setEnabled(False)
        
    def _on_checkbox_changed(self, state: int):
        """複選框狀態變更"""
        self._emit_selection()
        
    def _emit_selection(self):
        """發送選擇變更信號"""
        selected = self.get_selected_platforms()
        self.selection_changed.emit(selected)
        
        # 更新狀態顯示選中數量
        total = len(self.checkboxes)
        selected_count = len(selected)
        self.status_label.setText(f"已選擇 {selected_count}/{total} 個平台")
        
    def _select_all(self):
        """全選"""
        for checkbox in self.checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(True)
            checkbox.blockSignals(False)
        self._emit_selection()
            
    def _deselect_all(self):
        """取消全選"""
        for checkbox in self.checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)
        self._emit_selection()
            
    def _invert_selection(self):
        """反向選擇"""
        for checkbox in self.checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(not checkbox.isChecked())
            checkbox.blockSignals(False)
        self._emit_selection()
            
    def get_selected_platforms(self) -> List[str]:
        """取得已選擇的平台清單"""
        return [name for name, cb in self.checkboxes.items() if cb.isChecked()]
            
    def clear(self):
        """清除所有平台"""
        self._clear_checkboxes()
        self.status_label.setText("請先選擇 ROM 目錄")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        self._disable_buttons()
