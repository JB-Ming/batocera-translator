"""
列出可用的 Gemini 模型
"""
import google.generativeai as genai

# 設定 API Key
genai.configure(api_key="AIzaSyACoHJ8APFTe8bN2auolexAp8AMyAneEes")

print("=" * 60)
print("可用的 Gemini 模型列表")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n模型: {model.name}")
        print(f"  顯示名稱: {model.display_name}")
        print(f"  描述: {model.description}")
        print(f"  支援方法: {model.supported_generation_methods}")

print("\n" + "=" * 60)
