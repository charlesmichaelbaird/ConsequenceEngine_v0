from __future__ import annotations

import bz2
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from consequence_engine_v0.models import ExtractedPage, ExtractionStats, IndexRecord
from consequence_engine_v0.normalize import normalize_text


def _strip_ns(tag: str) -> str:
    return tag.rsplit("}", maxsplit=1)[-1]


def _page_fields(page_elem: ET.Element) -> tuple[int, str, str]:
    title = ""
    page_id: int | None = None
    text = ""

    for child in page_elem:
        name = _strip_ns(child.tag)
        if name == "title":
            title = child.text or ""
        elif name == "id" and page_id is None:
            # First id under <page> is the page id (revision id appears later).
            page_id = int(child.text or "0")
        elif name == "revision":
            for rev_child in child:
                if _strip_ns(rev_child.tag) == "text":
                    text = rev_child.text or ""
                    break

    if page_id is None:
        raise ValueError(f"Missing page id for title={title!r}")
    return page_id, title, text


def _print_progress(scanned_pages: int, matched_pages: int, target_count: int) -> None:
    print(
        f"\rScanning pages: {scanned_pages:,} | matched: {matched_pages}/{target_count}",
        end="",
        file=sys.stderr,
        flush=True,
    )


def extract_pages_sequential(
    dump_path: Path,
    targets: list[IndexRecord],
    *,
    max_pages_to_scan: int | None = None,
    show_progress: bool = False,
    progress_every: int = 1_000,
) -> tuple[list[ExtractedPage], ExtractionStats]:
    """
    Sequential v0 extraction from compressed XML dump.

    This intentionally scans pages in order and filters to a tiny target set.
    It does not yet seek via multistream offsets.
    """
    if not dump_path.exists():
        raise FileNotFoundError(f"Dump file not found: {dump_path}")

    wanted_titles = {record.title.casefold(): record for record in targets}
    if not wanted_titles:
        stats = ExtractionStats(scanned_pages=0, matched_pages=0, stopped_due_to_limit=False)
        return [], stats

    results: list[ExtractedPage] = []
    scanned_pages = 0
    stopped_due_to_limit = False

    with bz2.open(dump_path, mode="rb") as compressed:
        for _event, elem in ET.iterparse(compressed, events=("end",)):
            if _strip_ns(elem.tag) != "page":
                continue

            scanned_pages += 1
            if show_progress and (scanned_pages == 1 or scanned_pages % progress_every == 0):
                _print_progress(scanned_pages, len(results), len(wanted_titles))

            page_id, title, raw_text = _page_fields(elem)
            key = title.casefold()
            if key in wanted_titles:
                source = wanted_titles[key]
                raw_xml = ET.tostring(elem, encoding="unicode")
                results.append(
                    ExtractedPage(
                        page_id=page_id,
                        title=title,
                        source_offset=source.offset,
                        raw_xml=raw_xml,
                        raw_text=raw_text,
                        normalized_text=normalize_text(raw_text),
                    )
                )
                if len(results) >= len(wanted_titles):
                    break

            if max_pages_to_scan is not None and scanned_pages >= max_pages_to_scan:
                stopped_due_to_limit = True
                break

            elem.clear()

    if show_progress:
        _print_progress(scanned_pages, len(results), len(wanted_titles))
        print(file=sys.stderr)

    stats = ExtractionStats(
        scanned_pages=scanned_pages,
        matched_pages=len(results),
        stopped_due_to_limit=stopped_due_to_limit,
    )
    return results, stats
