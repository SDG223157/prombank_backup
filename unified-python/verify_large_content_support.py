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


def main() -> None:
    if not str(engine.url).startswith("mysql"):
        print(f"Skip: DATABASE_URL is not MySQL ({engine.url.drivername}).")
        return

    test_enabled = os.getenv("VERIFY_INSERT_TEST", "").strip().lower() in {"1", "true", "yes", "y"}
    test_size_kb = int(os.getenv("TEST_SIZE_KB", "200"))
    test_size_bytes = test_size_kb * 1024

    with engine.begin() as conn:
        print("## Column types (information_schema.columns)")
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
                print(
                    f"- {r.table_name}.{r.column_name}: "
                    f"data_type={r.data_type}, column_type={r.column_type}, nullable={r.is_nullable}"
                )

        print("\n## Server setting: max_allowed_packet")
        max_packet = _fetchone(conn, "SHOW VARIABLES LIKE 'max_allowed_packet'")
        if max_packet:
            val = int(max_packet[1])  # (Variable_name, Value)
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
        conn.execute(
            text(
                """
                INSERT INTO articles (
                  id, title, content, category, tags, prompt_id, user_id, word_count, char_count, metadata, created_at, updated_at
                ) VALUES (
                  :id, :title, :content, :category, CAST('[]' AS JSON), NULL, :user_id, NULL, :char_count, CAST('{}' AS JSON), NOW(3), NOW(3)
                )
                """
            ),
            {
                "id": article_id,
                "title": title,
                "content": content,
                "category": "Diagnostics",
                "user_id": user_id,
                "char_count": len(content),
            },
        )

        persisted = _fetchone(
            conn,
            "SELECT char_count, LENGTH(content) AS content_len FROM articles WHERE id=:id",
            {"id": article_id},
        )
        print(f"- Persisted: char_count={persisted.char_count}, content_len={persisted.content_len}")

        conn.execute(text("DELETE FROM articles WHERE id=:id"), {"id": article_id})
        print("✅ Insert test passed and cleaned up.")


if __name__ == "__main__":
    main()


