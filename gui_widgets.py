#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自訂 GUI 元件

此檔案包含可重複使用的自訂 UI 元件
"""

import tkinter as tk
from tkinter import ttk


class LabeledEntry(ttk.Frame):
    """帶標籤的輸入框元件"""

    def __init__(self, parent, label_text, button_text=None, button_command=None, **kwargs):
        super().__init__(parent)

        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side=tk.LEFT, padx=(0, 5))

        self.var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var, **kwargs)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        if button_text and button_command:
            self.button = ttk.Button(
                self, text=button_text, command=button_command)
            self.button.pack(side=tk.LEFT)

    def get(self):
        """取得輸入值"""
        return self.var.get()

    def set(self, value):
        """設定輸入值"""
        self.var.set(value)


class ProgressLogger(ttk.Frame):
    """進度條 + 日誌元件"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # 狀態標籤
        self.status_label = ttk.Label(self, text="準備就緒")
        self.status_label.pack(fill=tk.X, pady=(0, 5))

        # 進度條
        self.progress = ttk.Progressbar(self, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 5))

        # 日誌區域
        from tkinter import scrolledtext
        self.log_text = scrolledtext.ScrolledText(
            self, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

    def set_status(self, text):
        """設定狀態文字"""
        self.status_label.config(text=text)

    def set_progress(self, value):
        """設定進度值 (0-100)"""
        self.progress['value'] = value

    def log(self, message):
        """寫入日誌"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear(self):
        """清空日誌"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.progress['value'] = 0


class ButtonGroup(ttk.Frame):
    """按鈕群組元件"""

    def __init__(self, parent, buttons, **kwargs):
        """
        Args:
            parent: 父元件
            buttons: [(text, command), ...] 的列表
        """
        super().__init__(parent, **kwargs)

        self.buttons = []
        for text, command in buttons:
            btn = ttk.Button(self, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons.append(btn)

    def enable_all(self):
        """啟用所有按鈕"""
        for btn in self.buttons:
            btn.config(state=tk.NORMAL)

    def disable_all(self):
        """禁用所有按鈕"""
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)


# 測試程式碼
if __name__ == "__main__":
    root = tk.Tk()
    root.title("測試自訂元件")
    root.geometry("600x400")

    # 測試 LabeledEntry
    entry = LabeledEntry(root, "路徑:", "瀏覽", lambda: print("瀏覽"))
    entry.pack(fill=tk.X, padx=10, pady=10)

    # 測試 ProgressLogger
    logger = ProgressLogger(root)
    logger.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    logger.log("測試訊息 1")
    logger.log("測試訊息 2")
    logger.set_progress(50)

    # 測試 ButtonGroup
    buttons = [
        ("開始", lambda: logger.log("開始")),
        ("停止", lambda: logger.log("停止")),
        ("清除", logger.clear)
    ]
    btn_group = ButtonGroup(root, buttons)
    btn_group.pack(pady=10)

    root.mainloop()
