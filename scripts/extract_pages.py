from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ce.config import load_settings
from ce.db import connect_db, init_db, upsert_wiki_page
from ce.scenarios import EARLY_COVID_SEED_TITLES
from ce.wiki_extract import extract_pages_sequential
from ce.wiki_index import find_titles_exact


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract tiny selected pages into SQLite")
    parser.add_argument("--index", type=Path, help="Path to decompressed multistream index file")
    parser.add_argument("--dump", type=Path, help="Path to compressed multistream XML dump (.bz2)")
    parser.add_argument("--db", type=Path, help="Path to SQLite output file")
    parser.add_argument(
        "--title",
        action="append",
        default=[],
        help="Exact title to extract. Repeat flag for multiple titles.",
    )
    parser.add_argument("--titles-file", type=Path, help="Text file with one title per line")
    parser.add_argument(
        "--seed",
        choices=["early-covid"],
        help="Include scenario seed titles (currently: early-covid)",
    )
    return parser


def _load_titles(args: argparse.Namespace) -> list[str]:
    titles: list[str] = []
    titles.extend([t.strip() for t in args.title if t.strip()])

    if args.titles_file:
        if not args.titles_file.exists():
            raise FileNotFoundError(f"Titles file not found: {args.titles_file}")
        lines = args.titles_file.read_text(encoding="utf-8").splitlines()
        titles.extend([line.strip() for line in lines if line.strip() and not line.strip().startswith("#")])

    if args.seed == "early-covid":
        titles.extend(EARLY_COVID_SEED_TITLES)

    deduped: list[str] = []
    seen: set[str] = set()
    for title in titles:
        key = title.casefold()
        if key not in seen:
            seen.add(key)
            deduped.append(title)
    return deduped


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    settings = load_settings()

    index_path = args.index or settings.wiki_index_path
    dump_path = args.dump or settings.wiki_dump_path
    db_path = args.db or settings.db_path

    try:
        titles = _load_titles(args)
        if not titles:
            raise ValueError("No titles provided. Use --title, --titles-file, or --seed early-covid.")

        candidate_records = find_titles_exact(index_path=index_path, titles=titles)
        if not candidate_records:
            print("No matching titles found in index; nothing to extract.")
            return 0

        extracted = extract_pages_sequential(dump_path=dump_path, targets=candidate_records)
        if not extracted:
            print("Index candidates found, but no pages were extracted from dump.")
            return 0

        conn = connect_db(db_path)
        try:
            init_db(conn)
            for page in extracted:
                upsert_wiki_page(conn, page)
        finally:
            conn.close()

        requested = len(titles)
        print(f"Requested titles: {requested}")
        print(f"Index matches: {len(candidate_records)}")
        print(f"Extracted + stored: {len(extracted)}")
        print(f"SQLite DB: {db_path}")
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
