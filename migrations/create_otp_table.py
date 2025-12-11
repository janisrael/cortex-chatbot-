"""
Migration script to create OTP verifications table
"""
import sqlite3
import mysql.connector
from db_config import DB_CONFIG
import os


def create_otp_table():
    """Create otp_verifications table"""
    try:
        # Try MySQL first
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS otp_verifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NULL,
                    email VARCHAR(255) NOT NULL,
                    otp_code VARCHAR(10) NOT NULL,
                    purpose VARCHAR(50) NOT NULL CHECK(purpose IN (
                        'registration',
                        'email_verification',
                        'forgot_password',
                        'email_change',
                        'two_factor_auth'
                    )),
                    expires_at DATETIME NOT NULL,
                    verified BOOLEAN DEFAULT 0,
                    attempts INT DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    verified_at DATETIME NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_otp_email (email),
                    INDEX idx_otp_code (otp_code),
                    INDEX idx_otp_expires (expires_at),
                    INDEX idx_otp_user (user_id)
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ OTP table created in MySQL")
            return True
            
        except Exception as mysql_error:
            print(f"⚠️ MySQL connection failed, trying SQLite: {mysql_error}")
            # Fallback to SQLite
            # Use PVC path if available, otherwise use default location
            db_path = os.getenv('SQLITE_DB_PATH', 'users.db')
            # If relative path, make it absolute from /app
            if not os.path.isabs(db_path):
                db_path = os.path.join('/app', db_path)
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            if not os.path.exists(db_path):
                print(f"⚠️ SQLite database not found at {db_path}, will create it")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS otp_verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NULL,
                    email TEXT NOT NULL,
                    otp_code TEXT NOT NULL,
                    purpose TEXT NOT NULL CHECK(purpose IN (
                        'registration',
                        'email_verification',
                        'forgot_password',
                        'email_change',
                        'two_factor_auth'
                    )),
                    expires_at DATETIME NOT NULL,
                    verified BOOLEAN DEFAULT 0,
                    attempts INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    verified_at DATETIME NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_otp_email ON otp_verifications(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_otp_code ON otp_verifications(otp_code)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_otp_expires ON otp_verifications(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_otp_user ON otp_verifications(user_id)")
            
            conn.commit()
            conn.close()
            print("✅ OTP table created in SQLite")
            return True
            
    except Exception as e:
        print(f"❌ Error creating OTP table: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Running OTP table migration...")
    create_otp_table()
    print("Migration complete!")

