#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batocera Gamelist 自動翻譯工具 - 核心翻譯邏輯

功能：
- 自動遍歷 Batocera roms 目錄
- 使用語系包（字典檔）快速查找翻譯
- 透過 Google 搜尋獲取遊戲中文譯名
- 支援多種顯示模式（僅中文、中英混合等）
- 翻譯遊戲名稱和描述
"""

import os
import sys
import json
import time
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from translation_api import TranslationAPIManager


def get_resource_path(relative_path: str) -> Path:
    """取得資源檔案的絕對路徑（支援 PyInstaller 打包）"""
    try:
        # PyInstaller 建立的臨時資料夾
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # 正常 Python 環境
        base_path = Path(__file__).parent

    return base_path / relative_path


# 平台對照表
PLATFORM_NAMES = {
    'nes': 'FC紅白機',
    'snes': '超級任天堂',
    'megadrive': 'MD Mega Drive',
    'genesis': 'MD Mega Drive',
    'gba': 'GBA Game Boy Advance',
    'gb': 'Game Boy',
    'gbc': 'Game Boy Color',
    'nds': 'NDS Nintendo DS',
    'n64': 'N64 Nintendo 64',
    'ps1': 'PS1 PlayStation',
    'psx': 'PS1 PlayStation',
    'ps2': 'PS2 PlayStation 2',
    'psp': 'PSP PlayStation Portable',
    'arcade': '街機',
    'mame': '街機 MAME',
    'fbneo': '街機 FBNeo',
    'neogeo': 'Neo Geo',
    'pcengine': 'PC Engine',
    'mastersystem': 'Master System',
    'gamegear': 'Game Gear',
    'dreamcast': 'Dreamcast',
    'saturn': 'Sega Saturn',
    'atari2600': 'Atari 2600',
    'atari7800': 'Atari 7800',
}

# 常見遊戲預設翻譯
DEFAULT_TRANSLATIONS = {
    "Super Mario Bros": "超級瑪利歐兄弟",
    "Super Mario Bros 2": "超級瑪利歐兄弟2",
    "Super Mario Bros 3": "超級瑪利歐兄弟3",
    "Super Mario World": "超級瑪利歐世界",
    "The Legend of Zelda": "薩爾達傳說",
    "Contra": "魂斗羅",
    "Super Contra": "超級魂斗羅",
    "Castlevania": "惡魔城",
    "Mega Man": "洛克人",
    "Mega Man 2": "洛克人2",
    "Metroid": "密特羅德",
    "Final Fantasy": "太空戰士",
    "Dragon Quest": "勇者鬥惡龍",
    "Street Fighter II": "快打旋風II",
    "Sonic the Hedgehog": "音速小子",
    "Tetris": "俄羅斯方塊",
    "Pac-Man": "小精靈",
    "Donkey Kong": "大金剛",
}


class GamelistTranslator:
    """Batocera Gamelist 翻譯器"""

    def __init__(self,
                 translations_dir: str = "translations",
                 local_cache_file: str = "local_cache.json",
                 display_mode: str = "chinese_only",
                 max_name_length: int = 100,
                 translate_desc: bool = True,
                 search_delay: float = 2.0,
                 fuzzy_match: bool = True,
                 groq_api_key: Optional[str] = None,
                 gemini_api_key: Optional[str] = None,
                 deepl_api_key: Optional[str] = None,
                 enable_groq: bool = True,
                 enable_gemini: bool = True,
                 enable_deepl: bool = True,
                 enable_mymemory: bool = True,
                 enable_googletrans: bool = True):
        """
        初始化翻譯器

        Args:
            translations_dir: 語系包目錄（可以是相對路徑）
            local_cache_file: 本地快取檔案
            display_mode: 顯示模式 (chinese_only, chinese_english, english_chinese, english_only)
            max_name_length: 名稱最大長度
            translate_desc: 是否翻譯描述
            search_delay: 搜尋延遲（秒）
            fuzzy_match: 是否啟用模糊比對（處理大小寫、空白等差異）
            groq_api_key: Groq API Key
            gemini_api_key: Google Gemini API Key
            deepl_api_key: DeepL API Key
            enable_groq: 是否啟用 Groq
            enable_gemini: 是否啟用 Gemini
            enable_deepl: 是否啟用 DeepL
            enable_mymemory: 是否啟用 MyMemory
            enable_googletrans: 是否啟用 googletrans
        """
        # 處理相對路徑（支援打包後的執行檔）
        if os.path.isabs(translations_dir):
            self.translations_dir = Path(translations_dir)
        else:
            self.translations_dir = get_resource_path(translations_dir)

        self.local_cache_file = local_cache_file
        self.display_mode = display_mode
        self.max_name_length = max_name_length
        self.translate_desc = translate_desc
        self.search_delay = search_delay
        self.fuzzy_match = fuzzy_match

        # 建立語系包目錄（如果不存在）
        self.translations_dir.mkdir(exist_ok=True)

        # 載入快取
        self.local_cache = self.load_local_cache()

        # HTTP 設定
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 如果沒有提供 API Keys，嘗試從 config.json 載入
        if not groq_api_key or not gemini_api_key:
            config_file = Path("config.json")
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    if not groq_api_key:
                        groq_api_key = config.get("groq_api_key")
                    if not gemini_api_key:
                        gemini_api_key = config.get("gemini_api_key")
                    if not deepl_api_key:
                        deepl_api_key = config.get("deepl_api_key")
                except Exception as e:
                    print(f"警告：無法載入 config.json: {e}")

        # 初始化 API 管理器
        self.api_manager = TranslationAPIManager(
            groq_api_key=groq_api_key,
            gemini_api_key=gemini_api_key,
            deepl_api_key=deepl_api_key,
            enable_groq=enable_groq,
            enable_gemini=enable_gemini,
            enable_deepl=enable_deepl,
            enable_mymemory=enable_mymemory,
            enable_googletrans=enable_googletrans
        )

    def scan_roms_directory(self, roms_path: str) -> List[Tuple[str, str]]:
        """
        掃描 roms 目錄，找出所有 gamelist.xml

        Args:
            roms_path: roms 根目錄路徑

        Returns:
            [(platform, gamelist_path), ...] 的列表
        """
        results = []
        roms_dir = Path(roms_path)

        if not roms_dir.exists():
            raise FileNotFoundError(f"Roms 目錄不存在: {roms_path}")

        # 遍歷所有子資料夾
        for platform_dir in roms_dir.iterdir():
            if platform_dir.is_dir():
                gamelist_path = platform_dir / "gamelist.xml"
                if gamelist_path.exists():
                    platform = platform_dir.name.lower()
                    results.append((platform, str(gamelist_path)))
                    print(f"找到 {platform} 的 gamelist.xml")

        return results

    def load_translation_dict(self, platform: str) -> Dict[str, str]:
        """載入指定平台的翻譯字典（語系包）"""
        dict_file = self.translations_dir / f"translations_{platform}.json"

        if dict_file.exists():
            with open(dict_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {}

    def load_description_dict(self, platform: str) -> Dict[str, str]:
        """載入指定平台的描述翻譯字典"""
        dict_file = self.translations_dir / f"descriptions_{platform}.json"

        if dict_file.exists():
            with open(dict_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {}

    def load_local_cache(self) -> Dict:
        """載入本地快取"""
        if os.path.exists(self.local_cache_file):
            with open(self.local_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {"names": {}, "descriptions": {}}

    def save_local_cache(self):
        """儲存本地快取（過濾無效翻譯）"""
        # 清理快取：移除中文對中文、英文對英文的無意義翻譯
        cleaned_cache = {
            "names": {},
            "descriptions": {}
        }

        for key, value in self.local_cache.get("names", {}).items():
            # 只保留有效的翻譯（英文→中文，且不相同）
            if value and key != value:
                # 如果原文是英文且譯文是中文，保留
                if not self.contains_chinese(key) and self.contains_chinese(value):
                    cleaned_cache["names"][key] = value
                # 如果原文和譯文都是中文但不同（例如簡繁轉換），也保留
                elif self.contains_chinese(key) and self.contains_chinese(value) and key != value:
                    cleaned_cache["names"][key] = value

        for key, value in self.local_cache.get("descriptions", {}).items():
            if value and key != value:
                cleaned_cache["descriptions"][key] = value

        with open(self.local_cache_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_cache, f, ensure_ascii=False, indent=2)

    def contains_chinese(self, text: str) -> bool:
        """檢查文字是否包含中文字元"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)

    def normalize_key(self, text: str) -> str:
        """
        正規化字串用於模糊比對
        - 轉小寫
        - 移除多餘空白
        - 移除常見標點符號
        - 統一連字符
        """
        if not text:
            return ""

        # 轉小寫
        normalized = text.lower()

        # 移除常見標點符號（保留連字符和撇號）
        normalized = re.sub(r'[.!?,;:"\[\]\(\)]', '', normalized)

        # 統一連字符（- 和 –）
        normalized = normalized.replace('–', '-').replace('—', '-')

        # 移除多餘空白
        normalized = ' '.join(normalized.split())

        return normalized

    def clean_game_name(self, name: str) -> str:
        """
        清理遊戲名稱（移除區域標記等）

        範例: "Super Mario Bros (USA) [!]" -> "Super Mario Bros"
        """
        # 移除括號和方括號內的內容
        name = re.sub(r'\([^)]*\)', '', name)
        name = re.sub(r'\[[^\]]*\]', '', name)

        # 移除多餘空格
        name = ' '.join(name.split())

        return name.strip()

    def lookup_translation(self, game_name: str, platform: str,
                           is_description: bool = False) -> Optional[str]:
        """
        查找翻譯（按優先順序）
        1. 精確匹配：預設翻譯、語系包、本地快取
        2. 模糊匹配（如果啟用）：正規化後比對
        3. 返回 None（需要搜尋）
        """
        # 1. 精確匹配 - 預設翻譯（僅遊戲名稱）
        if not is_description and game_name in DEFAULT_TRANSLATIONS:
            return DEFAULT_TRANSLATIONS[game_name]

        # 2. 精確匹配 - 語系包
        if is_description:
            desc_dict = self.load_description_dict(platform)
            if game_name in desc_dict:
                return desc_dict[game_name]
        else:
            trans_dict = self.load_translation_dict(platform)
            if game_name in trans_dict:
                return trans_dict[game_name]

        # 3. 精確匹配 - 本地快取
        cache_key = "descriptions" if is_description else "names"
        if game_name in self.local_cache[cache_key]:
            return self.local_cache[cache_key][game_name]

        # 4. 模糊匹配（如果啟用）
        if self.fuzzy_match:
            normalized_input = self.normalize_key(game_name)

            # 從預設翻譯模糊匹配
            if not is_description:
                for key, value in DEFAULT_TRANSLATIONS.items():
                    if self.normalize_key(key) == normalized_input:
                        print(f"  ✓ 模糊匹配: '{game_name}' → '{key}' = {value}")
                        return value

            # 從語系包模糊匹配
            target_dict = desc_dict if is_description else trans_dict
            for key, value in target_dict.items():
                if self.normalize_key(key) == normalized_input:
                    print(f"  ✓ 模糊匹配: '{game_name}' → '{key}' = {value}")
                    return value

            # 從本地快取模糊匹配
            for key, value in self.local_cache[cache_key].items():
                if self.normalize_key(key) == normalized_input:
                    print(f"  ✓ 模糊匹配: '{game_name}' → '{key}' = {value}")
                    return value

        return None

    def search_google(self, query: str) -> str:
        """搜尋 Google 並返回 HTML"""
        url = f"https://www.google.com/search?q={query}&hl=zh-TW"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"搜尋失敗: {e}")
            return ""

    def extract_chinese_name(self, html: str, original_name: str) -> Optional[str]:
        """從搜尋結果提取中文名稱"""
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        # 擴展黑名單：排除這些詞和包含這些關鍵字的句子
        blacklist = {'請按一下這裡', '請按此處', '點擊這裡', '點此', '更多資訊',
                     '查看更多', '閱讀更多', '繼續閱讀', '了解更多', '系統', '重新導向',
                     '數秒鐘', '頁面', '網站', '連結', '存取', '瀏覽器'}

        # 黑名單關鍵字 - 包含任一關鍵字就排除整個句子
        blacklist_keywords = ['系統', '重新導向', '數秒鐘', '請按', '點擊', '點此', '連結']

        def is_blacklisted(text):
            """檢查文字是否在黑名單中或包含黑名單關鍵字"""
            if text in blacklist:
                return True
            for keyword in blacklist_keywords:
                if keyword in text:
                    return True
            return False

        candidates = {}

        # 優先從 h1, h2, h3 標題提取 (通常是頁面主標題)
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            text = heading.get_text().strip()

            # 尋找包含中英文的標題格式: "中文名稱 (English Name)"
            # 例如: "動物森友會 快樂之家設計師 (Animal Crossing: Happy Home Designer)"
            match = re.search(r'([^\(]+)\s*\([^)]*' + re.escape(original_name.replace(
                '-', '').replace(':', '')) + r'[^)]*\)', text, re.IGNORECASE)
            if match:
                chinese_part = match.group(1).strip()
                if self.contains_chinese(chinese_part) and not is_blacklisted(chinese_part):
                    candidates[chinese_part] = candidates.get(
                        chinese_part, 0) + 10

        # 尋找所有文字內容
        for text_elem in soup.find_all(['h3', 'span', 'div', 'p']):
            text = text_elem.get_text()

            # 過濾掉黑名單句子
            if is_blacklisted(text):
                continue

            # 尋找書名號內的內容（最高優先級）
            matches = re.findall(r'《([^》]+)》', text)
            for match in matches:
                if self.contains_chinese(match) and not is_blacklisted(match):
                    candidates[match] = candidates.get(match, 0) + 5

            # 尋找「中文名：XXX」或「中文譯名：XXX」格式
            title_matches = re.findall(
                r'(?:中文名|中文譯名|譯名)[：:](.*?)(?:[，。；]|$)', text)
            for match in title_matches:
                match = match.strip()
                if self.contains_chinese(match) and not is_blacklisted(match):
                    candidates[match] = candidates.get(match, 0) + 4

            # 尋找包含中文的片段
            chinese_parts = re.findall(r'[\u4e00-\u9fff]+', text)
            for part in chinese_parts:
                if 3 <= len(part) <= 20 and not is_blacklisted(part):
                    candidates[part] = candidates.get(part, 0) + 1

        if not candidates:
            return None

        # 選擇得分最高的候選
        best_candidate = max(candidates.items(), key=lambda x: x[1])
        return best_candidate[0]

    def translate_name(self, game_name: str, platform: str) -> str:
        """
        翻譯遊戲名稱（台灣慣用譯名）

        策略：
        1. 字典查詢（語系包、預設翻譯、本地快取）
        2. Google 搜尋（抓取維基百科、巴哈姆特等網站的譯名）
        3. Gemini API（AI 推斷台灣慣用譯名）
        4. 保持原名
        """
        # 如果已是中文，直接返回
        if self.contains_chinese(game_name):
            return game_name

        # 清理名稱
        clean_name = self.clean_game_name(game_name)

        # 1. 查找翻譯（語系包、預設翻譯、本地快取）
        translation = self.lookup_translation(
            clean_name, platform, is_description=False)
        if translation:
            print(f"  [字典] {clean_name} → {translation}")
            return translation

        # 2. Google 搜尋
        query = clean_name
        print(f"  [Google搜尋] {clean_name}...", end='', flush=True)

        html = self.search_google(query)
        print(f" 完成", flush=True)

        print(f"  [分析結果]...", end='', flush=True)
        chinese_name = self.extract_chinese_name(html, clean_name)
        print(f" 完成", flush=True)

        if chinese_name:
            print(f"  → {chinese_name}")
            # 加入本地快取
            self.local_cache["names"][clean_name] = chinese_name
            self.save_local_cache()

            # 短暫延遲避免被封鎖
            if self.search_delay > 0:
                time.sleep(self.search_delay)
            return chinese_name

        # 3. 嘗試 Gemini API（AI 推斷台灣慣用譯名）
        platform_chinese = PLATFORM_NAMES.get(platform.lower(), platform)
        gemini_result = self.api_manager.translate_game_name(
            clean_name, platform_chinese)

        if gemini_result:
            print(f"  → {gemini_result}")
            # 加入本地快取
            self.local_cache["names"][clean_name] = gemini_result
            self.save_local_cache()
            return gemini_result

        # 4. 全部失敗，保持原名
        print(f"  [保持原名] {clean_name}")
        return clean_name

    def translate_description(self, description: str, platform: str) -> str:
        """
        翻譯遊戲描述

        策略：
        1. 字典查詢（描述語系包、本地快取）
        2. DeepL API（品質最好）
        3. MyMemory API（免費，無需 Key）
        4. googletrans（最後手段）
        """
        if not description or self.contains_chinese(description):
            return description

        # 1. 查找快取
        translation = self.lookup_translation(
            description, platform, is_description=True)
        if translation:
            print(f"  [字典] 描述翻譯")
            return translation

        # 2-4. 使用 API 管理器翻譯（會自動降級）
        translated = self.api_manager.translate_description(description)

        if translated:
            # 儲存到快取
            self.local_cache["descriptions"][description] = translated
            self.save_local_cache()
            return translated
        else:
            # 全部失敗，保持原文
            print(f"  [描述] 翻譯失敗，保持原文")
            return description

    def format_game_name(self, english_name: str, chinese_name: str) -> str:
        """根據顯示模式格式化遊戲名稱"""
        # 如果沒有中文譯名，使用英文原名
        if not chinese_name:
            return english_name

        if self.display_mode == "chinese_only":
            result = chinese_name
        elif self.display_mode == "chinese_english":
            result = f"{chinese_name} ({english_name})"
        elif self.display_mode == "english_chinese":
            result = f"{english_name} ({chinese_name})"
        elif self.display_mode == "english_only":
            result = english_name
        else:
            result = chinese_name

        # 處理長度限制
        if len(result) > self.max_name_length:
            result = result[:self.max_name_length] + "..."

        return result

    def update_gamelist(self, gamelist_path: str, platform: str, dry_run: bool = False, limit: int = 0, use_batch: bool = True):
        """更新單一 gamelist.xml

        Args:
            limit: 限制處理的遊戲數量,0 表示處理全部
            use_batch: 是否使用批次翻譯（預設 True，更快速）
        """
        print(f"\n>> 開始處理平台: {platform.upper()}")
        print(f">> 讀取檔案: {gamelist_path}...", end='', flush=True)

        # 解析 XML
        tree = ET.parse(gamelist_path)
        root = tree.getroot()
        print(" 完成", flush=True)

        games = root.findall('game')
        total = len(games)

        # 如果有限制,只處理指定數量
        if limit > 0 and limit < total:
            games = games[:limit]
            print(f">> 限制處理前 {limit} 個遊戲 (總共 {total} 個)\n")
        else:
            print(f">> 共有 {total} 個遊戲需要處理\n")

        # === 批次翻譯模式 ===
        if use_batch:
            # 收集所有需要翻譯的遊戲名稱
            games_to_translate = []
            game_elements = []

            for game in games:
                name_elem = game.find('name')
                if name_elem is not None and name_elem.text:
                    original_name = name_elem.text
                    clean_name = self.clean_game_name(original_name)

                    # 檢查快取
                    cached = self.lookup_translation(
                        clean_name, platform, is_description=False)
                    if not cached:
                        games_to_translate.append(clean_name)
                        game_elements.append(
                            (game, original_name, clean_name, name_elem))

            if games_to_translate:
                print(f">> 使用批次翻譯模式，共 {len(games_to_translate)} 個遊戲需要翻譯\n")

                # 分批處理（每批 50 個，避免超過 API token 限制）
                batch_size = 50
                all_batch_results = {}

                for i in range(0, len(games_to_translate), batch_size):
                    batch = games_to_translate[i:i + batch_size]
                    batch_num = i // batch_size + 1
                    total_batches = (len(games_to_translate) +
                                     batch_size - 1) // batch_size

                    print(
                        f">> 批次 {batch_num}/{total_batches}：翻譯 {len(batch)} 個遊戲...")

                    # 批次呼叫 API
                    platform_chinese = PLATFORM_NAMES.get(
                        platform.lower(), platform)
                    batch_results = self.api_manager.translate_game_names_batch(
                        batch, platform_chinese)

                    # 確保 batch_results 不為 None
                    if batch_results:
                        all_batch_results.update(batch_results)
                    else:
                        print(f"   ⚠️  批次 {batch_num} API 翻譯失敗")

                # 應用翻譯結果
                success_count = 0
                for game, original_name, clean_name, name_elem in game_elements:
                    chinese_name = all_batch_results.get(clean_name)

                    if chinese_name:
                        # 只儲存有效的英文→中文翻譯到快取
                        # 避免中文對中文、或相同的無意義翻譯
                        if (not self.contains_chinese(clean_name) and
                            self.contains_chinese(chinese_name) and
                                clean_name != chinese_name):
                            self.local_cache["names"][clean_name] = chinese_name
                            success_count += 1

                    formatted_name = self.format_game_name(
                        clean_name, chinese_name)

                    if not dry_run:
                        name_elem.text = formatted_name

                    # 顯示翻譯結果（清楚顯示英文 → 中文）
                    if chinese_name:
                        print(f"  [API] {clean_name} → {chinese_name}")
                    else:
                        print(f"  [保留] {clean_name}")

                # 儲存快取
                if all_batch_results:
                    self.save_local_cache()
                    print(
                        f"\n>> API 翻譯成功: {success_count}/{len(games_to_translate)} 個遊戲")

            # 處理已有快取的遊戲
            cached_count = 0
            cached_names_to_collect = []
            for game in games:
                name_elem = game.find('name')
                if name_elem is not None and name_elem.text:
                    clean_name = self.clean_game_name(name_elem.text)

                    # 只處理不在待翻譯清單中的遊戲
                    if clean_name not in [g[2] for g in game_elements]:
                        cached = self.lookup_translation(
                            clean_name, platform, is_description=False)

                        if cached:
                            formatted_name = self.format_game_name(
                                clean_name, cached)
                            if not dry_run:
                                name_elem.text = formatted_name
                            cached_count += 1
                            cached_names_to_collect.append(
                                (clean_name, cached))

            if cached_count > 0:
                print(f"\n>> 從快取載入 {cached_count} 個遊戲翻譯")
                # 顯示前 5 個快取範例
                for i, (eng, chi) in enumerate(cached_names_to_collect[:5]):
                    print(f"  [快取] {eng} → {chi}")
                if cached_count > 5:
                    print(f"  ... 還有 {cached_count - 5} 個")

            updated = len(games_to_translate) + cached_count

        # === 逐一翻譯模式（舊方法） ===
        else:
            updated = 0
            for idx, game in enumerate(games, 1):
                name_elem = game.find('name')
                desc_elem = game.find('desc')

                if name_elem is not None and name_elem.text:
                    original_name = name_elem.text
                    print(f"\n[{idx}/{len(games)}] {original_name}")
                    clean_name = self.clean_game_name(original_name)

                    # 翻譯名稱
                    chinese_name = self.translate_name(clean_name, platform)
                    formatted_name = self.format_game_name(
                        clean_name, chinese_name)

                    if not dry_run:
                        name_elem.text = formatted_name

                    print(f"  最終: {formatted_name}")
                    updated += 1

                    # 翻譯描述
                    if self.translate_desc and desc_elem is not None and desc_elem.text:
                        original_desc = desc_elem.text
                        print(f"  >> 翻譯描述...", end='', flush=True)
                        translated_desc = self.translate_description(
                            original_desc, platform)

                        if not dry_run and translated_desc != original_desc:
                            desc_elem.text = translated_desc

                        if translated_desc != original_desc:
                            print(f" {translated_desc[:50]}...", flush=True)
                        else:
                            print(" 保持原文", flush=True)

        # 儲存檔案
        if not dry_run:
            # 使用 tostring + open 寫入 (相容 WSL 路徑)
            xml_str = ET.tostring(tree.getroot(), encoding='unicode',
                                  method='xml')
            xml_content = f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'

            with open(gamelist_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)

            print(f"\n[OK] 已更新 {updated}/{total} 個遊戲")
        else:
            print(f"\n[預覽模式] 將更新 {updated}/{total} 個遊戲")

        return updated  # 回傳更新數量

    def batch_update(self, roms_path: str, dry_run: bool = False):
        """
        批次更新所有平台

        Args:
            roms_path: roms 根目錄
            dry_run: 預覽模式，不實際修改檔案
        """
        print("=" * 60)
        print("Batocera Gamelist 自動翻譯工具")
        print("=" * 60)

        # 掃描所有 gamelist.xml
        platforms = self.scan_roms_directory(roms_path)

        if not platforms:
            print("未找到任何 gamelist.xml 檔案")
            return

        print(f"\n找到 {len(platforms)} 個平台\n")

        # 逐一處理
        for platform, gamelist_path in platforms:
            try:
                self.update_gamelist(gamelist_path, platform, dry_run)
            except Exception as e:
                print(f"✗ 處理 {platform} 時發生錯誤: {e}")
                continue

        print("\n" + "=" * 60)
        print("處理完成！")
        print("=" * 60)


def main():
    """命令列介面"""
    import argparse

    parser = argparse.ArgumentParser(description='Batocera Gamelist 自動翻譯工具')
    parser.add_argument('--roms-path', required=True, help='Roms 根目錄路徑')
    parser.add_argument('--mode', default='chinese_only',
                        choices=['chinese_only', 'chinese_english',
                                 'english_chinese', 'english_only'],
                        help='顯示模式')
    parser.add_argument('--max-length', type=int, default=100, help='名稱最大長度')
    parser.add_argument('--no-desc', action='store_true', help='不翻譯描述')
    parser.add_argument('--no-fuzzy', action='store_true',
                        help='停用模糊比對（精確匹配）')
    parser.add_argument('--dry-run', action='store_true', help='預覽模式（不實際修改檔案）')
    parser.add_argument('--translations-dir',
                        default='translations', help='語系包目錄')

    args = parser.parse_args()

    # 建立翻譯器
    translator = GamelistTranslator(
        translations_dir=args.translations_dir,
        display_mode=args.mode,
        max_name_length=args.max_length,
        translate_desc=not args.no_desc,
        fuzzy_match=not args.no_fuzzy
    )

    # 執行批次更新
    translator.batch_update(args.roms_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
