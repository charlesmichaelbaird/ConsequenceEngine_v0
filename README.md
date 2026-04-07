# ConsequenceEngine_v0

## Build offline Wikipedia title catalog

This one-time step converts the local multistream index text file into a compact SQLite title catalog.

### Input
- `local_data/enwiki-latest-pages-articles-multistream-index.txt`

### Output
- `local_data/wiki_title_catalog.db`
- Table: `title_catalog(title, page_id, offset, namespace, normalized_title)`
- Table: `build_metadata(source_filename, source_file_size, source_mtime_utc, built_at_utc, rows_inserted, malformed_lines_skipped, elapsed_seconds)`
- Indexes: title, normalized title, `(namespace, normalized_title)`, and unique `page_id`

### Run (Windows PowerShell)

```powershell
$env:PYTHONPATH = "src"
python scripts/build_title_catalog.py --force
```

Use `--force` to rebuild if the database already exists.
