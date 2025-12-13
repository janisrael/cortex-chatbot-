"""
Database Migration System
Handles schema changes and data migrations
"""
import os
import sqlite3
from models import User
from models.prompt_preset import PromptPreset
from models.crawled_url import CrawledUrl
from models.faq import FAQ
from models.uploaded_file import UploadedFile


class MigrationManager:
    """Manages database migrations"""
    
    MIGRATIONS_DIR = "migrations"
    MIGRATION_TABLE = "schema_migrations"
    
    @staticmethod
    def init_migrations():
        """Initialize migration system"""
        os.makedirs(MigrationManager.MIGRATIONS_DIR, exist_ok=True)
        
        # Create migrations table
        conn = User._get_db_connection()
        is_sqlite = User._is_sqlite(conn)
        
        try:
            if is_sqlite:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {MigrationManager.MIGRATION_TABLE} (
                        version INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {MigrationManager.MIGRATION_TABLE} (
                        version INT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                cursor.close()
        except Exception as e:
            print(f"⚠️ Error initializing migrations: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def get_applied_migrations():
        """Get list of applied migrations"""
        conn = User._get_db_connection()
        is_sqlite = User._is_sqlite(conn)
        
        try:
            if is_sqlite:
                cursor = conn.execute(f"SELECT version FROM {MigrationManager.MIGRATION_TABLE} ORDER BY version")
                versions = [row[0] for row in cursor.fetchall()]
            else:
                cursor = conn.cursor()
                cursor.execute(f"SELECT version FROM {MigrationManager.MIGRATION_TABLE} ORDER BY version")
                versions = [row[0] for row in cursor.fetchall()]
                cursor.close()
            
            conn.close()
            return set(versions)
        except Exception as e:
            print(f"⚠️ Error getting applied migrations: {e}")
            conn.close()
            return set()
    
    @staticmethod
    def mark_migration_applied(version, name):
        """Mark a migration as applied"""
        conn = User._get_db_connection()
        is_sqlite = User._is_sqlite(conn)
        
        try:
            from datetime import datetime
            if is_sqlite:
                conn.execute(f"""
                    INSERT INTO {MigrationManager.MIGRATION_TABLE} (version, name, applied_at)
                    VALUES (?, ?, ?)
                """, (version, name, datetime.now()))
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute(f"""
                    INSERT INTO {MigrationManager.MIGRATION_TABLE} (version, name, applied_at)
                    VALUES (%s, %s, %s)
                """, (version, name, datetime.now()))
                conn.commit()
                cursor.close()
        except Exception as e:
            print(f"⚠️ Error marking migration as applied: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def run_migrations():
        """Run all pending migrations"""
        MigrationManager.init_migrations()
        applied = MigrationManager.get_applied_migrations()
        
        # Define migrations
        migrations = [
            (1, "001_initial_schema", MigrationManager._migration_001_initial_schema),
            (2, "002_add_username_field", MigrationManager._migration_002_add_username_field),
            (3, "003_create_prompt_presets", MigrationManager._migration_003_create_prompt_presets),
            (4, "004_create_crawled_urls", MigrationManager._migration_004_create_crawled_urls),
            (5, "005_create_chatbot_appearance", MigrationManager._migration_005_create_chatbot_appearance),
            (6, "006_create_faqs", MigrationManager._migration_006_create_faqs),
            (7, "007_create_uploaded_files", MigrationManager._migration_007_create_uploaded_files),
            (8, "008_create_demo_user", MigrationManager._migration_008_create_demo_user),
        ]
        
        for version, name, migration_func in migrations:
            if version not in applied:
                print(f"🔄 Running migration {version}: {name}...")
                try:
                    migration_func()
                    MigrationManager.mark_migration_applied(version, name)
                    print(f"✅ Migration {version} completed")
                except Exception as e:
                    print(f"❌ Migration {version} failed: {e}")
                    raise
            else:
                print(f"✓ Migration {version} already applied")
    
    @staticmethod
    def _migration_001_initial_schema():
        """Initial schema - creates users table if it doesn't exist"""
        # This is handled by User.init_db(), so we just ensure it's called
        User.init_db()
    
    @staticmethod
    def _migration_002_add_username_field():
        """Add username field if it doesn't exist"""
        conn = User._get_db_connection()
        is_sqlite = User._is_sqlite(conn)
        
        try:
            # Check if username column exists
            if is_sqlite:
                cursor = conn.execute("PRAGMA table_info(users)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'username' not in columns:
                    # SQLite doesn't support ALTER TABLE ADD COLUMN with constraints easily
                    # So we'll just ensure it exists via init_db
                    print("ℹ️ Username field check - handled by init_db")
            else:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'username'
                """)
                if not cursor.fetchone():
                    cursor.execute("""
                        ALTER TABLE users 
                        ADD COLUMN username VARCHAR(100) UNIQUE AFTER email
                    """)
                    conn.commit()
                cursor.close()
        except Exception as e:
            # Column might already exist, which is fine
            if "Duplicate column" not in str(e) and "already exists" not in str(e):
                print(f"⚠️ Migration 002 note: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def _migration_003_create_prompt_presets():
        """Create prompt_presets table and populate with default presets"""
        # This is handled by PromptPreset.init_presets_db(), so we just ensure it's called
        PromptPreset.init_presets_db()
    
    @staticmethod
    def _migration_004_create_crawled_urls():
        """Create crawled_urls table for storing crawled website data"""
        from models.crawled_url import CrawledUrl
        # This is handled by CrawledUrl.init_db(), so we just ensure it's called
        CrawledUrl.init_db()
    
    @staticmethod
    def _migration_005_create_chatbot_appearance():
        """Create chatbot_appearance table for storing appearance configuration"""
        from models.chatbot_appearance import ChatbotAppearance
        # This is handled by ChatbotAppearance.init_db(), so we just ensure it's called
        ChatbotAppearance.init_db()
    
    @staticmethod
    def _migration_006_create_faqs():
        """Create faqs table for storing user-specific FAQ entries"""
        from models.faq import FAQ
        # This is handled by FAQ.init_db(), so we just ensure it's called
        FAQ.init_db()
    
    @staticmethod
    def _migration_007_create_uploaded_files():
        """Create uploaded_files table for storing uploaded file data with status tracking"""
        from models.uploaded_file import UploadedFile
        # This is handled by UploadedFile.init_db(), so we just ensure it's called
        UploadedFile.init_db()
    
    @staticmethod
    def _migration_008_create_demo_user():
        """Create demo user account for portfolio showcase"""
        try:
            from models.user import User
            
            # Check if user already exists
            existing_user = User.get_by_email('user@example.com')
            if existing_user:
                print("ℹ️  Demo user (user@example.com) already exists, skipping creation")
                return
            
            # Create the demo user
            user_id, error = User.create_user(
                email='user@example.com',
                username='UserNormal',
                password='user123',
                role='user'
            )
            
            if user_id:
                print(f"✅ Demo user created successfully (ID: {user_id})")
            else:
                print(f"⚠️  Failed to create demo user: {error}")
        except Exception as e:
            # Don't fail the entire migration if demo user creation fails
            print(f"⚠️  Warning: Could not create demo user: {e}")
            print("   Migration will continue - this is not critical")


def run_migrations():
    """Convenience function to run migrations"""
    MigrationManager.run_migrations()

