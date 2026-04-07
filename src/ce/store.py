from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .wiki import ExtractedPage


def ensure_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pages (
                title TEXT PRIMARY KEY,
                page_id INTEGER,
                source_offset INTEGER NOT NULL,
                extracted_at TEXT NOT NULL,
                raw_xml TEXT NOT NULL
            )
            """
        )
        conn.commit()


def upsert_pages(db_path: Path, pages: Iterable[ExtractedPage]) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        rows = [
            (p.title, p.page_id, p.source_offset, now, p.raw_xml)
            for p in pages
        ]
        conn.executemany(
            """
            INSERT INTO pages (title, page_id, source_offset, extracted_at, raw_xml)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(title) DO UPDATE SET
                page_id=excluded.page_id,
                source_offset=excluded.source_offset,
                extracted_at=excluded.extracted_at,
                raw_xml=excluded.raw_xml
            """,
            rows,
        )
        conn.commit()
    return len(rows)
