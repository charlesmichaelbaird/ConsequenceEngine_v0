from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    wiki_index_path: Path
    wiki_dump_path: Path
    db_path: Path


def _expand(path_value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path_value))).resolve()


def _default_index_path() -> str:
    fixture = Path("data/fixtures/enwiki-20260301-pages-articles-multistream-index.txt")
    if fixture.exists():
        return str(fixture)
    return "local_data/enwiki-latest-pages-articles-multistream-index.txt"


def load_settings() -> Settings:
    """Load file locations from environment with practical local defaults."""
    wiki_index_path = _expand(os.getenv("CE_WIKI_INDEX_PATH", _default_index_path()))
    wiki_dump_path = _expand(
        os.getenv(
            "CE_WIKI_DUMP_PATH",
            "local_data/enwiki-latest-pages-articles-multistream.xml.bz2",
        )
    )
    db_path = _expand(os.getenv("CE_DB_PATH", "output/ce_v0.sqlite"))
    return Settings(
        wiki_index_path=wiki_index_path,
        wiki_dump_path=wiki_dump_path,
        db_path=db_path,
    )
