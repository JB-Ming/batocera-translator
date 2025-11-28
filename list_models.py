"""列出可用的 Gemini 模型"""
import google.generativeai as genai

API_KEY = "AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes"
genai.configure(api_key=API_KEY)

print("可用的 Gemini 模型：\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  顯示名稱: {model.display_name}")
        print(f"  支援方法: {model.supported_generation_methods}")
        print()
