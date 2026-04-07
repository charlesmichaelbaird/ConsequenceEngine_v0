from __future__ import annotations

import bz2
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_PAGE_BLOCK_RE = re.compile(r"<page>.*?</page>", re.DOTALL)
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
_PAGE_ID_RE = re.compile(r"<page>\s*<title>.*?</title>\s*<ns>\d+</ns>\s*<id>(\d+)</id>", re.DOTALL)


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


def load_index(index_path: Path) -> list[IndexEntry]:
    """Load the multistream index file into memory."""
    entries: list[IndexEntry] = []
    with index_path.open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
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
            entries.append(IndexEntry(offset=offset, page_id=page_id, title=title))
    if not entries:
        raise ValueError(f"No valid index entries loaded from {index_path}")
    return entries


def search_titles(entries: Iterable[IndexEntry], query: str, limit: int = 50) -> list[IndexEntry]:
    q = query.casefold().strip()
    if not q:
        return []
    matches = [entry for entry in entries if q in entry.title.casefold()]
    return matches[:limit]


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
