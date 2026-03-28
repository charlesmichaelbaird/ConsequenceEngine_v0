from __future__ import annotations

import unittest

from ce.normalize import normalize_text


class NormalizeTests(unittest.TestCase):
    def test_normalize_text_collapses_whitespace(self) -> None:
        self.assertEqual(normalize_text(" a\n\t b   c "), "a b c")


if __name__ == "__main__":
    unittest.main()
