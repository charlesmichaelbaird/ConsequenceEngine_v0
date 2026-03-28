from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Simple v0 normalization: collapse whitespace and trim."""
    return _WHITESPACE_RE.sub(" ", text).strip()
