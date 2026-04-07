from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA_DIR = REPO_ROOT / "local_data"
WIKI_INDEX_PATH = LOCAL_DATA_DIR / "enwiki-latest-pages-articles-multistream-index.txt"
TITLE_CATALOG_DB_PATH = LOCAL_DATA_DIR / "wiki_title_catalog.db"
