"""
OTP Model for email verification and authentication
"""
import sqlite3
import mysql.connector
from db_config import DB_CONFIG
from datetime import datetime, timedelta
import secrets
import os


class OTP:
    """Model for OTP verifications"""
    
    # OTP expiration time (15 minutes)
    EXPIRATION_MINUTES = 15
    
    # Maximum verification attempts
    MAX_ATTEMPTS = 5
    
    @staticmethod
    def _get_db_connection():
        """Get database connection (MySQL or SQLite fallback)"""
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Exception as e:
            # Fallback to SQLite if MySQL is not available
            # Use PVC path if available, otherwise use default location
            db_path = os.getenv('SQLITE_DB_PATH', 'users.db')
            # If relative path, make it absolute from /app
            if not os.path.isabs(db_path):
                db_path = os.path.join('/app', db_path)
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    @staticmethod
    def _is_sqlite(conn):
        """Check if connection is SQLite"""
        return isinstance(conn, sqlite3.Connection)
    
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    @staticmethod
    def create_otp(email, purpose='registration', user_id=None):
        """
        Create a new OTP verification record
        
        Args:
            email: Email address to send OTP to
            purpose: Purpose of OTP (registration, forgot_password, etc.)
            user_id: Optional user ID (for existing users)
            
        Returns:
            str: OTP code, or None if creation failed
        """
        try:
            conn = OTP._get_db_connection()
            is_sqlite = OTP._is_sqlite(conn)
            
            # Generate OTP
            otp_code = OTP.generate_otp()
            
            # Calculate expiration time
            expires_at = datetime.now() + timedelta(minutes=OTP.EXPIRATION_MINUTES)
            
            if is_sqlite:
                query = """
                    INSERT INTO otp_verifications (user_id, email, otp_code, purpose, expires_at, verified, attempts)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                """
                cursor = conn.execute(query, (user_id, email, otp_code, purpose, expires_at))
                conn.commit()
            else:
                cursor = conn.cursor()
                query = """
                    INSERT INTO otp_verifications (user_id, email, otp_code, purpose, expires_at, verified, attempts)
                    VALUES (%s, %s, %s, %s, %s, 0, 0)
                """
                cursor.execute(query, (user_id, email, otp_code, purpose, expires_at))
                conn.commit()
                cursor.close()
            
            conn.close()
            print(f"✅ OTP created for {email} (purpose: {purpose})")
            return otp_code
            
        except Exception as e:
            print(f"❌ Error creating OTP: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def verify_otp(email, otp_code, purpose='registration'):
        """
        Verify an OTP code
        
        Args:
            email: Email address
            otp_code: OTP code to verify
            purpose: Purpose of OTP
            
        Returns:
            tuple: (success: bool, message: str, otp_id: int or None)
        """
        try:
            conn = OTP._get_db_connection()
            is_sqlite = OTP._is_sqlite(conn)
            
            if is_sqlite:
                # Get the most recent unverified OTP for this email and purpose
                query = """
                    SELECT * FROM otp_verifications
                    WHERE email = ? AND purpose = ? AND verified = 0
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                cursor = conn.execute(query, (email, purpose))
                otp_record = cursor.fetchone()
            else:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT * FROM otp_verifications
                    WHERE email = %s AND purpose = %s AND verified = 0
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                cursor.execute(query, (email, purpose))
                otp_record = cursor.fetchone()
                cursor.close()
            
            if not otp_record:
                conn.close()
                return False, "No valid OTP found for this email", None
            
            # Check if OTP is expired
            expires_at = otp_record['expires_at']
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            
            if datetime.now() > expires_at:
                conn.close()
                return False, "OTP has expired. Please request a new one.", None
            
            # Check attempts
            attempts = otp_record['attempts']
            if attempts >= OTP.MAX_ATTEMPTS:
                conn.close()
                return False, "Maximum verification attempts exceeded. Please request a new OTP.", None
            
            # Verify OTP code
            if otp_record['otp_code'] != otp_code:
                # Increment attempts
                otp_id = otp_record['id']
                if is_sqlite:
                    conn.execute(
                        "UPDATE otp_verifications SET attempts = attempts + 1 WHERE id = ?",
                        (otp_id,)
                    )
                else:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE otp_verifications SET attempts = attempts + 1 WHERE id = %s",
                        (otp_id,)
                    )
                    cursor.close()
                conn.commit()
                conn.close()
                return False, "Invalid OTP code", None
            
            # Mark as verified
            otp_id = otp_record['id']
            if is_sqlite:
                conn.execute(
                    "UPDATE otp_verifications SET verified = 1, verified_at = ? WHERE id = ?",
                    (datetime.now(), otp_id)
                )
            else:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE otp_verifications SET verified = 1, verified_at = %s WHERE id = %s",
                    (datetime.now(), otp_id)
                )
                cursor.close()
            conn.commit()
            conn.close()
            
            print(f"✅ OTP verified for {email}")
            return True, "OTP verified successfully", otp_id
            
        except Exception as e:
            print(f"❌ Error verifying OTP: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error verifying OTP: {str(e)}", None
    
    @staticmethod
    def cleanup_expired():
        """Remove expired OTPs (older than 24 hours)"""
        try:
            conn = OTP._get_db_connection()
            is_sqlite = OTP._is_sqlite(conn)
            
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            if is_sqlite:
                cursor = conn.execute(
                    "DELETE FROM otp_verifications WHERE expires_at < ?",
                    (cutoff_time,)
                )
            else:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM otp_verifications WHERE expires_at < %s",
                    (cutoff_time,)
                )
                cursor.close()
            
            conn.commit()
            conn.close()
            print("✅ Cleaned up expired OTPs")
            return True
            
        except Exception as e:
            print(f"❌ Error cleaning up expired OTPs: {e}")
            return False
    
    @staticmethod
    def get_recent_otp_count(email, purpose, minutes=15):
        """Get count of OTPs created for email in last N minutes (for rate limiting)"""
        try:
            conn = OTP._get_db_connection()
            is_sqlite = OTP._is_sqlite(conn)
            
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            if is_sqlite:
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM otp_verifications WHERE email = ? AND purpose = ? AND created_at > ?",
                    (email, purpose, cutoff_time)
                )
                result = cursor.fetchone()
                count = result['count'] if result else 0
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT COUNT(*) as count FROM otp_verifications WHERE email = %s AND purpose = %s AND created_at > %s",
                    (email, purpose, cutoff_time)
                )
                result = cursor.fetchone()
                count = result['count'] if result else 0
                cursor.close()
            
            conn.close()
            return count
            
        except Exception as e:
            print(f"❌ Error getting recent OTP count: {e}")
            return 0
    
    @staticmethod
    def get_oldest_recent_otp_time(email, purpose, minutes=60):
        """Get the creation time of the oldest OTP in the last N minutes (for rate limiting)"""
        try:
            conn = OTP._get_db_connection()
            is_sqlite = OTP._is_sqlite(conn)
            
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            if is_sqlite:
                cursor = conn.execute(
                    "SELECT MIN(created_at) as oldest_time FROM otp_verifications WHERE email = ? AND purpose = ? AND created_at > ?",
                    (email, purpose, cutoff_time)
                )
                result = cursor.fetchone()
                oldest_time = result['oldest_time'] if result and result['oldest_time'] else None
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT MIN(created_at) as oldest_time FROM otp_verifications WHERE email = %s AND purpose = %s AND created_at > %s",
                    (email, purpose, cutoff_time)
                )
                result = cursor.fetchone()
                oldest_time = result['oldest_time'] if result and result['oldest_time'] else None
                cursor.close()
            
            conn.close()
            return oldest_time
            
        except Exception as e:
            print(f"❌ Error getting oldest OTP time: {e}")
            return None

