#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Phase 1 - Scan and Retrieve

Test Items:
1. ROM folder scan function
2. Platform auto-detection (by folder name)
3. gamelist.xml copy to local cache
"""
import sys
import os

# Ensure src module can be found (go up one level from tests/ to project root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.scanner import Scanner, PlatformInfo

def test_scanner(roms_path: str):
    """Test scanner functionality"""
    print("=" * 60)
    print("Phase 1: Scan and Retrieve - Functionality Test")
    print("=" * 60)
    print(f"\n[PATH] Test path: {roms_path}\n")
    
    # 1. Initialize scanner
    print("[1] Initialize scanner...")
    scanner = Scanner(roms_path=roms_path, local_cache_path='./gamelists_local')
    print(f"    [+] ROM path: {scanner.roms_path}")
    print(f"    [+] Cache path: {scanner.local_cache_path}")
    
    # 2. Execute scan
    print("\n[2] Execute scan...")
    try:
        platforms = scanner.scan()
        print(f"    [+] Scan complete! Found {len(platforms)} folders")
    except FileNotFoundError as e:
        print(f"    [X] Scan failed: {e}")
        return False
    
    # 3. Show all discovered folders
    print("\n[3] Discovered folders:")
    for p in platforms:
        status = "[O] has gamelist.xml" if p.has_gamelist else "[X] no gamelist.xml"
        print(f"    {p.name:20} {status}")
    
    # 4. Filter platforms with gamelist
    print("\n[4] Platforms with gamelist.xml:")
    platforms_with_gamelist = scanner.get_platforms_with_gamelist()
    if platforms_with_gamelist:
        for p in platforms_with_gamelist:
            print(f"    [+] {p.name} -> {p.gamelist_path}")
    else:
        print("    (none)")
    
    # 5. Filter known platforms
    print("\n[5] Known game platforms (matching Batocera naming):")
    known_platforms = scanner.get_known_platforms()
    if known_platforms:
        for p in known_platforms:
            status = "[O] has gamelist" if p.has_gamelist else "[X] no gamelist"
            print(f"    {p.name:20} {status}")
    else:
        print("    (none)")
    
    # 6. Test copy to cache
    copied = {}
    print("\n[6] Copy gamelist.xml to local cache:")
    if platforms_with_gamelist:
        try:
            copied = scanner.copy_all_gamelists()
            for platform_name, cache_path in copied.items():
                print(f"    [+] {platform_name} -> {cache_path}")
            print(f"\n    [+] Successfully copied {len(copied)} gamelist.xml to cache")
        except Exception as e:
            print(f"    [X] Copy failed: {e}")
            return False
    else:
        print("    (no gamelist.xml to copy)")
    
    # 7. Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"    Total folders:        {len(platforms)}")
    print(f"    With gamelist:        {len(platforms_with_gamelist)}")
    print(f"    Known platforms:      {len(known_platforms)}")
    print(f"    Copied to cache:      {len(copied)}")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    # Default test path
    default_path = r"D:\download\RPI_Ready\Roms"
    
    # Path can be specified via command line
    if len(sys.argv) > 1:
        roms_path = sys.argv[1]
    else:
        roms_path = default_path
    
    success = test_scanner(roms_path)
    
    if success:
        print("\n[PASS] Phase 1 test passed!")
    else:
        print("\n[FAIL] Phase 1 test failed!")
        sys.exit(1)
