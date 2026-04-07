from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepoPaths:
    """Resolved repository-relative paths for local data and cache files."""

    repo_root: Path
    local_data_dir: Path
    index_path: Path
    dump_path: Path
    sqlite_path: Path

    @classmethod
    def from_repo_root(cls, repo_root: Path | None = None) -> "RepoPaths":
        root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
        local_data = root / "local_data"
        return cls(
            repo_root=root,
            local_data_dir=local_data,
            index_path=local_data / "enwiki-latest-pages-articles-multistream-index.txt",
            dump_path=local_data / "enwiki-latest-pages-articles-multistream.xml.bz2",
            sqlite_path=local_data / "ce_cache.sqlite3",
        )

    def validate_required_inputs(self) -> None:
        """Fail fast with clear messages when expected dump files are missing."""
        if not self.local_data_dir.exists():
            raise FileNotFoundError(
                f"Expected local data directory at: {self.local_data_dir}\n"
                "Create it in the repo root and place the Wikipedia dump files there."
            )
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Missing multistream index file: {self.index_path}\n"
                "Expected filename: enwiki-latest-pages-articles-multistream-index.txt"
            )
        if not self.dump_path.exists():
            raise FileNotFoundError(
                f"Missing multistream dump file: {self.dump_path}\n"
                "Expected filename: enwiki-latest-pages-articles-multistream.xml.bz2"
            )
