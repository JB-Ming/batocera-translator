# Tests Directory

This directory contains test scripts for the Batocera Gamelist Translator.

## Running Tests

```bash
# Phase 1: Scan and Retrieve
python tests/test_scanner.py "D:\path\to\your\Roms"

# Phase 2: Generate Dictionary
python tests/test_dictionary.py

# Phase 3: Translation (limited API calls)
python tests/test_translator.py [dictionary_path] [language] [limit]
# Example: python tests/test_translator.py ./dictionaries zh-TW 3
```

## Test Files

| File | Description |
|------|-------------|
| `test_scanner.py` | Tests ROM folder scanning and gamelist.xml copying |
| `test_dictionary.py` | Tests dictionary generation and merge strategies |
| `test_translator.py` | Tests translation engine, Wikipedia API, keep original logic |
