from __future__ import annotations

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from consequence_engine_v0.wiki_index import IndexParseError, parse_index_line, search_titles


FIXTURE_INDEX = Path("data/fixtures/sample_index.txt")


class WikiIndexTests(unittest.TestCase):
    def test_parse_index_line_ok(self) -> None:
        record = parse_index_line("123:456:COVID-19 pandemic\n")
        self.assertEqual(record.offset, 123)
        self.assertEqual(record.page_id, 456)
        self.assertEqual(record.title, "COVID-19 pandemic")

    def test_parse_index_line_error(self) -> None:
        with self.assertRaises(IndexParseError):
            parse_index_line("bad line")

    def test_search_titles_case_insensitive(self) -> None:
        rows = search_titles(FIXTURE_INDEX, "panic")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].title, "Panic buying")


if __name__ == "__main__":
    unittest.main()
