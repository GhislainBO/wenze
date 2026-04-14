"""CLI entry point to initialise the WENZE SQLite database.

Usage (from backend/ directory):
    python -m scripts.init_db
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running as a plain script too: `python scripts/init_db.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import DB_PATH, init_db  # noqa: E402


def main() -> None:
    init_db()
    print(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    main()
