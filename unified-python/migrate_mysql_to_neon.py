#!/usr/bin/env python3
"""
Migrate data from old DigitalOcean MySQL to new Neon PostgreSQL.
Run this inside the Coolify terminal where both databases are accessible.
"""

import os
import sys
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

# Old MySQL connection - set via OLD_DATABASE_URL env var
OLD_MYSQL_URL = os.getenv("OLD_DATABASE_URL")

if not OLD_MYSQL_URL:
    print("❌ OLD_DATABASE_URL not set. Set it to the old MySQL connection string.")
    print("   Example: OLD_DATABASE_URL='mysql+pymysql://user:pass@host:port/db?charset=utf8mb4'")
    sys.exit(1)

# New Neon PostgreSQL (from env)
NEW_PG_URL = os.getenv("DATABASE_URL")

if not NEW_PG_URL:
    print("❌ DATABASE_URL not set. Run this inside the Coolify container.")
    sys.exit(1)


def migrate():
    from sqlalchemy import create_engine, text, inspect
    import ssl as _ssl

    # Connect to old MySQL
    logger.info("🔌 Connecting to old MySQL...")
    try:
        mysql_ctx = _ssl.SSLContext(_ssl.PROTOCOL_TLS_CLIENT)
        mysql_ctx.check_hostname = False
        mysql_ctx.verify_mode = _ssl.CERT_NONE
        old_engine = create_engine(
            OLD_MYSQL_URL,
            connect_args={"ssl": mysql_ctx},
            pool_pre_ping=True,
        )
        with old_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Old MySQL connected!")
    except Exception as e:
        logger.error(f"❌ Cannot connect to old MySQL: {e}")
        sys.exit(1)

    # Connect to new Neon PostgreSQL
    logger.info("🔌 Connecting to new Neon PostgreSQL...")
    # Clean the URL
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    parsed = urlparse(NEW_PG_URL)
    params = parse_qs(parsed.query)
    params.pop("channel_binding", None)
    params.setdefault("sslmode", ["require"])
    clean_pg_url = urlunparse(parsed._replace(query=urlencode(params, doseq=True)))

    os.environ["PGSSLCERT"] = "/tmp/.postgresql/nonexistent.crt"
    os.environ["PGSSLKEY"] = "/tmp/.postgresql/nonexistent.key"

    new_engine = create_engine(clean_pg_url, pool_pre_ping=True)
    try:
        with new_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ New Neon PostgreSQL connected!")
    except Exception as e:
        logger.error(f"❌ Cannot connect to new Neon: {e}")
        sys.exit(1)

    # Ensure tables exist on Neon
    logger.info("📦 Creating tables on Neon...")
    from database import Base
    Base.metadata.create_all(bind=new_engine)
    logger.info("✅ Tables ready")

    # Tables to migrate in order (respecting dependencies)
    tables = ["users", "prompts", "tokens", "articles", "skills"]

    with old_engine.connect() as old_conn:
        # Check which tables exist in MySQL
        inspector = inspect(old_engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"📊 MySQL tables: {existing_tables}")

        for table in tables:
            if table not in existing_tables:
                logger.info(f"⏭️  Table '{table}' not in MySQL, skipping")
                continue

            # Read all rows from MySQL
            result = old_conn.execute(text(f"SELECT * FROM `{table}`"))
            columns = list(result.keys())
            rows = result.fetchall()
            logger.info(f"📥 {table}: {len(rows)} rows to migrate")

            if not rows:
                continue

            # Insert into Neon
            with new_engine.begin() as new_conn:
                # Clear existing data in Neon table first
                new_conn.execute(text(f'DELETE FROM "{table}"'))

                for i, row in enumerate(rows):
                    row_dict = {}
                    for col_idx, col_name in enumerate(columns):
                        val = row[col_idx]
                        # Handle bytes
                        if isinstance(val, bytes):
                            val = val.decode('utf-8', errors='replace')
                        # Serialize dict/list to JSON string for psycopg2
                        if isinstance(val, (dict, list)):
                            val = json.dumps(val, default=str)
                        # Handle JSON string from MySQL - parse then re-dump
                        if isinstance(val, str) and val.startswith(('[', '{')):
                            try:
                                parsed = json.loads(val)
                                val = json.dumps(parsed, default=str)
                            except (json.JSONDecodeError, TypeError):
                                pass
                        row_dict[col_name] = val

                    # Build INSERT
                    col_names = ', '.join(f'"{c}"' for c in row_dict.keys())
                    placeholders = ', '.join(f':{c}' for c in row_dict.keys())
                    sql = f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders})'

                    try:
                        new_conn.execute(text(sql), row_dict)
                    except Exception as e:
                        logger.warning(f"  ⚠️  Row {i} in {table} failed: {e}")
                        continue

                logger.info(f"✅ {table}: {len(rows)} rows migrated!")

    logger.info("🎉 Migration completed!")

    # Summary
    with new_engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                count = result.scalar()
                logger.info(f"  📊 {table}: {count} rows in Neon")
            except Exception:
                pass


if __name__ == "__main__":
    migrate()
