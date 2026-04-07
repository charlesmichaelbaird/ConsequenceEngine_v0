from __future__ import annotations

import argparse
import datetime as dt
import os
import sqlite3
import sys
import time
from pathlib import Path

from .config import TITLE_CATALOG_DB_PATH, WIKI_INDEX_PATH


def normalize_title(title: str) -> str:
    return " ".join(title.replace("_", " ").strip().lower().split())


def parse_namespace(title: str) -> str:
    if ":" not in title:
        return "main"
    return title.split(":", 1)[0].strip().lower() or "main"


def parse_index_line(line: str):
    parts = line.split(":", 2)
    if len(parts) != 3:
        return None
    offset_raw, page_id_raw, title = parts
    try:
        offset = int(offset_raw)
        page_id = int(page_id_raw)
    except ValueError:
        return None
    return title, page_id, offset, parse_namespace(title), normalize_title(title)


def iter_index_rows(index_path: Path):
    with index_path.open("rb") as handle:
        while True:
            raw_line = handle.readline()
            if not raw_line:
                break
            position = handle.tell()
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
            if not line:
                continue
            yield position, parse_index_line(line)


def print_progress(processed: int, total: int) -> None:
    width = 28
    ratio = 1.0 if total == 0 else min(processed / total, 1.0)
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    percent = ratio * 100
    sys.stdout.write(f"\r[{bar}] {percent:6.2f}%  {processed}/{total} bytes")
    sys.stdout.flush()


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE title_catalog (
            title TEXT NOT NULL,
            page_id INTEGER NOT NULL,
            offset INTEGER NOT NULL,
            namespace TEXT NOT NULL,
            normalized_title TEXT NOT NULL
        );

        CREATE INDEX idx_title_catalog_title ON title_catalog(title);
        CREATE INDEX idx_title_catalog_normalized_title ON title_catalog(normalized_title);
        CREATE INDEX idx_title_catalog_namespace_normalized
            ON title_catalog(namespace, normalized_title);
        CREATE UNIQUE INDEX idx_title_catalog_page_id ON title_catalog(page_id);

        CREATE TABLE build_metadata (
            source_filename TEXT NOT NULL,
            source_file_size INTEGER NOT NULL,
            source_mtime_utc TEXT NOT NULL,
            built_at_utc TEXT NOT NULL,
            rows_inserted INTEGER NOT NULL,
            malformed_lines_skipped INTEGER NOT NULL,
            elapsed_seconds REAL NOT NULL
        );
        """
    )


def build_title_catalog(index_path: Path, db_path: Path, force: bool = False) -> int:
    if not index_path.exists():
        raise FileNotFoundError(f"Wikipedia index file not found: {index_path}")

    if db_path.exists():
        if not force:
            raise FileExistsError(f"Catalog already exists: {db_path} (use --force to rebuild)")
        db_path.unlink()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    total_bytes = index_path.stat().st_size
    source_mtime_utc = dt.datetime.fromtimestamp(index_path.stat().st_mtime, tz=dt.timezone.utc).isoformat()
    started_at = time.perf_counter()
    processed_bytes = 0
    row_count = 0
    malformed_lines_skipped = 0

    conn = sqlite3.connect(db_path)
    try:
        create_schema(conn)
        batch: list[tuple[str, int, int, str, str]] = []

        for processed_bytes, row in iter_index_rows(index_path):
            if row is None:
                malformed_lines_skipped += 1
                continue
            batch.append(row)

            if len(batch) >= 5000:
                conn.executemany(
                    """
                    INSERT INTO title_catalog(title, page_id, offset, namespace, normalized_title)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    batch,
                )
                conn.commit()
                row_count += len(batch)
                batch.clear()
                print_progress(processed_bytes, total_bytes)

        if batch:
            conn.executemany(
                """
                INSERT INTO title_catalog(title, page_id, offset, namespace, normalized_title)
                VALUES (?, ?, ?, ?, ?)
                """,
                batch,
            )
            conn.commit()
            row_count += len(batch)
            print_progress(total_bytes, total_bytes)

        elapsed_seconds = time.perf_counter() - started_at
        built_at_utc = dt.datetime.now(dt.timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO build_metadata(
                source_filename,
                source_file_size,
                source_mtime_utc,
                built_at_utc,
                rows_inserted,
                malformed_lines_skipped,
                elapsed_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                index_path.name,
                total_bytes,
                source_mtime_utc,
                built_at_utc,
                row_count,
                malformed_lines_skipped,
                elapsed_seconds,
            ),
        )
        conn.commit()

        sys.stdout.write("\n")
        return row_count
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a SQLite title catalog from a Wikipedia multistream index.")
    parser.add_argument("--index-path", type=Path, default=WIKI_INDEX_PATH)
    parser.add_argument("--db-path", type=Path, default=TITLE_CATALOG_DB_PATH)
    parser.add_argument("--force", action="store_true", help="Replace existing catalog database if it exists.")
    args = parser.parse_args()

    try:
        rows = build_title_catalog(args.index_path, args.db_path, force=args.force)
    except (FileNotFoundError, FileExistsError) as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    file_size = os.path.getsize(args.db_path)
    print(f"Built title catalog at {args.db_path}")
    print(f"Rows inserted: {rows}")
    print(f"Database size: {file_size} bytes")


if __name__ == "__main__":
    main()
