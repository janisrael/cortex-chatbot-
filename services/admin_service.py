"""
Admin Service for managing admin dashboard statistics and user management
"""
from models.user import User
from models.uploaded_file import UploadedFile
from models.crawled_url import CrawledUrl
from models.faq import FAQ
import sqlite3
import mysql.connector
from db_config import DB_CONFIG


class AdminService:
    """Service for admin operations and statistics"""
    
    @staticmethod
    def _get_db_connection():
        """Get database connection (MySQL or SQLite fallback)"""
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Exception as e:
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
    def get_all_users():
        """
        Get all users with their basic information
        
        Returns:
            list: List of user dictionaries with id, email, username, role, created_at, last_login
        """
        try:
            conn = AdminService._get_db_connection()
            is_sqlite = AdminService._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT id, email, username, role, created_at, last_login FROM users ORDER BY created_at DESC"
                cursor = conn.execute(query)
                users = [dict(row) for row in cursor.fetchall()]
            else:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT id, email, username, role, created_at, last_login FROM users ORDER BY created_at DESC"
                cursor.execute(query)
                users = cursor.fetchall()
                cursor.close()
            
            conn.close()
            return users
        except Exception as e:
            print(f"❌ Error getting all users: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_user_stats(user_id):
        """
        Get statistics for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            dict: User statistics including file count, crawl count, FAQ count
        """
        try:
            stats = {
                'user_id': user_id,
                'files_count': AdminService.get_user_files_count(user_id),
                'crawls_count': AdminService.get_user_crawls_count(user_id),
                'faqs_count': AdminService.get_user_faqs_count(user_id),
                'total_items': 0
            }
            stats['total_items'] = stats['files_count'] + stats['crawls_count'] + stats['faqs_count']
            return stats
        except Exception as e:
            print(f"❌ Error getting user stats: {e}")
            import traceback
            traceback.print_exc()
            return {
                'user_id': user_id,
                'files_count': 0,
                'crawls_count': 0,
                'faqs_count': 0,
                'total_items': 0
            }
    
    @staticmethod
    def get_user_files_count(user_id):
        """Get count of uploaded files for a user"""
        try:
            conn = AdminService._get_db_connection()
            is_sqlite = AdminService._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT COUNT(*) as count FROM uploaded_files WHERE user_id = ?"
                cursor = conn.execute(query, (user_id,))
                result = cursor.fetchone()
                count = result['count'] if result else 0
            else:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT COUNT(*) as count FROM uploaded_files WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                count = result['count'] if result else 0
                cursor.close()
            
            conn.close()
            return count
        except Exception as e:
            print(f"❌ Error getting user files count: {e}")
            return 0
    
    @staticmethod
    def get_user_crawls_count(user_id):
        """Get count of crawled URLs for a user"""
        try:
            conn = AdminService._get_db_connection()
            is_sqlite = AdminService._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT COUNT(*) as count FROM crawled_urls WHERE user_id = ?"
                cursor = conn.execute(query, (user_id,))
                result = cursor.fetchone()
                count = result['count'] if result else 0
            else:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT COUNT(*) as count FROM crawled_urls WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                count = result['count'] if result else 0
                cursor.close()
            
            conn.close()
            return count
        except Exception as e:
            print(f"❌ Error getting user crawls count: {e}")
            return 0
    
    @staticmethod
    def get_user_faqs_count(user_id):
        """Get count of FAQs for a user"""
        try:
            conn = AdminService._get_db_connection()
            is_sqlite = AdminService._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT COUNT(*) as count FROM faqs WHERE user_id = ?"
                cursor = conn.execute(query, (user_id,))
                result = cursor.fetchone()
                count = result['count'] if result else 0
            else:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT COUNT(*) as count FROM faqs WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                count = result['count'] if result else 0
                cursor.close()
            
            conn.close()
            return count
        except Exception as e:
            print(f"❌ Error getting user FAQs count: {e}")
            return 0
    
    @staticmethod
    def get_system_stats():
        """
        Get overall system statistics
        
        Returns:
            dict: System-wide statistics
        """
        try:
            conn = AdminService._get_db_connection()
            is_sqlite = AdminService._is_sqlite(conn)
            
            stats = {
                'total_users': 0,
                'total_admins': 0,
                'total_regular_users': 0,
                'total_files': 0,
                'total_crawls': 0,
                'total_faqs': 0,
                'active_users': 0  # Users with last_login in last 30 days
            }
            
            if is_sqlite:
                # Total users
                cursor = conn.execute("SELECT COUNT(*) as count FROM users")
                result = cursor.fetchone()
                stats['total_users'] = result['count'] if result else 0
                
                # Total admins
                cursor = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
                result = cursor.fetchone()
                stats['total_admins'] = result['count'] if result else 0
                
                # Total regular users
                cursor = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'user'")
                result = cursor.fetchone()
                stats['total_regular_users'] = result['count'] if result else 0
                
                # Total files
                cursor = conn.execute("SELECT COUNT(*) as count FROM uploaded_files")
                result = cursor.fetchone()
                stats['total_files'] = result['count'] if result else 0
                
                # Total crawls
                cursor = conn.execute("SELECT COUNT(*) as count FROM crawled_urls")
                result = cursor.fetchone()
                stats['total_crawls'] = result['count'] if result else 0
                
                # Total FAQs
                cursor = conn.execute("SELECT COUNT(*) as count FROM faqs")
                result = cursor.fetchone()
                stats['total_faqs'] = result['count'] if result else 0
                
                # Active users (last 30 days)
                cursor = conn.execute("""
                    SELECT COUNT(*) as count FROM users 
                    WHERE last_login IS NOT NULL 
                    AND datetime(last_login) > datetime('now', '-30 days')
                """)
                result = cursor.fetchone()
                stats['active_users'] = result['count'] if result else 0
            else:
                cursor = conn.cursor(dictionary=True)
                
                # Total users
                cursor.execute("SELECT COUNT(*) as count FROM users")
                result = cursor.fetchone()
                stats['total_users'] = result['count'] if result else 0
                
                # Total admins
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
                result = cursor.fetchone()
                stats['total_admins'] = result['count'] if result else 0
                
                # Total regular users
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'user'")
                result = cursor.fetchone()
                stats['total_regular_users'] = result['count'] if result else 0
                
                # Total files
                cursor.execute("SELECT COUNT(*) as count FROM uploaded_files")
                result = cursor.fetchone()
                stats['total_files'] = result['count'] if result else 0
                
                # Total crawls
                cursor.execute("SELECT COUNT(*) as count FROM crawled_urls")
                result = cursor.fetchone()
                stats['total_crawls'] = result['count'] if result else 0
                
                # Total FAQs
                cursor.execute("SELECT COUNT(*) as count FROM faqs")
                result = cursor.fetchone()
                stats['total_faqs'] = result['count'] if result else 0
                
                # Active users (last 30 days)
                cursor.execute("""
                    SELECT COUNT(*) as count FROM users 
                    WHERE last_login IS NOT NULL 
                    AND last_login > DATE_SUB(NOW(), INTERVAL 30 DAY)
                """)
                result = cursor.fetchone()
                stats['active_users'] = result['count'] if result else 0
                
                cursor.close()
            
            conn.close()
            return stats
        except Exception as e:
            print(f"❌ Error getting system stats: {e}")
            import traceback
            traceback.print_exc()
            return {
                'total_users': 0,
                'total_admins': 0,
                'total_regular_users': 0,
                'total_files': 0,
                'total_crawls': 0,
                'total_faqs': 0,
                'active_users': 0
            }
    
    @staticmethod
    def get_users_with_stats():
        """
        Get all users with their statistics
        
        Returns:
            list: List of user dictionaries with stats
        """
        try:
            users = AdminService.get_all_users()
            users_with_stats = []
            
            for user in users:
                user_id = user['id']
                user_stats = AdminService.get_user_stats(user_id)
                
                user_dict = {
                    'id': user_id,
                    'email': user['email'],
                    'username': user['username'],
                    'role': user['role'],
                    'created_at': user['created_at'],
                    'last_login': user['last_login'],
                    'files_count': user_stats['files_count'],
                    'crawls_count': user_stats['crawls_count'],
                    'faqs_count': user_stats['faqs_count'],
                    'total_items': user_stats['total_items']
                }
                users_with_stats.append(user_dict)
            
            return users_with_stats
        except Exception as e:
            print(f"❌ Error getting users with stats: {e}")
            import traceback
            traceback.print_exc()
            return []

