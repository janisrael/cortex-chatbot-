"""
Message Model for storing individual chat messages within conversations
"""
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG
from datetime import datetime
import sqlite3
import json


class Message:
    """Message model for storing chat messages"""
    
    def __init__(self, id, conversation_id, role, content, created_at=None, metadata=None):
        self.id = id
        self.conversation_id = conversation_id
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.created_at = created_at
        self.metadata = metadata if metadata else {}
    
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
        """Ensure messages table exists (create if not)"""
        conn = None
        try:
            conn = Message._get_db_connection()
            cursor = conn.cursor()
            
            # Check if MySQL or SQLite
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                # MySQL table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        conversation_id INT NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                        INDEX idx_conversation_id (conversation_id),
                        INDEX idx_created_at (created_at),
                        INDEX idx_role (role)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            else:
                # SQLite table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_id ON messages(conversation_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON messages(created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_role ON messages(role)")
            
            conn.commit()
        except Exception as e:
            print(f"Error ensuring messages table: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def create(conversation_id, role, content, metadata=None):
        """Create a new message"""
        Message._ensure_tables()
        conn = None
        try:
            conn = Message._get_db_connection()
            cursor = conn.cursor()
            
            # Serialize metadata to JSON string
            metadata_json = json.dumps(metadata) if metadata else None
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    INSERT INTO messages (conversation_id, role, content, metadata)
                    VALUES (%s, %s, %s, %s)
                """, (conversation_id, role, content, metadata_json))
                message_id = cursor.lastrowid
            else:
                cursor.execute("""
                    INSERT INTO messages (conversation_id, role, content, metadata)
                    VALUES (?, ?, ?, ?)
                """, (conversation_id, role, content, metadata_json))
                message_id = cursor.lastrowid
            
            conn.commit()
            
            # Fetch the created message
            return Message.get_by_id(message_id)
        except Exception as e:
            print(f"Error creating message: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def get_by_id(message_id):
        """Get message by ID"""
        Message._ensure_tables()
        conn = None
        try:
            conn = Message._get_db_connection()
            cursor = conn.cursor(dictionary=True) if isinstance(conn, mysql.connector.MySQLConnection) else conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("SELECT * FROM messages WHERE id = %s", (message_id,))
            else:
                cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
            
            row = cursor.fetchone()
            if row:
                if is_mysql:
                    return Message._from_dict(row)
                else:
                    return Message._from_dict(dict(row))
            return None
        except Exception as e:
            print(f"Error getting message by id: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def get_conversation_messages(conversation_id, limit=20, offset=0):
        """Get messages for a conversation, ordered by created_at"""
        Message._ensure_tables()
        conn = None
        try:
            conn = Message._get_db_connection()
            cursor = conn.cursor(dictionary=True) if isinstance(conn, mysql.connector.MySQLConnection) else conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE conversation_id = %s
                    ORDER BY created_at ASC
                    LIMIT %s OFFSET %s
                """, (conversation_id, limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE conversation_id = ?
                    ORDER BY created_at ASC
                    LIMIT ? OFFSET ?
                """, (conversation_id, limit, offset))
            
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                if is_mysql:
                    messages.append(Message._from_dict(row))
                else:
                    messages.append(Message._from_dict(dict(row)))
            return messages
        except Exception as e:
            print(f"Error getting conversation messages: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def get_recent_messages(conversation_id, limit=10):
        """Get most recent messages for a conversation (for context building)"""
        Message._ensure_tables()
        conn = None
        try:
            conn = Message._get_db_connection()
            cursor = conn.cursor(dictionary=True) if isinstance(conn, mysql.connector.MySQLConnection) else conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE conversation_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (conversation_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE conversation_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (conversation_id, limit))
            
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                if is_mysql:
                    messages.append(Message._from_dict(row))
                else:
                    messages.append(Message._from_dict(dict(row)))
            # Reverse to get chronological order
            return list(reversed(messages))
        except Exception as e:
            print(f"Error getting recent messages: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def count_by_conversation(conversation_id):
        """Count messages in a conversation"""
        Message._ensure_tables()
        conn = None
        try:
            conn = Message._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = %s", (conversation_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = ?", (conversation_id,))
            
            result = cursor.fetchone()
            count = result[0] if result else 0
            return count
        except Exception as e:
            print(f"Error counting messages: {e}")
            return 0
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def delete(self):
        """Delete message"""
        conn = None
        try:
            conn = Message._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("DELETE FROM messages WHERE id = %s", (self.id,))
            else:
                cursor.execute("DELETE FROM messages WHERE id = ?", (self.id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting message: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def _from_dict(row):
        """Create Message object from database row"""
        metadata = row.get('metadata')
        if metadata and isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        elif not metadata:
            metadata = {}
        
        return Message(
            id=row.get('id'),
            conversation_id=row.get('conversation_id'),
            role=row.get('role'),
            content=row.get('content'),
            created_at=row.get('created_at'),
            metadata=metadata
        )
    
    def to_dict(self):
        """Convert message to dictionary"""
        # Handle datetime serialization safely
        created_at = None
        if self.created_at:
            if hasattr(self.created_at, 'isoformat'):
                created_at = self.created_at.isoformat()
            else:
                created_at = str(self.created_at)
        
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'created_at': created_at,
            'metadata': self.metadata
        }

