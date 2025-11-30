#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多 API 翻譯管理器
支援多種翻譯 API 並實作降級機制

遊戲名稱翻譯策略：
1. Gemini API (AI 推斷台灣慣用譯名)
2. 保持原名 (避免亂翻)

遊戲描述翻譯策略：
1. DeepL API (品質最好)
2. MyMemory API (免費，無需 Key)
3. googletrans (最後手段)
"""

import os
import time
from typing import Optional
import requests


class TranslationAPIManager:
    """多 API 翻譯管理器，實作降級機制"""

    def __init__(self,
                 groq_api_key: Optional[str] = None,
                 gemini_api_key: Optional[str] = None,
                 deepl_api_key: Optional[str] = None,
                 enable_groq: bool = True,
                 enable_gemini: bool = True,
                 enable_deepl: bool = True,
                 enable_mymemory: bool = True,
                 enable_googletrans: bool = True):
        """
        初始化翻譯 API 管理器

        Args:
            groq_api_key: Groq API Key
            gemini_api_key: Google Gemini API Key
            deepl_api_key: DeepL API Key
            enable_groq: 是否啟用 Groq
            enable_gemini: 是否啟用 Gemini
            enable_deepl: 是否啟用 DeepL
            enable_mymemory: 是否啟用 MyMemory
            enable_googletrans: 是否啟用 googletrans
        """
        self.groq_api_key = groq_api_key
        self.gemini_api_key = gemini_api_key
        self.deepl_api_key = deepl_api_key

        self.enable_groq = enable_groq
        self.enable_gemini = enable_gemini
        self.enable_deepl = enable_deepl
        self.enable_mymemory = enable_mymemory
        self.enable_googletrans = enable_googletrans

        # 統計資訊
        self.stats = {
            'groq': {'success': 0, 'fail': 0},
            'gemini': {'success': 0, 'fail': 0},
            'deepl': {'success': 0, 'fail': 0},
            'mymemory': {'success': 0, 'fail': 0},
            'googletrans': {'success': 0, 'fail': 0}
        }

    def translate_game_name(self, game_name: str, platform: str) -> Optional[str]:
        """
        翻譯遊戲名稱（台灣慣用譯名）

        策略：Groq API (速度最快) → Gemini API (備援) → 返回 None (保持原名)

        Args:
            game_name: 遊戲英文名稱
            platform: 遊戲平台 (例如: FC紅白機)

        Returns:
            台灣慣用譯名，如果失敗返回 None
        """
        # 1. 嘗試 Groq API (速度最快，優先使用)
        if self.enable_groq and self.groq_api_key:
            result = self._translate_with_groq(game_name, platform)
            if result:
                self.stats['groq']['success'] += 1
                return result
            else:
                self.stats['groq']['fail'] += 1

        # 2. 嘗試 Gemini API (備援)
        if self.enable_gemini and self.gemini_api_key:
            result = self._translate_with_gemini(game_name, platform)
            if result:
                self.stats['gemini']['success'] += 1
                return result
            else:
                self.stats['gemini']['fail'] += 1

        # 3. 失敗或未啟用，返回 None（由 translator.py 決定保持原名）
        return None

    def translate_description(self, description: str) -> Optional[str]:
        """
        翻譯遊戲描述

        策略：DeepL → MyMemory → googletrans

        Args:
            description: 英文描述

        Returns:
            繁體中文翻譯，如果全部失敗返回 None
        """
        if not description or len(description.strip()) == 0:
            return None

        # 1. 嘗試 DeepL API
        if self.enable_deepl and self.deepl_api_key:
            result = self._translate_with_deepl(description)
            if result:
                self.stats['deepl']['success'] += 1
                return result
            else:
                self.stats['deepl']['fail'] += 1

        # 2. 嘗試 MyMemory API
        if self.enable_mymemory:
            result = self._translate_with_mymemory(description)
            if result:
                self.stats['mymemory']['success'] += 1
                return result
            else:
                self.stats['mymemory']['fail'] += 1

        # 3. 嘗試 googletrans
        if self.enable_googletrans:
            result = self._translate_with_googletrans(description)
            if result:
                self.stats['googletrans']['success'] += 1
                return result
            else:
                self.stats['googletrans']['fail'] += 1

        # 全部失敗
        return None

    def _translate_with_groq(self, game_name: str, platform: str) -> Optional[str]:
        """
        使用 Groq API (Llama 3.1) 推斷台灣慣用遊戲譯名

        Args:
            game_name: 遊戲英文名稱
            platform: 遊戲平台

        Returns:
            台灣慣用譯名或 None
        """
        try:
            from groq import Groq

            # 初始化 Groq 客戶端
            client = Groq(api_key=self.groq_api_key)

            # 專業提示詞（與 Gemini 相同）
            prompt = f"""你是遊戲本地化專家。請提供這款遊戲在台灣的正式譯名或慣用名稱。

遊戲：{game_name}
平台：{platform}

要求：
- 只回答遊戲名稱，不要解釋或加其他內容
- 使用台灣慣用譯名（例如「瑪利歐」而非「馬里奧」）
- 如果是知名遊戲，使用官方中文名稱
- 如果沒有官方譯名，提供台灣玩家常用的稱呼
- 如果完全不確定，回答「未知」

範例：
- Super Mario Bros → 超級瑪利歐兄弟
- The Legend of Zelda → 薩爾達傳說
- Contra → 魂斗羅
- Street Fighter II → 快打旋風II"""

            # 使用 Llama 3.3 70B 模型（最新版本，速度快、品質好）
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",  # Groq 最新推薦模型
                temperature=0.3,  # 降低隨機性，提高一致性
                max_tokens=100,  # 遊戲名稱不需要太長
            )

            # 提取回應文字
            if chat_completion and chat_completion.choices:
                result = chat_completion.choices[0].message.content.strip()

                # 過濾無效回應
                if result and result != "未知" and len(result) > 0:
                    # 移除可能的引號或多餘標點
                    result = result.strip('"\'\'。！？')
                    print(f"  [Groq] {game_name} → {result}")
                    return result

            return None

        except Exception as e:
            print(f"  [Groq 錯誤] {e}")
            return None

    def _translate_with_gemini(self, game_name: str, platform: str) -> Optional[str]:
        """
        使用 Google Gemini API 推斷台灣慣用遊戲譯名

        Args:
            game_name: 遊戲英文名稱
            platform: 遊戲平台

        Returns:
            台灣慣用譯名或 None
        """
        try:
            import google.generativeai as genai

            # 設定 API Key
            genai.configure(api_key=self.gemini_api_key)

            # 使用 Gemini 2.5 Flash (速度快、免費額度高)
            model = genai.GenerativeModel('gemini-2.5-flash')

            # 專業提示詞
            prompt = f"""你是遊戲本地化專家。請提供這款遊戲在台灣的正式譯名或慣用名稱。

遊戲：{game_name}
平台：{platform}

要求：
- 只回答遊戲名稱，不要解釋或加其他內容
- 使用台灣慣用譯名（例如「瑪利歐」而非「馬里奧」）
- 如果是知名遊戲，使用官方中文名稱
- 如果沒有官方譯名，提供台灣玩家常用的稱呼
- 如果完全不確定，回答「未知」

範例：
- Super Mario Bros → 超級瑪利歐兄弟
- The Legend of Zelda → 薩爾達傳說
- Contra → 魂斗羅
- Street Fighter II → 快打旋風II"""

            response = model.generate_content(prompt)

            # 提取回應文字
            if response and response.text:
                result = response.text.strip()

                # 過濾無效回應
                if result and result != "未知" and len(result) > 0:
                    # 移除可能的引號或多餘標點
                    result = result.strip('"\'。！？')
                    print(f"  [Gemini] {game_name} → {result}")
                    return result

            return None

        except Exception as e:
            print(f"  [Gemini 錯誤] {e}")
            return None

    def _translate_with_deepl(self, text: str) -> Optional[str]:
        """
        使用 DeepL API 翻譯

        Args:
            text: 要翻譯的文字

        Returns:
            繁體中文翻譯或 None
        """
        try:
            # 限制長度避免超額
            if len(text) > 500:
                text = text[:500] + "..."

            url = "https://api-free.deepl.com/v2/translate"

            params = {
                'auth_key': self.deepl_api_key,
                'text': text,
                'source_lang': 'EN',
                'target_lang': 'ZH'  # 中文（繁體或簡體由 DeepL 自動判斷）
            }

            response = requests.post(url, data=params, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if 'translations' in result and len(result['translations']) > 0:
                    translated = result['translations'][0]['text']
                    print(f"  [DeepL] 翻譯成功")
                    return translated
            elif response.status_code == 456:
                print(f"  [DeepL] 額度用完")
            else:
                print(f"  [DeepL] 錯誤 {response.status_code}")

            return None

        except Exception as e:
            print(f"  [DeepL 錯誤] {e}")
            return None

    def _translate_with_mymemory(self, text: str) -> Optional[str]:
        """
        使用 MyMemory API 翻譯（免費，無需 Key）

        Args:
            text: 要翻譯的文字

        Returns:
            繁體中文翻譯或 None
        """
        try:
            # 限制長度
            if len(text) > 500:
                text = text[:500] + "..."

            url = "https://api.mymemory.translated.net/get"

            params = {
                'q': text,
                'langpair': 'en|zh-TW'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                result = response.json()

                if 'responseData' in result and 'translatedText' in result['responseData']:
                    translated = result['responseData']['translatedText']

                    # 檢查是否是有效翻譯（MyMemory 有時會返回原文）
                    if translated and translated != text:
                        print(f"  [MyMemory] 翻譯成功")
                        return translated

            return None

        except Exception as e:
            print(f"  [MyMemory 錯誤] {e}")
            return None

    def _translate_with_googletrans(self, text: str) -> Optional[str]:
        """
        使用 googletrans 翻譯（最後手段）

        Args:
            text: 要翻譯的文字

        Returns:
            繁體中文翻譯或 None
        """
        try:
            from googletrans import Translator

            translator = Translator()

            # 限制長度
            if len(text) > 500:
                text = text[:500] + "..."

            result = translator.translate(text, src='en', dest='zh-tw')

            if result and result.text:
                print(f"  [googletrans] 翻譯成功")
                return result.text

            return None

        except Exception as e:
            print(f"  [googletrans 錯誤] {e}")
            return None

    def get_stats(self) -> dict:
        """取得使用統計"""
        return self.stats

    def print_stats(self):
        """顯示使用統計"""
        print("\n" + "=" * 60)
        print("翻譯 API 使用統計")
        print("=" * 60)

        for api, stat in self.stats.items():
            total = stat['success'] + stat['fail']
            if total > 0:
                success_rate = (stat['success'] / total) * 100
                print(
                    f"{api:15} 成功: {stat['success']:4} | 失敗: {stat['fail']:4} | 成功率: {success_rate:.1f}%")

        print("=" * 60)
