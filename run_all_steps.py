"""
Batocera Gamelist 翻譯工具 - 完整流程執行腳本
整合三個階段的完整自動化流程
"""
import sys
import subprocess


def run_stage(stage_num, script_name, description):
    """執行單一階段"""
    print("\n" + "=" * 70)
    print(f"執行階段 {stage_num}: {description}")
    print("=" * 70)

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✓ 階段 {stage_num} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 階段 {stage_num} 失敗: {e}")
        return False


def main():
    print("=" * 70)
    print("Batocera Gamelist 翻譯工具")
    print("三階段完整流程")
    print("=" * 70)
    print("\n流程說明:")
    print("  階段 1: 從遠端目錄提取 gamelist.xml，生成待翻譯語系包")
    print("  階段 2: 翻譯語系包（使用模擬翻譯或真實 API）")
    print("  階段 3: 套用翻譯並寫回遠端目錄")
    print("\n注意:")
    print("  - roms_remote/ 模擬遠端 WSL 路徑（實際使用時改為 \\\\wsl$\\...）")
    print("  - 階段 2 目前使用模擬翻譯，請替換成真實的翻譯 API")
    print("  - 所有原始檔案會自動備份到 backups/ 目錄")

    input("\n按 Enter 開始執行...")

    # 執行三個階段
    stages = [
        (1, "step1_extract.py", "提取待翻譯內容"),
        (2, "step2_translate.py", "翻譯語系包"),
        (3, "step3_apply.py", "應用翻譯並寫回")
    ]

    for stage_num, script, desc in stages:
        success = run_stage(stage_num, script, desc)
        if not success:
            print(f"\n流程在階段 {stage_num} 中斷")
            return 1

    print("\n" + "=" * 70)
    print("✓ 所有階段完成！")
    print("=" * 70)
    print("\n處理結果:")
    print("  - 待翻譯語系包: translations/to_translate_*.json")
    print("  - 翻譯語系包: translations/translations_*.json")
    print("  - 原始備份: backups/")
    print("  - 已更新檔案: roms_remote/")
    print("\n下一步:")
    print("  1. 檢查 roms_remote/ 中的 gamelist.xml 確認翻譯結果")
    print("  2. 將階段 2 的模擬翻譯替換成真實的翻譯 API")
    print("  3. 在實際環境中，將 roms_remote 路徑改為 WSL 路徑")
    print("     例如: \\\\wsl.localhost\\Ubuntu\\userdata\\roms")

    return 0


if __name__ == "__main__":
    sys.exit(main())
