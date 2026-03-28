from __future__ import annotations

from pathlib import Path
from typing import Iterator

from ce.models import IndexRecord


class IndexParseError(ValueError):
    """Raised when a multistream index line cannot be parsed."""


def parse_index_line(line: str) -> IndexRecord:
    raw = line.rstrip("\n")
    try:
        offset_str, page_id_str, title = raw.split(":", maxsplit=2)
    except ValueError as exc:
        raise IndexParseError(f"Malformed index line: {raw!r}") from exc

    if not title:
        raise IndexParseError(f"Missing title in index line: {raw!r}")

    try:
        offset = int(offset_str)
        page_id = int(page_id_str)
    except ValueError as exc:
        raise IndexParseError(f"Invalid numeric field in index line: {raw!r}") from exc

    return IndexRecord(offset=offset, page_id=page_id, title=title)


def iter_index_records(index_path: Path) -> Iterator[IndexRecord]:
    if not index_path.exists():
        raise FileNotFoundError(f"Index file not found: {index_path}")

    with index_path.open("r", encoding="utf-8", errors="replace") as handle:
        for lineno, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield parse_index_line(line)
            except IndexParseError as exc:
                raise IndexParseError(f"{exc} (line {lineno})") from exc


def search_titles(index_path: Path, query: str, limit: int = 50) -> list[IndexRecord]:
    if not query.strip():
        raise ValueError("Query must be non-empty")

    q = query.casefold()
    matches: list[IndexRecord] = []
    for record in iter_index_records(index_path):
        if q in record.title.casefold():
            matches.append(record)
            if len(matches) >= limit:
                break
    return matches


def find_titles_exact(index_path: Path, titles: list[str]) -> list[IndexRecord]:
    title_map = {title.casefold(): title for title in titles if title.strip()}
    if not title_map:
        return []

    matches: list[IndexRecord] = []
    for record in iter_index_records(index_path):
        if record.title.casefold() in title_map:
            matches.append(record)
    return matches
