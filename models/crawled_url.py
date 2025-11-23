"""
CrawledUrl Model for storing crawled website data
User-isolated, similar to uploaded files
"""
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG
from datetime import datetime
import sqlite3
import os


class CrawledUrl:
    """Model for crawled URLs"""
    
    @staticmethod
    def _get_db_connection():
        """Get database connection (MySQL or SQLite fallback)"""
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except (Error, Exception) as e:
            # Fallback to SQLite if MySQL is not available
            db_path = 'users.db'
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    @staticmethod
    def _is_sqlite(conn):
        """Check if connection is SQLite"""
        return isinstance(conn, sqlite3.Connection)
    
    @staticmethod
    def init_db():
        """Initialize crawled_urls table"""
        conn = CrawledUrl._get_db_connection()
        is_sqlite = CrawledUrl._is_sqlite(conn)
        
        try:
            if is_sqlite:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS crawled_urls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        url TEXT NOT NULL,
                        title TEXT,
                        extracted_text TEXT,
                        word_count INTEGER DEFAULT 0,
                        char_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'preview',
                        category TEXT DEFAULT 'company_details',
                        crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ingested_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON crawled_urls(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON crawled_urls(status)")
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS crawled_urls (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        user_id INT NOT NULL,
                        url VARCHAR(500) NOT NULL,
                        title VARCHAR(255),
                        extracted_text TEXT,
                        word_count INT DEFAULT 0,
                        char_count INT DEFAULT 0,
                        status ENUM('preview', 'ingested', 'deleted') DEFAULT 'preview',
                        category VARCHAR(50) DEFAULT 'company_details',
                        crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ingested_at DATETIME NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_user_id (user_id),
                        INDEX idx_status (status),
                        INDEX idx_url (url(255))
                    )
                """)
                conn.commit()
                cursor.close()
        except Exception as e:
            print(f"⚠️ Error creating crawled_urls table: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def create(user_id, url, title=None, extracted_text=None, word_count=0, char_count=0, category='company_details', status='preview'):
        """Create a new crawled URL entry"""
        conn = CrawledUrl._get_db_connection()
        is_sqlite = CrawledUrl._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    INSERT INTO crawled_urls (user_id, url, title, extracted_text, word_count, char_count, category, status, crawled_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, url, title, extracted_text, word_count, char_count, category, status, datetime.now()))
                conn.commit()
                return cursor.lastrowid
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO crawled_urls (user_id, url, title, extracted_text, word_count, char_count, category, status, crawled_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, url, title, extracted_text, word_count, char_count, category, status, datetime.now()))
                conn.commit()
                crawled_id = cursor.lastrowid
                cursor.close()
                return crawled_id
        except Exception as e:
            print(f"❌ Error creating crawled URL: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id, crawled_id):
        """Get crawled URL by ID (user-isolated)"""
        conn = CrawledUrl._get_db_connection()
        is_sqlite = CrawledUrl._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    SELECT * FROM crawled_urls 
                    WHERE id = ? AND user_id = ? AND status != 'deleted'
                """, (crawled_id, user_id))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM crawled_urls 
                    WHERE id = %s AND user_id = %s AND status != 'deleted'
                """, (crawled_id, user_id))
                row = cursor.fetchone()
                cursor.close()
                return row
            return None
        except Exception as e:
            print(f"❌ Error getting crawled URL: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_url(user_id, url):
        """Get crawled URL by URL (user-isolated)"""
        conn = CrawledUrl._get_db_connection()
        is_sqlite = CrawledUrl._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    SELECT * FROM crawled_urls 
                    WHERE url = ? AND user_id = ? AND status != 'deleted'
                    ORDER BY crawled_at DESC
                    LIMIT 1
                """, (url, user_id))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM crawled_urls 
                    WHERE url = %s AND user_id = %s AND status != 'deleted'
                    ORDER BY crawled_at DESC
                    LIMIT 1
                """, (url, user_id))
                row = cursor.fetchone()
                cursor.close()
                return row
            return None
        except Exception as e:
            print(f"❌ Error getting crawled URL by URL: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all_by_user(user_id):
        """Get all crawled URLs for a user"""
        conn = CrawledUrl._get_db_connection()
        is_sqlite = CrawledUrl._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    SELECT * FROM crawled_urls 
                    WHERE user_id = ? AND status != 'deleted'
                    ORDER BY crawled_at DESC
                """, (user_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM crawled_urls 
                    WHERE user_id = %s AND status != 'deleted'
                    ORDER BY crawled_at DESC
                """, (user_id,))
                rows = cursor.fetchall()
                cursor.close()
                return rows
        except Exception as e:
            print(f"❌ Error getting crawled URLs: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def update_text(crawled_id, text):
        """Update extracted text"""
        conn = CrawledUrl._get_db_connection()
        is_sqlite = CrawledUrl._is_sqlite(conn)
        
        try:
            word_count = len(text.split()) if text else 0
            char_count = len(text) if text else 0
            
            if is_sqlite:
                conn.execute("""
                    UPDATE crawled_urls 
                    SET extracted_text = ?, word_count = ?, char_count = ?, updated_at = ?
                    WHERE id = ?
                """, (text, word_count, char_count, datetime.now(), crawled_id))
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE crawled_urls 
                    SET extracted_text = %s, word_count = %s, char_count = %s, updated_at = %s
                    WHERE id = %s
                """, (text, word_count, char_count, datetime.now(), crawled_id))
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error updating crawled URL text: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def update_status(crawled_id, status):
        """Update status (preview, ingested, deleted)"""
        conn = CrawledUrl._get_db_connection()
        is_sqlite = CrawledUrl._is_sqlite(conn)
        
        try:
            if is_sqlite:
                if status == 'ingested':
                    conn.execute("""
                        UPDATE crawled_urls 
                        SET status = ?, ingested_at = ?, updated_at = ?
                        WHERE id = ?
                    """, (status, datetime.now(), datetime.now(), crawled_id))
                else:
                    conn.execute("""
                        UPDATE crawled_urls 
                        SET status = ?, updated_at = ?
                        WHERE id = ?
                    """, (status, datetime.now(), crawled_id))
                conn.commit()
            else:
                cursor = conn.cursor()
                if status == 'ingested':
                    cursor.execute("""
                        UPDATE crawled_urls 
                        SET status = %s, ingested_at = %s, updated_at = %s
                        WHERE id = %s
                    """, (status, datetime.now(), datetime.now(), crawled_id))
                else:
                    cursor.execute("""
                        UPDATE crawled_urls 
                        SET status = %s, updated_at = %s
                        WHERE id = %s
                    """, (status, datetime.now(), crawled_id))
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error updating crawled URL status: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(crawled_id):
        """Delete crawled URL (soft delete by setting status to 'deleted')"""
        conn = CrawledUrl._get_db_connection()
        is_sqlite = CrawledUrl._is_sqlite(conn)
        
        try:
            if is_sqlite:
                conn.execute("""
                    UPDATE crawled_urls 
                    SET status = 'deleted', updated_at = ?
                    WHERE id = ?
                """, (datetime.now(), crawled_id))
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE crawled_urls 
                    SET status = 'deleted', updated_at = %s
                    WHERE id = %s
                """, (datetime.now(), crawled_id))
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error deleting crawled URL: {e}")
            return False
        finally:
            conn.close()

