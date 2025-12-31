# 預覽對話框模組
"""
翻譯預覽對話框，顯示變更前後對照。
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QLabel,
    QHeaderView, QAbstractItemView, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class PreviewDialog(QDialog):
    """
    預覽對話框
    
    功能：
    - 顯示變更前後對照
    - 變更類型篩選
    - 展開詳細
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._changes = []
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("預覽變更")
        self.setMinimumSize(800, 500)
        
        layout = QVBoxLayout(self)
        
        # 篩選工具列
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("類型篩選:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["全部", "新增", "覆寫", "跳過"])
        self.type_combo.currentTextChanged.connect(self._filter_changes)
        filter_layout.addWidget(self.type_combo)
        
        filter_layout.addWidget(QLabel("來源篩選:"))
        self.source_combo = QComboBox()
        self.source_combo.addItems(["全部", "wiki", "search", "api", "keep", "manual", "pack"])
        self.source_combo.currentTextChanged.connect(self._filter_changes)
        filter_layout.addWidget(self.source_combo)
        
        filter_layout.addStretch()
        
        self.count_label = QLabel("共 0 項變更")
        filter_layout.addWidget(self.count_label)
        
        layout.addLayout(filter_layout)
        
        # 變更表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["遊戲", "欄位", "變更前", "變更後", "來源"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # 統計資訊
        stats_group = QGroupBox("統計")
        stats_layout = QHBoxLayout(stats_group)
        
        self.new_label = QLabel("新增: 0")
        stats_layout.addWidget(self.new_label)
        
        self.overwrite_label = QLabel("覆寫: 0")
        stats_layout.addWidget(self.overwrite_label)
        
        self.skip_label = QLabel("跳過: 0")
        stats_layout.addWidget(self.skip_label)
        
        stats_layout.addStretch()
        layout.addWidget(stats_group)
        
        # 按鈕
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        refresh_btn = QPushButton("重新載入")
        refresh_btn.clicked.connect(self._load_preview)
        btn_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("關閉")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # 載入預覽資料
        self._load_preview()
    
    def _load_preview(self):
        """載入預覽資料"""
        # TODO: 從主視窗取得實際的預覽資料
        # 目前顯示範例資料
        self._changes = [
            {
                'key': './Super Mario Bros.nes',
                'field': 'name',
                'before': 'Super Mario Bros',
                'after': '超級瑪利歐兄弟',
                'source': 'wiki',
                'type': '覆寫'
            },
            {
                'key': './The Legend of Zelda.nes',
                'field': 'name',
                'before': 'The Legend of Zelda',
                'after': '薩爾達傳說',
                'source': 'wiki',
                'type': '覆寫'
            },
            {
                'key': './Contra.nes',
                'field': 'name',
                'before': 'Contra',
                'after': '魂斗羅',
                'source': 'search',
                'type': '覆寫'
            },
            {
                'key': './F-Zero.snes',
                'field': 'name',
                'before': 'F-Zero',
                'after': 'F-Zero',
                'source': 'keep',
                'type': '跳過'
            },
        ]
        
        self._filter_changes()
    
    def _filter_changes(self):
        """篩選並顯示變更"""
        type_filter = self.type_combo.currentText()
        source_filter = self.source_combo.currentText()
        
        filtered = []
        for change in self._changes:
            if type_filter != "全部" and change.get('type') != type_filter:
                continue
            if source_filter != "全部" and change.get('source') != source_filter:
                continue
            filtered.append(change)
        
        # 更新表格
        self.table.setRowCount(len(filtered))
        
        for row, change in enumerate(filtered):
            # 遊戲
            key_item = QTableWidgetItem(change['key'])
            self.table.setItem(row, 0, key_item)
            
            # 欄位
            field_item = QTableWidgetItem(change['field'])
            self.table.setItem(row, 1, field_item)
            
            # 變更前
            before_item = QTableWidgetItem(change['before'])
            self.table.setItem(row, 2, before_item)
            
            # 變更後
            after_item = QTableWidgetItem(change['after'])
            # 標記顏色
            if change['before'] != change['after']:
                after_item.setBackground(QColor(50, 100, 50))
            self.table.setItem(row, 3, after_item)
            
            # 來源
            source_item = QTableWidgetItem(change['source'])
            self.table.setItem(row, 4, source_item)
        
        # 更新統計
        self.count_label.setText(f"共 {len(filtered)} 項變更")
        
        # 計算類型統計
        new_count = sum(1 for c in self._changes if c.get('type') == '新增')
        overwrite_count = sum(1 for c in self._changes if c.get('type') == '覆寫')
        skip_count = sum(1 for c in self._changes if c.get('type') == '跳過')
        
        self.new_label.setText(f"新增: {new_count}")
        self.overwrite_label.setText(f"覆寫: {overwrite_count}")
        self.skip_label.setText(f"跳過: {skip_count}")
    
    def set_changes(self, changes: list):
        """設定變更資料"""
        self._changes = changes
        self._filter_changes()
