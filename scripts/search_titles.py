from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ce.config import RepoPaths
from ce.wiki import search_title_catalog


def main() -> int:
    parser = argparse.ArgumentParser(description="Search compiled Wikipedia title catalog")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=25, help="Maximum matches to print")
    parser.add_argument(
        "--all-namespaces",
        action="store_true",
        help="Include all namespaces (default is article namespace only)",
    )
    args = parser.parse_args()

    paths = RepoPaths.from_repo_root()
    if not paths.sqlite_path.exists():
        raise FileNotFoundError(
            f"Missing SQLite cache at {paths.sqlite_path}. Run: python scripts/compile_title_catalog.py"
        )

    try:
        matches = search_title_catalog(
            paths.sqlite_path,
            args.query,
            limit=args.limit,
            article_only=not args.all_namespaces,
        )
    except sqlite3.OperationalError as exc:
        raise RuntimeError(
            "title_catalog table not found. Run: python scripts/compile_title_catalog.py"
        ) from exc

    print(f"Found {len(matches)} match(es) for query: {args.query!r}")
    for idx, entry in enumerate(matches, start=1):
        print(
            f"{idx:>3}. title={entry.title} | page_id={entry.page_id} | offset={entry.offset}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
