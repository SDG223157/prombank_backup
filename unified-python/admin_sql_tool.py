#!/usr/bin/env python3
"""
Admin SQL Tool - Execute SQL operations on the database
Usage: python admin_sql_tool.py
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://mysql:password@localhost:3306/default')

def get_engine_config():
    """Configure engine with proper SSL settings for DigitalOcean"""
    database_url = DATABASE_URL
    connect_args = {"charset": "utf8mb4"}
    
    # Check if SSL is required (DigitalOcean databases)
    if "ondigitalocean.com" in database_url:
        # DigitalOcean databases require SSL, configure it properly
        connect_args.update({
            "ssl_disabled": False,
            "ssl_verify_cert": False
        })
        print("🔒 Configured SSL for DigitalOcean database")
    
    # Remove any ssl-mode parameters from URL as PyMySQL doesn't recognize them
    if "ssl-mode=" in database_url:
        import re
        database_url = re.sub(r'[?&]ssl-mode=[^&]*', '', database_url)
        print("🔧 Removed ssl-mode parameter from DATABASE_URL")
    
    return database_url, connect_args

# Get proper engine configuration
engine_url, engine_connect_args = get_engine_config()

# Create SQLAlchemy engine
engine = create_engine(
    engine_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
    connect_args=engine_connect_args
)

from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_sql_query(query, fetch_results=True):
    """Execute a SQL query and return results"""
    
    db = SessionLocal()
    try:
        logger.info(f"🔍 Executing SQL: {query[:100]}...")
        
        result = db.execute(text(query))
        
        if fetch_results:
            rows = result.fetchall()
            columns = result.keys() if hasattr(result, 'keys') else []
            
            logger.info(f"✅ Query executed successfully. Found {len(rows)} rows.")
            
            # Print results in a formatted way
            if rows:
                print("\n" + "="*80)
                print("QUERY RESULTS:")
                print("="*80)
                
                # Print headers
                if columns:
                    header = " | ".join([f"{col:>15}" for col in columns])
                    print(header)
                    print("-" * len(header))
                
                # Print rows
                for row in rows:
                    if hasattr(row, '_asdict'):
                        # Named tuple (SQLAlchemy result)
                        values = [f"{str(val):>15}" for val in row]
                    else:
                        # Regular tuple
                        values = [f"{str(val):>15}" for val in row]
                    print(" | ".join(values))
                
                print("="*80)
            else:
                print("✅ Query executed successfully (no results returned)")
            
            return rows
        else:
            # For INSERT, UPDATE, DELETE operations
            db.commit()
            affected_rows = result.rowcount if hasattr(result, 'rowcount') else 0
            logger.info(f"✅ Query executed successfully. {affected_rows} rows affected.")
            return affected_rows
            
    except Exception as e:
        logger.error(f"❌ Error executing SQL: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def interactive_sql_shell():
    """Interactive SQL shell for admin operations"""
    
    print("🔧 Admin SQL Tool - Interactive Mode")
    print("="*50)
    print("Enter SQL commands (type 'exit' to quit, 'help' for commands)")
    print("="*50)
    
    while True:
        try:
            query = input("\nSQL> ").strip()
            
            if query.lower() == 'exit':
                print("👋 Goodbye!")
                break
            elif query.lower() == 'help':
                print_help()
                continue
            elif not query:
                continue
            
            # Determine if this is a SELECT query
            is_select = query.upper().startswith('SELECT') or query.upper().startswith('SHOW') or query.upper().startswith('DESCRIBE')
            
            execute_sql_query(query, fetch_results=is_select)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def print_help():
    """Print help information"""
    print("\n📚 Available Commands:")
    print("="*50)
    print("SELECT * FROM users;                    # View all users")
    print("SELECT * FROM prompts LIMIT 10;        # View prompts")
    print("SELECT * FROM articles LIMIT 10;       # View articles")
    print("SELECT * FROM tokens;                   # View API tokens")
    print("SHOW TABLES;                           # List all tables")
    print("DESCRIBE users;                        # Show table structure")
    print("SELECT COUNT(*) FROM users;            # Count records")
    print("")
    print("UPDATE users SET is_admin=1 WHERE email='admin@example.com';")
    print("DELETE FROM prompts WHERE id='some-id';")
    print("")
    print("exit                                   # Quit the tool")
    print("help                                   # Show this help")
    print("="*50)

def quick_queries():
    """Execute common admin queries"""
    
    print("🔍 Quick Database Overview")
    print("="*50)
    
    queries = [
        ("📊 Total Users", "SELECT COUNT(*) as total_users FROM users"),
        ("👑 Admin Users", "SELECT email, first_name, last_name, is_admin FROM users WHERE is_admin = 1"),
        ("📝 Total Prompts", "SELECT COUNT(*) as total_prompts FROM prompts"),
        ("📄 Total Articles", "SELECT COUNT(*) as total_articles FROM articles"),
        ("🔑 Total API Tokens", "SELECT COUNT(*) as total_tokens FROM tokens"),
        ("📋 Table List", "SHOW TABLES"),
    ]
    
    for description, query in queries:
        print(f"\n{description}:")
        print("-" * 30)
        execute_sql_query(query)

def main():
    """Main function"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'overview':
            quick_queries()
        elif sys.argv[1] == 'interactive':
            interactive_sql_shell()
        else:
            # Execute single query from command line
            query = ' '.join(sys.argv[1:])
            is_select = query.upper().startswith('SELECT') or query.upper().startswith('SHOW')
            execute_sql_query(query, fetch_results=is_select)
    else:
        print("🔧 Admin SQL Tool")
        print("="*50)
        print("Usage options:")
        print("  python admin_sql_tool.py overview           # Quick database overview")
        print("  python admin_sql_tool.py interactive        # Interactive SQL shell")
        print("  python admin_sql_tool.py 'SELECT * FROM users LIMIT 5'  # Execute single query")
        print("")
        print("Examples:")
        print("  python admin_sql_tool.py overview")
        print("  python admin_sql_tool.py interactive")
        print("  python admin_sql_tool.py 'SHOW TABLES'")
        print("="*50)

if __name__ == "__main__":
    main()
