from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ce.config import RepoPaths
from ce.store import ensure_db, upsert_pages
from ce.wiki import extract_pages_by_titles, load_index


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract exact-title pages from multistream dump and cache to SQLite"
    )
    parser.add_argument(
        "titles",
        nargs="+",
        help="One or more exact page titles (match exactly as in the index)",
    )
    args = parser.parse_args()

    paths = RepoPaths.from_repo_root()
    paths.validate_required_inputs()

    entries = load_index(paths.index_path)
    pages = extract_pages_by_titles(paths.dump_path, entries, args.titles)

    if not pages:
        print("No pages extracted. Check exact title spelling/casing from search results.")
        return 1

    ensure_db(paths.sqlite_path)
    saved = upsert_pages(paths.sqlite_path, pages)

    print(f"Extracted {len(pages)} page(s); saved {saved} row(s) to {paths.sqlite_path}")
    for page in pages:
        print(
            f"- title={page.title} | page_id={page.page_id} | offset={page.source_offset} | xml_chars={len(page.raw_xml)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
