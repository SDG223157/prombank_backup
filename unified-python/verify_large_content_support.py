#!/usr/bin/env python3
"""
Verify end-to-end support for large markdown content in the live MySQL DB.

This verifies the *remaining* piece after the code changes:
the actual database schema in production must have LONGTEXT, and the server must allow
packets big enough for the payload (max_allowed_packet).

What it checks:
1) Column types for `prompts.content`, `prompts.description`, `articles.content`
2) MySQL `max_allowed_packet` (practical upper bound for single INSERT payload)
3) Optional: performs a safe INSERT/DELETE test with a large payload (default 200KB)

Usage (from repo root):
  cd prombank_backup/unified-python
  python verify_large_content_support.py

Optional insert test:
  VERIFY_INSERT_TEST=1 TEST_SIZE_KB=200 python verify_large_content_support.py
"""

import os
import uuid

from sqlalchemy import text

from database import engine


def _fetchone(conn, sql: str, params: dict | None = None):
    return conn.execute(text(sql), params or {}).fetchone()


def _get_table_columns(conn, table_name: str) -> dict:
    """Return column metadata for a table in the current DB schema."""
    rows = conn.execute(
        text(
            """
            SELECT column_name, is_nullable, column_default, extra, data_type
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = :table_name
            """
        ),
        {"table_name": table_name},
    ).fetchall()
    return {
        r[0]: {
            "is_nullable": r[1],
            "column_default": r[2],
            "extra": r[3],
            "data_type": r[4],
        }
        for r in rows
    }


def _add_insert_col(insert_cols, insert_vals, params, col: str, expr: str, param_key: str | None = None, param_val=None):
    insert_cols.append(f"`{col}`")
    insert_vals.append(expr)
    if param_key is not None:
        params[param_key] = param_val


def _row_get(row, key: str, index: int | None = None):
    """Robust row accessor across SQLAlchemy versions / row implementations.

    Prefer tuple positional access when an index is provided.
    Avoid fragile attribute access (which breaks in some SQLAlchemy configs).
    """
    if row is None:
        return None
    if index is not None:
        return row[index]
    mapping = getattr(row, "_mapping", None)
    if mapping is not None and key in mapping:
        return mapping[key]
    if isinstance(row, dict) and key in row:
        return row[key]
    raise KeyError(f"Row does not contain key '{key}' and no index was provided.")


def main() -> None:
    if not str(engine.url).startswith("mysql"):
        print(f"Skip: DATABASE_URL is not MySQL ({engine.url.drivername}).")
        return

    test_enabled = os.getenv("VERIFY_INSERT_TEST", "").strip().lower() in {"1", "true", "yes", "y"}
    test_size_kb = int(os.getenv("TEST_SIZE_KB", "200"))
    test_size_bytes = test_size_kb * 1024

    with engine.begin() as conn:
        print("## Column types (information_schema.columns)")
        # Keep rows positional for maximum compatibility across SQLAlchemy environments.
        rows = conn.execute(
            text(
                """
                SELECT table_name, column_name, data_type, column_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND (
                    (table_name = 'prompts'  AND column_name IN ('content','description'))
                    OR
                    (table_name = 'articles' AND column_name IN ('content'))
                  )
                ORDER BY table_name, column_name
                """
            )
        ).fetchall()

        if not rows:
            print("⚠️  No matching columns found (are tables created in this schema?).")
        else:
            for r in rows:
                # (table_name, column_name, data_type, column_type, is_nullable)
                print(f"- {r[0]}.{r[1]}: data_type={r[2]}, column_type={r[3]}, nullable={r[4]}")

        print("\n## Server setting: max_allowed_packet")
        max_packet = _fetchone(conn, "SHOW VARIABLES LIKE 'max_allowed_packet'")
        if max_packet:
            # row format is often (Variable_name, Value)
            val = int(max_packet[1])
            print(f"- max_allowed_packet: {val} bytes (~{val/1024/1024:.2f} MB)")
        else:
            print("- Could not read max_allowed_packet")

        print("\n## Insert test")
        if not test_enabled:
            print(f"- Skipped. Set VERIFY_INSERT_TEST=1 to run a {test_size_kb}KB insert test.")
            return

        # Need a valid user_id FK.
        user = _fetchone(conn, "SELECT id FROM users ORDER BY created_at DESC LIMIT 1")
        if not user:
            print("❌ No users found. Cannot run insert test (articles.user_id is required).")
            return
        user_id = user[0]

        article_id = str(uuid.uuid4())
        title = f"Large content verification test ({test_size_kb}KB)"
        content = "A" * test_size_bytes

        print(f"- Inserting article id={article_id} (user_id={user_id}) bytes={len(content)}")

        articles_cols = _get_table_columns(conn, "articles")

        insert_cols: list[str] = []
        insert_vals: list[str] = []
        params: dict = {}

        # Required
        _add_insert_col(insert_cols, insert_vals, params, "id", ":id", "id", article_id)
        _add_insert_col(insert_cols, insert_vals, params, "title", ":title", "title", title)
        _add_insert_col(insert_cols, insert_vals, params, "content", ":content", "content", content)
        _add_insert_col(insert_cols, insert_vals, params, "user_id", ":user_id", "user_id", user_id)

        # Optional common
        if "category" in articles_cols:
            _add_insert_col(insert_cols, insert_vals, params, "category", ":category", "category", "Diagnostics")
        if "tags" in articles_cols:
            _add_insert_col(insert_cols, insert_vals, params, "tags", "CAST(:tags AS JSON)", "tags", "[]")

        # Optional prompt references
        if "prompt_id" in articles_cols:
            _add_insert_col(insert_cols, insert_vals, params, "prompt_id", "NULL")
        if "prompt_title" in articles_cols:
            _add_insert_col(insert_cols, insert_vals, params, "prompt_title", "NULL")

        # Counts
        if "char_count" in articles_cols:
            _add_insert_col(insert_cols, insert_vals, params, "char_count", ":char_count", "char_count", len(content))
        if "word_count" in articles_cols:
            _add_insert_col(insert_cols, insert_vals, params, "word_count", "NULL")

        # Metadata column name differs between schemas
        if "article_metadata" in articles_cols:
            _add_insert_col(insert_cols, insert_vals, params, "article_metadata", "CAST(:meta AS JSON)", "meta", "{}")
        elif "metadata" in articles_cols:
            _add_insert_col(insert_cols, insert_vals, params, "metadata", "CAST(:meta AS JSON)", "meta", "{}")

        # Timestamps: insert only if NOT NULL and no default
        for ts_col in ("created_at", "updated_at"):
            if ts_col in articles_cols:
                c = articles_cols[ts_col]
                needs_value = (c["is_nullable"] == "NO" and c["column_default"] is None)
                if needs_value:
                    _add_insert_col(insert_cols, insert_vals, params, ts_col, "NOW(3)")

        sql = f"INSERT INTO articles ({', '.join(insert_cols)}) VALUES ({', '.join(insert_vals)})"
        conn.execute(text(sql), params)

        persisted = _fetchone(
            conn,
            "SELECT char_count, LENGTH(content) AS content_len FROM articles WHERE id=:id",
            {"id": article_id},
        )
        print(f"- Persisted: char_count={persisted[0]}, content_len={persisted[1]}")

        conn.execute(text("DELETE FROM articles WHERE id=:id"), {"id": article_id})
        print("✅ Insert test passed and cleaned up.")


if __name__ == "__main__":
    main()


