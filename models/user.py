"""
User Model for RBAC Authentication with SQLite Fallback
"""
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from db_config import DB_CONFIG
from datetime import datetime
import sqlite3
import os


class User(UserMixin):
    """User model for authentication and RBAC"""
    
    def __init__(self, id, email, username, password_hash, role='user', created_at=None, last_login=None):
        self.id = id
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin', 'user', 'viewer'
        self.created_at = created_at
        self.last_login = last_login
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def is_user(self):
        """Check if user has user role"""
        return self.role in ['admin', 'user']
    
    def is_viewer(self):
        """Check if user has viewer role (read-only)"""
        return self.role in ['admin', 'user', 'viewer']
    
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
    def get_by_id(user_id):
        """Get user by ID"""
        try:
            conn = User._get_db_connection()
            is_sqlite = User._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT * FROM users WHERE id = ?"
                cursor = conn.execute(query, (user_id,))
                user_data = cursor.fetchone()
            else:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT * FROM users WHERE id = %s"
                cursor.execute(query, (user_id,))
                user_data = cursor.fetchone()
                cursor.close()
            
            conn.close()
            
            if user_data:
                if is_sqlite:
                    return User(
                        id=user_data['id'],
                        email=user_data['email'],
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        role=user_data['role'],
                        created_at=user_data['created_at'],
                        last_login=user_data['last_login']
                    )
                else:
                    return User(
                        id=user_data['id'],
                        email=user_data['email'],
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        role=user_data['role'],
                        created_at=user_data['created_at'],
                        last_login=user_data['last_login']
                    )
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        try:
            conn = User._get_db_connection()
            is_sqlite = User._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT * FROM users WHERE email = ?"
                cursor = conn.execute(query, (email,))
                user_data = cursor.fetchone()
            else:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                user_data = cursor.fetchone()
                cursor.close()
            
            conn.close()
            
            if user_data:
                if is_sqlite:
                    return User(
                        id=user_data['id'],
                        email=user_data['email'],
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        role=user_data['role'],
                        created_at=user_data['created_at'],
                        last_login=user_data['last_login']
                    )
                else:
                    return User(
                        id=user_data['id'],
                        email=user_data['email'],
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        role=user_data['role'],
                        created_at=user_data['created_at'],
                        last_login=user_data['last_login']
                    )
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def email_exists(email):
        """Check if email already exists"""
        try:
            conn = User._get_db_connection()
            is_sqlite = User._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT COUNT(*) as count FROM users WHERE email = ?"
                cursor = conn.execute(query, (email,))
                result = cursor.fetchone()
                count = result['count'] if result else 0
            else:
                cursor = conn.cursor()
                query = "SELECT COUNT(*) FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                count = cursor.fetchone()[0]
                cursor.close()
            
            conn.close()
            return count > 0
        except Exception as e:
            print(f"Error checking email: {e}")
            return False
    
    @staticmethod
    def username_exists(username):
        """Check if username already exists"""
        try:
            conn = User._get_db_connection()
            is_sqlite = User._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT COUNT(*) as count FROM users WHERE username = ?"
                cursor = conn.execute(query, (username,))
                result = cursor.fetchone()
                count = result['count'] if result else 0
            else:
                cursor = conn.cursor()
                query = "SELECT COUNT(*) FROM users WHERE username = %s"
                cursor.execute(query, (username,))
                count = cursor.fetchone()[0]
                cursor.close()
            
            conn.close()
            return count > 0
        except Exception as e:
            print(f"Error checking username: {e}")
            return False
    
    @staticmethod
    def create_user(email, username, password, role='user'):
        """
        Create a new user
        
        Returns:
            tuple: (user_id: int or None, error_message: str or None)
                   If successful, returns (user_id, None)
                   If failed, returns (None, error_message)
        """
        try:
            # Check if email already exists
            if User.get_by_email(email):
                return None, "An account with this email already exists. Please use a different email or log in."
            
            # Check if username already exists
            if User.username_exists(username):
                return None, f"Username '{username}' is already taken. Please choose a different username."
            
            conn = User._get_db_connection()
            is_sqlite = User._is_sqlite(conn)
            
            password_hash = generate_password_hash(password)
            created_at = datetime.now()
            
            if is_sqlite:
                query = """
                    INSERT INTO users (email, username, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor = conn.execute(query, (email, username, password_hash, role, created_at))
                conn.commit()
                user_id = cursor.lastrowid
            else:
                cursor = conn.cursor()
                query = """
                    INSERT INTO users (email, username, password_hash, role, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (email, username, password_hash, role, created_at))
                conn.commit()
                user_id = cursor.lastrowid
                cursor.close()
            
            conn.close()
            
            # Create user-specific directories
            if user_id:
                User._create_user_directories(user_id)
            
            return user_id, None
        except mysql.connector.errors.IntegrityError as e:
            error_msg = str(e)
            print(f"Error creating user (IntegrityError): {e}")
            import traceback
            traceback.print_exc()
            
            # Check for duplicate username
            if 'username' in error_msg.lower() or 'duplicate entry' in error_msg.lower():
                if username.lower() in error_msg.lower():
                    return None, f"Username '{username}' is already taken. Please choose a different username."
            
            # Check for duplicate email
            if 'email' in error_msg.lower() or 'duplicate entry' in error_msg.lower():
                if email.lower() in error_msg.lower():
                    return None, "An account with this email already exists. Please use a different email or log in."
            
            return None, "Username or email already exists. Please choose different credentials."
        except sqlite3.IntegrityError as e:
            error_msg = str(e)
            print(f"Error creating user (SQLite IntegrityError): {e}")
            import traceback
            traceback.print_exc()
            
            if 'username' in error_msg.lower() or 'UNIQUE constraint' in error_msg:
                return None, f"Username '{username}' is already taken. Please choose a different username."
            if 'email' in error_msg.lower() or 'UNIQUE constraint' in error_msg:
                return None, "An account with this email already exists. Please use a different email or log in."
            
            return None, "Username or email already exists. Please choose different credentials."
        except Exception as e:
            print(f"Error creating user: {e}")
            import traceback
            traceback.print_exc()
            return None, f"Failed to create account: {str(e)}"
    
    @staticmethod
    def _create_user_directories(user_id):
        """Create user-specific directories for data isolation"""
        user_dirs = [
            f"chroma_db/user_{user_id}",
            f"uploads/user_{user_id}",
            f"config/user_{user_id}",
            f"data/user_{user_id}"
        ]
        for dir_path in user_dirs:
            os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created directories for user {user_id}")
    
    @staticmethod
    def update_last_login(user_id):
        """Update last login timestamp"""
        try:
            conn = User._get_db_connection()
            is_sqlite = User._is_sqlite(conn)
            
            if is_sqlite:
                query = "UPDATE users SET last_login = ? WHERE id = ?"
                conn.execute(query, (datetime.now(), user_id))
                conn.commit()
            else:
                cursor = conn.cursor()
                query = "UPDATE users SET last_login = %s WHERE id = %s"
                cursor.execute(query, (datetime.now(), user_id))
                conn.commit()
                cursor.close()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False
    
    @staticmethod
    def init_db():
        """Initialize database tables"""
        conn = None
        try:
            conn = User._get_db_connection()
            is_sqlite = User._is_sqlite(conn)
            
            if is_sqlite:
                # SQLite table creation
                create_table_query = """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user', 'viewer')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
                """
                conn.execute(create_table_query)
                conn.commit()
                
                # Create index
                conn.execute("CREATE INDEX IF NOT EXISTS idx_email ON users(email)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_username ON users(username)")
                conn.commit()
            else:
                # MySQL table creation
                cursor = conn.cursor()
                create_table_query = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'user', 'viewer') DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME NULL,
                    INDEX idx_email (email),
                    INDEX idx_username (username)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(create_table_query)
            
            # Check if admin user exists
            if is_sqlite:
                cursor = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
                result = cursor.fetchone()
                admin_count = result['count'] if result else 0
            else:
                check_admin_query = "SELECT COUNT(*) FROM users WHERE role = 'admin'"
                cursor.execute(check_admin_query)
                admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                admin_password = generate_password_hash('admin123')
                created_at = datetime.now()
                
                if is_sqlite:
                    conn.execute("""
                        INSERT INTO users (email, username, password_hash, role, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, ('admin@example.com', 'admin', admin_password, 'admin', created_at))
                    conn.commit()
                    user_id = conn.lastrowid
                else:
                    insert_admin_query = """
                        INSERT INTO users (email, username, password_hash, role, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_admin_query, ('admin@example.com', 'admin', admin_password, 'admin', created_at))
                    conn.commit()
                    user_id = cursor.lastrowid
                
                # Create admin user directories
                if user_id:
                    User._create_user_directories(user_id)
                
                print("✅ Created default admin user: admin@example.com / admin123")
            
            if not is_sqlite:
                cursor.close()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            if conn:
                try:
                    conn.close()
                except:
                    pass
            return False
