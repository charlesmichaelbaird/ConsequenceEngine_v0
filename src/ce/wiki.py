from __future__ import annotations

import bz2
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


_PAGE_BLOCK_RE = re.compile(r"<page>.*?</page>", re.DOTALL)
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
_PAGE_ID_RE = re.compile(r"<page>\s*<title>.*?</title>\s*<ns>\d+</ns>\s*<id>(\d+)</id>", re.DOTALL)
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

_NAMESPACE_TO_ID = {
    "talk": 1,
    "user": 2,
    "wikipedia": 4,
    "project": 4,
    "file": 6,
    "image": 6,
    "mediawiki": 8,
    "template": 10,
    "help": 12,
    "category": 14,
    "portal": 100,
    "draft": 118,
    "timedtext": 710,
    "module": 828,
}


@dataclass(frozen=True)
class IndexEntry:
    offset: int
    page_id: int | None
    title: str


@dataclass(frozen=True)
class ExtractedPage:
    title: str
    page_id: int | None
    source_offset: int
    raw_xml: str


def normalize_title(text: str) -> str:
    cleaned = _NON_ALNUM_RE.sub(" ", text.replace("_", " ").casefold())
    return " ".join(cleaned.split())


def infer_namespace_id(title: str) -> int:
    if ":" not in title:
        return 0
    maybe_ns = title.split(":", 1)[0].strip().casefold()
    return _NAMESPACE_TO_ID.get(maybe_ns, 0)


def iter_index_entries(index_path: Path) -> Iterator[IndexEntry]:
    with index_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            raw = line.rstrip("\n")
            if not raw:
                continue
            parts = raw.split(":", 2)
            if len(parts) != 3:
                continue
            try:
                offset = int(parts[0])
            except ValueError:
                continue
            page_id = _safe_int(parts[1])
            title = parts[2]
            yield IndexEntry(offset=offset, page_id=page_id, title=title)


def load_index(index_path: Path) -> list[IndexEntry]:
    """Load the multistream index file into memory."""
    entries = list(iter_index_entries(index_path))
    if not entries:
        raise ValueError(f"No valid index entries loaded from {index_path}")
    return entries


def compile_title_catalog(index_path: Path, db_path: Path, batch_size: int = 5000) -> int:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS title_catalog")
        conn.execute(
            """
            CREATE TABLE title_catalog (
                title TEXT NOT NULL,
                page_id INTEGER,
                offset INTEGER NOT NULL,
                namespace INTEGER NOT NULL,
                normalized_title TEXT NOT NULL
            )
            """
        )

        batch = []
        for entry in iter_index_entries(index_path):
            batch.append(
                (
                    entry.title,
                    entry.page_id,
                    entry.offset,
                    infer_namespace_id(entry.title),
                    normalize_title(entry.title),
                )
            )
            if len(batch) >= batch_size:
                conn.executemany(
                    "INSERT INTO title_catalog (title, page_id, offset, namespace, normalized_title) VALUES (?, ?, ?, ?, ?)",
                    batch,
                )
                total += len(batch)
                batch.clear()
        if batch:
            conn.executemany(
                "INSERT INTO title_catalog (title, page_id, offset, namespace, normalized_title) VALUES (?, ?, ?, ?, ?)",
                batch,
            )
            total += len(batch)

        conn.execute("CREATE INDEX idx_title_catalog_norm ON title_catalog(normalized_title)")
        conn.execute("CREATE INDEX idx_title_catalog_ns ON title_catalog(namespace)")
        conn.commit()
    return total


def search_title_catalog(
    db_path: Path,
    query: str,
    limit: int = 25,
    article_only: bool = True,
) -> list[IndexEntry]:
    q = normalize_title(query)
    if not q:
        return []

    sql = """
        SELECT title, page_id, offset
        FROM title_catalog
        WHERE normalized_title LIKE ?
    """
    params: list[object] = [f"%{q}%"]
    if article_only:
        sql += " AND namespace = 0"

    sql += """
        ORDER BY
            CASE
                WHEN normalized_title = ? THEN 0
                WHEN normalized_title LIKE ? THEN 1
                WHEN normalized_title LIKE ? THEN 2
                WHEN normalized_title LIKE ? THEN 3
                ELSE 4
            END,
            length(title) ASC,
            title ASC
        LIMIT ?
    """
    params.extend([q, f"{q} %", f"% {q} %", f"{q}%", limit])

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()

    return [IndexEntry(title=r[0], page_id=r[1], offset=r[2]) for r in rows]


def extract_pages_by_titles(
    dump_path: Path, entries: Iterable[IndexEntry], exact_titles: Iterable[str]
) -> list[ExtractedPage]:
    requested = {title.strip() for title in exact_titles if title.strip()}
    if not requested:
        return []

    matching_entries = [entry for entry in entries if entry.title in requested]
    if not matching_entries:
        return []

    offsets = sorted({entry.offset for entry in matching_entries})
    by_offset = {offset: _decompress_multistream_block(dump_path, offset) for offset in offsets}

    extracted: list[ExtractedPage] = []
    for entry in matching_entries:
        block_text = by_offset[entry.offset]
        page_xml = _find_page_xml_by_title(block_text, entry.title)
        if page_xml is None:
            continue
        extracted.append(
            ExtractedPage(
                title=entry.title,
                page_id=entry.page_id if entry.page_id is not None else _extract_page_id(page_xml),
                source_offset=entry.offset,
                raw_xml=page_xml,
            )
        )
    return extracted


def _decompress_multistream_block(dump_path: Path, offset: int, chunk_size: int = 1024 * 1024) -> str:
    with dump_path.open("rb") as fh:
        fh.seek(offset)
        decompressor = bz2.BZ2Decompressor()
        out = bytearray()
        while not decompressor.eof:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            out.extend(decompressor.decompress(chunk))
    if not out:
        raise ValueError(f"No decompressed data produced at offset={offset} from {dump_path}")
    return out.decode("utf-8", errors="replace")


def _find_page_xml_by_title(block_text: str, title: str) -> str | None:
    for match in _PAGE_BLOCK_RE.finditer(block_text):
        page_xml = match.group(0)
        parsed_title = _extract_title(page_xml)
        if parsed_title == title:
            return page_xml
    return None


def _extract_title(page_xml: str) -> str | None:
    match = _TITLE_RE.search(page_xml)
    return match.group(1) if match else None


def _extract_page_id(page_xml: str) -> int | None:
    match = _PAGE_ID_RE.search(page_xml)
    return int(match.group(1)) if match else None


def _safe_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None
