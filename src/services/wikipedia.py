# 維基百科 API 服務
"""
封裝維基百科 API，用於搜尋遊戲名稱的正式譯名。
"""
import re
import time
import requests
from typing import Optional, Dict, Any
from urllib.parse import quote


class WikipediaService:
    """
    維基百科 API 服務

    功能：
    - 搜尋遊戲名稱的維基百科頁面
    - 取得頁面標題（通常是正式譯名）
    - 取得頁面摘要（遊戲描述）
    """

    # 語系對應的維基百科網域
    WIKI_DOMAINS = {
        'zh-TW': 'zh.wikipedia.org',
        'zh-CN': 'zh.wikipedia.org',
        'ja': 'ja.wikipedia.org',
        'ko': 'ko.wikipedia.org',
        'en': 'en.wikipedia.org',
    }

    # 語系對應的維基百科變體
    WIKI_VARIANTS = {
        'zh-TW': 'zh-tw',
        'zh-CN': 'zh-cn',
    }

    def __init__(self, request_delay: float = 1.0):
        """
        初始化維基百科服務

        Args:
            request_delay: 請求間隔時間（秒），避免被封鎖
        """
        self.request_delay = request_delay
        self._last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BatoceraTranslator/1.0 (https://github.com/example/batocera-translator)'
        })
        # 優化連接池
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # 添加記憶體快取 (query + language -> result)
        self._search_cache = {}
        self._desc_cache = {}

    def clear_cache(self, query: Optional[str] = None) -> None:
        """
        清除快取

        Args:
            query: 如果指定，只清除特定查詢的快取；否則清除所有快取
        """
        if query is None:
            # 清除所有快取
            self._search_cache.clear()
            self._desc_cache.clear()
        else:
            # 清除特定查詢的快取（所有語系）
            keys_to_remove = [
                k for k in self._search_cache.keys() if k.startswith(f"{query}|")]
            for key in keys_to_remove:
                del self._search_cache[key]

            keys_to_remove = [
                k for k in self._desc_cache.keys() if k.startswith(f"{query}|")]
            for key in keys_to_remove:
                del self._desc_cache[key]

    def _rate_limit(self) -> None:
        """速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()

    def _get_api_url(self, language: str) -> str:
        """取得 API URL"""
        domain = self.WIKI_DOMAINS.get(language, 'en.wikipedia.org')
        return f"https://{domain}/w/api.php"

    def search(self, query: str, language: str = 'zh-TW') -> Optional[str]:
        """
        搜尋遊戲名稱的維基百科譯名

        Args:
            query: 搜尋關鍵字（通常是英文遊戲名稱）
            language: 目標語系

        Returns:
            找到的譯名，找不到返回 None
        """
        # 檢查快取
        cache_key = f"{query}|{language}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        self._rate_limit()

        api_url = self._get_api_url(language)

        # 搜尋 API 參數
        # 使用更精確的搜尋詞，優先找遊戲而非電影/書籍
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': f'{query} (video game OR 電子遊戲 OR 遊戲 OR ゲーム)',
            'srlimit': 15,  # 增加搜尋結果數量，提高找到正確結果的機會
        }

        # 加入語系變體
        variant = self.WIKI_VARIANTS.get(language)
        if variant:
            params['variant'] = variant

        try:
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # 取得搜尋結果
            search_results = data.get('query', {}).get('search', [])
            if not search_results:
                return None

            # 嘗試多個搜尋結果，找到第一個有效的
            for result in search_results:
                title = result.get('title', '')

                # 過濾非遊戲結果並驗證翻譯有效性
                if self._is_game_page(title, query) and self._is_valid_translation(title, query, language):
                    # 儲存到快取
                    self._search_cache[cache_key] = title
                    return title

            # 沒找到，也要快取結果避免重複查詢
            self._search_cache[cache_key] = None
            return None

        except requests.RequestException:
            # 錯誤時不快取
            return None

    def get_page_info(self, title: str, language: str = 'zh-TW') -> Optional[Dict[str, str]]:
        """
        取得頁面資訊

        Args:
            title: 頁面標題
            language: 語系

        Returns:
            包含 title 和 extract 的字典
        """
        self._rate_limit()

        api_url = self._get_api_url(language)

        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'exsectionformat': 'plain',
        }

        variant = self.WIKI_VARIANTS.get(language)
        if variant:
            params['variant'] = variant

        try:
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            for page_id, page in pages.items():
                if page_id == '-1':
                    return None
                return {
                    'title': page.get('title', ''),
                    'extract': page.get('extract', '')
                }

            return None

        except requests.RequestException:
            return None

    def get_description(self, query: str, language: str = 'zh-TW') -> Optional[str]:
        """
        取得遊戲描述

        Args:
            query: 搜尋關鍵字
            language: 語系

        Returns:
            遊戲描述文字
        """
        # 檢查快取
        cache_key = f"{query}|{language}"
        if cache_key in self._desc_cache:
            cached = self._desc_cache[cache_key]
            print(f"[維基] 使用快取：{query} -> {'有描述' if cached else '無描述'}")
            return cached

        print(f"[維基] 開始搜尋描述：{query}")
        title = self.search(query, language)
        if not title:
            print(f"[維基] 搜尋失敗，找不到標題：{query}")
            self._desc_cache[cache_key] = None
            return None

        print(f"[維基] 找到標題：{title}")

        page_info = self.get_page_info(title, language)
        if page_info:
            desc = page_info.get('extract', '')

            # 檢查描述內容，確保是遊戲而非電影/書籍
            if desc and not self._is_game_description(desc):
                # 描述看起來像電影/書籍，不是遊戲
                print(f"[維基] 過濾掉非遊戲內容：{title}")
                print(f"  描述開頭：{desc[:100]}...")
                self._desc_cache[cache_key] = None
                return None

            print(f"[維基] 描述驗證通過，長度：{len(desc)}")
            self._desc_cache[cache_key] = desc
            return desc

        print(f"[維基] 取得頁面資訊失敗")
        self._desc_cache[cache_key] = None
        return None

    def _is_game_description(self, desc: str) -> bool:
        """
        檢查描述內容是否為遊戲相關

        Args:
            desc: 描述文字

        Returns:
            True 表示是遊戲描述，False 表示可能是電影/書籍等
        """
        # 如果描述太短，無法判斷
        if len(desc) < 50:
            return True  # 給予通過，因為無法確定

        # 遊戲相關關鍵字（出現這些表示是遊戲）
        game_keywords = [
            '遊戲', '游戏', 'ゲーム', 'game', 'video game',
            '電子遊戲', '电子游戏', 'electronic game',
            '玩家', '玩家', 'player',
            '主機', '主机', '平台', '平台', 'console', 'platform',
            '關卡', '关卡', 'level', 'stage',
            '任天堂', '世嘉', 'SEGA', 'Nintendo', 'Atari', 'Capcom', 'Konami',
            '街機', '街机', 'arcade',
            '卡帶', '卡带', 'cartridge',
            'FC', 'NES', 'SNES', 'MD', 'PS', 'Xbox', 'Game Boy',
        ]

        # 強烈的非遊戲標識（出現即拒絕，不管有無遊戲關鍵字）
        # 這些模式通常出現在描述的最開頭，明確表明媒體類型
        strong_non_game_patterns = [
            r'是\s*\d{4}\s*年.*?電影',  # 「是1982年美國科幻電影」
            r'是\s*\d{4}\s*年.*?电影',
            r'是.*?年.*?上映.*?電影',
            r'是.*?年.*?上映.*?电影',
            r'是一部\s*\d{4}\s*年.*?電影',
            r'是一部\s*\d{4}\s*年.*?电影',
            r'是.*?執導.*?電影',  # 「是由XX執導的電影」
            r'是.*?执导.*?电影',
            r'是.*?導演.*?電影',
            r'是.*?导演.*?电影',
            r'\d{4}\s*film directed by',
            r'is a \d{4}.*?film',
        ]

        # 檢查前 200 個字符（通常媒體類型會在最開頭說明）
        check_text_short = desc[:200]

        # 先檢查強烈標識
        for pattern in strong_non_game_patterns:
            if re.search(pattern, check_text_short, re.IGNORECASE):
                return False  # 明確是電影/劇集，立即拒絕

        # 次要非遊戲關鍵字（需結合遊戲關鍵字判斷）
        weak_non_game_keywords = [
            '導演', '导演', 'director',
            '主演', '演員', '演员', 'starring', 'actor',
            '票房', 'box office',
            '上映', 'release', 'premiere',
            '製片', '制片', 'producer',
            '改編自', '改编自', 'adapted from',
            '科幻片', '動作片', '动作片',
            '奥斯卡', '奧斯卡', 'Oscar', 'Academy Award',
        ]

        # 檢查前 300 個字符
        check_text = desc[:300]

        # 計算遊戲關鍵字出現次數
        game_count = sum(
            1 for keyword in game_keywords if keyword in check_text)

        # 計算次要非遊戲關鍵字出現次數
        non_game_count = sum(
            1 for keyword in weak_non_game_keywords if keyword in check_text)

        # 如果有遊戲關鍵字，認為是遊戲
        if game_count > 0:
            return True

        # 如果有多個非遊戲關鍵字但沒有遊戲關鍵字，拒絕
        if non_game_count >= 2:
            return False

        # 無法判斷，傾向認為不是（避免誤判電影為遊戲）
        return False

    def _is_valid_translation(self, result: str, original: str, language: str) -> bool:
        """
        驗證翻譯結果是否有效

        判斷條件：
        1. 結果不能與原文相同（忽略大小寫）
        2. 若目標語言為中文，結果必須包含中文字符
        3. 版本號必須匹配（如 II、III、2、3 等）

        Args:
            result: 翻譯結果
            original: 原始查詢
            language: 目標語系

        Returns:
            翻譯是否有效
        """
        # 結果與原文相同，無效
        if result.lower().strip() == original.lower().strip():
            return False

        # 檢查是否為中文語系
        if language.startswith('zh'):
            # 必須包含至少一個中文字符（Unicode CJK 基本區）
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in result)
            if not has_chinese:
                return False

        # 版本號匹配檢查
        if not self._check_version_match(original, result):
            return False

        return True

    def _extract_version_numbers(self, text: str) -> list:
        """
        從文字中提取版本號

        支援格式：
        - 羅馬數字：I, II, III, IV, V, VI, VII, VIII, IX, X, XI, XII 等
        - 阿拉伯數字：1, 2, 3, 4 等
        - 中文數字：一, 二, 三, 四 等

        Returns:
            標準化後的版本號列表（全部轉為阿拉伯數字）
        """
        # 羅馬數字對照表
        roman_to_arabic = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
            'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
            'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
            'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20
        }

        # 中文數字對照表
        chinese_to_arabic = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16
        }

        versions = []

        # 提取羅馬數字（支援中文字符旁邊的羅馬數字）
        # 使用負向前後斷言避免匹配英文單詞中的字母
        roman_pattern = r'(?<![A-Za-z])(XVIII|XVII|XIII|XIV|XII|XVI|VIII|VII|III|IV|VI|IX|XV|XI|II|X|V|I)(?![A-Za-z])'
        for match in re.finditer(roman_pattern, text):
            roman = match.group(1)
            if roman in roman_to_arabic:
                versions.append(roman_to_arabic[roman])

        # 提取阿拉伯數字（使用更寬鬆的匹配，支援中文字串中的數字）
        # 匹配獨立的數字，或在中文字符旁邊的數字
        arabic_pattern = r'(?<![a-zA-Z])(\d+)(?![a-zA-Z])'
        for match in re.finditer(arabic_pattern, text):
            versions.append(int(match.group(1)))

        # 提取中文數字
        for cn, num in sorted(chinese_to_arabic.items(), key=lambda x: -len(x[0])):
            if cn in text:
                versions.append(num)

        return versions

    def _check_version_match(self, original: str, result: str) -> bool:
        """
        檢查原始名稱和翻譯結果的版本號是否匹配

        規則：
        - 如果原始名稱沒有版本號，不進行檢查（返回 True）
        - 如果原始名稱有版本號，翻譯結果必須也包含相同的版本號

        Args:
            original: 原始遊戲名稱
            result: 翻譯結果

        Returns:
            版本號是否匹配
        """
        orig_versions = self._extract_version_numbers(original)

        # 原始名稱沒有明確版本號，不需要檢查
        if not orig_versions:
            return True

        result_versions = self._extract_version_numbers(result)

        # 翻譯結果沒有版本號，可能有問題
        if not result_versions:
            # 但如果原始版本號是 1，有些遊戲第一代不會標示版本號
            if orig_versions == [1]:
                return True
            return False

        # 檢查主要版本號是否匹配
        # 取原始名稱的第一個版本號（通常是主要版本）
        main_orig_version = orig_versions[0]

        # 檢查翻譯結果是否包含相同的版本號
        if main_orig_version in result_versions:
            return True

        # 特殊處理：合集遊戲（如 "I & II"、"1.2" 等）
        if len(orig_versions) > 1:
            # 如果是合集，檢查結果是否包含任一版本號
            for v in orig_versions:
                if v in result_versions:
                    return True

        return False

    def _is_game_page(self, title: str, query: str) -> bool:
        """
        判斷是否為遊戲頁面

        簡單的判斷邏輯，避免選到同名的電影、書籍等
        注意：只過濾「括號標註」的非遊戲分類，不過濾標題本身包含這些詞
        這樣可以保留「電影大亨」、「Movie Tycoon」等遊戲名稱
        """
        # 排除明顯非遊戲的頁面
        exclude_patterns = [
            r'\(電影\)',      # 括號標註：(電影)、(2020年電影) 等
            r'\(电影\)',
            r'\(.*電影\)',    # 如 (1982年電影)
            r'\(.*电影\)',
            r'\(film\)',
            r'\(movie\)',
            r'\(.*film\)',    # 如 (1982 film)
            r'\(.*movie\)',
            r'\(電視\)',      # 括號標註：(電視劇) 等
            r'\(电视\)',
            r'\(TV\)',
            r'\(動畫\)',      # 括號標註
            r'\(动画\)',
            r'\(anime\)',
            r'\(漫畫\)',      # 括號標註
            r'\(漫画\)',
            r'\(manga\)',
            r'\(小說\)',      # 括號標註
            r'\(小说\)',
            r'\(novel\)',
            r'\(書籍\)',      # 括號標註
            r'\(书籍\)',
            r'\(book\)',
            r'\(專輯\)',      # 括號標註
            r'\(专辑\)',
            r'\(album\)',
            r'原聲帶',         # 遊戲原聲帶（不是遊戲本身）
            r'原声带',
            r'配樂',
            r'配乐',
            r'soundtrack',
            r'歌曲',
            r'列表',           # 排除列表頁面
            r'游戏列表',       # 排除遊戲列表頁面
            r'遊戲列表',       # 繁體
            r'List of',        # 英文列表
            r'索引',
            r'年表',
            r'人物',
            r'角色',
            r'配音',
            r'Category',
            r'Template',
            r'\d{4}年',        # 年份頁面 (如 "1989年电子游戏界")
            r'有生之年',       # 書籍/排行榜頁面
            r'1001款',
            r'游戏界',
            r'遊戲界',
            r'遊戲類型',
            r'游戏类型',
            r'砍殺遊戲',       # 遊戲類型頁面
            r'砍杀游戏',
            r'格鬥遊戲',
            r'格斗游戏',
            r'動作遊戲',
            r'动作游戏',
            r'射擊遊戲',
            r'射击游戏',
            r'角色扮演遊戲',
            r'角色扮演游戏',
            r'系列$',          # 排除「XXX系列」頁面（如「勇者鬥惡龍系列」）
            r'遊戲系列',       # 繁體
            r'游戏系列',       # 簡體
            r'Series$',        # 英文系列頁面
            r'series$',
        ]

        # 排除遊戲平台/訂閱服務頁面 - 這些頁面會提到很多遊戲但不是具體遊戲
        platform_patterns = [
            r'Nintendo Switch Online',
            r'任天堂Switch Online',
            r'Xbox Game Pass',
            r'PlayStation Now',
            r'PlayStation Plus',
            r'Virtual Console',
            r'虛擬主機',
            r'虚拟主机',
            r'Sega Genesis Mini',
            r'迷你',
            r'Mini',
            r'Collection',       # 遊戲合集頁面
            r'合集',
            r'合輯',
            r'Anthology',
            r'Compilation',
            r'經典回顧',
            r'经典回顾',
        ]

        for pattern in exclude_patterns + platform_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return False

        # 檢查標題是否與查詢有足夠的關聯性
        # 如果標題主要是中文，則不強制要求英文詞彙匹配
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in title)

        if has_chinese:
            # 常見英文遊戲詞彙的中文意譯對照表
            # 用於判斷中文標題是否與英文查詢有語義關聯
            translation_hints = {
                'golden': ['金', '黃金'],
                'axe': ['斧', '戰斧'],
                'sonic': ['索尼克', '音速'],
                'hedgehog': ['刺蝟', '刺猬'],
                'mario': ['瑪利歐', '馬里奧', '瑪莉歐'],
                'super': ['超級'],
                'street': ['街', '街頭'],
                'fighter': ['鬥士', '格鬥', '戰士', '快打'],
                'knight': ['騎士', '武士'],
                'dragon': ['龍', '飛龍'],
                'sword': ['劍', '刀劍'],
                'warrior': ['戰士', '勇士'],
                'king': ['王', '國王'],
                'legend': ['傳說', '傳奇'],
                'world': ['世界'],
                'adventure': ['冒險', '大冒險'],
                'battle': ['戰鬥', '對戰'],
                'force': ['力量', '戰隊', '部隊'],
                'shadow': ['影', '暗影', '闇'],
                'fire': ['火', '烈火', '炎'],
                'ice': ['冰'],
                'thunder': ['雷', '雷電'],
                'light': ['光'],
                'dark': ['暗', '黑暗', '闇'],
                'castle': ['城', '城堡'],
                'quest': ['任務', '探索', '傳說'],
                'vector': ['向量', '維克特'],
                'mega': ['百萬', '洛克人'],
                'master': ['大師', '主人'],
                'star': ['星', '明星', '星際'],
                'space': ['太空', '宇宙'],
                'heart': ['心', '之心'],
                'soul': ['魂', '靈魂'],
                'racing': ['賽車', '競速'],
                'run': ['跑', '逃跑'],
                'shooter': ['射擊'],
                'contra': ['魂斗羅', '魂鬥羅'],
                'metal': ['金屬', '鋼鐵'],
                'gear': ['齒輪', '裝備'],
                'mortal': ['真人', '致命'],
                'kombat': ['快打', '格鬥'],
                'tekken': ['鐵拳'],
                'final': ['終極', '最終'],
                'fantasy': ['幻想'],
                'resident': ['惡靈', '生化'],
                'evil': ['惡', '邪惡'],
                'silent': ['沉默', '寂靜'],
                'hill': ['之丘', '山丘'],
                'tomb': ['古墓'],
                'raider': ['奇兵', '掠奪者'],
                'doom': ['毀滅'],
                'wolf': ['狼'],
                'stein': ['斯坦'],
            }

            query_lower = query.lower()
            query_words = query_lower.split()
            title_lower = title.lower()

            # 檢查是否有語義關聯
            has_semantic_match = False
            for word in query_words:
                # 檢查英文詞是否直接在標題中
                if word in title_lower:
                    has_semantic_match = True
                    break
                # 檢查對應的中文意譯是否在標題中
                if word in translation_hints:
                    for zh in translation_hints[word]:
                        if zh in title:
                            has_semantic_match = True
                            break
                if has_semantic_match:
                    break

            # 如果沒有任何語義關聯，返回 False
            if not has_semantic_match:
                return False

            return True

        # 純英文標題：要求較嚴格的詞彙匹配
        clean_query = re.sub(r'\s*\([^)]*\)\s*', ' ', query)  # 移除括號內容
        clean_query = re.sub(r'\s*\[[^\]]*\]\s*', ' ', clean_query)  # 移除方括號內容
        clean_query = re.sub(
            # 移除羅馬數字/阿拉伯數字版本
            r'\s+(I{1,3}|IV|V|VI{0,3}|[2-9]|10)\s*$', '', clean_query)

        query_words = [w for w in clean_query.lower().split() if len(w) > 2]
        title_lower = title.lower()

        # 計算匹配的核心詞彙數量
        matched_words = 0
        for word in query_words:
            if word in title_lower:
                matched_words += 1

        # 至少有一個核心詞彙匹配
        if len(query_words) > 0 and matched_words == 0:
            # 沒有任何詞彙匹配，檢查字符相似度
            query_set = set(clean_query.lower().replace(' ', ''))
            title_set = set(title_lower.replace(' ', ''))
            common = len(query_set & title_set)
            similarity = common / max(len(query_set), 1)

            if similarity < 0.4:  # 字符相似度太低
                return False

        return True
