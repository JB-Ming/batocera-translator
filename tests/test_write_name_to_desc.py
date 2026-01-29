# -*- coding: utf-8 -*-
"""
Test: Write translated name to desc field
Verify that when setting name -> desc, even if there is no desc element, it can be written correctly
"""
from src.core.dictionary import GameEntry
from src.core.writer import XmlWriter, WriteStrategy
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_name_to_desc_without_existing_desc():
    """Test: name writes to desc, but original XML has no desc element"""
    print("=" * 60)
    print("Test 1: name -> desc (no existing desc element)")
    print("=" * 60)

    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = Path(tmpdir) / "gamelist.xml"

        # Create test XML (no desc element)
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<gameList>
    <game>
        <path>./test_game.zip</path>
        <name>Test Game</name>
    </game>
    <game>
        <path>./another_game.zip</path>
        <name>Another Game</name>
    </game>
</gameList>
'''
        xml_path.write_text(xml_content, encoding='utf-8')

        # Create dictionary
        dictionary = {
            'test_game': GameEntry(
                key='test_game',
                name='測試遊戲',
                original_name='Test Game',
                desc='',
                original_desc=''
            ),
            'another_game': GameEntry(
                key='another_game',
                name='另一個遊戲',
                original_name='Another Game',
                desc='',
                original_desc=''
            )
        }

        # Set write rules: name -> desc
        write_rules = {
            'name': {'target': 'desc', 'format': 'translated'},
            'desc': {'target': 'skip', 'format': 'translated'}
        }

        # Execute write
        writer = XmlWriter()
        result = writer.write_translations(
            xml_path=xml_path,
            dictionary=dictionary,
            platform='test',
            strategy=WriteStrategy.OVERWRITE_ALL,
            write_rules=write_rules
        )

        # Read result
        result_content = xml_path.read_text(encoding='utf-8')
        print(
            f"Write result: updated {result.updated}, skipped {result.skipped}")
        print("\nResult XML:")
        print(result_content)

        # Verify
        assert '測試遊戲' in result_content, "Should contain translated name '測試遊戲'"
        assert '另一個遊戲' in result_content, "Should contain translated name '另一個遊戲'"
        assert '<desc>測試遊戲</desc>' in result_content, "Translated name should be in desc tag"
        assert '<desc>另一個遊戲</desc>' in result_content, "Translated name should be in desc tag"
        # name should remain unchanged
        assert '<name>Test Game</name>' in result_content, "name should remain unchanged"

        print("\n✅ Test passed!")
        return True


def test_name_to_desc_with_existing_desc():
    """Test: name writes to desc, original has desc element"""
    print("\n" + "=" * 60)
    print("Test 2: name -> desc (with existing desc element)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = Path(tmpdir) / "gamelist.xml"

        # Create test XML (has desc element)
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<gameList>
    <game>
        <path>./test_game.zip</path>
        <name>Test Game</name>
        <desc>Original description here.</desc>
    </game>
</gameList>
'''
        xml_path.write_text(xml_content, encoding='utf-8')

        dictionary = {
            'test_game': GameEntry(
                key='test_game',
                name='測試遊戲',
                original_name='Test Game',
                desc='',
                original_desc=''
            )
        }

        write_rules = {
            'name': {'target': 'desc', 'format': 'translated'},
            'desc': {'target': 'skip', 'format': 'translated'}
        }

        writer = XmlWriter()
        result = writer.write_translations(
            xml_path=xml_path,
            dictionary=dictionary,
            platform='test',
            strategy=WriteStrategy.OVERWRITE_ALL,
            write_rules=write_rules
        )

        result_content = xml_path.read_text(encoding='utf-8')
        print(
            f"Write result: updated {result.updated}, skipped {result.skipped}")
        print("\nResult XML:")
        print(result_content)

        assert '<desc>測試遊戲</desc>' in result_content, "desc should be overwritten with translated name"
        assert 'Original description' not in result_content, "Original desc should be overwritten"

        print("\n✅ Test passed!")
        return True


def test_desc_to_name_without_existing_name():
    """Test: desc writes to name, but original has no name element (rare case)"""
    print("\n" + "=" * 60)
    print("Test 3: desc -> name (no existing name element)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = Path(tmpdir) / "gamelist.xml"

        # Create test XML (no name element, rare case)
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<gameList>
    <game>
        <path>./test_game.zip</path>
        <desc>This is the original description.</desc>
    </game>
</gameList>
'''
        xml_path.write_text(xml_content, encoding='utf-8')

        dictionary = {
            'test_game': GameEntry(
                key='test_game',
                name='',
                original_name='',
                desc='這是翻譯後的說明',
                original_desc='This is the original description.'
            )
        }

        write_rules = {
            'name': {'target': 'skip', 'format': 'translated'},
            'desc': {'target': 'name', 'format': 'translated'}
        }

        writer = XmlWriter()
        result = writer.write_translations(
            xml_path=xml_path,
            dictionary=dictionary,
            platform='test',
            strategy=WriteStrategy.OVERWRITE_ALL,
            write_rules=write_rules
        )

        result_content = xml_path.read_text(encoding='utf-8')
        print(
            f"Write result: updated {result.updated}, skipped {result.skipped}")
        print("\nResult XML:")
        print(result_content)

        assert '<name>這是翻譯後的說明</name>' in result_content, "Translated desc should be written to newly created name tag"

        print("\n✅ Test passed!")
        return True


def test_name_to_desc_with_format():
    """Test: name writes to desc with different format"""
    print("\n" + "=" * 60)
    print("Test 4: name -> desc (with trans_orig format)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = Path(tmpdir) / "gamelist.xml"

        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<gameList>
    <game>
        <path>./test_game.zip</path>
        <name>Test Game</name>
    </game>
</gameList>
'''
        xml_path.write_text(xml_content, encoding='utf-8')

        dictionary = {
            'test_game': GameEntry(
                key='test_game',
                name='測試遊戲',
                original_name='Test Game',
                desc='',
                original_desc=''
            )
        }

        # Use trans_orig format
        write_rules = {
            'name': {'target': 'desc', 'format': 'trans_orig'},
            'desc': {'target': 'skip', 'format': 'translated'}
        }

        writer = XmlWriter()
        result = writer.write_translations(
            xml_path=xml_path,
            dictionary=dictionary,
            platform='test',
            strategy=WriteStrategy.OVERWRITE_ALL,
            write_rules=write_rules
        )

        result_content = xml_path.read_text(encoding='utf-8')
        print(
            f"Write result: updated {result.updated}, skipped {result.skipped}")
        print("\nResult XML:")
        print(result_content)

        assert '測試遊戲' in result_content, "Should contain translated name"
        assert 'Test Game' in result_content, "Should contain original name"
        assert '<desc>' in result_content, "Should have desc tag"

        print("\n✅ Test passed!")
        return True


if __name__ == '__main__':
    print("Starting tests for name -> desc write functionality\n")

    all_passed = True

    try:
        test_name_to_desc_without_existing_desc()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        all_passed = False

    try:
        test_name_to_desc_with_existing_desc()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        all_passed = False

    try:
        test_desc_to_name_without_existing_name()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        all_passed = False

    try:
        test_name_to_desc_with_format()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed")
    print("=" * 60)
