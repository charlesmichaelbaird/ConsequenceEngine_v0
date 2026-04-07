# ConsequenceEngine_v0

Minimal local-first substrate for reading and extracting a few pages from a local Wikipedia multistream dump.

## Requirements

- Python 3.10+
- Local files in `local_data/`:
  - `enwiki-latest-pages-articles-multistream-index.txt`
  - `enwiki-latest-pages-articles-multistream.xml.bz2`

## Usage

### 1) Search titles

```bash
python scripts/search_titles.py "COVID" --limit 20
```

Output includes `title`, `page_id`, and `offset` from the multistream index.

### 2) Extract exact titles and cache in SQLite

```bash
python scripts/extract_pages.py "COVID-19 pandemic" "Panic buying"
```

This extracts matching pages from the dump and writes them into:

- `local_data/ce_cache.sqlite3`

Stored fields are minimal: title, page id, source offset, extraction timestamp, and raw page XML.

## Notes / limitations

- First pass keeps scope narrow and stores raw XML (not normalized plain text).
- Title extraction uses exact title matches from index results.
- Extraction uses the multistream byte offset and decompresses only the needed stream block.
- If `local_data/` or expected dump files are missing, scripts fail fast with a clear error.
- Designed to work with standard Python on Windows (no WSL required).
