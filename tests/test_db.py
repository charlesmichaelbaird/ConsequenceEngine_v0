from __future__ import annotations

import sqlite3
import unittest

from ce.db import init_db


class DbTests(unittest.TestCase):
    def test_init_db_creates_wiki_pages_table(self) -> None:
        conn = sqlite3.connect(":memory:")
        try:
            init_db(conn)
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_pages'"
            ).fetchone()
            self.assertIsNotNone(row)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
