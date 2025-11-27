#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動偵測並掛載 Batocera 外接硬碟

功能：
- 自動偵測 Batocera 磁碟（不管在哪個磁碟機代號）
- 在 Windows 上使用 WSL2 掛載 ext4 分區
- 提供跨電腦的相容性
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import platform


class BatoceraDetector:
    """Batocera 磁碟偵測器"""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.batocera_boot_drive = None
        self.batocera_data_drive = None
        self.wsl_mount_point = None

    def detect_batocera_disk(self):
        """偵測 Batocera 磁碟"""
        print("🔍 正在偵測 Batocera 磁碟...")

        if not self.is_windows:
            print("❌ 此工具目前僅支援 Windows 系統")
            return False

        # 方法 1: 尋找標記為 "BATOCERA" 的磁碟區
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-Volume | Where-Object { $_.FileSystemLabel -eq 'BATOCERA' } | Select-Object -ExpandProperty DriveLetter"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.stdout.strip():
                self.batocera_boot_drive = result.stdout.strip() + ":"
                print(f"✓ 找到 BATOCERA 系統分區: {self.batocera_boot_drive}")
                return True

        except Exception as e:
            print(f"⚠ 搜尋失敗: {e}")

        # 方法 2: 掃描所有磁碟機，尋找 batocera-boot.conf
        print("🔍 掃描所有磁碟機...")
        for drive_letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{drive_letter}:"
            boot_conf = Path(drive) / "batocera-boot.conf"

            if boot_conf.exists():
                self.batocera_boot_drive = drive
                print(f"✓ 找到 Batocera 系統分區: {drive}")
                return True

        print("❌ 未找到 Batocera 磁碟")
        return False

    def get_physical_disk_number(self):
        """取得 Batocera 磁碟的實體磁碟編號"""
        if not self.batocera_boot_drive:
            return None

        try:
            # 取得磁碟區對應的實體磁碟編號
            cmd = f"""
            $partition = Get-Partition -DriveLetter {self.batocera_boot_drive[0]}
            $partition.DiskNumber
            """

            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                check=False
            )

            if result.stdout.strip().isdigit():
                disk_number = int(result.stdout.strip())
                print(f"✓ 實體磁碟編號: {disk_number}")
                return disk_number

        except Exception as e:
            print(f"⚠ 無法取得磁碟編號: {e}")

        return None

    def find_ext4_partition(self, disk_number):
        """尋找 ext4 分區（userdata）"""
        try:
            cmd = f"""
            Get-Partition -DiskNumber {disk_number} | 
            Where-Object {{ $_.Type -eq 'Unknown' -or $_.Type -eq 'Basic' }} | 
            Select-Object PartitionNumber, Size | 
            ConvertTo-Json
            """

            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                check=False
            )

            if result.stdout.strip():
                partitions = json.loads(result.stdout)

                # 如果只有一個結果，轉換為列表
                if isinstance(partitions, dict):
                    partitions = [partitions]

                # 尋找最大的分區（通常是 userdata）
                if partitions:
                    # 過濾掉小於 1GB 的分區
                    large_partitions = [
                        p for p in partitions if p['Size'] > 1_000_000_000]

                    if large_partitions:
                        largest = max(large_partitions,
                                      key=lambda x: x['Size'])
                        partition_number = largest['PartitionNumber']
                        size_gb = largest['Size'] / 1_073_741_824

                        print(
                            f"✓ 找到 userdata 分區: 分區 {partition_number} ({size_gb:.1f} GB)")
                        return partition_number

        except Exception as e:
            print(f"⚠ 搜尋 ext4 分區失敗: {e}")

        return None

    def check_wsl_available(self):
        """檢查 WSL2 是否可用"""
        try:
            result = subprocess.run(
                ["wsl", "--status"],
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',
                errors='ignore'
            )

            if result.returncode == 0 and result.stdout and ("版本: 2" in result.stdout or "version: 2" in result.stdout.lower()):
                print("✓ WSL2 可用")
                return True
            else:
                print("❌ WSL2 未安裝或未啟用")
                print("\n請執行以下指令安裝 WSL2:")
                print("  wsl --install")
                return False

        except FileNotFoundError:
            print("❌ WSL 未安裝")
            print("\n請執行以下指令安裝 WSL2:")
            print("  wsl --install")
            return False

    def mount_ext4_partition(self, disk_number, partition_number):
        """使用 WSL2 掛載 ext4 分區"""
        print(f"\n📂 正在掛載分區 {partition_number}...")

        try:
            # 先卸載（如果已掛載）
            subprocess.run(
                ["wsl", "--unmount", f"\\\\.\\PHYSICALDRIVE{disk_number}"],
                capture_output=True,
                check=False
            )

            # 掛載分區
            result = subprocess.run(
                ["wsl", "--mount", f"\\\\.\\PHYSICALDRIVE{disk_number}",
                 "--partition", str(partition_number)],
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',
                errors='ignore'
            )

            if result.returncode == 0:
                # 取得掛載點
                mount_point = f"/mnt/wsl/PHYSICALDRIVE{disk_number}p{partition_number}"
                self.wsl_mount_point = mount_point

                print(f"✓ 已掛載到 WSL: {mount_point}")

                # 驗證掛載
                verify_result = subprocess.run(
                    ["wsl", "ls", mount_point],
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding='utf-8',
                    errors='ignore'
                )

                if verify_result.returncode == 0:
                    print(f"✓ 掛載成功！內容:")
                    for line in verify_result.stdout.strip().split('\n')[:5]:
                        print(f"  - {line}")

                    # 檢查是否有 roms 資料夾
                    roms_check = subprocess.run(
                        ["wsl", "test", "-d", f"{mount_point}/roms"],
                        check=False
                    )

                    if roms_check.returncode == 0:
                        print(f"✓ 找到 roms 資料夾: {mount_point}/roms")
                        return mount_point
                    else:
                        # 嘗試尋找 share/roms
                        share_roms_check = subprocess.run(
                            ["wsl", "test", "-d", f"{mount_point}/share/roms"],
                            check=False
                        )

                        if share_roms_check.returncode == 0:
                            print(f"✓ 找到 roms 資料夾: {mount_point}/share/roms")
                            return f"{mount_point}/share"

                return mount_point
            else:
                print(f"❌ 掛載失敗: {result.stderr}")
                print("\n請以系統管理員權限執行此程式")
                return None

        except Exception as e:
            print(f"❌ 掛載過程發生錯誤: {e}")
            return None

    def unmount(self, disk_number):
        """卸載磁碟"""
        try:
            print(f"\n📤 卸載磁碟 {disk_number}...")
            result = subprocess.run(
                ["wsl", "--unmount", f"\\\\.\\PHYSICALDRIVE{disk_number}"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                print("✓ 已卸載")
            else:
                print(f"⚠ 卸載可能失敗: {result.stderr}")

        except Exception as e:
            print(f"⚠ 卸載錯誤: {e}")

    def get_windows_path(self, wsl_path):
        """將 WSL 路徑轉換為 Windows 路徑（使用 \\wsl$）"""
        if not wsl_path:
            return None

        # WSL 路徑範例: /mnt/wsl/PHYSICALDRIVE2p2/share/roms
        # Windows 路徑: \\wsl$\Ubuntu\mnt\wsl\PHYSICALDRIVE2p2\share\roms

        # 取得 WSL 發行版名稱
        try:
            result = subprocess.run(
                ["wsl", "-l", "-q"],
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-16le'  # WSL 輸出使用 UTF-16LE
            )

            if result.stdout:
                distros = [line.strip() for line in result.stdout.strip().split(
                    '\n') if line.strip()]
                if distros:
                    default_distro = distros[0].replace(
                        '\x00', '')  # 移除 null 字元

                    # 移除開頭的 /
                    wsl_path_clean = wsl_path.lstrip('/')

                    windows_path = f"\\\\wsl$\\{default_distro}\\{wsl_path_clean.replace('/', '\\')}"

                    print(f"\n📁 Windows 路徑: {windows_path}")
                    return windows_path

        except Exception as e:
            print(f"⚠ 轉換路徑時發生錯誤: {e}")

        return None

    def auto_detect_and_mount(self):
        """自動偵測並掛載 Batocera 磁碟"""
        print("=" * 70)
        print("  Batocera 磁碟自動偵測與掛載工具")
        print("=" * 70)

        # 步驟 1: 偵測 Batocera 磁碟
        if not self.detect_batocera_disk():
            return None

        # 步驟 2: 取得實體磁碟編號
        disk_number = self.get_physical_disk_number()
        if disk_number is None:
            return None

        # 步驟 3: 尋找 ext4 分區
        partition_number = self.find_ext4_partition(disk_number)
        if partition_number is None:
            print("⚠ 未找到 userdata 分區")
            return None

        # 步驟 4: 檢查 WSL2
        if not self.check_wsl_available():
            return None

        # 步驟 5: 掛載分區
        mount_point = self.mount_ext4_partition(disk_number, partition_number)
        if mount_point:
            # 轉換為 Windows 路徑
            windows_path = self.get_windows_path(mount_point)

            print("\n" + "=" * 70)
            print("✓ 掛載成功！")
            print("=" * 70)
            print(f"WSL 路徑: {mount_point}")
            if windows_path:
                print(f"Windows 路徑: {windows_path}")
            print(f"\n您可以使用翻譯工具處理此路徑")
            print("=" * 70)

            return {
                'disk_number': disk_number,
                'partition_number': partition_number,
                'wsl_path': mount_point,
                'windows_path': windows_path,
                'boot_drive': self.batocera_boot_drive
            }

        return None


def main():
    """主程式"""
    detector = BatoceraDetector()

    try:
        result = detector.auto_detect_and_mount()

        if result:
            print("\n提示：")
            print("  - 使用完畢後，請執行以下指令卸載:")
            print(
                f"    wsl --unmount \\\\.\\PHYSICALDRIVE{result['disk_number']}")
            print("  - 或重新執行此程式並選擇卸載選項")

            # 儲存結果供其他程式使用
            config_file = Path(__file__).parent / "batocera_mount.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\n✓ 掛載資訊已保存到: {config_file}")

            return result
        else:
            print("\n❌ 偵測或掛載失敗")
            return None

    except KeyboardInterrupt:
        print("\n\n已取消")
        return None


if __name__ == "__main__":
    result = main()

    if result:
        sys.exit(0)
    else:
        sys.exit(1)
