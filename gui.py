#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batocera Gamelist 自動翻譯工具 - GUI 介面

使用 Tkinter 建立圖形化介面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import json
import os
from datetime import datetime
from translator import GamelistTranslator

# 程式版本
VERSION = "1.0"


class TranslatorGUI:
    """翻譯器 GUI 主視窗"""

    def __init__(self, root):
        self.root = root
        self.root.title(f"Batocera Gamelist 中文化工具 v{VERSION}")
        self.root.geometry("800x700")
        self.root.minsize(800, 600)

        # 設定變數
        self.roms_path = tk.StringVar()
        self.translations_dir = tk.StringVar(value="translations")  # 使用相對路徑
        self.display_mode = tk.StringVar(value="chinese_only")
        self.translate_desc = tk.BooleanVar(value=True)
        self.fuzzy_match = tk.BooleanVar(value=True)  # 模糊比對（預設開啟）
        self.max_length = tk.IntVar(value=100)

        # API 設定
        self.groq_api_key = tk.StringVar(value="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")
        self.gemini_api_key = tk.StringVar()
        self.deepl_api_key = tk.StringVar()
        self.enable_groq = tk.BooleanVar(value=True)
        self.enable_gemini = tk.BooleanVar(value=True)
        self.enable_deepl = tk.BooleanVar(value=True)
        self.enable_mymemory = tk.BooleanVar(value=True)
        self.enable_googletrans = tk.BooleanVar(value=True)

        # 狀態變數
        self.is_running = False
        self.log_queue = queue.Queue()
        self.translator = None

        # 建立 UI
        self.setup_ui()

        # 載入設定
        self.load_config()

        # 啟動日誌更新
        self.update_log()

        # 視窗關閉處理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """建立所有 UI 元件"""
        # 建立主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 設定權重讓元件可以縮放
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # 1. 路徑設定區
        self.create_path_section(main_frame)

        # 2. 翻譯設定區
        self.create_settings_section(main_frame)

        # 3. 進度顯示區
        self.create_progress_section(main_frame)

        # 4. 操作按鈕區
        self.create_button_section(main_frame)

        # 5. 狀態列
        self.create_statusbar(main_frame)

    def create_path_section(self, parent):
        """建立路徑設定區"""
        frame = ttk.LabelFrame(parent, text="路徑設定", padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)

        # Roms 目錄
        ttk.Label(frame, text="Roms 目錄:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.roms_path).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(frame, text="瀏覽...", command=self.browse_roms_path).grid(
            row=0, column=2)

        # 語系包目錄
        ttk.Label(frame, text="語系包目錄:").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.translations_dir).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(frame, text="瀏覽...", command=self.browse_translations_dir).grid(
            row=1, column=2)

    def create_settings_section(self, parent):
        """建立翻譯設定區"""
        frame = ttk.LabelFrame(parent, text="翻譯設定", padding="10")
        frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)

        # 顯示模式
        ttk.Label(frame, text="顯示模式:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        mode_frame = ttk.Frame(frame)
        mode_frame.grid(row=0, column=1, sticky=tk.W, columnspan=2)

        ttk.Radiobutton(mode_frame, text="僅中文", variable=self.display_mode,
                        value="chinese_only").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="中文 (英文)", variable=self.display_mode,
                        value="chinese_english").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="英文 (中文)", variable=self.display_mode,
                        value="english_chinese").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="僅英文", variable=self.display_mode,
                        value="english_only").pack(side=tk.LEFT, padx=5)

        # 翻譯描述
        ttk.Checkbutton(frame, text="翻譯遊戲描述", variable=self.translate_desc).grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=5)

        # 模糊比對
        fuzzy_cb = ttk.Checkbutton(
            frame, text="啟用模糊比對 (忽略大小寫、空白差異)",
            variable=self.fuzzy_match)
        fuzzy_cb.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)

        # 最大長度
        ttk.Label(frame, text="最大名稱長度:").grid(
            row=3, column=0, sticky=tk.W, pady=5)
        length_spinbox = ttk.Spinbox(
            frame, from_=50, to=200, textvariable=self.max_length, width=10)
        length_spinbox.grid(row=3, column=1, sticky=tk.W, padx=5)
        ttk.Label(frame, text="字元").grid(row=3, column=2, sticky=tk.W)

        # API 設定區
        ttk.Separator(frame, orient='horizontal').grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(frame, text="API 設定", font=('', 9, 'bold')).grid(
            row=5, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        # Groq API (最優先)
        groq_frame = ttk.Frame(frame)
        groq_frame.grid(row=6, column=0, columnspan=3,
                        sticky=(tk.W, tk.E), pady=2)
        ttk.Checkbutton(groq_frame, text="Groq API (遊戲名稱，速度最快)",
                        variable=self.enable_groq).pack(side=tk.LEFT)
        ttk.Label(groq_frame, text="Key:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Entry(groq_frame, textvariable=self.groq_api_key,
                  show="*", width=30).pack(side=tk.LEFT, padx=2)

        # Gemini API
        gemini_frame = ttk.Frame(frame)
        gemini_frame.grid(row=7, column=0, columnspan=3,
                          sticky=(tk.W, tk.E), pady=2)
        ttk.Checkbutton(gemini_frame, text="Gemini API (遊戲名稱備援)",
                        variable=self.enable_gemini).pack(side=tk.LEFT)
        ttk.Label(gemini_frame, text="Key:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Entry(gemini_frame, textvariable=self.gemini_api_key,
                  show="*", width=30).pack(side=tk.LEFT, padx=2)

        # DeepL API
        deepl_frame = ttk.Frame(frame)
        deepl_frame.grid(row=8, column=0, columnspan=3,
                         sticky=(tk.W, tk.E), pady=2)
        ttk.Checkbutton(deepl_frame, text="DeepL API (描述翻譯)",
                        variable=self.enable_deepl).pack(side=tk.LEFT)
        ttk.Label(deepl_frame, text="Key:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Entry(deepl_frame, textvariable=self.deepl_api_key,
                  show="*", width=30).pack(side=tk.LEFT, padx=2)

        # MyMemory API
        ttk.Checkbutton(frame, text="MyMemory API (描述翻譯，免費無需 Key)",
                        variable=self.enable_mymemory).grid(
            row=9, column=0, columnspan=3, sticky=tk.W, pady=2)

        # googletrans
        ttk.Checkbutton(frame, text="googletrans (備用，不穩定)",
                        variable=self.enable_googletrans).grid(
            row=10, column=0, columnspan=3, sticky=tk.W, pady=2)

    def create_progress_section(self, parent):
        """建立進度顯示區"""
        frame = ttk.LabelFrame(parent, text="處理進度", padding="10")
        frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        parent.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # 狀態標籤
        self.status_label = ttk.Label(frame, text="目前狀態: 準備就緒")
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        # 進度條
        self.progress_bar = ttk.Progressbar(frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # 日誌輸出區
        self.log_text = scrolledtext.ScrolledText(
            frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=2, column=0, sticky=(
            tk.W, tk.E, tk.N, tk.S), pady=5)
        self.log_text.config(state=tk.DISABLED)

    def create_button_section(self, parent):
        """建立操作按鈕區"""
        frame = ttk.Frame(parent, padding="10")
        frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)

        # 第一排按鈕
        btn_frame1 = ttk.Frame(frame)
        btn_frame1.pack(fill=tk.X, pady=2)

        self.start_btn = ttk.Button(
            btn_frame1, text="開始翻譯", command=self.start_translation)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.preview_btn = ttk.Button(
            btn_frame1, text="預覽模式", command=self.preview_translation)
        self.preview_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            btn_frame1, text="停止", command=self.stop_translation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame1, text="清空日誌", command=self.clear_log).pack(
            side=tk.LEFT, padx=5)

        # 第二排按鈕
        btn_frame2 = ttk.Frame(frame)
        btn_frame2.pack(fill=tk.X, pady=2)

        ttk.Button(btn_frame2, text="語系包管理", command=self.show_dict_manager).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="匯入語系包", command=self.import_dict).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="匯出語系包", command=self.export_dict).pack(
            side=tk.LEFT, padx=5)

        # 第三排按鈕
        btn_frame3 = ttk.Frame(frame)
        btn_frame3.pack(fill=tk.X, pady=2)

        ttk.Button(btn_frame3, text="設定", command=self.show_settings).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame3, text="關於", command=self.show_about).pack(
            side=tk.LEFT, padx=5)

    def create_statusbar(self, parent):
        """建立狀態列"""
        frame = ttk.Frame(parent, relief=tk.SUNKEN)
        frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=2)

        self.statusbar_label = ttk.Label(frame, text=f"v{VERSION} | 準備就緒")
        self.statusbar_label.pack(side=tk.LEFT, padx=5)

    # ========== 按鈕功能 ==========

    def browse_roms_path(self):
        """瀏覽 Roms 目錄"""
        path = filedialog.askdirectory(title="選擇 Roms 根目錄")
        if path:
            self.roms_path.set(path)

    def browse_translations_dir(self):
        """瀏覽語系包目錄"""
        path = filedialog.askdirectory(title="選擇語系包目錄")
        if path:
            self.translations_dir.set(path)

    def start_translation(self):
        """開始翻譯"""
        if not self.validate_inputs():
            return

        self.is_running = True
        self.toggle_buttons(False)
        self.log("開始翻譯作業...")

        # 在背景執行緒執行
        config = self.get_config()
        thread = threading.Thread(
            target=self.translation_worker, args=(config, False))
        thread.daemon = True
        thread.start()

    def preview_translation(self):
        """預覽模式"""
        if not self.validate_inputs():
            return

        self.is_running = True
        self.toggle_buttons(False)
        self.log("預覽模式（不會修改檔案）...")

        config = self.get_config()
        thread = threading.Thread(
            target=self.translation_worker, args=(config, True))
        thread.daemon = True
        thread.start()

    def stop_translation(self):
        """停止翻譯"""
        self.is_running = False
        self.log("正在停止...")

    def clear_log(self):
        """清空日誌"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def show_dict_manager(self):
        """顯示語系包管理視窗"""
        messagebox.showinfo("開發中", "語系包管理功能開發中...")

    def import_dict(self):
        """匯入語系包"""
        filepath = filedialog.askopenfilename(
            title="選擇語系包檔案",
            filetypes=[("JSON 檔案", "*.json"), ("所有檔案", "*.*")]
        )
        if filepath:
            self.log(f"匯入語系包: {filepath}")
            messagebox.showinfo("完成", "語系包匯入功能開發中...")

    def export_dict(self):
        """匯出語系包"""
        filepath = filedialog.asksaveasfilename(
            title="儲存語系包",
            defaultextension=".json",
            filetypes=[("JSON 檔案", "*.json"), ("所有檔案", "*.*")]
        )
        if filepath:
            self.log(f"匯出語系包: {filepath}")
            messagebox.showinfo("完成", "語系包匯出功能開發中...")

    def show_settings(self):
        """顯示設定視窗"""
        messagebox.showinfo("開發中", "進階設定功能開發中...")

    def show_about(self):
        """顯示關於對話框"""
        about_text = f"""Batocera Gamelist 中文化工具 v{VERSION}

自動將 Batocera 遊戲模擬器的英文遊戲名稱和描述翻譯成繁體中文

功能特色:
• 使用共享語系包快速查找翻譯
• 支援多種顯示模式
• 自動遍歷所有平台
• 社群協作分享翻譯成果

開發: Ming
授權: MIT License
"""
        messagebox.showinfo("關於", about_text)

    # ========== 核心功能 ==========

    def validate_inputs(self) -> bool:
        """驗證輸入"""
        if not self.roms_path.get():
            messagebox.showerror("錯誤", "請選擇 Roms 目錄")
            return False

        if not os.path.exists(self.roms_path.get()):
            messagebox.showerror("錯誤", "Roms 目錄不存在")
            return False

        return True

    def get_config(self) -> dict:
        """取得設定"""
        return {
            'roms_path': self.roms_path.get(),
            'translations_dir': self.translations_dir.get(),
            'display_mode': self.display_mode.get(),
            'max_name_length': self.max_length.get(),
            'translate_desc': self.translate_desc.get(),
            'fuzzy_match': self.fuzzy_match.get(),
            'groq_api_key': self.groq_api_key.get() or None,
            'gemini_api_key': self.gemini_api_key.get() or None,
            'deepl_api_key': self.deepl_api_key.get() or None,
            'enable_groq': self.enable_groq.get(),
            'enable_gemini': self.enable_gemini.get(),
            'enable_deepl': self.enable_deepl.get(),
            'enable_mymemory': self.enable_mymemory.get(),
            'enable_googletrans': self.enable_googletrans.get(),
        }

    def translation_worker(self, config: dict, dry_run: bool):
        """背景執行翻譯"""
        try:
            # 建立翻譯器
            self.translator = GamelistTranslator(
                translations_dir=config['translations_dir'],
                display_mode=config['display_mode'],
                max_name_length=config['max_name_length'],
                translate_desc=config['translate_desc'],
                fuzzy_match=config['fuzzy_match'],
                groq_api_key=config.get('groq_api_key'),
                gemini_api_key=config.get('gemini_api_key'),
                deepl_api_key=config.get('deepl_api_key'),
                enable_groq=config.get('enable_groq', True),
                enable_gemini=config.get('enable_gemini', True),
                enable_deepl=config.get('enable_deepl', True),
                enable_mymemory=config.get('enable_mymemory', True),
                enable_googletrans=config.get('enable_googletrans', True)
            )

            # 執行翻譯
            self.translator.batch_update(config['roms_path'], dry_run=dry_run)

            self.log_queue.put("✓ 翻譯完成！")
            self.log_queue.put("STATUS:完成")

        except Exception as e:
            self.log_queue.put(f"✗ 發生錯誤: {e}")
            self.log_queue.put("STATUS:錯誤")

        finally:
            self.is_running = False
            self.log_queue.put("BUTTONS:enable")

    def toggle_buttons(self, enabled: bool):
        """切換按鈕狀態"""
        state = tk.NORMAL if enabled else tk.DISABLED

        self.start_btn.config(state=state)
        self.preview_btn.config(state=state)
        self.stop_btn.config(state=tk.DISABLED if enabled else tk.NORMAL)

    def log(self, message: str):
        """寫入日誌"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_log(self):
        """定期檢查 queue 並更新日誌"""
        try:
            while True:
                msg = self.log_queue.get_nowait()

                if msg.startswith("STATUS:"):
                    status = msg.split(":")[1]
                    self.status_label.config(text=f"目前狀態: {status}")
                elif msg == "BUTTONS:enable":
                    self.toggle_buttons(True)
                else:
                    self.log(msg)

        except queue.Empty:
            pass

        # 每 100ms 檢查一次
        self.root.after(100, self.update_log)

    # ========== 設定檔管理 ==========

    def load_config(self):
        """載入使用者設定"""
        config_file = "gui_config.json"

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                self.roms_path.set(config.get('roms_path', ''))
                self.translations_dir.set(config.get(
                    'translations_dir', 'translations'))
                self.display_mode.set(config.get(
                    'display_mode', 'chinese_only'))
                self.translate_desc.set(config.get('translate_desc', True))
                self.fuzzy_match.set(config.get('fuzzy_match', True))
                self.max_length.set(config.get('max_length', 100))

                # API 設定
                # 注意: groq_api_key 已在初始化時設定，不從配置檔載入
                self.gemini_api_key.set(config.get('gemini_api_key', ''))
                self.deepl_api_key.set(config.get('deepl_api_key', ''))
                self.enable_groq.set(config.get('enable_groq', True))
                self.enable_gemini.set(config.get('enable_gemini', True))
                self.enable_deepl.set(config.get('enable_deepl', True))
                self.enable_mymemory.set(config.get('enable_mymemory', True))
                self.enable_googletrans.set(
                    config.get('enable_googletrans', True))

                self.log("✓ 已載入設定")
            except Exception as e:
                self.log(f"載入設定失敗: {e}")

    def save_config(self):
        """儲存使用者設定"""
        config = {
            'roms_path': self.roms_path.get(),
            'translations_dir': self.translations_dir.get(),
            'display_mode': self.display_mode.get(),
            'translate_desc': self.translate_desc.get(),
            'fuzzy_match': self.fuzzy_match.get(),
            'max_length': self.max_length.get(),
            # 注意: groq_api_key 不儲存到配置檔（已寫死在程式碼中）
            'gemini_api_key': self.gemini_api_key.get(),
            'deepl_api_key': self.deepl_api_key.get(),
            'enable_groq': self.enable_groq.get(),
            'enable_gemini': self.enable_gemini.get(),
            'enable_deepl': self.enable_deepl.get(),
            'enable_mymemory': self.enable_mymemory.get(),
            'enable_googletrans': self.enable_googletrans.get(),
        }

        try:
            with open('gui_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存設定失敗: {e}")

    def on_closing(self):
        """視窗關閉處理"""
        if self.is_running:
            if messagebox.askokcancel("確認", "翻譯作業進行中，確定要關閉嗎？"):
                self.save_config()
                self.root.destroy()
        else:
            self.save_config()
            self.root.destroy()


def main():
    """啟動 GUI"""
    root = tk.Tk()
    app = TranslatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
