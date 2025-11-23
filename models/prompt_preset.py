"""
Prompt Preset Model - Global presets stored in database
"""
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG
from datetime import datetime
import sqlite3


class PromptPreset:
    """Model for prompt presets (global, not user-specific)"""
    
    def __init__(self, id, name, icon, description, prompt, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.icon = icon
        self.description = description
        self.prompt = prompt
        self.created_at = created_at
        self.updated_at = updated_at
    
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
    def get_all():
        """Get all prompt presets"""
        try:
            conn = PromptPreset._get_db_connection()
            is_sqlite = PromptPreset._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT * FROM prompt_presets ORDER BY id ASC"
                cursor = conn.execute(query)
                rows = cursor.fetchall()
                presets = []
                for row in rows:
                    presets.append({
                        'id': str(row['id']),  # Convert to string for consistency
                        'name': row['name'],
                        'icon': row['icon'],
                        'description': row['description'],
                        'prompt': row['prompt'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
            else:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT * FROM prompt_presets ORDER BY id ASC"
                cursor.execute(query)
                presets = cursor.fetchall()
                cursor.close()
            
            conn.close()
            return presets
        except Exception as e:
            print(f"Error getting presets: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_by_id(preset_id):
        """Get preset by ID"""
        try:
            conn = PromptPreset._get_db_connection()
            is_sqlite = PromptPreset._is_sqlite(conn)
            
            if is_sqlite:
                query = "SELECT * FROM prompt_presets WHERE id = ?"
                cursor = conn.execute(query, (preset_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': str(row['id']),  # Convert to string for consistency
                        'name': row['name'],
                        'icon': row['icon'],
                        'description': row['description'],
                        'prompt': row['prompt'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
            else:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT * FROM prompt_presets WHERE id = %s"
                cursor.execute(query, (preset_id,))
                preset = cursor.fetchone()
                cursor.close()
                if preset:
                    preset['id'] = str(preset['id'])  # Convert to string for consistency
                    return preset
            
            conn.close()
            return None
        except Exception as e:
            print(f"Error getting preset by ID: {e}")
            return None
    
    @staticmethod
    def init_presets_db():
        """Initialize prompt_presets table and populate with default presets"""
        conn = None
        try:
            conn = PromptPreset._get_db_connection()
            is_sqlite = PromptPreset._is_sqlite(conn)
            
            if is_sqlite:
                # SQLite table creation
                create_table_query = """
                CREATE TABLE IF NOT EXISTS prompt_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    icon TEXT NOT NULL,
                    description TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                conn.execute(create_table_query)
                conn.commit()
            else:
                # MySQL table creation
                cursor = conn.cursor()
                create_table_query = """
                CREATE TABLE IF NOT EXISTS prompt_presets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    icon VARCHAR(50) NOT NULL,
                    description TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(create_table_query)
                cursor.close()
            
            # Check if presets already exist
            if is_sqlite:
                cursor = conn.execute("SELECT COUNT(*) as count FROM prompt_presets")
                result = cursor.fetchone()
                preset_count = result['count'] if result else 0
            else:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM prompt_presets")
                preset_count = cursor.fetchone()[0]
                cursor.close()
            
            # Only insert if table is empty
            if preset_count == 0:
                default_presets = [
                    {
                        'name': 'Virtual Assistant',
                        'icon': 'support_agent',
                        'description': 'General-purpose helpful assistant',
                        'prompt': '''You are {bot_name}, an intelligent AI assistant.

Your job is to help users with their questions. Always be polite, helpful, and conversational.

INSTRUCTIONS:
- Vary your greetings and responses to avoid sounding repetitive or robotic.
- Reference the user's specific question in your answer.
- Use ONLY the information provided in the "Relevant Info" section below.
- If you don't know the answer or the information isn't available, respond with a polite fallback.
- Only ask follow-up questions if they make sense and feel natural.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- Keep your tone friendly and concise.
- Always finish with a relevant follow-up or offer to help further.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
                    },
                    {
                        'name': 'Tech Support',
                        'icon': 'computer',
                        'description': 'Technical support and troubleshooting',
                        'prompt': '''You are {bot_name}, a technical support specialist.

Your role is to help users resolve technical issues, answer questions about products or services, and provide clear, step-by-step guidance.

INSTRUCTIONS:
- Be patient and understanding, especially with technical difficulties.
- Break down complex solutions into simple, numbered steps.
- Use technical terms when appropriate, but explain them clearly.
- If you don't have the answer, guide users to the right resources.
- Always confirm understanding before moving to the next step.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- End with a clear next step or follow-up question.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
                    },
                    {
                        'name': 'Sales Agent',
                        'icon': 'shopping_cart',
                        'description': 'Sales and product recommendations',
                        'prompt': '''You are {bot_name}, a knowledgeable sales representative.

Your goal is to help customers find the right products or services, answer questions about offerings, and guide them through the purchase process.

INSTRUCTIONS:
- Be enthusiastic but not pushy.
- Focus on benefits and value, not just features.
- Ask qualifying questions to understand customer needs.
- Provide clear pricing and availability information.
- Address objections professionally and helpfully.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- Always include a clear call-to-action.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
                    },
                    {
                        'name': 'Customer Service',
                        'icon': 'headset_mic',
                        'description': 'Customer support and inquiries',
                        'prompt': '''You are {bot_name}, a friendly customer service representative.

Your mission is to provide excellent customer service, resolve issues, answer questions, and ensure customer satisfaction.

INSTRUCTIONS:
- Always greet customers warmly and professionally.
- Listen carefully to customer concerns and acknowledge them.
- Provide accurate information from the knowledge base.
- If you cannot resolve an issue, escalate appropriately.
- Maintain a positive, solution-oriented attitude.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- End with an offer to help further or confirm resolution.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
                    },
                    {
                        'name': 'Educator',
                        'icon': 'school',
                        'description': 'Educational content and tutoring',
                        'prompt': '''You are {bot_name}, an educational assistant.

Your purpose is to help students learn, explain concepts clearly, and provide educational support.

INSTRUCTIONS:
- Break down complex topics into understandable parts.
- Use examples and analogies to clarify concepts.
- Encourage questions and active learning.
- Provide accurate information from educational materials.
- Adapt explanations to the student's level of understanding.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- End with a question to check understanding or suggest next steps.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
                    }
                ]
                
                created_at = datetime.now()
                
                for preset in default_presets:
                    if is_sqlite:
                        conn.execute("""
                            INSERT INTO prompt_presets (name, icon, description, prompt, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            preset['name'],
                            preset['icon'],
                            preset['description'],
                            preset['prompt'],
                            created_at,
                            created_at
                        ))
                    else:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO prompt_presets (name, icon, description, prompt, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            preset['name'],
                            preset['icon'],
                            preset['description'],
                            preset['prompt'],
                            created_at,
                            created_at
                        ))
                        cursor.close()
                
                conn.commit()
                print(f"✅ Created {len(default_presets)} default prompt presets")
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error initializing prompt presets: {e}")
            import traceback
            traceback.print_exc()
            if conn:
                try:
                    conn.close()
                except:
                    pass
            return False

