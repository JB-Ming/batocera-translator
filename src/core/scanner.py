# ROM 資料夾掃描模組
"""
負責掃描 ROM 資料夾，識別遊戲平台，複製 gamelist.xml 到暫存區。
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class PlatformInfo:
    """遊戲平台資訊"""
    name: str                   # 平台代碼（資料夾名稱）
    path: Path                  # 平台資料夾路徑
    gamelist_path: Optional[Path]  # gamelist.xml 路徑
    has_gamelist: bool          # 是否有 gamelist.xml


class Scanner:
    """
    ROM 資料夾掃描器
    
    功能：
    - 掃描指定的 ROM 根目錄
    - 自動識別遊戲平台（依資料夾名稱）
    - 檢查各平台是否有 gamelist.xml
    - 複製 gamelist.xml 到本地暫存區
    """
    
    # 已知的遊戲平台清單（Batocera 支援的平台）
    KNOWN_PLATFORMS = [
        'nes', 'snes', 'megadrive', 'genesis', 'gba', 'gb', 'gbc',
        'nds', 'n64', 'gamecube', 'wii', 'ps1', 'psx', 'ps2', 'psp',
        'arcade', 'mame', 'neogeo', 'dreamcast', 'saturn', 'pcengine',
        'mastersystem', 'sega32x', 'segacd', 'atari2600', 'atari5200',
        'atari7800', 'lynx', 'jaguar', 'colecovision', 'intellivision',
        'vectrex', 'wonderswan', 'wonderswancolor', 'ngp', 'ngpc',
        'virtualboy', '3do', 'fds', 'scummvm', 'dos', 'amiga',
        'amstradcpc', 'c64', 'msx', 'msx2', 'zxspectrum', 'atarist',
        'x68000', 'pc88', 'pc98', 'fba', 'fbneo', 'naomi', 'atomiswave'
    ]
    
    def __init__(self, roms_path: str, local_cache_path: str = './gamelists_local'):
        """
        初始化掃描器
        
        Args:
            roms_path: ROM 根目錄路徑
            local_cache_path: 本地暫存區路徑
        """
        self.roms_path = Path(roms_path)
        self.local_cache_path = Path(local_cache_path)
        self.platforms: List[PlatformInfo] = []
        
    def scan(self) -> List[PlatformInfo]:
        """
        掃描 ROM 資料夾，識別所有遊戲平台
        
        Returns:
            平台資訊清單
        """
        self.platforms = []
        
        if not self.roms_path.exists():
            raise FileNotFoundError(f"ROM 目錄不存在: {self.roms_path}")
            
        # 掃描所有子資料夾
        for item in self.roms_path.iterdir():
            if item.is_dir():
                platform_name = item.name.lower()
                gamelist_path = item / 'gamelist.xml'
                
                platform_info = PlatformInfo(
                    name=platform_name,
                    path=item,
                    gamelist_path=gamelist_path if gamelist_path.exists() else None,
                    has_gamelist=gamelist_path.exists()
                )
                self.platforms.append(platform_info)
                
        return self.platforms
    
    def get_platforms_with_gamelist(self) -> List[PlatformInfo]:
        """取得有 gamelist.xml 的平台清單"""
        return [p for p in self.platforms if p.has_gamelist]
    
    def get_known_platforms(self) -> List[PlatformInfo]:
        """取得已知平台清單（過濾不認識的資料夾）"""
        return [p for p in self.platforms if p.name in self.KNOWN_PLATFORMS]
    
    def copy_gamelist_to_cache(self, platform: PlatformInfo) -> Path:
        """
        複製平台的 gamelist.xml 到本地暫存區
        
        Args:
            platform: 平台資訊
            
        Returns:
            暫存區的檔案路徑
        """
        if not platform.has_gamelist or platform.gamelist_path is None:
            raise FileNotFoundError(f"平台 {platform.name} 沒有 gamelist.xml")
            
        # 建立暫存區目錄
        cache_dir = self.local_cache_path / platform.name
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 複製檔案
        dest_path = cache_dir / 'gamelist.xml'
        shutil.copy2(platform.gamelist_path, dest_path)
        
        return dest_path
    
    def copy_all_gamelists(self, platforms: Optional[List[PlatformInfo]] = None) -> Dict[str, Path]:
        """
        複製所有平台的 gamelist.xml 到本地暫存區
        
        Args:
            platforms: 要處理的平台清單，None 表示全部有 gamelist 的平台
            
        Returns:
            平台名稱到暫存路徑的對應字典
        """
        if platforms is None:
            platforms = self.get_platforms_with_gamelist()
            
        result = {}
        for platform in platforms:
            if platform.has_gamelist:
                result[platform.name] = self.copy_gamelist_to_cache(platform)
                
        return result
