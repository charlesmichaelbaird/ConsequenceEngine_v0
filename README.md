# CE_v0 (Consequence Engine v0)

CE_v0 is a **local-first historical consequence engine** prototype.

This first vertical slice is intentionally narrow:
- inspect a local Wikipedia multistream index
- find candidate pages by title
- extract a tiny selected subset from a local `.xml.bz2` dump
- normalize/stage text in SQLite for later consequence-graph work

## Current scope

### In scope (this increment)
- CLI-first scripts (`inspect_index.py`, `extract_pages.py`)
- Windows-friendly local path configuration via environment variables
- Minimal multistream index parsing and title search
- Sequential tiny-subset extraction from compressed dump with CLI progress updates
- SQLite table for extracted pages
- Focus on early COVID scenario seeding

### Out of scope (intentional)
- Full-corpus parse/throughput optimization
- UI/frontend
- embeddings/vector DB
- LLM runtime integration
- live web/news scraping
- real-time forecasting claims

---

## Project layout

```text
src/consequence_engine_v0/
  config.py
  db.py
  graph_build.py
  models.py
  normalize.py
  scenarios.py
  wiki_extract.py
  wiki_index.py
scripts/
  inspect_index.py
  extract_pages.py
data/fixtures/
tests/
```

---

## Local data setup

Large corpora stay local and out of git (for example under `local_data/`).

Copy `.env.example` values into your environment (PowerShell example, Windows):

```powershell
$env:CE_WIKI_INDEX_PATH = "C:\path\to\enwiki-latest-pages-articles-multistream-index.txt"
$env:CE_WIKI_DUMP_PATH  = "C:\path\to\enwiki-latest-pages-articles-multistream.xml.bz2"
$env:CE_DB_PATH         = "C:\path\to\output\ce_v0.sqlite"
```

If unset, defaults are:
- `data/fixtures/enwiki-20260301-pages-articles-multistream-index.txt` (if present) or `local_data/enwiki-latest-pages-articles-multistream-index.txt`
- `local_data/enwiki-latest-pages-articles-multistream.xml.bz2`
- `output/ce_v0.sqlite`

---

## Usage

> Run commands from repo root.

### 1) Inspect index quickly

PowerShell / PyCharm local terminal on Windows:

```powershell
python scripts\inspect_index.py --query covid --limit 10
```

Or preview first lines (no query):

```powershell
python scripts\inspect_index.py --limit 10
```

### 2) Extract a tiny title set into SQLite

Use explicit titles:

```powershell
python scripts\extract_pages.py `
  --title "COVID-19 pandemic" `
  --title "Panic buying" `
  --title "Remote work"
```

Use a titles file (one title per line):

```powershell
python scripts\extract_pages.py --titles-file data\fixtures\early_covid_seed_titles.txt
```

Use built-in seed list for early COVID workflow:

```powershell
python scripts\extract_pages.py --seed early-covid
```


For quick local smoke tests on large dumps, cap the scan window:

```powershell
python scripts\extract_pages.py --seed early-covid --quick-test
```

(Equivalent explicit control: `--max-pages-to-scan 20000`.)

The script will:
1. find exact title matches in index
2. sequentially scan compressed XML dump and extract those pages
3. normalize text (whitespace collapse)
4. upsert into SQLite table `wiki_pages`
5. print scan progress while reading the dump (disable with `--no-progress`)

---

## SQLite output

Database path comes from `CE_DB_PATH` (default `output/ce_v0.sqlite`).

Current table:
- `wiki_pages(page_id, title, source_offset, raw_xml, raw_text, normalized_text, extracted_at)`

This schema is intentionally simple and expected to evolve.

---

## Development checks

```powershell
python -m unittest discover -s tests -v
```

---

## Known limitations (honest v0)

- Extraction mode is currently **sequential scan** over the compressed dump.
- Multistream offsets are parsed/stored, but not yet used for direct random-access seeks.
- Exact-title matching in extraction is strict; redirect/disambiguation handling is not implemented yet.
- Normalization is intentionally minimal.
