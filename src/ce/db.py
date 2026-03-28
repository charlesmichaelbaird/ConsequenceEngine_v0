from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ce.models import ExtractedPage


def connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS wiki_pages (
            page_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            source_offset INTEGER,
            raw_xml TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            normalized_text TEXT NOT NULL,
            extracted_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def upsert_wiki_page(conn: sqlite3.Connection, page: ExtractedPage) -> None:
    extracted_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO wiki_pages (
            page_id, title, source_offset, raw_xml, raw_text, normalized_text, extracted_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(page_id) DO UPDATE SET
            title = excluded.title,
            source_offset = excluded.source_offset,
            raw_xml = excluded.raw_xml,
            raw_text = excluded.raw_text,
            normalized_text = excluded.normalized_text,
            extracted_at = excluded.extracted_at
        """,
        (
            page.page_id,
            page.title,
            page.source_offset,
            page.raw_xml,
            page.raw_text,
            page.normalized_text,
            extracted_at,
        ),
    )
    conn.commit()
