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
import json
import time
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup

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
                 search_delay: float = 2.0):
        """
        初始化翻譯器

        Args:
            translations_dir: 語系包目錄
            local_cache_file: 本地快取檔案
            display_mode: 顯示模式 (chinese_only, chinese_english, english_chinese, english_only)
            max_name_length: 名稱最大長度
            translate_desc: 是否翻譯描述
            search_delay: 搜尋延遲（秒）
        """
        self.translations_dir = Path(translations_dir)
        self.local_cache_file = local_cache_file
        self.display_mode = display_mode
        self.max_name_length = max_name_length
        self.translate_desc = translate_desc
        self.search_delay = search_delay

        # 建立語系包目錄
        self.translations_dir.mkdir(exist_ok=True)

        # 載入快取
        self.local_cache = self.load_local_cache()

        # HTTP 設定
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

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
        """儲存本地快取"""
        with open(self.local_cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.local_cache, f, ensure_ascii=False, indent=2)

    def contains_chinese(self, text: str) -> bool:
        """檢查文字是否包含中文字元"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)

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

    def lookup_translation(self, game_name: str, platform: str, is_description: bool = False) -> Optional[str]:
        """
        查找翻譯（按優先順序）
        1. 預設翻譯（僅名稱）
        2. 語系包字典
        3. 本地快取
        4. 返回 None（需要搜尋）
        """
        # 1. 預設翻譯（僅遊戲名稱）
        if not is_description and game_name in DEFAULT_TRANSLATIONS:
            return DEFAULT_TRANSLATIONS[game_name]

        # 2. 語系包
        if is_description:
            desc_dict = self.load_description_dict(platform)
            if game_name in desc_dict:
                return desc_dict[game_name]
        else:
            trans_dict = self.load_translation_dict(platform)
            if game_name in trans_dict:
                return trans_dict[game_name]

        # 3. 本地快取
        cache_key = "descriptions" if is_description else "names"
        if game_name in self.local_cache[cache_key]:
            return self.local_cache[cache_key][game_name]

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
        candidates = {}

        # 尋找所有文字內容
        for text_elem in soup.find_all(['h3', 'span', 'div', 'p']):
            text = text_elem.get_text()

            # 尋找書名號內的內容
            matches = re.findall(r'《([^》]+)》', text)
            for match in matches:
                if self.contains_chinese(match):
                    candidates[match] = candidates.get(match, 0) + 3  # 書名號內容加分

            # 尋找包含中文的片段
            chinese_parts = re.findall(r'[\u4e00-\u9fff]+', text)
            for part in chinese_parts:
                if 4 <= len(part) <= 15:  # 長度適中
                    candidates[part] = candidates.get(part, 0) + 1

        if not candidates:
            return None

        # 選擇得分最高的候選
        best_candidate = max(candidates.items(), key=lambda x: x[1])
        return best_candidate[0]

    def translate_name(self, game_name: str, platform: str) -> str:
        """翻譯遊戲名稱（先查字典，再搜尋）"""
        # 如果已是中文，直接返回
        if self.contains_chinese(game_name):
            return game_name

        # 清理名稱
        clean_name = self.clean_game_name(game_name)

        # 查找翻譯
        translation = self.lookup_translation(
            clean_name, platform, is_description=False)
        if translation:
            print(f"✓ 從字典找到翻譯: {clean_name} → {translation}")
            return translation

        # Google 搜尋
        platform_name = PLATFORM_NAMES.get(platform, platform)
        query = f"{clean_name} {platform_name} 遊戲 中文"
        print(f"搜尋: {query}")

        html = self.search_google(query)
        chinese_name = self.extract_chinese_name(html, clean_name)

        if chinese_name:
            print(f"✓ 找到翻譯: {clean_name} → {chinese_name}")
            # 加入本地快取
            self.local_cache["names"][clean_name] = chinese_name
            self.save_local_cache()
            return chinese_name
        else:
            print(f"✗ 找不到翻譯，保持原名: {clean_name}")
            return clean_name

        # 延遲避免被封鎖
        time.sleep(self.search_delay)

    def translate_description(self, description: str, platform: str) -> str:
        """翻譯遊戲描述（先查字典，再用 API）"""
        if not description or self.contains_chinese(description):
            return description

        # 查找快取
        translation = self.lookup_translation(
            description, platform, is_description=True)
        if translation:
            return translation

        # TODO: 整合翻譯 API (googletrans, Google Cloud, etc.)
        # 目前先返回原文
        print(f"描述翻譯功能待實作: {description[:50]}...")
        return description

    def format_game_name(self, english_name: str, chinese_name: str) -> str:
        """根據顯示模式格式化遊戲名稱"""
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

    def update_gamelist(self, gamelist_path: str, platform: str, dry_run: bool = False):
        """更新單一 gamelist.xml"""
        print(f"\n處理平台: {platform.upper()}")
        print(f"檔案: {gamelist_path}")

        # 解析 XML
        tree = ET.parse(gamelist_path)
        root = tree.getroot()

        games = root.findall('game')
        total = len(games)
        updated = 0

        print(f"共有 {total} 個遊戲\n")

        for idx, game in enumerate(games, 1):
            name_elem = game.find('name')
            desc_elem = game.find('desc')

            if name_elem is not None and name_elem.text:
                original_name = name_elem.text
                clean_name = self.clean_game_name(original_name)

                # 翻譯名稱
                chinese_name = self.translate_name(clean_name, platform)
                formatted_name = self.format_game_name(
                    clean_name, chinese_name)

                if not dry_run:
                    name_elem.text = formatted_name

                print(f"[{idx}/{total}] {original_name} → {formatted_name}")
                updated += 1

                # 翻譯描述
                if self.translate_desc and desc_elem is not None and desc_elem.text:
                    original_desc = desc_elem.text
                    translated_desc = self.translate_description(
                        original_desc, platform)

                    if not dry_run and translated_desc != original_desc:
                        desc_elem.text = translated_desc

                    if translated_desc != original_desc:
                        print(
                            f"    描述: {original_desc[:50]}... → {translated_desc[:50]}...")

        # 儲存檔案
        if not dry_run:
            # 備份原始檔案
            backup_path = gamelist_path + ".backup"
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy2(gamelist_path, backup_path)
                print(f"\n✓ 已備份原始檔案: {backup_path}")

            # 寫入新檔案
            tree.write(gamelist_path, encoding='utf-8', xml_declaration=True)
            print(f"✓ 已更新 {updated}/{total} 個遊戲")
        else:
            print(f"\n[預覽模式] 將更新 {updated}/{total} 個遊戲")

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
    parser.add_argument('--dry-run', action='store_true', help='預覽模式（不實際修改檔案）')
    parser.add_argument('--translations-dir',
                        default='translations', help='語系包目錄')

    args = parser.parse_args()

    # 建立翻譯器
    translator = GamelistTranslator(
        translations_dir=args.translations_dir,
        display_mode=args.mode,
        max_name_length=args.max_length,
        translate_desc=not args.no_desc
    )

    # 執行批次更新
    translator.batch_update(args.roms_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
