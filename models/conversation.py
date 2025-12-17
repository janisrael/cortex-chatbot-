"""
Conversation Model for storing chat conversations
"""
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG
from datetime import datetime
import sqlite3
import os
import uuid


class Conversation:
    """Conversation model for managing chat sessions"""
    
    def __init__(self, id, user_id, session_id, title=None, created_at=None, updated_at=None, message_count=0, is_active=True, metadata=None):
        self.id = id
        self.user_id = user_id
        self.session_id = session_id
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.message_count = message_count
        self.is_active = is_active
        self.metadata = metadata
    
    @staticmethod
    def _get_db_connection():
        """Get database connection (MySQL or SQLite fallback)"""
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except (Error, Exception) as e:
            # Fallback to SQLite if MySQL is not available
            db_path = 'conversations.db'
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    @staticmethod
    def _ensure_tables():
        """Ensure conversations table exists (create if not)"""
        conn = None
        try:
            conn = Conversation._get_db_connection()
            cursor = conn.cursor()
            
            # Check if MySQL or SQLite
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                # MySQL table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        session_id VARCHAR(255) NOT NULL,
                        title VARCHAR(500),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        message_count INT DEFAULT 0,
                        is_active BOOLEAN DEFAULT 1,
                        metadata TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_user_id (user_id),
                        INDEX idx_session_id (session_id),
                        INDEX idx_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                
                # Check if metadata column exists, add if not
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'conversations' 
                    AND COLUMN_NAME = 'metadata'
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("ALTER TABLE conversations ADD COLUMN metadata TEXT")
            else:
                # SQLite table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_id TEXT NOT NULL,
                        title TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        message_count INTEGER DEFAULT 0,
                        is_active INTEGER DEFAULT 1,
                        metadata TEXT
                    )
                """)
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON conversations(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON conversations(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON conversations(created_at)")
                
                # Check if metadata column exists, add if not (SQLite)
                cursor.execute("PRAGMA table_info(conversations)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'metadata' not in columns:
                    cursor.execute("ALTER TABLE conversations ADD COLUMN metadata TEXT")
            
            conn.commit()
        except Exception as e:
            print(f"Error ensuring conversations table: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def create(user_id, session_id, title=None):
        """Create a new conversation"""
        Conversation._ensure_tables()
        conn = None
        try:
            conn = Conversation._get_db_connection()
            cursor = conn.cursor()
            
            # Generate title from first message if not provided
            if not title:
                title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    INSERT INTO conversations (user_id, session_id, title, message_count, is_active)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, session_id, title, 0, True))
                conversation_id = cursor.lastrowid
            else:
                cursor.execute("""
                    INSERT INTO conversations (user_id, session_id, title, message_count, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, session_id, title, 0, 1))
                conversation_id = cursor.lastrowid
            
            conn.commit()
            
            # Fetch the created conversation
            return Conversation.get_by_id(conversation_id)
        except Exception as e:
            print(f"Error creating conversation: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def get_by_id(conversation_id):
        """Get conversation by ID"""
        Conversation._ensure_tables()
        conn = None
        try:
            conn = Conversation._get_db_connection()
            cursor = conn.cursor(dictionary=True) if isinstance(conn, mysql.connector.MySQLConnection) else conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("SELECT * FROM conversations WHERE id = %s", (conversation_id,))
            else:
                cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
            
            row = cursor.fetchone()
            if row:
                if is_mysql:
                    return Conversation._from_dict(row)
                else:
                    return Conversation._from_dict(dict(row))
            return None
        except Exception as e:
            print(f"Error getting conversation by id: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def get_by_session(user_id, session_id, active_only=True):
        """Get active conversation by user_id and session_id"""
        Conversation._ensure_tables()
        conn = None
        try:
            conn = Conversation._get_db_connection()
            cursor = conn.cursor(dictionary=True) if isinstance(conn, mysql.connector.MySQLConnection) else conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if active_only:
                if is_mysql:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        WHERE user_id = %s AND session_id = %s AND is_active = 1
                        ORDER BY updated_at DESC LIMIT 1
                    """, (user_id, session_id))
                else:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        WHERE user_id = ? AND session_id = ? AND is_active = 1
                        ORDER BY updated_at DESC LIMIT 1
                    """, (user_id, session_id))
            else:
                if is_mysql:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        WHERE user_id = %s AND session_id = %s
                        ORDER BY updated_at DESC LIMIT 1
                    """, (user_id, session_id))
                else:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        WHERE user_id = ? AND session_id = ?
                        ORDER BY updated_at DESC LIMIT 1
                    """, (user_id, session_id))
            
            row = cursor.fetchone()
            if row:
                if is_mysql:
                    return Conversation._from_dict(row)
                else:
                    return Conversation._from_dict(dict(row))
            return None
        except Exception as e:
            print(f"Error getting conversation by session: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def get_user_conversations(user_id, limit=10, active_only=False):
        """Get user's conversations"""
        Conversation._ensure_tables()
        conn = None
        try:
            conn = Conversation._get_db_connection()
            cursor = conn.cursor(dictionary=True) if isinstance(conn, mysql.connector.MySQLConnection) else conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if active_only:
                if is_mysql:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        WHERE user_id = %s AND is_active = 1
                        ORDER BY updated_at DESC LIMIT %s
                    """, (user_id, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        WHERE user_id = ? AND is_active = 1
                        ORDER BY updated_at DESC LIMIT ?
                    """, (user_id, limit))
            else:
                if is_mysql:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        WHERE user_id = %s
                        ORDER BY updated_at DESC LIMIT %s
                    """, (user_id, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        WHERE user_id = ?
                        ORDER BY updated_at DESC LIMIT ?
                    """, (user_id, limit))
            
            rows = cursor.fetchall()
            conversations = []
            for row in rows:
                if is_mysql:
                    conversations.append(Conversation._from_dict(row))
                else:
                    conversations.append(Conversation._from_dict(dict(row)))
            return conversations
        except Exception as e:
            print(f"Error getting user conversations: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def update_title(self, title):
        """Update conversation title"""
        conn = None
        try:
            conn = Conversation._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("UPDATE conversations SET title = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (title, self.id))
            else:
                cursor.execute("UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (title, self.id))
            
            conn.commit()
            self.title = title
            return True
        except Exception as e:
            print(f"Error updating conversation title: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def increment_message_count(self):
        """Increment message count"""
        conn = None
        try:
            conn = Conversation._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    UPDATE conversations 
                    SET message_count = message_count + 1, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (self.id,))
            else:
                cursor.execute("""
                    UPDATE conversations 
                    SET message_count = message_count + 1, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (self.id,))
            
            conn.commit()
            self.message_count += 1
            return True
        except Exception as e:
            print(f"Error incrementing message count: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def end(self):
        """Mark conversation as inactive"""
        conn = None
        try:
            conn = Conversation._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("UPDATE conversations SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (self.id,))
            else:
                cursor.execute("UPDATE conversations SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (self.id,))
            
            conn.commit()
            self.is_active = False
            return True
        except Exception as e:
            print(f"Error ending conversation: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def update_metadata(self, metadata):
        """Update conversation metadata
        
        Args:
            metadata: Dictionary to store as JSON in metadata field
        
        Returns:
            bool: Success status
        """
        conn = None
        try:
            import json
            metadata_json = json.dumps(metadata) if metadata else None
            
            conn = Conversation._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    UPDATE conversations 
                    SET metadata = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (metadata_json, self.id))
            else:
                cursor.execute("""
                    UPDATE conversations 
                    SET metadata = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (metadata_json, self.id))
            
            conn.commit()
            self.metadata = metadata
            return True
        except Exception as e:
            print(f"Error updating conversation metadata: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def delete(self):
        """Delete conversation (cascade will delete messages)"""
        conn = None
        try:
            conn = Conversation._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("DELETE FROM conversations WHERE id = %s", (self.id,))
            else:
                cursor.execute("DELETE FROM conversations WHERE id = ?", (self.id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def _from_dict(row):
        """Create Conversation object from database row"""
        is_active = row.get('is_active', True)
        if isinstance(is_active, int):
            is_active = bool(is_active)
        
        metadata = row.get('metadata')
        if metadata and isinstance(metadata, str):
            try:
                import json
                metadata = json.loads(metadata)
            except:
                metadata = None
        
        return Conversation(
            id=row.get('id'),
            user_id=row.get('user_id'),
            session_id=row.get('session_id'),
            title=row.get('title'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
            message_count=row.get('message_count', 0),
            is_active=is_active,
            metadata=metadata
        )
    
    def to_dict(self):
        """Convert conversation to dictionary"""
        # Handle datetime serialization safely
        created_at = None
        if self.created_at:
            if hasattr(self.created_at, 'isoformat'):
                created_at = self.created_at.isoformat()
            else:
                created_at = str(self.created_at)
        
        updated_at = None
        if self.updated_at:
            if hasattr(self.updated_at, 'isoformat'):
                updated_at = self.updated_at.isoformat()
            else:
                updated_at = str(self.updated_at)
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'title': self.title,
            'created_at': created_at,
            'updated_at': updated_at,
            'message_count': self.message_count,
            'is_active': self.is_active,
            'metadata': self.metadata
        }

