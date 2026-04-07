# ConsequenceEngine_v0

Minimal local-first substrate for reading and extracting a few pages from a local Wikipedia multistream dump.

## Requirements

- Python 3.10+
- Local files in `local_data/`:
  - `enwiki-latest-pages-articles-multistream-index.txt`
  - `enwiki-latest-pages-articles-multistream.xml.bz2`

## Usage

### 1) Compile title catalog (one-time / when index changes)

```bash
python scripts/compile_title_catalog.py
```

This creates/refreshes SQLite table `title_catalog` in `local_data/ce_cache.sqlite3`.

### 2) Search titles (uses compiled SQLite catalog)

```bash
python scripts/search_titles.py "COVID" --limit 20
```

Default search targets article namespace only (`namespace=0`). To include all namespaces:

```bash
python scripts/search_titles.py "COVID" --all-namespaces
```

Output includes `title`, `page_id`, and `offset`.

### 3) Extract exact titles and cache page XML

```bash
python scripts/extract_pages.py "COVID-19 pandemic" "Panic buying"
```

This extracts matching pages from the dump and writes into `local_data/ce_cache.sqlite3` (`pages` table).

## Notes / limitations

- First pass keeps scope narrow and stores raw XML (not normalized plain text).
- `title_catalog` is the canonical title lookup layer for fast reuse.
- Search ranking prefers exact and prefix-like normalized matches over looser matches.
- Extraction still uses exact title matching and multistream offsets from the index.
- If `local_data/` or expected dump files are missing, scripts fail fast with a clear error.
- Designed to work with standard Python on Windows (no WSL required).
