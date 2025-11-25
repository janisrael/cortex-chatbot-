"""
FAQ Model for storing user-specific FAQ entries
User-isolated, similar to crawled URLs and uploaded files
"""
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG
from datetime import datetime
import sqlite3
import os


class FAQ:
    """Model for FAQ entries"""
    
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
        """Initialize faqs table"""
        conn = FAQ._get_db_connection()
        is_sqlite = FAQ._is_sqlite(conn)
        
        try:
            if is_sqlite:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS faqs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        category TEXT DEFAULT 'company_details',
                        status TEXT DEFAULT 'draft',
                        ingested_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON faqs(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON faqs(status)")
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS faqs (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        user_id INT NOT NULL,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        category VARCHAR(50) DEFAULT 'company_details',
                        status ENUM('draft', 'active', 'deleted') DEFAULT 'draft',
                        ingested_at DATETIME NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_user_id (user_id),
                        INDEX idx_status (status)
                    )
                """)
                conn.commit()
                cursor.close()
        except Exception as e:
            print(f"⚠️ Error creating faqs table: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def create(user_id, question, answer, category='company_details', status='draft'):
        """Create a new FAQ entry"""
        conn = FAQ._get_db_connection()
        is_sqlite = FAQ._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    INSERT INTO faqs (user_id, question, answer, category, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, question, answer, category, status, datetime.now()))
                conn.commit()
                return cursor.lastrowid
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO faqs (user_id, question, answer, category, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, question, answer, category, status, datetime.now()))
                conn.commit()
                faq_id = cursor.lastrowid
                cursor.close()
                return faq_id
        except Exception as e:
            print(f"❌ Error creating FAQ: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id, faq_id):
        """Get FAQ by ID (user-isolated)"""
        conn = FAQ._get_db_connection()
        is_sqlite = FAQ._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    SELECT * FROM faqs 
                    WHERE id = ? AND user_id = ? AND status != 'deleted'
                """, (faq_id, user_id))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM faqs 
                    WHERE id = %s AND user_id = %s AND status != 'deleted'
                """, (faq_id, user_id))
                row = cursor.fetchone()
                cursor.close()
                return row
            return None
        except Exception as e:
            print(f"❌ Error getting FAQ: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all_by_user(user_id, status=None):
        """Get all FAQs for a user"""
        conn = FAQ._get_db_connection()
        is_sqlite = FAQ._is_sqlite(conn)
        
        try:
            if status:
                if is_sqlite:
                    cursor = conn.execute("""
                        SELECT * FROM faqs 
                        WHERE user_id = ? AND status = ?
                        ORDER BY created_at DESC
                    """, (user_id, status))
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("""
                        SELECT * FROM faqs 
                        WHERE user_id = %s AND status = %s
                        ORDER BY created_at DESC
                    """, (user_id, status))
                    rows = cursor.fetchall()
                    cursor.close()
                    return rows
            else:
                # Get all non-deleted FAQs
                if is_sqlite:
                    cursor = conn.execute("""
                        SELECT * FROM faqs 
                        WHERE user_id = ? AND status != 'deleted'
                        ORDER BY created_at DESC
                    """, (user_id,))
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("""
                        SELECT * FROM faqs 
                        WHERE user_id = %s AND status != 'deleted'
                        ORDER BY created_at DESC
                    """, (user_id,))
                    rows = cursor.fetchall()
                    cursor.close()
                    return rows
        except Exception as e:
            print(f"❌ Error getting FAQs: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def update(user_id, faq_id, question=None, answer=None, category=None):
        """Update FAQ question, answer, or category"""
        conn = FAQ._get_db_connection()
        is_sqlite = FAQ._is_sqlite(conn)
        
        try:
            updates = []
            params = []
            
            if question is not None:
                updates.append("question = ?" if is_sqlite else "question = %s")
                params.append(question)
            if answer is not None:
                updates.append("answer = ?" if is_sqlite else "answer = %s")
                params.append(answer)
            if category is not None:
                updates.append("category = ?" if is_sqlite else "category = %s")
                params.append(category)
            
            if not updates:
                return True  # Nothing to update
            
            updates.append("updated_at = ?" if is_sqlite else "updated_at = %s")
            params.append(datetime.now())
            params.append(faq_id)
            params.append(user_id)
            
            if is_sqlite:
                query = f"""
                    UPDATE faqs 
                    SET {', '.join(updates)}
                    WHERE id = ? AND user_id = ?
                """
                conn.execute(query, params)
                conn.commit()
            else:
                cursor = conn.cursor()
                query = f"""
                    UPDATE faqs 
                    SET {', '.join(updates)}
                    WHERE id = %s AND user_id = %s
                """
                cursor.execute(query, params)
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error updating FAQ: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def update_status(faq_id, status):
        """Update status (draft, active, deleted)"""
        conn = FAQ._get_db_connection()
        is_sqlite = FAQ._is_sqlite(conn)
        
        try:
            if is_sqlite:
                if status == 'active':
                    conn.execute("""
                        UPDATE faqs 
                        SET status = ?, ingested_at = ?, updated_at = ?
                        WHERE id = ?
                    """, (status, datetime.now(), datetime.now(), faq_id))
                else:
                    conn.execute("""
                        UPDATE faqs 
                        SET status = ?, updated_at = ?
                        WHERE id = ?
                    """, (status, datetime.now(), faq_id))
                conn.commit()
            else:
                cursor = conn.cursor()
                if status == 'active':
                    cursor.execute("""
                        UPDATE faqs 
                        SET status = %s, ingested_at = %s, updated_at = %s
                        WHERE id = %s
                    """, (status, datetime.now(), datetime.now(), faq_id))
                else:
                    cursor.execute("""
                        UPDATE faqs 
                        SET status = %s, updated_at = %s
                        WHERE id = %s
                    """, (status, datetime.now(), faq_id))
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error updating FAQ status: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(faq_id):
        """Delete FAQ (soft delete by setting status to 'deleted')"""
        conn = FAQ._get_db_connection()
        is_sqlite = FAQ._is_sqlite(conn)
        
        try:
            if is_sqlite:
                conn.execute("""
                    UPDATE faqs 
                    SET status = 'deleted', updated_at = ?
                    WHERE id = ?
                """, (datetime.now(), faq_id))
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE faqs 
                    SET status = 'deleted', updated_at = %s
                    WHERE id = %s
                """, (datetime.now(), faq_id))
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error deleting FAQ: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def to_dict(row):
        """Convert database row to dictionary"""
        if not row:
            return None
        
        result = dict(row) if not isinstance(row, dict) else row
        return result

