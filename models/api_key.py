"""
Admin API Key Model for database storage
"""
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG
from datetime import datetime
import sqlite3
import os
import secrets
import hashlib


class AdminAPIKey:
    """Admin API Key model for storing API keys in database"""
    
    def __init__(self, id=None, name=None, key_hash=None, key_type='default', is_active=True, 
                 created_at=None, updated_at=None, created_by=None):
        self.id = id
        self.name = name
        self.key_hash = key_hash
        self.key_type = key_type  # 'default', 'fallback', 'custom'
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
    
    @staticmethod
    def _get_db_connection():
        """Get database connection (MySQL or SQLite fallback)"""
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except (Error, Exception) as e:
            db_path = 'users.db'
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    @staticmethod
    def _ensure_tables():
        """Ensure admin_api_keys table exists"""
        conn = None
        try:
            conn = AdminAPIKey._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admin_api_keys (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        key_hash VARCHAR(255) NOT NULL UNIQUE,
                        key_type ENUM('default', 'fallback', 'custom') DEFAULT 'custom',
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        created_by INT,
                        INDEX idx_key_hash (key_hash),
                        INDEX idx_key_type (key_type),
                        INDEX idx_is_active (is_active)
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admin_api_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        key_hash TEXT NOT NULL UNIQUE,
                        key_type TEXT DEFAULT 'custom' CHECK(key_type IN ('default', 'fallback', 'custom')),
                        is_active INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER
                    )
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_key_hash ON admin_api_keys(key_hash)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_key_type ON admin_api_keys(key_type)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_is_active ON admin_api_keys(is_active)
                """)
            
            conn.commit()
        except Exception as e:
            print(f"Error ensuring admin_api_keys table: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def generate_key():
        """Generate a new API key"""
        token = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        return token, key_hash
    
    @staticmethod
    def hash_key(key):
        """Hash an API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def validate_key(api_key):
        """Validate API key against database"""
        if not api_key:
            return None
        
        conn = None
        try:
            AdminAPIKey._ensure_tables()
            conn = AdminAPIKey._get_db_connection()
            cursor = conn.cursor()
            
            key_hash = AdminAPIKey.hash_key(api_key)
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    SELECT id, name, key_type, is_active 
                    FROM admin_api_keys 
                    WHERE key_hash = %s AND is_active = TRUE
                """, (key_hash,))
            else:
                cursor.execute("""
                    SELECT id, name, key_type, is_active 
                    FROM admin_api_keys 
                    WHERE key_hash = ? AND is_active = 1
                """, (key_hash,))
            
            result = cursor.fetchone()
            
            if result:
                if is_mysql:
                    return {
                        'id': result[0],
                        'name': result[1],
                        'key_type': result[2],
                        'is_active': bool(result[3])
                    }
                else:
                    return {
                        'id': result[0],
                        'name': result[1],
                        'key_type': result[2],
                        'is_active': bool(result[3])
                    }
            
            return None
        except Exception as e:
            print(f"Error validating API key: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def create(name, key_type='custom', created_by=None):
        """Create a new API key"""
        conn = None
        try:
            AdminAPIKey._ensure_tables()
            conn = AdminAPIKey._get_db_connection()
            cursor = conn.cursor()
            
            token, key_hash = AdminAPIKey.generate_key()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    INSERT INTO admin_api_keys (name, key_hash, key_type, created_by)
                    VALUES (%s, %s, %s, %s)
                """, (name, key_hash, key_type, created_by))
            else:
                cursor.execute("""
                    INSERT INTO admin_api_keys (name, key_hash, key_type, created_by)
                    VALUES (?, ?, ?, ?)
                """, (name, key_hash, key_type, created_by))
            
            conn.commit()
            
            return {
                'id': cursor.lastrowid,
                'token': token,
                'name': name,
                'key_type': key_type
            }
        except Exception as e:
            print(f"Error creating API key: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def get_all():
        """Get all API keys (without tokens)"""
        conn = None
        try:
            AdminAPIKey._ensure_tables()
            conn = AdminAPIKey._get_db_connection()
            cursor = conn.cursor(dictionary=True if isinstance(conn, mysql.connector.MySQLConnection) else None)
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    SELECT id, name, key_type, is_active, created_at, updated_at, created_by
                    FROM admin_api_keys
                    ORDER BY created_at DESC
                """)
            else:
                cursor.execute("""
                    SELECT id, name, key_type, is_active, created_at, updated_at, created_by
                    FROM admin_api_keys
                    ORDER BY created_at DESC
                """)
            
            results = cursor.fetchall()
            
            if is_mysql:
                return [dict(row) for row in results]
            else:
                return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting API keys: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def update(id, name=None, is_active=None):
        """Update an API key"""
        conn = None
        try:
            conn = AdminAPIKey._get_db_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = %s" if isinstance(conn, mysql.connector.MySQLConnection) else "name = ?")
                params.append(name)
            
            if is_active is not None:
                updates.append("is_active = %s" if isinstance(conn, mysql.connector.MySQLConnection) else "is_active = ?")
                params.append(1 if is_active else 0)
            
            if not updates:
                return False
            
            params.append(id)
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute(f"""
                    UPDATE admin_api_keys 
                    SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, params)
            else:
                cursor.execute(f"""
                    UPDATE admin_api_keys 
                    SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, params)
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating API key: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def delete(id):
        """Delete an API key"""
        conn = None
        try:
            conn = AdminAPIKey._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("DELETE FROM admin_api_keys WHERE id = %s", (id,))
            else:
                cursor.execute("DELETE FROM admin_api_keys WHERE id = ?", (id,))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting API key: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def set_system_api_key(key_value, key_type='default', provider='openai'):
        """Store system API key in database"""
        conn = None
        try:
            AdminAPIKey._ensure_system_keys_table()
            conn = AdminAPIKey._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            # Check if key exists
            if is_mysql:
                cursor.execute("""
                    SELECT id FROM system_api_keys 
                    WHERE key_type = %s AND provider = %s
                """, (key_type, provider))
            else:
                cursor.execute("""
                    SELECT id FROM system_api_keys 
                    WHERE key_type = ? AND provider = ?
                """, (key_type, provider))
            
            existing = cursor.fetchone()
            
            # Encrypt the key (simple base64 for now, in production use proper encryption)
            import base64
            encrypted_key = base64.b64encode(key_value.encode()).decode()
            
            if existing:
                # Update existing
                if is_mysql:
                    cursor.execute("""
                        UPDATE system_api_keys 
                        SET key_value = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE key_type = %s AND provider = %s
                    """, (encrypted_key, key_type, provider))
                else:
                    cursor.execute("""
                        UPDATE system_api_keys 
                        SET key_value = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE key_type = ? AND provider = ?
                    """, (encrypted_key, key_type, provider))
            else:
                # Insert new
                if is_mysql:
                    cursor.execute("""
                        INSERT INTO system_api_keys (key_type, provider, key_value)
                        VALUES (%s, %s, %s)
                    """, (key_type, provider, encrypted_key))
                else:
                    cursor.execute("""
                        INSERT INTO system_api_keys (key_type, provider, key_value)
                        VALUES (?, ?, ?)
                    """, (key_type, provider, encrypted_key))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting system API key: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def get_system_api_key(key_type='default', provider='openai'):
        """Get system API key from database"""
        conn = None
        try:
            AdminAPIKey._ensure_system_keys_table()
            conn = AdminAPIKey._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    SELECT key_value FROM system_api_keys 
                    WHERE key_type = %s AND provider = %s
                """, (key_type, provider))
            else:
                cursor.execute("""
                    SELECT key_value FROM system_api_keys 
                    WHERE key_type = ? AND provider = ?
                """, (key_type, provider))
            
            result = cursor.fetchone()
            
            if result:
                # Decrypt the key
                import base64
                encrypted_key = result[0] if is_mysql else result[0]
                key_value = base64.b64decode(encrypted_key.encode()).decode()
                return key_value
            
            return None
        except Exception as e:
            print(f"Error getting system API key: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    @staticmethod
    def _ensure_system_keys_table():
        """Ensure system_api_keys table exists"""
        conn = None
        try:
            conn = AdminAPIKey._get_db_connection()
            cursor = conn.cursor()
            
            is_mysql = isinstance(conn, mysql.connector.MySQLConnection)
            
            if is_mysql:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_api_keys (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        key_type VARCHAR(50) NOT NULL,
                        provider VARCHAR(50) NOT NULL,
                        key_value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_key_type_provider (key_type, provider),
                        INDEX idx_provider (provider)
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_api_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key_type TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        key_value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(key_type, provider)
                    )
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_provider ON system_api_keys(provider)
                """)
            
            conn.commit()
        except Exception as e:
            print(f"Error ensuring system_api_keys table: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'key_type': self.key_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at) if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else str(self.updated_at) if self.updated_at else None,
            'created_by': self.created_by
        }

