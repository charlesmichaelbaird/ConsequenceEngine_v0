from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make src importable when running as a plain script.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ce.config import load_settings
from ce.wiki_index import IndexParseError, iter_index_records, search_titles


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect Wikipedia multistream index")
    parser.add_argument("--index", type=Path, help="Path to decompressed multistream index file")
    parser.add_argument("--query", type=str, help="Case-insensitive title substring")
    parser.add_argument("--limit", type=int, default=20, help="Maximum rows to print")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    settings = load_settings()
    index_path = args.index or settings.wiki_index_path

    try:
        if args.query:
            rows = search_titles(index_path=index_path, query=args.query, limit=args.limit)
        else:
            rows = []
            for idx, record in enumerate(iter_index_records(index_path), start=1):
                rows.append(record)
                if idx >= args.limit:
                    break
    except (FileNotFoundError, IndexParseError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not rows:
        print("No matching titles found.")
        return 0

    print(f"Index: {index_path}")
    print(f"Rows: {len(rows)}")
    print("offset\tpage_id\ttitle")
    for row in rows:
        print(f"{row.offset}\t{row.page_id}\t{row.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
