"""
Database Manager for Web Scraper
Handles PostgreSQL database operations
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from config import DATABASE_CONFIG

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            # Try DATABASE_URL first (for Neon/Vercel)
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                self.connection = psycopg2.connect(database_url)
            else:
                # Fallback to individual parameters
                self.connection = psycopg2.connect(
                    host=DATABASE_CONFIG['host'],
                    port=DATABASE_CONFIG['port'],
                    database=DATABASE_CONFIG['database'],
                    user=DATABASE_CONFIG['user'],
                    password=DATABASE_CONFIG['password']
                )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            create_table_query = """
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
            
            CREATE INDEX IF NOT EXISTS idx_scraped_data_timestamp ON scraped_data(timestamp);
            CREATE INDEX IF NOT EXISTS idx_scraped_data_url ON scraped_data(url);
            CREATE INDEX IF NOT EXISTS idx_scraped_data_job_id ON scraped_data(job_id);
            """
            
            self.cursor.execute(create_table_query)
            self.connection.commit()
            print("✅ Database tables created/verified")
            return True
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            self.connection.rollback()
            return False
    
    def insert_scraped_data(self, url, data, method="static", proxy_info="No proxy", job_id=None):
        """Insert scraped data into database"""
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            insert_query = """
            INSERT INTO scraped_data (url, method, proxy_info, data, destination, job_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, timestamp;
            """
            
            self.cursor.execute(insert_query, (
                url,
                method,
                proxy_info,
                data[:10000],  # Limit data size
                'database',
                job_id
            ))
            
            result = self.cursor.fetchone()
            self.connection.commit()
            
            print(f"✅ Data inserted into database with ID: {result['id']}")
            return result
        except Exception as e:
            print(f"❌ Failed to insert data: {e}")
            self.connection.rollback()
            return None
    
    def disconnect(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print("Database connection closed")
        except Exception as e:
            print(f"Error closing connection: {e}")
    
    def get_recent_scrapes(self, limit=10):
        """Get recent scraping results"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            query = """
            SELECT id, timestamp, url, method, LENGTH(data) as data_size
            FROM scraped_data
            ORDER BY timestamp DESC
            LIMIT %s;
            """
            
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            print(f"❌ Failed to fetch recent scrapes: {e}")
            return []
    
    def get_scrape_by_job_id(self, job_id):
        """Get scraping result by job ID"""
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            query = """
            SELECT * FROM scraped_data
            WHERE job_id = %s
            ORDER BY timestamp DESC
            LIMIT 1;
            """
            
            self.cursor.execute(query, (job_id,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(f"❌ Failed to fetch scrape by job ID: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print("Database connection closed")
        except Exception as e:
            print(f"Error closing database connection: {e}")

# Global instance
database_manager = DatabaseManager()