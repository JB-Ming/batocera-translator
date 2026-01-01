# 字典編輯器模組
"""
提供字典檔管理與編輯功能的對話框。
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QHeaderView,
    QAbstractItemView, QGroupBox, QCheckBox, QMenu, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QAction
from pathlib import Path
from typing import Dict, Optional

from ..core.dictionary import DictionaryManager, GameEntry
from ..utils.file_utils import get_dictionaries_dir


class GameEditDialog(QDialog):
    """
    單一遊戲項目編輯對話框
    """
    
    def __init__(self, entry: GameEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.result_entry: Optional[GameEntry] = None
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle(f"編輯: {self.entry.original_name}")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 原始名稱（唯讀）
        name_group = QGroupBox("名稱")
        name_layout = QVBoxLayout(name_group)
        
        name_layout.addWidget(QLabel("原始名稱:"))
        original_name_label = QLabel(self.entry.original_name)
        original_name_label.setStyleSheet("color: #888;")
        name_layout.addWidget(original_name_label)
        
        name_layout.addWidget(QLabel("翻譯名稱:"))
        self.name_input = QLineEdit(self.entry.name)
        name_layout.addWidget(self.name_input)
        
        layout.addWidget(name_group)
        
        # 原始描述（唯讀）
        desc_group = QGroupBox("描述")
        desc_layout = QVBoxLayout(desc_group)
        
        desc_layout.addWidget(QLabel("原始描述:"))
        original_desc = self.entry.original_desc[:200] + "..." if len(self.entry.original_desc) > 200 else self.entry.original_desc
        original_desc_label = QLabel(original_desc)
        original_desc_label.setStyleSheet("color: #888;")
        original_desc_label.setWordWrap(True)
        desc_layout.addWidget(original_desc_label)
        
        desc_layout.addWidget(QLabel("翻譯描述:"))
        self.desc_input = QLineEdit(self.entry.desc)
        desc_layout.addWidget(self.desc_input)
        
        layout.addWidget(desc_group)
        
        # 重翻標記
        self.retranslate_checkbox = QCheckBox("標記需要重新翻譯")
        self.retranslate_checkbox.setChecked(self.entry.needs_retranslate)
        layout.addWidget(self.retranslate_checkbox)
        
        # 翻譯資訊（唯讀）
        info_group = QGroupBox("翻譯資訊")
        info_layout = QVBoxLayout(info_group)
        
        info_layout.addWidget(QLabel(f"名稱來源: {self.entry.name_source or '無'}"))
        info_layout.addWidget(QLabel(f"名稱翻譯時間: {self.entry.name_translated_at or '無'}"))
        info_layout.addWidget(QLabel(f"描述來源: {self.entry.desc_source or '無'}"))
        info_layout.addWidget(QLabel(f"描述翻譯時間: {self.entry.desc_translated_at or '無'}"))
        
        layout.addWidget(info_group)
        
        # 按鈕
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("儲存")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _save(self):
        """儲存變更"""
        # 更新 entry
        self.entry.name = self.name_input.text().strip()
        self.entry.desc = self.desc_input.text().strip()
        self.entry.needs_retranslate = self.retranslate_checkbox.isChecked()
        
        # 如果手動編輯，更新來源
        if self.entry.name and self.entry.name != self.entry.original_name:
            if self.entry.name_source != "manual":
                self.entry.name_source = "manual"
        if self.entry.desc and self.entry.desc != self.entry.original_desc:
            if self.entry.desc_source != "manual":
                self.entry.desc_source = "manual"
        
        self.result_entry = self.entry
        self.accept()


class DictionaryEditorDialog(QDialog):
    """
    字典編輯器對話框
    
    功能：
    - 瀏覽、刪除字典檔
    - 編輯字典內容
    - 標記項目需要重新翻譯
    """
    
    # 字典變更訊號
    dictionary_changed = pyqtSignal()
    
    def __init__(self, language: str = "zh-TW", parent=None):
        super().__init__(parent)
        self.language = language
        self.dict_manager = DictionaryManager()
        self.current_platform: Optional[str] = None
        self.current_dictionary: Dict[str, GameEntry] = {}
        self._modified = False
        
        self._init_ui()
        self._load_platforms()
    
    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("字典編輯器")
        self.setMinimumSize(1000, 600)
        
        layout = QVBoxLayout(self)
        
        # 主分割面板
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ===== 左側：字典檔列表 =====
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("字典檔列表"))
        
        self.platform_list = QListWidget()
        self.platform_list.currentItemChanged.connect(self._on_platform_selected)
        left_layout.addWidget(self.platform_list)
        
        # 左側按鈕
        left_btn_layout = QHBoxLayout()
        
        self.delete_dict_btn = QPushButton("刪除字典")
        self.delete_dict_btn.setEnabled(False)
        self.delete_dict_btn.clicked.connect(self._delete_dictionary)
        left_btn_layout.addWidget(self.delete_dict_btn)
        
        left_layout.addLayout(left_btn_layout)
        
        splitter.addWidget(left_widget)
        
        # ===== 右側：遊戲項目表格 =====
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 工具列
        toolbar_layout = QHBoxLayout()
        
        toolbar_layout.addWidget(QLabel("搜尋:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("輸入關鍵字搜尋...")
        self.search_input.textChanged.connect(self._filter_entries)
        toolbar_layout.addWidget(self.search_input)
        
        # 篩選
        self.show_retranslate_only = QCheckBox("僅顯示需重翻")
        self.show_retranslate_only.stateChanged.connect(self._filter_entries)
        toolbar_layout.addWidget(self.show_retranslate_only)
        
        right_layout.addLayout(toolbar_layout)
        
        # 表格（隱藏 Key 欄位，改存到 UserRole）
        self.entry_table = QTableWidget()
        self.entry_table.setColumnCount(4)
        self.entry_table.setHorizontalHeaderLabels(["原始名稱", "翻譯名稱", "來源", "重翻"])
        self.entry_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.entry_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.entry_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.entry_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.entry_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.entry_table.setAlternatingRowColors(True)
        self.entry_table.doubleClicked.connect(self._edit_entry)
        self.entry_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.entry_table.customContextMenuRequested.connect(self._show_context_menu)
        self.entry_table.cellChanged.connect(self._on_cell_changed)
        right_layout.addWidget(self.entry_table)
        
        # 統計區域
        self.stats_label = QLabel("選擇一個字典檔以查看內容")
        right_layout.addWidget(self.stats_label)
        
        splitter.addWidget(right_widget)
        
        # 設定分割比例
        splitter.setSizes([200, 800])
        
        layout.addWidget(splitter)
        
        # ===== 底部按鈕 =====
        btn_layout = QHBoxLayout()
        
        self.mark_all_retranslate_btn = QPushButton("全部標記重翻")
        self.mark_all_retranslate_btn.clicked.connect(self._mark_all_retranslate)
        btn_layout.addWidget(self.mark_all_retranslate_btn)
        
        self.clear_all_retranslate_btn = QPushButton("清除所有標記")
        self.clear_all_retranslate_btn.clicked.connect(self._clear_all_retranslate)
        btn_layout.addWidget(self.clear_all_retranslate_btn)
        
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("儲存變更")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_dictionary)
        btn_layout.addWidget(self.save_btn)
        
        close_btn = QPushButton("關閉")
        close_btn.clicked.connect(self._close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_platforms(self):
        """載入平台列表"""
        self.platform_list.clear()
        
        platforms = self.dict_manager.get_available_platforms(self.language)
        
        for platform in sorted(platforms):
            item = QListWidgetItem(platform)
            self.platform_list.addItem(item)
    
    def _on_platform_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """平台選擇變更"""
        if self._modified:
            reply = QMessageBox.question(
                self, "未儲存的變更",
                "目前的變更尚未儲存，是否儲存？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._save_dictionary()
            elif reply == QMessageBox.StandardButton.Cancel:
                # 恢復選擇
                self.platform_list.blockSignals(True)
                self.platform_list.setCurrentItem(previous)
                self.platform_list.blockSignals(False)
                return
        
        if current:
            self.current_platform = current.text()
            self._load_dictionary()
            self.delete_dict_btn.setEnabled(True)
        else:
            self.current_platform = None
            self.current_dictionary = {}
            self.entry_table.setRowCount(0)
            self.delete_dict_btn.setEnabled(False)
    
    def _load_dictionary(self):
        """載入字典內容"""
        if not self.current_platform:
            return
        
        self.current_dictionary = self.dict_manager.load_dictionary(
            self.language, self.current_platform
        )
        
        self._filter_entries()
        self._modified = False
        self.save_btn.setEnabled(False)
    
    def _filter_entries(self):
        """篩選並顯示項目"""
        search_text = self.search_input.text().lower()
        show_retranslate_only = self.show_retranslate_only.isChecked()
        
        # 篩選
        filtered = []
        for key, entry in self.current_dictionary.items():
            # 搜尋篩選
            if search_text:
                if (search_text not in key.lower() and
                    search_text not in entry.original_name.lower() and
                    search_text not in entry.name.lower()):
                    continue
            
            # 重翻篩選
            if show_retranslate_only and not entry.needs_retranslate:
                continue
            
            filtered.append((key, entry))
        
        # 暫時阻擋訊號避免觸發 cellChanged
        self.entry_table.blockSignals(True)
        
        # 更新表格
        self.entry_table.setRowCount(len(filtered))
        
        for row, (key, entry) in enumerate(filtered):
            # 原始名稱（儲存 key 到 UserRole）
            original_item = QTableWidgetItem(entry.original_name)
            original_item.setData(Qt.ItemDataRole.UserRole, key)  # 儲存 key 用於編輯
            original_item.setFlags(original_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entry_table.setItem(row, 0, original_item)
            
            # 翻譯名稱
            name_item = QTableWidgetItem(entry.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if entry.name:
                name_item.setBackground(QColor(50, 80, 50))
            self.entry_table.setItem(row, 1, name_item)
            
            # 來源
            source_item = QTableWidgetItem(entry.name_source)
            source_item.setFlags(source_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entry_table.setItem(row, 2, source_item)
            
            # 重翻標記（可勾選的 checkbox）
            retranslate_item = QTableWidgetItem()
            retranslate_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            retranslate_item.setCheckState(Qt.CheckState.Checked if entry.needs_retranslate else Qt.CheckState.Unchecked)
            retranslate_item.setData(Qt.ItemDataRole.UserRole, key)  # 儲存 key
            if entry.needs_retranslate:
                retranslate_item.setBackground(QColor(100, 80, 50))
            self.entry_table.setItem(row, 3, retranslate_item)
        
        # 恢復訊號
        self.entry_table.blockSignals(False)
        
        # 更新統計
        total = len(self.current_dictionary)
        translated = sum(1 for e in self.current_dictionary.values() if e.name)
        retranslate = sum(1 for e in self.current_dictionary.values() if e.needs_retranslate)
        
        self.stats_label.setText(
            f"共 {total} 個項目 | 已翻譯: {translated} | 待重翻: {retranslate} | 顯示: {len(filtered)}"
        )
    
    def _on_cell_changed(self, row: int, column: int):
        """處理表格儲存格變更（主要處理重翻 checkbox）"""
        # 只處理重翻欄位（第 3 欄，從 0 開始）
        if column != 3:
            return
        
        item = self.entry_table.item(row, column)
        if not item:
            return
        
        key = item.data(Qt.ItemDataRole.UserRole)
        if not key or key not in self.current_dictionary:
            return
        
        entry = self.current_dictionary[key]
        new_state = item.checkState() == Qt.CheckState.Checked
        
        if entry.needs_retranslate != new_state:
            entry.needs_retranslate = new_state
            self._modified = True
            self.save_btn.setEnabled(True)
            
            # 更新背景色
            if new_state:
                item.setBackground(QColor(100, 80, 50))
            else:
                item.setBackground(QColor(0, 0, 0, 0))  # 透明
            
            # 更新統計
            retranslate = sum(1 for e in self.current_dictionary.values() if e.needs_retranslate)
            total = len(self.current_dictionary)
            translated = sum(1 for e in self.current_dictionary.values() if e.name)
            self.stats_label.setText(
                f"共 {total} 個項目 | 已翻譯: {translated} | 待重翻: {retranslate}"
            )
    
    def _edit_entry(self):
        """編輯選中的項目"""
        current_row = self.entry_table.currentRow()
        if current_row < 0:
            return
        
        key_item = self.entry_table.item(current_row, 0)
        key = key_item.data(Qt.ItemDataRole.UserRole)
        
        if key not in self.current_dictionary:
            return
        
        entry = self.current_dictionary[key]
        
        dialog = GameEditDialog(entry, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_entry:
            self.current_dictionary[key] = dialog.result_entry
            self._modified = True
            self.save_btn.setEnabled(True)
            self._filter_entries()
    
    def _show_context_menu(self, pos):
        """顯示右鍵選單"""
        current_row = self.entry_table.currentRow()
        if current_row < 0:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("編輯", self)
        edit_action.triggered.connect(self._edit_entry)
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        toggle_retranslate_action = QAction("切換重翻標記", self)
        toggle_retranslate_action.triggered.connect(self._toggle_retranslate)
        menu.addAction(toggle_retranslate_action)
        
        clear_translation_action = QAction("清除翻譯", self)
        clear_translation_action.triggered.connect(self._clear_translation)
        menu.addAction(clear_translation_action)
        
        menu.exec(self.entry_table.mapToGlobal(pos))
    
    def _toggle_retranslate(self):
        """切換重翻標記"""
        current_row = self.entry_table.currentRow()
        if current_row < 0:
            return
        
        key_item = self.entry_table.item(current_row, 0)
        key = key_item.data(Qt.ItemDataRole.UserRole)
        
        if key in self.current_dictionary:
            entry = self.current_dictionary[key]
            entry.needs_retranslate = not entry.needs_retranslate
            self._modified = True
            self.save_btn.setEnabled(True)
            self._filter_entries()
    
    def _clear_translation(self):
        """清除選中項目的翻譯"""
        current_row = self.entry_table.currentRow()
        if current_row < 0:
            return
        
        key_item = self.entry_table.item(current_row, 0)
        key = key_item.data(Qt.ItemDataRole.UserRole)
        
        if key in self.current_dictionary:
            entry = self.current_dictionary[key]
            entry.name = ""
            entry.name_source = ""
            entry.name_translated_at = ""
            entry.desc = ""
            entry.desc_source = ""
            entry.desc_translated_at = ""
            entry.needs_retranslate = False
            self._modified = True
            self.save_btn.setEnabled(True)
            self._filter_entries()
    
    def _mark_all_retranslate(self):
        """標記所有項目需要重翻"""
        if not self.current_dictionary:
            return
        
        reply = QMessageBox.question(
            self, "確認",
            f"確定要將 {len(self.current_dictionary)} 個項目全部標記為需要重新翻譯嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for entry in self.current_dictionary.values():
                entry.needs_retranslate = True
            self._modified = True
            self.save_btn.setEnabled(True)
            self._filter_entries()
    
    def _clear_all_retranslate(self):
        """清除所有重翻標記"""
        if not self.current_dictionary:
            return
        
        for entry in self.current_dictionary.values():
            entry.needs_retranslate = False
        self._modified = True
        self.save_btn.setEnabled(True)
        self._filter_entries()
    
    def _save_dictionary(self):
        """儲存字典"""
        if not self.current_platform or not self.current_dictionary:
            return
        
        self.dict_manager.save_dictionary(
            self.language, self.current_platform, self.current_dictionary
        )
        
        self._modified = False
        self.save_btn.setEnabled(False)
        self.dictionary_changed.emit()
        
        QMessageBox.information(self, "成功", "字典已儲存！")
    
    def _delete_dictionary(self):
        """刪除字典檔"""
        if not self.current_platform:
            return
        
        reply = QMessageBox.warning(
            self, "確認刪除",
            f"確定要刪除字典檔 '{self.current_platform}' 嗎？此操作無法復原！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            dict_path = get_dictionaries_dir() / self.language / f"{self.current_platform}.json"
            
            if dict_path.exists():
                dict_path.unlink()
            
            self.current_platform = None
            self.current_dictionary = {}
            self._modified = False
            
            self._load_platforms()
            self.entry_table.setRowCount(0)
            self.stats_label.setText("字典已刪除")
            self.dictionary_changed.emit()
    
    def _close(self):
        """關閉對話框"""
        if self._modified:
            reply = QMessageBox.question(
                self, "未儲存的變更",
                "目前的變更尚未儲存，是否儲存？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._save_dictionary()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.accept()
