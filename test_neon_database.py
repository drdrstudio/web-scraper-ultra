#!/usr/bin/env python3
"""
Test Neon Database Connection and Setup
"""

import os
import sys
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.database')

def test_connection():
    """Test basic database connection"""
    print("1. Testing Neon database connection...")
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return None
    
    print(f"   Connection string: {database_url[:50]}...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"   ✅ Connected successfully!")
        print(f"   Database version: {version[0][:50]}...")
        
        cursor.close()
        return conn
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return None

def create_tables(conn):
    """Create necessary tables"""
    print("\n2. Creating tables...")
    
    try:
        cursor = conn.cursor()
        
        # Create scraped_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                url TEXT NOT NULL,
                method VARCHAR(50),
                proxy_info TEXT,
                data TEXT,
                destination VARCHAR(50),
                job_id VARCHAR(100)
            );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scraped_data_timestamp ON scraped_data(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scraped_data_url ON scraped_data(url);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scraped_data_job_id ON scraped_data(job_id);")
        
        # Create recipes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                config JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                tags TEXT[]
            );
        """)
        
        # Create jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_jobs (
                id VARCHAR(100) PRIMARY KEY,
                url TEXT,
                status VARCHAR(50),
                strategy VARCHAR(50),
                output_format VARCHAR(50),
                proxy_used TEXT,
                result JSONB,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );
        """)
        
        # Create schedules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_jobs (
                id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(255),
                recipe_id VARCHAR(100),
                schedule_type VARCHAR(50),
                schedule_config JSONB,
                webhook_url TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        
        print("   ✅ Tables created successfully!")
        
        # List tables
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public';
        """)
        
        tables = cursor.fetchall()
        print(f"   Tables in database: {[t[0] for t in tables]}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Table creation failed: {e}")
        conn.rollback()
        return False

def test_insert_data(conn):
    """Test inserting data"""
    print("\n3. Testing data insertion...")
    
    try:
        cursor = conn.cursor()
        
        # Insert test scraping data
        cursor.execute("""
            INSERT INTO scraped_data (url, method, proxy_info, data, destination, job_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, timestamp;
        """, (
            'https://example.com',
            'test',
            'Neon test',
            '{"test": "data"}',
            'database',
            'test-job-123'
        ))
        
        result = cursor.fetchone()
        conn.commit()
        
        print(f"   ✅ Data inserted successfully!")
        print(f"   Record ID: {result[0]}")
        print(f"   Timestamp: {result[1]}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Data insertion failed: {e}")
        conn.rollback()
        return False

def test_query_data(conn):
    """Test querying data"""
    print("\n4. Testing data retrieval...")
    
    try:
        cursor = conn.cursor()
        
        # Query recent records
        cursor.execute("""
            SELECT id, url, method, timestamp 
            FROM scraped_data 
            ORDER BY timestamp DESC 
            LIMIT 5;
        """)
        
        records = cursor.fetchall()
        
        print(f"   ✅ Query successful!")
        print(f"   Found {len(records)} records")
        
        for record in records:
            print(f"   - ID: {record[0]}, URL: {record[1]}, Method: {record[2]}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        return False

def test_database_manager():
    """Test the DatabaseManager class"""
    print("\n5. Testing DatabaseManager class...")
    
    # Set DATABASE_URL in environment
    os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL')
    
    from database_manager import database_manager
    
    # Test connection
    if database_manager.connect():
        print("   ✅ DatabaseManager connected successfully!")
        
        # Test create tables
        database_manager.create_tables()
        
        # Test insert
        database_manager.insert_scraped_data(
            url='https://test.com',
            data='{"test": "from DatabaseManager"}',
            method='auto',
            proxy_info='Test proxy',
            job_id='manager-test-456'
        )
        
        print("   ✅ DatabaseManager operations successful!")
        
        # Close connection
        database_manager.disconnect()
        return True
    else:
        print("   ❌ DatabaseManager connection failed")
        return False

def main():
    print("="*60)
    print("NEON DATABASE TESTING")
    print("="*60)
    
    # Test connection
    conn = test_connection()
    
    if not conn:
        print("\n❌ Cannot proceed without database connection")
        return 1
    
    # Run tests
    tests = []
    tests.append(("Create Tables", create_tables(conn)))
    tests.append(("Insert Data", test_insert_data(conn)))
    tests.append(("Query Data", test_query_data(conn)))
    
    # Close direct connection
    conn.close()
    
    # Test DatabaseManager
    tests.append(("DatabaseManager", test_database_manager()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS:")
    for name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {name}: {status}")
    print("="*60)
    
    if all(r for _, r in tests):
        print("\n✅ All Neon database tests PASSED!")
        print("\nDatabase is ready for production use!")
        print("Connection string is stored in DATABASE_URL environment variable")
        return 0
    else:
        print("\n⚠️ Some database tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())