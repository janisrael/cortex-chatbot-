"""
Chatbot Appearance Configuration Model
Stores user-specific appearance settings (color, avatar, suggested messages)
"""
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG
from datetime import datetime
import sqlite3
import json
import os


class ChatbotAppearance:
    """Model for chatbot appearance configuration"""
    
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
        """Initialize chatbot_appearance table"""
        conn = ChatbotAppearance._get_db_connection()
        is_sqlite = ChatbotAppearance._is_sqlite(conn)
        
        try:
            if is_sqlite:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS chatbot_appearance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL UNIQUE,
                        short_info TEXT,
                        primary_color TEXT,
                        avatar_type VARCHAR(50) DEFAULT 'preset',
                        avatar_value VARCHAR(255),
                        suggested_messages TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id_appearance ON chatbot_appearance(user_id)")
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chatbot_appearance (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        user_id INT NOT NULL UNIQUE,
                        short_info VARCHAR(200),
                        primary_color TEXT,
                        avatar_type ENUM('preset', 'upload', 'generated') DEFAULT 'preset',
                        avatar_value VARCHAR(255),
                        suggested_messages TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_user_id (user_id)
                    )
                """)
                conn.commit()
                cursor.close()
        except Exception as e:
            print(f"⚠️ Error creating chatbot_appearance table: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def get_by_user(user_id):
        """Get appearance config for a user"""
        conn = ChatbotAppearance._get_db_connection()
        is_sqlite = ChatbotAppearance._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute("""
                    SELECT * FROM chatbot_appearance 
                    WHERE user_id = ?
                """, (user_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM chatbot_appearance 
                    WHERE user_id = %s
                """, (user_id,))
                row = cursor.fetchone()
                cursor.close()
                return row
            return None
        except Exception as e:
            print(f"❌ Error getting appearance config: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def create_or_update(user_id, short_info=None, primary_color=None, avatar_type=None, avatar_value=None, suggested_messages=None):
        """Create or update appearance config for a user"""
        conn = ChatbotAppearance._get_db_connection()
        is_sqlite = ChatbotAppearance._is_sqlite(conn)
        
        try:
            # Serialize complex fields
            primary_color_json = json.dumps(primary_color) if primary_color and isinstance(primary_color, dict) else primary_color
            suggested_messages_json = json.dumps(suggested_messages) if suggested_messages and isinstance(suggested_messages, list) else suggested_messages
            
            # Check if exists
            existing = ChatbotAppearance.get_by_user(user_id)
            
            if existing:
                # Update
                if is_sqlite:
                    updates = []
                    params = []
                    if short_info is not None:
                        updates.append("short_info = ?")
                        params.append(short_info)
                    if primary_color_json is not None:
                        updates.append("primary_color = ?")
                        params.append(primary_color_json)
                    if avatar_type is not None:
                        updates.append("avatar_type = ?")
                        params.append(avatar_type)
                    if avatar_value is not None:
                        updates.append("avatar_value = ?")
                        params.append(avatar_value)
                    if suggested_messages_json is not None:
                        updates.append("suggested_messages = ?")
                        params.append(suggested_messages_json)
                    updates.append("updated_at = ?")
                    params.append(datetime.now())
                    params.append(user_id)
                    
                    conn.execute(f"""
                        UPDATE chatbot_appearance 
                        SET {', '.join(updates)}
                        WHERE user_id = ?
                    """, params)
                    conn.commit()
                else:
                    cursor = conn.cursor()
                    updates = []
                    params = []
                    if short_info is not None:
                        updates.append("short_info = %s")
                        params.append(short_info)
                    if primary_color_json is not None:
                        updates.append("primary_color = %s")
                        params.append(primary_color_json)
                    if avatar_type is not None:
                        updates.append("avatar_type = %s")
                        params.append(avatar_type)
                    if avatar_value is not None:
                        updates.append("avatar_value = %s")
                        params.append(avatar_value)
                    if suggested_messages_json is not None:
                        updates.append("suggested_messages = %s")
                        params.append(suggested_messages_json)
                    updates.append("updated_at = %s")
                    params.append(datetime.now())
                    params.append(user_id)
                    
                    cursor.execute(f"""
                        UPDATE chatbot_appearance 
                        SET {', '.join(updates)}
                        WHERE user_id = %s
                    """, params)
                    conn.commit()
                    cursor.close()
            else:
                # Create
                if is_sqlite:
                    conn.execute("""
                        INSERT INTO chatbot_appearance (user_id, short_info, primary_color, avatar_type, avatar_value, suggested_messages, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, short_info, primary_color_json, avatar_type or 'preset', avatar_value, suggested_messages_json, datetime.now(), datetime.now()))
                    conn.commit()
                else:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO chatbot_appearance (user_id, short_info, primary_color, avatar_type, avatar_value, suggested_messages, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, short_info, primary_color_json, avatar_type or 'preset', avatar_value, suggested_messages_json, datetime.now(), datetime.now()))
                    conn.commit()
                    cursor.close()
            return True
        except Exception as e:
            print(f"❌ Error saving appearance config: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()
    
    @staticmethod
    def to_dict(row):
        """Convert database row to dictionary with parsed JSON fields"""
        if not row:
            return None
        
        result = dict(row) if not isinstance(row, dict) else row
        
        # Parse JSON fields
        if result.get('primary_color'):
            try:
                if isinstance(result['primary_color'], str):
                    result['primary_color'] = json.loads(result['primary_color'])
            except:
                pass
        
        if result.get('suggested_messages'):
            try:
                if isinstance(result['suggested_messages'], str):
                    result['suggested_messages'] = json.loads(result['suggested_messages'])
            except:
                pass
        
        # Build avatar object
        if result.get('avatar_type') or result.get('avatar_value'):
            avatar_value = result.get('avatar_value', 'avatar_1')
            result['avatar'] = {
                'type': result.get('avatar_type', 'preset'),
                'value': avatar_value,
                'fallback': 'ui-avatars',
                'src': f"/static/img/avatar/{avatar_value}.png" if avatar_value else None
            }
        
        return result

