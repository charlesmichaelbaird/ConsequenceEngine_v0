from __future__ import annotations

import unittest

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from consequence_engine_v0.normalize import normalize_text


class NormalizeTests(unittest.TestCase):
    def test_normalize_text_collapses_whitespace(self) -> None:
        self.assertEqual(normalize_text(" a\n\t b   c "), "a b c")


if __name__ == "__main__":
    unittest.main()
