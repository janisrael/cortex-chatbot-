"""
Flask RAG Chatbot Application
Main application file - minimal initialization only
All routes are in blueprints
"""
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models and blueprints
from models import User
from models.prompt_preset import PromptPreset
from blueprints import register_blueprints

# App setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "admin123")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
CORS(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.get_by_id(int(user_id))

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('chroma_db', exist_ok=True)
os.makedirs('config', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# 🔐 LLM Configuration
# Using unified LLM service (default: OpenAI, fallback: OpenAI)
from services.llm_service import LLMProvider

# Default system LLM (used for system-level features like AI text cleaning)
# User-specific LLMs are created dynamically in chatbot_service.py
llm = LLMProvider.get_default_llm(temperature=0.3, max_tokens=2000)
print(f"🤖 Using OpenAI model: gpt-4o-mini (unified LLM service)")

# Make llm available globally (needed by chat blueprint)
app.config['LLM'] = llm

# 🔍 Embeddings setup
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Set embeddings in knowledge service
    from services.knowledge_service import set_embeddings
    set_embeddings(embeddings)
    
    print("✅ Embeddings loaded successfully")
except Exception as e:
    print(f"⚠️ Embeddings initialization failed: {e}")
    embeddings = None

# Register all blueprints
register_blueprints(app)

# Make llm available to blueprints via app context
@app.before_request
def set_llm():
    """Make llm available to request context"""
    from flask import g
    g.llm = llm

# Update chat blueprint to use g.llm
def get_llm():
    """Get LLM instance"""
    from flask import g
    return getattr(g, 'llm', llm)

# Export llm for chat blueprint
import sys
sys.modules['app'] = sys.modules[__name__]

if __name__ == "__main__":
    print("🤖 Starting Flask RAG Chatbot...")
    print(f"📊 Vector store location: ./chroma_db")
    print(f"📝 Upload folder: ./uploads")
    print(f"📋 Logs will be saved to: ./logs/")
    print(f"🔑 Default admin: admin@example.com / admin123")
    
    # Initialize database tables and run migrations
    print("📦 Initializing database...")
    from migrations import run_migrations
    run_migrations()
    
    port = int(os.getenv('PORT', 6001))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
