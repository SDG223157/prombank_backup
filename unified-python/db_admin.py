#!/usr/bin/env python3
"""
Simple Database Admin Client
Direct MySQL connection for admin operations
"""

import os
import pymysql
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_database_url():
    """Parse DATABASE_URL to extract connection parameters"""
    
    database_url = os.getenv('DATABASE_URL', '')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not found")
        return None
    
    # Remove mysql+pymysql:// prefix
    url = database_url.replace('mysql+pymysql://', 'mysql://')
    parsed = urlparse(url)
    
    return {
        'host': parsed.hostname,
        'port': parsed.port or 3306,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/').split('?')[0],
        'charset': 'utf8mb4'
    }

def connect_to_database():
    """Create direct MySQL connection"""
    
    conn_params = parse_database_url()
    if not conn_params:
        return None
    
    try:
        # For DigitalOcean, add SSL configuration
        if 'ondigitalocean.com' in conn_params['host']:
            conn_params['ssl_disabled'] = False
            conn_params['ssl_verify_cert'] = False
            conn_params['ssl_verify_identity'] = False
            logger.info("🔒 Configured SSL for DigitalOcean database")
        
        connection = pymysql.connect(**conn_params)
        logger.info(f"✅ Connected to database: {conn_params['host']}:{conn_params['port']}")
        return connection
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None

def execute_query(connection, query):
    """Execute SQL query and return results"""
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                print(f"\n✅ Query executed successfully. Found {len(results)} rows.")
                
                if results:
                    print("\n" + "="*80)
                    print("RESULTS:")
                    print("="*80)
                    
                    # Print headers
                    if columns:
                        header = " | ".join([f"{col:>15}" for col in columns])
                        print(header)
                        print("-" * len(header))
                    
                    # Print rows
                    for row in results:
                        values = [f"{str(val):>15}" for val in row]
                        print(" | ".join(values))
                    
                    print("="*80)
                
                return results
            else:
                # For INSERT, UPDATE, DELETE
                connection.commit()
                affected = cursor.rowcount
                print(f"✅ Query executed successfully. {affected} rows affected.")
                return affected
                
    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}")
        connection.rollback()
        return None

def main():
    """Main function"""
    
    print("🔧 Database Admin Client")
    print("="*50)
    
    # Connect to database
    connection = connect_to_database()
    if not connection:
        print("❌ Failed to connect to database")
        return
    
    print("📊 Database Connection Successful!")
    print("Type SQL commands (type 'exit' to quit)")
    print("="*50)
    
    try:
        while True:
            query = input("\nSQL> ").strip()
            
            if query.lower() == 'exit':
                break
            elif query.lower() == 'help':
                print("\n📚 Common Queries:")
                print("SHOW TABLES;")
                print("SELECT * FROM users LIMIT 10;")
                print("SELECT * FROM prompts LIMIT 10;")
                print("DESCRIBE users;")
                print("SELECT COUNT(*) FROM users;")
                continue
            elif not query:
                continue
            
            execute_query(connection, query)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        connection.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    main()
