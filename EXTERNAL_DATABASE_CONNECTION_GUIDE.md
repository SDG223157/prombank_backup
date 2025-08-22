# External Database Connection Guide

## Overview

This guide explains how to connect external databases to your Prompt House Premium application, including configuration, troubleshooting, and best practices for various database providers.

## Supported Database Types

### ✅ Fully Supported
- **MySQL/MariaDB** - Primary support with full feature compatibility
- **DigitalOcean Managed MySQL** - Optimized configuration with SSL support
- **AWS RDS MySQL** - Compatible with SSL and security groups
- **Google Cloud SQL MySQL** - Supported with proper SSL configuration
- **Azure Database for MySQL** - Compatible with SSL requirements

### ⚠️ Experimental Support
- **PostgreSQL** - Requires code modifications
- **SQLite** - Local development only
- **SQL Server** - Requires additional drivers

---

## Configuration Steps

### Step 1: Prepare Your External Database

#### For DigitalOcean Managed MySQL:
1. **Create Database Cluster** in DigitalOcean control panel
2. **Note connection details**:
   - Host: `db-mysql-xxx.xxx.db.ondigitalocean.com`
   - Port: `25060`
   - Username: `doadmin`
   - Password: Generated password
   - Database: `defaultdb`
   - SSL: Required

#### For AWS RDS MySQL:
1. **Create RDS MySQL instance**
2. **Configure security groups** to allow application access
3. **Enable SSL** if required
4. **Note connection details**

#### For Other Providers:
1. **Create MySQL database instance**
2. **Configure firewall/security** to allow connections
3. **Obtain connection credentials**
4. **Check SSL requirements**

### Step 2: Format Database URL

Transform your connection details into the correct DATABASE_URL format:

#### Basic Format:
```
mysql+pymysql://username:password@host:port/database
```

#### With SSL (DigitalOcean):
```
mysql+pymysql://username:password@host:port/database?ssl-mode=REQUIRED
```

#### Example Configurations:

**DigitalOcean:**
```bash
DATABASE_URL=mysql+pymysql://doadmin:YOUR_PASSWORD@your-cluster.db.ondigitalocean.com:25060/defaultdb
```

**AWS RDS:**
```bash
DATABASE_URL=mysql+pymysql://admin:mypassword@mydb.abc123.us-east-1.rds.amazonaws.com:3306/prombank
```

**Google Cloud SQL:**
```bash
DATABASE_URL=mysql+pymysql://root:mypassword@34.123.45.67:3306/prombank
```

**Local MySQL:**
```bash
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/prombank
```

### Step 3: Update Environment Configuration

#### Complete Environment Variables:
```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@host:port/database

# Application URLs
ALLOWED_ORIGINS=https://yourdomain.com
BACKEND_URL=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com/api

# Authentication
JWT_SECRET=your-jwt-secret-base64-encoded
SESSION_SECRET=your-session-secret-base64-encoded

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-google-client-secret
GOOGLE_CALLBACK_URL=https://yourdomain.com/api/auth/google/callback
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback

# Application Settings
PORT=3000
TRUST_PROXY=true
```

---

## SSL Configuration

### Automatic SSL Detection

The application automatically detects and configures SSL for supported providers:

```python
# In database.py
def get_engine_config():
    """Configure engine with proper SSL settings"""
    database_url = DATABASE_URL
    connect_args = {"charset": "utf8mb4"}
    
    # Auto-detect DigitalOcean and configure SSL
    if "ondigitalocean.com" in database_url:
        connect_args.update({
            "ssl_disabled": False,
            "ssl_verify_cert": False
        })
        print("🔒 Configured SSL for DigitalOcean database")
    
    # Remove problematic ssl-mode parameters
    if "ssl-mode=" in database_url:
        import re
        database_url = re.sub(r'[?&]ssl-mode=[^&]*', '', database_url)
        print("🔧 Removed ssl-mode parameter from DATABASE_URL")
    
    return database_url, connect_args
```

### Manual SSL Configuration

For custom SSL requirements, modify `unified-python/database.py`:

```python
# Custom SSL configuration
if "your-custom-host.com" in database_url:
    connect_args.update({
        "ssl_disabled": False,
        "ssl_verify_cert": True,  # Set to False if using self-signed
        "ssl_ca": "/path/to/ca-cert.pem",  # Optional CA certificate
        "ssl_cert": "/path/to/client-cert.pem",  # Optional client cert
        "ssl_key": "/path/to/client-key.pem"   # Optional client key
    })
```

---

## Database Migration

### Automatic Table Creation

The application automatically creates required tables on startup:

```python
# Tables created automatically:
- users          # User accounts and authentication
- prompts        # AI prompts and templates  
- articles       # AI-generated articles
- tokens         # API access tokens
```

### Manual Migration (If Needed)

If automatic migration fails, run manually:

```bash
# Using Python script
cd unified-python
python apply_admin_migration.py

# Or via SQL
mysql -h your-host -P port -u username -p database_name < migration.sql
```

---

## Connection Testing

### Method 1: Application Health Check

```bash
curl https://yourdomain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "backend": "python-fastapi",
  "timestamp": "2025-01-XX",
  "version": "1.0.0"
}
```

### Method 2: Admin Diagnostic

```bash
curl https://yourdomain.com/api/admin/diagnostic
```

### Method 3: Python Test Script

```python
#!/usr/bin/env python3
"""
Database Connection Test Script
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = "your-database-url-here"

def test_connection():
    try:
        # Configure for DigitalOcean if needed
        connect_args = {"charset": "utf8mb4"}
        if "ondigitalocean.com" in DATABASE_URL:
            connect_args.update({
                "ssl_disabled": False,
                "ssl_verify_cert": False
            })
        
        engine = create_engine(DATABASE_URL, connect_args=connect_args)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test, NOW() as timestamp"))
            row = result.fetchone()
            print(f"✅ Database connection successful!")
            print(f"Test result: {row[0]}")
            print(f"Database time: {row[1]}")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. SSL Connection Errors

**Error**: `Connection.__init__() got an unexpected keyword argument 'ssl-mode'`

**Solution**: Remove `?ssl-mode=REQUIRED` from DATABASE_URL:
```bash
# Wrong
DATABASE_URL=mysql+pymysql://user:pass@host:port/db?ssl-mode=REQUIRED

# Correct  
DATABASE_URL=mysql+pymysql://user:pass@host:port/db
```

#### 2. Connection Timeout

**Error**: `Can't connect to MySQL server (timed out)`

**Solutions**:
- Check firewall settings on database server
- Verify host and port are correct
- Ensure application server can reach database server
- Check security groups (AWS) or firewall rules

#### 3. Authentication Failed

**Error**: `Access denied for user`

**Solutions**:
- Verify username and password are correct
- Check user permissions on database
- Ensure user can connect from application server IP
- Verify database name exists

#### 4. SSL Certificate Issues

**Error**: SSL certificate verification failed

**Solutions**:
```python
# Disable SSL verification (not recommended for production)
connect_args.update({
    "ssl_verify_cert": False,
    "ssl_verify_identity": False
})
```

#### 5. Character Encoding Issues

**Error**: Incorrect string value or encoding errors

**Solution**: Ensure UTF8MB4 charset:
```python
connect_args = {"charset": "utf8mb4"}
```

### Debug Connection Issues

#### Enable SQL Logging:
```python
# In database.py, change:
engine = create_engine(
    engine_url,
    echo=True,  # Enable SQL logging
    connect_args=engine_connect_args
)
```

#### Test Network Connectivity:
```bash
# Test if port is reachable
nc -zv your-database-host 3306

# Test with telnet
telnet your-database-host 3306
```

---

## Security Best Practices

### 1. Use Environment Variables
Never hardcode database credentials in code:

```bash
# ✅ Good - Use environment variables
DATABASE_URL=mysql+pymysql://user:pass@host:port/db

# ❌ Bad - Hardcoded in code
DATABASE_URL = "mysql+pymysql://user:password@host:port/db"
```

### 2. Enable SSL
Always use SSL for production databases:

```bash
# Enable SSL in connection string or configure in connect_args
ssl_disabled=False
ssl_verify_cert=True  # Set to False only if using self-signed certificates
```

### 3. Restrict Database User Permissions
Create dedicated application user with minimal required permissions:

```sql
-- Create application-specific user
CREATE USER 'prombank_app'@'%' IDENTIFIED BY 'secure_password';

-- Grant only required permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON prombank.* TO 'prombank_app'@'%';
GRANT CREATE, ALTER, INDEX ON prombank.* TO 'prombank_app'@'%';

-- Do not grant DROP, SUPER, or other dangerous permissions
FLUSH PRIVILEGES;
```

### 4. Use Connection Pooling
Configure appropriate connection pool settings:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Number of permanent connections
    max_overflow=20,       # Additional connections when needed
    pool_pre_ping=True,    # Validate connections before use
    pool_recycle=3600      # Recycle connections every hour
)
```

---

## Provider-Specific Configurations

### DigitalOcean Managed MySQL

```bash
# Environment configuration
DATABASE_URL=mysql+pymysql://doadmin:your-password@your-host.db.ondigitalocean.com:25060/defaultdb

# Features:
✅ Automatic SSL configuration
✅ High availability
✅ Automated backups
✅ Monitoring included
✅ Automatic updates
```

### AWS RDS MySQL

```bash
# Environment configuration  
DATABASE_URL=mysql+pymysql://admin:password@mydb.abc123.us-east-1.rds.amazonaws.com:3306/prombank

# Additional considerations:
- Configure VPC security groups
- Enable SSL if required
- Set up automated backups
- Configure monitoring with CloudWatch
```

### Google Cloud SQL

```bash
# Environment configuration
DATABASE_URL=mysql+pymysql://root:password@34.123.45.67:3306/prombank

# Additional considerations:
- Configure authorized networks
- Enable SSL certificates
- Set up Cloud SQL Proxy for secure connections
- Configure automated backups
```

### Local Development

```bash
# Docker MySQL for development
docker run --name mysql-dev \
  -e MYSQL_ROOT_PASSWORD=devpassword \
  -e MYSQL_DATABASE=prombank \
  -p 3306:3306 \
  -d mysql:8.0

# Environment configuration
DATABASE_URL=mysql+pymysql://root:devpassword@localhost:3306/prombank
```

---

## Performance Optimization

### 1. Connection Pool Tuning

```python
# Optimize for your workload
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Increase for high concurrency
    max_overflow=30,        # Allow burst connections
    pool_pre_ping=True,     # Validate connections
    pool_recycle=7200       # 2 hours for long-running apps
)
```

### 2. Query Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_prompts_user_id ON prompts(user_id);
CREATE INDEX idx_articles_created_at ON articles(created_at);
CREATE INDEX idx_tokens_user_id ON tokens(user_id);
```

### 3. Database Monitoring

Monitor these metrics:
- Connection pool usage
- Query execution time
- Database size growth
- Index usage statistics

---

## Migration from Local to External Database

### Step 1: Export Existing Data

```bash
# Export from local database
mysqldump -h localhost -u root -p prombank > backup.sql

# Or using Python script
python export_data.py > data_backup.json
```

### Step 2: Import to External Database

```bash
# Import to external database
mysql -h external-host -P port -u username -p database_name < backup.sql

# Or using Python script
python import_data.py data_backup.json
```

### Step 3: Update Configuration

```bash
# Update DATABASE_URL to point to external database
DATABASE_URL=mysql+pymysql://user:pass@external-host:port/database
```

### Step 4: Test and Verify

```bash
# Test application health
curl https://yourdomain.com/health

# Verify data integrity
curl https://yourdomain.com/api/admin/diagnostic
```

---

## Database Administration

### Admin SQL Interface

Once deployed, your application includes a built-in SQL interface:

#### Access Methods:

**1. Admin Dashboard:**
- Go to https://yourdomain.com/admin
- Login as admin
- Click "SQL Query" tab
- Use quick queries or custom SQL

**2. API Endpoints:**
```bash
# Execute custom SQL
curl -X POST "https://yourdomain.com/api/admin/execute-sql" \
  -H "Content-Type: application/json" \
  -d '{"query": "SHOW TABLES;"}'

# Get database space analysis
curl -X GET "https://yourdomain.com/api/admin/database/space-analysis"

# Get table information
curl -X GET "https://yourdomain.com/api/admin/database/tables-info"
```

**3. Browser Developer Tools:**
```javascript
// Execute any SQL query
fetch('/api/admin/execute-sql', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  credentials: 'include',
  body: JSON.stringify({
    query: 'SELECT table_schema AS "Database", ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "Size (MB)" FROM information_schema.TABLES GROUP BY table_schema;'
  })
})
.then(r => r.json())
.then(d => console.table(d.rows));
```

### Common Admin Queries

#### Database Space Analysis:
```sql
-- Total database space by schema
SELECT table_schema AS "Database", 
ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "Size (MB)" 
FROM information_schema.TABLES 
GROUP BY table_schema;

-- Table space usage
SELECT table_name, 
ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size (MB)",
table_rows 
FROM information_schema.tables 
WHERE table_schema = DATABASE() 
ORDER BY (data_length + index_length) DESC;
```

#### User Management:
```sql
-- View all users
SELECT email, first_name, last_name, is_admin, auth_provider, created_at 
FROM users 
ORDER BY created_at DESC;

-- Admin users only
SELECT * FROM users WHERE is_admin = 1;

-- User statistics
SELECT 
  COUNT(*) as total_users,
  SUM(is_admin) as admin_users,
  SUM(CASE WHEN auth_provider = 'google' THEN 1 ELSE 0 END) as google_users,
  SUM(CASE WHEN auth_provider = 'local' THEN 1 ELSE 0 END) as local_users
FROM users;
```

#### Content Analysis:
```sql
-- Content statistics
SELECT 
  (SELECT COUNT(*) FROM users) as Users,
  (SELECT COUNT(*) FROM prompts) as Prompts,
  (SELECT COUNT(*) FROM articles) as Articles,
  (SELECT COUNT(*) FROM tokens) as Tokens;

-- Recent activity
SELECT 'prompts' as type, title as name, created_at 
FROM prompts 
ORDER BY created_at DESC LIMIT 10
UNION ALL
SELECT 'articles' as type, title as name, created_at 
FROM articles 
ORDER BY created_at DESC LIMIT 10
ORDER BY created_at DESC;
```

---

## Backup and Recovery

### Automated Backups

#### DigitalOcean:
- **Automatic daily backups** included
- **Point-in-time recovery** available
- **Backup retention** configurable

#### AWS RDS:
```bash
# Enable automated backups
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"
```

#### Manual Backup:
```bash
# Create backup
mysqldump -h host -P port -u user -p database > backup_$(date +%Y%m%d).sql

# Restore backup
mysql -h host -P port -u user -p database < backup_20250122.sql
```

### Application-Level Backup

```python
#!/usr/bin/env python3
"""
Application Data Backup Script
"""
import json
from database import SessionLocal, User, Prompt, Article, Token

def backup_application_data():
    db = SessionLocal()
    try:
        backup_data = {
            "users": [user_to_dict(user) for user in db.query(User).all()],
            "prompts": [prompt_to_dict(prompt) for prompt in db.query(Prompt).all()],
            "articles": [article_to_dict(article) for article in db.query(Article).all()],
            "tokens": [token_to_dict(token) for token in db.query(Token).all()],
            "backup_timestamp": datetime.utcnow().isoformat()
        }
        
        with open(f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
            
        print("✅ Backup completed successfully")
        
    finally:
        db.close()

if __name__ == "__main__":
    backup_application_data()
```

---

## Monitoring and Maintenance

### Database Health Monitoring

#### Key Metrics to Track:
- **Connection count** - Monitor active connections
- **Query performance** - Slow query log analysis  
- **Database size** - Growth rate monitoring
- **Index usage** - Optimize unused indexes
- **Error rates** - Connection failures and timeouts

#### Monitoring Queries:
```sql
-- Connection information
SHOW PROCESSLIST;

-- Database size growth
SELECT 
  table_schema,
  ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.TABLES 
GROUP BY table_schema;

-- Table growth analysis
SELECT 
  table_name,
  table_rows,
  ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)',
  ROUND((data_length / 1024 / 1024), 2) AS 'Data (MB)',
  ROUND((index_length / 1024 / 1024), 2) AS 'Index (MB)'
FROM information_schema.tables 
WHERE table_schema = DATABASE()
ORDER BY (data_length + index_length) DESC;
```

### Performance Optimization

#### Index Optimization:
```sql
-- Check index usage
SELECT 
  TABLE_NAME,
  INDEX_NAME,
  COLUMN_NAME,
  CARDINALITY
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME, INDEX_NAME;

-- Identify missing indexes
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';
```

#### Query Performance:
```sql
-- Enable slow query log (if admin access)
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM prompts WHERE user_id = 'some-id';
```

---

## Environment-Specific Configurations

### Development Environment

```bash
# Local development with Docker
DATABASE_URL=mysql+pymysql://root:devpassword@localhost:3306/prombank_dev
NODE_ENV=development
DEBUG=true
```

### Staging Environment

```bash
# Staging with managed database
DATABASE_URL=mysql+pymysql://staging_user:password@staging-db.example.com:3306/prombank_staging
NODE_ENV=staging
TRUST_PROXY=true
```

### Production Environment

```bash
# Production with external managed database
DATABASE_URL=mysql+pymysql://prod_user:secure_password@prod-db.example.com:3306/prombank
NODE_ENV=production
TRUST_PROXY=true

# Additional production settings
DATABASE_RETRY_ATTEMPTS=12
DATABASE_RETRY_DELAY=5000
DB_CONNECTION_TIMEOUT=60000
```

---

## Quick Reference

### Essential Commands

```bash
# Test database connection
curl https://yourdomain.com/health

# Get database overview
curl https://yourdomain.com/api/admin/diagnostic

# Show all tables (via browser console)
fetch('/api/admin/execute-sql', {method: 'POST', headers: {'Content-Type': 'application/json'}, credentials: 'include', body: JSON.stringify({query: 'SHOW TABLES;'})}).then(r => r.json()).then(d => console.table(d.rows));

# Database space analysis (via browser console)
fetch('/api/admin/execute-sql', {method: 'POST', headers: {'Content-Type': 'application/json'}, credentials: 'include', body: JSON.stringify({query: 'SELECT table_schema AS "Database", ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "Size (MB)" FROM information_schema.TABLES GROUP BY table_schema;'})}).then(r => r.json()).then(d => console.table(d.rows));
```

### Database URL Examples

```bash
# DigitalOcean
DATABASE_URL=mysql+pymysql://doadmin:password@host.db.ondigitalocean.com:25060/defaultdb

# AWS RDS
DATABASE_URL=mysql+pymysql://admin:password@mydb.region.rds.amazonaws.com:3306/prombank

# Google Cloud SQL
DATABASE_URL=mysql+pymysql://root:password@ip-address:3306/prombank

# Local Docker
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/prombank
```

---

## Support and Resources

### Getting Help

1. **Application Health Check**: https://yourdomain.com/health
2. **Admin Diagnostic**: https://yourdomain.com/api/admin/diagnostic  
3. **Database Logs**: Check application logs for connection errors
4. **Provider Documentation**: Consult your database provider's connection guides

### Useful Resources

- **MySQL Documentation**: https://dev.mysql.com/doc/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **DigitalOcean Database Docs**: https://docs.digitalocean.com/products/databases/
- **AWS RDS Documentation**: https://docs.aws.amazon.com/rds/

---

*This guide provides comprehensive instructions for connecting external databases to your Prompt House Premium application. For specific issues or advanced configurations, consult your database provider's documentation or contact support.*
