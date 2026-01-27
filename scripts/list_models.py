#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""列出可用的 Gemini 模型"""
from src.utils.settings import SettingsManager
import google.generativeai as genai
import warnings
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

warnings.filterwarnings('ignore')


settings = SettingsManager().load()
api_key = settings.get_gemini_api_key()

genai.configure(api_key=api_key)

print("可用的 Gemini 模型：")
print("=" * 60)
for m in genai.list_models():
    methods = m.supported_generation_methods
    if 'generateContent' in methods:
        print(f"  {m.name}")
