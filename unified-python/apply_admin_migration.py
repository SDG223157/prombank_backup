#!/usr/bin/env python3
"""
Script to manually apply the admin role migration.
Run this if the is_admin column is missing from the users table.
Cross-database compatible (MySQL + PostgreSQL/Neon).
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prevent libpq from reading stale SSL client certs
os.environ.setdefault("PGSSLCERT", "/tmp/.postgresql/nonexistent.crt")
os.environ.setdefault("PGSSLKEY", "/tmp/.postgresql/nonexistent.key")


def get_database_url():
    """Get and clean DATABASE_URL"""
    url = os.getenv('DATABASE_URL', 'mysql+pymysql://mysql:password@localhost:3306/default')
    if "postgresql" in url:
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params.pop("channel_binding", None)
        params.setdefault("sslmode", ["require"])
        url = urlunparse(parsed._replace(query=urlencode(params, doseq=True)))
    return url


def apply_admin_migration():
    """Apply the admin role migration manually (cross-database compatible)"""

    DATABASE_URL = get_database_url()
    logger.info("Connecting to database...")

    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)

        # Check if users table exists
        inspector = inspect(engine)
        if "users" not in inspector.get_table_names():
            logger.info("⏭️  Users table not yet created, skipping migration")
            return True

        # Check if is_admin column exists
        columns = [c["name"] for c in inspector.get_columns("users")]

        with engine.connect() as conn:
            if "is_admin" in columns:
                logger.info("✅ is_admin column already exists!")
            else:
                logger.info("❌ is_admin column does not exist. Adding it...")
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT false"
                ))
                conn.commit()
                logger.info("✅ is_admin column added successfully!")

            # Set the admin user
            logger.info("Setting admin user (isky999@gmail.com)...")
            result = conn.execute(text(
                "UPDATE users SET is_admin = true WHERE email = 'isky999@gmail.com'"
            ))
            conn.commit()

            if result.rowcount > 0:
                logger.info(f"✅ Admin user updated! ({result.rowcount} rows)")
            else:
                logger.warning("⚠️  No user found with email 'isky999@gmail.com'")

            logger.info("🎉 Migration completed successfully!")
            return True

    except OperationalError as e:
        logger.error(f"❌ Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = apply_admin_migration()
    sys.exit(0 if success else 1)
