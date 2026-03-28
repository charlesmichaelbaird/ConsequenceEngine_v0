from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndexRecord:
    """Single title row from a Wikipedia multistream index file."""

    offset: int
    page_id: int
    title: str


@dataclass(frozen=True)
class ExtractedPage:
    """Extracted Wikipedia page payload before/after basic normalization."""

    page_id: int
    title: str
    source_offset: int | None
    raw_xml: str
    raw_text: str
    normalized_text: str


@dataclass(frozen=True)
class ExtractionStats:
    """Basic extraction metrics for CLI feedback and quick-test tuning."""

    scanned_pages: int
    matched_pages: int
    stopped_due_to_limit: bool
