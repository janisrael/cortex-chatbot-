"""
UploadedFile Model for storing uploaded file data
User-isolated, similar to crawled URLs
"""
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG
from datetime import datetime
import sqlite3
import os


class UploadedFile:
    """Model for uploaded files"""
    
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
        """Initialize uploaded_files table"""
        conn = UploadedFile._get_db_connection()
        is_sqlite = UploadedFile._is_sqlite(conn)
        
        try:
            if is_sqlite:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS uploaded_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        filename TEXT NOT NULL,
                        filepath TEXT NOT NULL,
                        category TEXT DEFAULT 'company_details',
                        extracted_text TEXT,
                        word_count INTEGER DEFAULT 0,
                        char_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'preview',
                        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ingested_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON uploaded_files(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON uploaded_files(status)")
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS uploaded_files (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        user_id INT NOT NULL,
                        filename VARCHAR(255) NOT NULL,
                        filepath VARCHAR(500) NOT NULL,
                        category VARCHAR(50) DEFAULT 'company_details',
                        extracted_text TEXT,
                        word_count INT DEFAULT 0,
                        char_count INT DEFAULT 0,
                        status ENUM('preview', 'ingested', 'deleted') DEFAULT 'preview',
                        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ingested_at DATETIME NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_user_id (user_id),
                        INDEX idx_status (status),
                        INDEX idx_filename (filename(255))
                    )
                """)
                conn.commit()
                cursor.close()
        except Exception as e:
            print(f"⚠️ Error creating uploaded_files table: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def create(user_id, filename, filepath, category='company_details', extracted_text=None, word_count=0, char_count=0, status='preview'):
        """Create a new uploaded file entry"""
        conn = UploadedFile._get_db_connection()
        is_sqlite = UploadedFile._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    INSERT INTO uploaded_files (user_id, filename, filepath, category, extracted_text, word_count, char_count, status, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, filename, filepath, category, extracted_text, word_count, char_count, status, datetime.now()))
                conn.commit()
                return cursor.lastrowid
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO uploaded_files (user_id, filename, filepath, category, extracted_text, word_count, char_count, status, uploaded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, filename, filepath, category, extracted_text, word_count, char_count, status, datetime.now()))
                conn.commit()
                file_id = cursor.lastrowid
                cursor.close()
                return file_id
        except Exception as e:
            print(f"❌ Error creating uploaded file: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id, file_id):
        """Get uploaded file by ID (user-isolated)"""
        conn = UploadedFile._get_db_connection()
        is_sqlite = UploadedFile._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    SELECT * FROM uploaded_files 
                    WHERE id = ? AND user_id = ? AND status != 'deleted'
                """, (file_id, user_id))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM uploaded_files 
                    WHERE id = %s AND user_id = %s AND status != 'deleted'
                """, (file_id, user_id))
                row = cursor.fetchone()
                cursor.close()
                return row
            return None
        except Exception as e:
            print(f"❌ Error getting uploaded file: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_filename(user_id, filename, category):
        """Get uploaded file by filename and category (user-isolated)"""
        conn = UploadedFile._get_db_connection()
        is_sqlite = UploadedFile._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    SELECT * FROM uploaded_files 
                    WHERE filename = ? AND category = ? AND user_id = ? AND status != 'deleted'
                    ORDER BY uploaded_at DESC
                    LIMIT 1
                """, (filename, category, user_id))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM uploaded_files 
                    WHERE filename = %s AND category = %s AND user_id = %s AND status != 'deleted'
                    ORDER BY uploaded_at DESC
                    LIMIT 1
                """, (filename, category, user_id))
                row = cursor.fetchone()
                cursor.close()
                return row
            return None
        except Exception as e:
            print(f"❌ Error getting uploaded file by filename: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all_by_user(user_id):
        """Get all uploaded files for a user"""
        conn = UploadedFile._get_db_connection()
        is_sqlite = UploadedFile._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    SELECT * FROM uploaded_files 
                    WHERE user_id = ? AND status != 'deleted'
                    ORDER BY uploaded_at DESC
                """, (user_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM uploaded_files 
                    WHERE user_id = %s AND status != 'deleted'
                    ORDER BY uploaded_at DESC
                """, (user_id,))
                rows = cursor.fetchall()
                cursor.close()
                return rows
        except Exception as e:
            print(f"❌ Error getting uploaded files: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def update_text(file_id, text):
        """Update extracted text"""
        conn = UploadedFile._get_db_connection()
        is_sqlite = UploadedFile._is_sqlite(conn)
        
        try:
            word_count = len(text.split()) if text else 0
            char_count = len(text) if text else 0
            
            if is_sqlite:
                conn.execute("""
                    UPDATE uploaded_files 
                    SET extracted_text = ?, word_count = ?, char_count = ?, updated_at = ?
                    WHERE id = ?
                """, (text, word_count, char_count, datetime.now(), file_id))
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE uploaded_files 
                    SET extracted_text = %s, word_count = %s, char_count = %s, updated_at = %s
                    WHERE id = %s
                """, (text, word_count, char_count, datetime.now(), file_id))
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error updating uploaded file text: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def update_status(file_id, status):
        """Update status (preview, ingested, deleted)"""
        conn = UploadedFile._get_db_connection()
        is_sqlite = UploadedFile._is_sqlite(conn)
        
        try:
            if is_sqlite:
                if status == 'ingested':
                    conn.execute("""
                        UPDATE uploaded_files 
                        SET status = ?, ingested_at = ?, updated_at = ?
                        WHERE id = ?
                    """, (status, datetime.now(), datetime.now(), file_id))
                else:
                    conn.execute("""
                        UPDATE uploaded_files 
                        SET status = ?, updated_at = ?
                        WHERE id = ?
                    """, (status, datetime.now(), file_id))
                conn.commit()
            else:
                cursor = conn.cursor()
                if status == 'ingested':
                    cursor.execute("""
                        UPDATE uploaded_files 
                        SET status = %s, ingested_at = %s, updated_at = %s
                        WHERE id = %s
                    """, (status, datetime.now(), datetime.now(), file_id))
                else:
                    cursor.execute("""
                        UPDATE uploaded_files 
                        SET status = %s, updated_at = %s
                        WHERE id = %s
                    """, (status, datetime.now(), file_id))
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error updating uploaded file status: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(file_id):
        """Delete uploaded file (soft delete by setting status to 'deleted')"""
        conn = UploadedFile._get_db_connection()
        is_sqlite = UploadedFile._is_sqlite(conn)
        
        try:
            if is_sqlite:
                conn.execute("""
                    UPDATE uploaded_files 
                    SET status = 'deleted', updated_at = ?
                    WHERE id = ?
                """, (datetime.now(), file_id))
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE uploaded_files 
                    SET status = 'deleted', updated_at = %s
                    WHERE id = %s
                """, (datetime.now(), file_id))
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error deleting uploaded file: {e}")
            return False
        finally:
            conn.close()

