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

# Phase 4: Write Back to XML
python tests/test_writer.py
```

## Test Files

| File | Description |
|------|-------------|
| `test_scanner.py` | Tests ROM folder scanning and gamelist.xml copying |
| `test_dictionary.py` | Tests dictionary generation and merge strategies |
| `test_translator.py` | Tests translation engine, Wikipedia API, keep original logic |
| `test_writer.py` | Tests XML write back, display formats, backup functionality |

