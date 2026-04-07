from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ce.config import RepoPaths
from ce.wiki import load_index, search_titles


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Wikipedia multistream titles")
    parser.add_argument("query", help="Case-insensitive substring query")
    parser.add_argument("--limit", type=int, default=25, help="Maximum matches to print")
    args = parser.parse_args()

    paths = RepoPaths.from_repo_root()
    paths.validate_required_inputs()

    entries = load_index(paths.index_path)
    matches = search_titles(entries, args.query, limit=args.limit)

    print(f"Found {len(matches)} match(es) for query: {args.query!r}")
    for idx, entry in enumerate(matches, start=1):
        print(
            f"{idx:>3}. title={entry.title} | page_id={entry.page_id} | offset={entry.offset}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
