from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ce.config import RepoPaths
from ce.wiki import compile_title_catalog


def main() -> int:
    paths = RepoPaths.from_repo_root()
    paths.validate_required_inputs()

    total = compile_title_catalog(paths.index_path, paths.sqlite_path)
    print(
        f"Compiled {total} title entries into SQLite catalog at {paths.sqlite_path} (table: title_catalog)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
