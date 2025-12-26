#!/usr/bin/env python3
"""
One-time DB migration: expand MySQL TEXT columns to LONGTEXT for large markdown content.

Why:
- SQLAlchemy `Text` maps to MySQL TEXT (~64KB max).
- Long articles/prompts can exceed that and fail inserts (often surfacing as HTTP 500).

What this script does (MySQL only):
- ALTER TABLE prompts  MODIFY content LONGTEXT, description LONGTEXT
- ALTER TABLE articles MODIFY content LONGTEXT

Usage:
  cd prombank_backup/unified-python
  python migrate_longtext_content.py
"""

from sqlalchemy import text
from database import engine


DDL = [
    # prompts
    "ALTER TABLE prompts MODIFY content LONGTEXT NOT NULL",
    "ALTER TABLE prompts MODIFY description LONGTEXT NULL",
    # articles
    "ALTER TABLE articles MODIFY content LONGTEXT NOT NULL",
]


def main() -> None:
    url = str(engine.url)
    if not url.startswith("mysql"):
        print(f"Skip: DATABASE_URL is not MySQL ({engine.url.drivername}). No changes applied.")
        return

    print("🔧 Migrating MySQL TEXT -> LONGTEXT for prompt/article content…")

    with engine.begin() as conn:
        for stmt in DDL:
            print(f"→ {stmt}")
            conn.execute(text(stmt))

    print("✅ Migration complete.")


if __name__ == "__main__":
    main()


