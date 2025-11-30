"""補翻語系包中未翻譯的遊戲（使用 Google Translate）"""
import json
from pathlib import Path
from deep_translator import GoogleTranslator
import time
import re

def is_translated(original, translated):
    """判斷是否已翻譯"""
    if original == translated:
        return False
    # 如果翻譯結果只是加了括號或符號，也算未翻譯
    if translated.replace('(', '').replace(')', '').strip() == original.replace('(', '').replace(')', '').strip():
        return False
    return True

def clean_game_name(name):
    """清理遊戲名稱，移除版本資訊等"""
    # 移除括號內容（通常是版本、廠商等資訊）
    cleaned = re.sub(r'\([^)]*\)', '', name)
    # 移除方括號內容
    cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)
    # 移除多餘空白
    cleaned = ' '.join(cleaned.split())
    return cleaned.strip()

def translate_with_google(text, max_retries=3):
    """使用 Google Translate 翻譯"""
    for attempt in range(max_retries):
        try:
            # 只翻譯遊戲名稱主體部分
            cleaned_name = clean_game_name(text)
            if not cleaned_name:
                return text
            
            result = GoogleTranslator(source='en', target='zh-TW').translate(cleaned_name)
            if result:
                return result
            return text
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                print(f"    ⚠️ Google 翻譯失敗: {text[:50]}... ({e})")
                return text
    return text

def fix_untranslated_games():
    """補翻所有未翻譯的遊戲"""
    translations_dir = Path("translations")
    
    if not translations_dir.exists():
        print("❌ translations 資料夾不存在")
        return
    
    total_translated = 0
    total_files = 0
    
    # 處理所有 translations_*.json 檔案
    for json_file in sorted(translations_dir.glob("translations_*.json")):
        platform = json_file.stem.replace("translations_", "")
        
        try:
            # 讀取 JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # 找出未翻譯的遊戲
            untranslated = {k: v for k, v in translations.items() 
                          if not is_translated(k, v)}
            
            if not untranslated:
                continue
            
            print(f"\n處理 {platform} ({len(untranslated)} 個未翻譯)")
            
            # 批次翻譯
            translated_count = 0
            for idx, (original, _) in enumerate(untranslated.items(), 1):
                try:
                    translated = translate_with_google(original)
                    if translated and translated != original:
                        translations[original] = translated
                        translated_count += 1
                        
                        if idx % 10 == 0:
                            print(f"  進度: {idx}/{len(untranslated)}")
                    
                    # 避免請求過快
                    if idx % 50 == 0:
                        time.sleep(2)
                    else:
                        time.sleep(0.1)
                        
                except Exception as e:
                    print(f"  ✗ 翻譯失敗: {original[:50]}... ({e})")
                    continue
            
            # 寫回檔案
            if translated_count > 0:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(translations, f, ensure_ascii=False, indent=2)
                
                total_translated += translated_count
                total_files += 1
                print(f"  ✓ {platform}: 翻譯了 {translated_count} 個遊戲")
            
        except Exception as e:
            print(f"  ✗ {platform}: 錯誤 - {e}")
    
    print("\n" + "=" * 60)
    print(f"補翻完成！")
    print(f"處理檔案數: {total_files}")
    print(f"翻譯遊戲數: {total_translated}")
    print("=" * 60)

if __name__ == "__main__":
    fix_untranslated_games()
