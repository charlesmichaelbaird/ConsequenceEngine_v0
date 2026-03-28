from __future__ import annotations

import bz2
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from consequence_engine_v0.models import IndexRecord
from consequence_engine_v0.wiki_extract import extract_pages_sequential


class WikiExtractTests(unittest.TestCase):
    def test_extract_respects_max_pages_to_scan(self) -> None:
        xml = (
            "<mediawiki>"
            "<page><title>Page A</title><id>1</id><revision><id>11</id><text>A</text></revision></page>"
            "<page><title>Page B</title><id>2</id><revision><id>22</id><text>B</text></revision></page>"
            "</mediawiki>"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            dump_path = Path(tmpdir) / "sample.xml.bz2"
            dump_path.write_bytes(bz2.compress(xml.encode("utf-8")))

            targets = [IndexRecord(offset=0, page_id=2, title="Page B")]
            extracted, stats = extract_pages_sequential(
                dump_path=dump_path,
                targets=targets,
                max_pages_to_scan=1,
                show_progress=False,
            )

        self.assertEqual(len(extracted), 0)
        self.assertEqual(stats.scanned_pages, 1)
        self.assertTrue(stats.stopped_due_to_limit)


if __name__ == "__main__":
    unittest.main()
