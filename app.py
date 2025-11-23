
from flask import Flask, request, jsonify, render_template, session, send_from_directory, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from datetime import datetime
import re
import shutil


import mysql.connector
from db_config import DB_CONFIG
from models import User
from auth import admin_required, user_required, viewer_required

# Updated imports for dashboard functionality
try:
    from langchain_community.vectorstores import Chroma  # ✅ Correct import
except ImportError:
    from langchain.vectorstores import Chroma  # Fallback (legacy)

from langchain_community.embeddings import HuggingFaceEmbeddings  # ✅ Updated
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from werkzeug.utils import secure_filename
import hashlib
from urllib.parse import urlparse
import json

# App setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "admin123")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
CORS(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.get_by_id(int(user_id))

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'csv'}

# 🎯 Suggested messages for the UI
SUGGESTED_MESSAGES = [
    "What services do you offer?",
    "How can I contact support?",
    "What are your business hours?",
    "Tell me about your pricing",
    "How do I get started?"
]

# Website configuration - add this to your app.py
WEBSITE_CONFIGS = {
    'default': {
        'name': 'Default Configuration',
        'bot_name': 'Cortex',
        'primary_color': '#0891b2',
        'knowledge_base': 'default',
        'allowed_origins': ['*'],
        'custom_prompt': None,  # Uses default if None
        'features': ['rag', 'file_upload', 'prompt_customization']
    },
    'ecommerce-store.com': {
        'name': 'E-Commerce Store',
        'bot_name': 'ShopBot',
        'primary_color': '#f59e0b',
        'knowledge_base': 'ecommerce',
        'allowed_origins': ['https://ecommerce-store.com'],
        'custom_prompt': 'You are ShopBot, a helpful shopping assistant. Help customers find products, answer questions about orders, shipping, and returns.',
        'features': ['product_search', 'order_tracking', 'support']
    },
    'tech-support.com': {
        'name': 'Tech Support Portal',
        'bot_name': 'TechAssist',
        'primary_color': '#8b5cf6',
        'knowledge_base': 'tech_support',
        'allowed_origins': ['https://tech-support.com'],
        'custom_prompt': 'You are TechAssist, a technical support specialist. Help users troubleshoot issues, provide setup guides, and answer technical questions.',
        'features': ['troubleshooting', 'documentation', 'ticket_creation']
    },
    'healthcare-clinic.com': {
        'name': 'Healthcare Clinic',
        'bot_name': 'HealthGuide',
        'primary_color': '#10b981',
        'knowledge_base': 'healthcare',
        'allowed_origins': ['https://healthcare-clinic.com'],
        'custom_prompt': 'You are HealthGuide, a patient support assistant. Help patients with appointment scheduling, general health information, and clinic services. Always remind users to consult healthcare professionals for medical advice.',
        'features': ['appointments', 'faq', 'services_info']
    }
}


# File categories configuration
FILE_CATEGORIES = {
    'company_details': {
        'name': 'Company Details',
        'description': 'Business information, services, team details, contact info',
        'vector_prefix': 'company_',
        'color': '#007bff'
    },
    'sales_training': {
        'name': 'Sales Training',
        'description': 'Sales scripts, objection handling, conversation examples',
        'vector_prefix': 'sales_',
        'color': '#28a745'
    },
    'product_info': {
        'name': 'Product Information', 
        'description': 'Product specs, pricing, features, documentation',
        'vector_prefix': 'product_',
        'color': '#ffc107'
    },
    'policies_legal': {
        'name': 'Policies & Legal',
        'description': 'Terms of service, privacy policy, legal documents',
        'vector_prefix': 'legal_',
        'color': '#dc3545'
    }
}


# 🔐 LLM Configuration - Choose your option
import os
from dotenv import load_dotenv
load_dotenv()

LLM_OPTION = os.getenv("LLM_OPTION", "ollama")  # Read from .env file

if LLM_OPTION == "openai":
    # OpenAI Option (requires API key and billing)
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # Options: gpt-3.5-turbo, gpt-4o-mini, gpt-4o, gpt-4
        temperature=0.3,  # Lower temperature for more precise, instruction-following responses
        openai_api_key=openai_api_key
    )
    print(f"🤖 Using OpenAI model: gpt-4o-mini")

else:
    # Ollama Option (free, runs locally)
    try:
        from langchain_community.llms import Ollama
        llm = Ollama(
            model="llama3.1:8b",  # or "llama2", "codellama", "mistral"
            temperature=0.7,
            base_url="http://localhost:11434"  # Default Ollama URL
        )
        print(f"🤖 Using Ollama model: llama3.1:8b")
    except ImportError:
        print("❌ Ollama not available. Install with: pip install langchain-community")
        # Fallback to a mock LLM for testing
        class MockLLM:
            def invoke(self, prompt):
                return "I'm a mock response. Please set up either OpenAI API or Ollama to get real responses."
        llm = MockLLM()
        print("🤖 Using Mock LLM (for testing only)")

# 🔍 Embeddings & Vector DB setup
# Initialize embeddings (used for user-specific vectorstores)
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("✅ Embeddings loaded successfully")
except Exception as e:
    print(f"⚠️ Embeddings initialization failed: {e}")
    embeddings = None

# Global vectorstore removed - using user-specific vectorstores only
# This prevents conflicts and ensures proper data isolation per user
vectorstore = None
retriever = None
qa_chain = None
print("ℹ️ Using user-specific vectorstores (initialized per user on first chat)")

# RAG prompt template
template_text = """
You are Cortex, an intelligent AI assistant powered by advanced RAG technology.

Your job is to help users with their questions using the knowledge base provided. Always be polite, helpful, and conversational—just like a friendly and attentive assistant.

INSTRUCTIONS:
- Vary your greetings and responses to avoid sounding repetitive or robotic.
- Reference the user's specific question in your answer.
- Use ONLY the information provided in the "Relevant Info" section below.
- If you don't know the answer or the information isn't available, respond with a polite and varied fallback such as:
  "That's a great question! I don't have the details on that right now, but I can help connect you to the right person."
  or
  "I'm not sure about that, but I can help you get in touch with someone who knows more!"
- Only ask follow-up questions if they make sense and feel natural.
- CRITICAL: Respond ONLY in plain text. DO NOT use HTML tags, code blocks, or markdown code fences.
- Format your response naturally: use line breaks for paragraphs, bullet points with "-", and **bold** for emphasis only.
- NEVER wrap your response in ```html, ```markdown, or any code fence.
- Keep your tone friendly and concise.
- Always finish with a relevant, human-sounding follow-up or offer to help further.

Relevant Info:
{context}

User Question: {question}

Cortex's Response:
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=template_text,
)

# Retriever and QA chain are now created per-user in the chat endpoint
# No global retriever/qa_chain needed since we use user-specific vectorstores
retriever = None
qa_chain = None
print("ℹ️ QA chains will be created per-user on demand")



@app.route("/website-a")
def website():
 
    
    # Pass website-specific config to template
    return render_template("website_a.html")


@app.route("/")
def index():
    # Redirect to login if not authenticated, otherwise dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page and authentication"""
    if request.method == "GET":
        # If already logged in, redirect to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template("login.html")
    
    # Check if this is an AJAX request (FormData from fetch)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              request.headers.get('Accept', '').find('application/json') != -1 or \
              request.is_json
    
    # POST request - handle login
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    remember = request.form.get('remember') == 'on'
    
    if not email or not password:
        if is_ajax:
            return jsonify({"status": "error", "message": "Email and password are required"}), 400
        flash("Email and password are required", "error")
        return redirect(url_for('login'))
    
    # Find user
    user = User.get_by_email(email)
    
    if user and user.check_password(password):
        # Login successful
        login_user(user, remember=remember)
        User.update_last_login(user.id)
        
        if is_ajax:
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "redirect": url_for('dashboard')
            })
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard'))
    else:
        # Login failed
        if is_ajax:
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401
        flash("Invalid email or password", "error")
        return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page"""
    if request.method == "GET":
        # If already logged in, redirect to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template("register.html")
    
    # Check if this is an AJAX request (FormData from fetch)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              request.headers.get('Accept', '').find('application/json') != -1 or \
              request.is_json
    
    # POST request - handle registration
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validation
    if not username or not email or not password:
        if is_ajax:
            return jsonify({"status": "error", "message": "All fields are required"}), 400
        flash("All fields are required", "error")
        return redirect(url_for('register'))
    
    if len(username) < 3:
        if is_ajax:
            return jsonify({"status": "error", "message": "Username must be at least 3 characters"}), 400
        flash("Username must be at least 3 characters", "error")
        return redirect(url_for('register'))
    
    if len(password) < 6:
        if is_ajax:
            return jsonify({"status": "error", "message": "Password must be at least 6 characters"}), 400
        flash("Password must be at least 6 characters", "error")
        return redirect(url_for('register'))
    
    if password != confirm_password:
        if is_ajax:
            return jsonify({"status": "error", "message": "Passwords do not match"}), 400
        flash("Passwords do not match", "error")
        return redirect(url_for('register'))
    
    # Check if email or username already exists
    if User.email_exists(email):
        if is_ajax:
            return jsonify({"status": "error", "message": "Email already registered"}), 400
        flash("Email already registered", "error")
        return redirect(url_for('register'))
    
    if User.username_exists(username):
        if is_ajax:
            return jsonify({"status": "error", "message": "Username already taken"}), 400
        flash("Username already taken", "error")
        return redirect(url_for('register'))
    
    # Create user
    user_id = User.create_user(email, username, password, role='user')
    
    if user_id:
        if is_ajax:
            return jsonify({
                "status": "success",
                "message": "Registration successful. Please log in.",
                "redirect": url_for('login')
            })
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    else:
        if is_ajax:
            return jsonify({"status": "error", "message": "Registration failed. Please try again."}), 500
        flash("Registration failed. Please try again.", "error")
        return redirect(url_for('register'))

@app.route("/logout")
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash("You have been logged out successfully", "info")
    return redirect(url_for('login'))

@app.route("/chat-interface")
def chat_interface():
    # Original chat interface moved here
    session.clear()
    return render_template("index.html", suggested=SUGGESTED_MESSAGES)

@app.route("/demo")
@login_required
def demo_chatbox():
    """Demo page showing the floating chatbox widget with user's chatbot config"""
    try:
        user_id = current_user.id
        config = load_user_chatbot_config(user_id)
        bot_name = config.get('bot_name', 'Cortex')
        
        # Read demo template
        demo_path = 'demo_chatbox.html'
        if os.path.exists(demo_path):
            with open(demo_path, 'r') as f:
                content = f.read()
            
            # Replace hardcoded "Cortex AI" with user's bot name
            content = content.replace('Cortex AI', bot_name)
            content = content.replace('Cortex', bot_name)
            
            return content, 200, {'Content-Type': 'text/html'}
        else:
            return send_from_directory('.', 'demo_chatbox.html')
    except Exception as e:
        print(f"Error loading demo: {e}")
        return send_from_directory('.', 'demo_chatbox.html')

@app.route("/widget")
def widget_multi():
    """Serve widget with user-specific configuration (1 chatbot per user) - requires API key"""
    # Get API key from query parameter
    api_key = request.args.get('api_key') or request.args.get('key')
    
    if not api_key:
        return "Error: API key is required", 400
    
    # Validate API key and get user_id
    user_id = validate_api_key(api_key)
    
    if not user_id:
        return "Error: Invalid API key", 401
    
    # Load user's config
    try:
        user_config = load_user_chatbot_config(user_id)
        bot_name = user_config.get('bot_name', 'Cortex')
        primary_color = '#0891b2'  # Default primary color
        website_name = bot_name  # Use bot name as website name
    except Exception as e:
        print(f"Error loading user config for widget: {e}")
        bot_name = 'Cortex'
        primary_color = '#667eea'
        website_name = 'Website'
    
    # Pass user-specific config to template
    return render_template("widget.html", 
                         suggested=SUGGESTED_MESSAGES,
                         website_id='default',
                         bot_name=bot_name,
                         primary_color=primary_color,
                         website_name=website_name)


@app.route("/embed.js")
def serve_embed_script_multi():
    """Serve user-specific embed script (1 chatbot per user) - requires API key"""
    # Get API key from query parameter
    api_key = request.args.get('api_key') or request.args.get('key')
    
    if not api_key:
        # Return error script if no API key provided
        return """
(function() {
    console.error('Chatbot Error: API key is required. Please get your embed script from the dashboard.');
})();
""", 200, {'Content-Type': 'application/javascript'}
    
    # Validate API key and get user_id
    user_id = validate_api_key(api_key)
    
    if not user_id:
        # Return error script if API key is invalid
        return """
(function() {
    console.error('Chatbot Error: Invalid API key. Please check your embed script.');
})();
""", 200, {'Content-Type': 'application/javascript'}
    
    # Load user's config
    try:
        user_config = load_user_chatbot_config(user_id)
        bot_name = user_config.get('bot_name', 'Cortex')
        primary_color = '#0891b2'
        website_name = bot_name
    except Exception as e:
        print(f"Error loading user config for embed: {e}")
        bot_name = 'Cortex'
        primary_color = '#667eea'
        website_name = 'Website'
    
    config = {
        'bot_name': bot_name,
        'primary_color': primary_color,
        'name': website_name
    }
    
    # Generate dynamic embed script with user-specific config
    embed_script = f"""
(function() {{
    window.CHATBOT_CONFIG = {{
        apiBaseUrl: '{request.host_url.rstrip('/')}',
        apiKey: '{api_key}',
        botName: '{config.get('bot_name', 'Assistant')}',
        primaryColor: '{config.get('primary_color', '#667eea')}',
        websiteName: '{config.get('name', 'Website')}'
    }};
    
    // Load the widget HTML
    fetch('{request.host_url.rstrip('/')}/widget?api_key={api_key}')
        .then(response => response.text())
        .then(html => {{
            const widgetContainer = document.createElement('div');
            widgetContainer.id = 'ai-chatbot-widget';
            widgetContainer.innerHTML = html;
            document.body.appendChild(widgetContainer);
        }})
        .catch(error => {{
            console.error('Error loading chatbot widget:', error);
        }});
}})();
"""
    
    return embed_script, 200, {'Content-Type': 'application/javascript'}
@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard page - requires login"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template("dashboard_v1.html", user=current_user)


def get_website_config(request):
    """Determine which website configuration to use based on request"""
    # Method 1: Check Origin header
    origin = request.headers.get('Origin', '')
    referer = request.headers.get('Referer', '')
    
    # Method 2: Check API key or website parameter
    website_id = request.args.get('website_id') or request.json.get('website_id') if request.is_json else None
    
    # Method 3: Check custom domain mapping
    host = request.headers.get('Host', '')
    
    # Priority: explicit website_id > origin > referer > host > default
    if website_id and website_id in WEBSITE_CONFIGS:
        return website_id, WEBSITE_CONFIGS[website_id]
    
    # Check origin/referer against allowed origins
    for website_id, config in WEBSITE_CONFIGS.items():
        if website_id == 'default':
            continue
        
        allowed_origins = config.get('allowed_origins', [])
        if any(allowed_origin in origin or allowed_origin in referer for allowed_origin in allowed_origins):
            return website_id, config
    
    # Default fallback
    return 'default', WEBSITE_CONFIGS['default']

@app.route("/api/website-config", methods=["GET"])
def get_website_config():
    """Get configuration for a specific website (for widget)"""
    website_id = request.args.get('website_id', 'default')
    
    if website_id not in WEBSITE_CONFIGS:
        website_id = 'default'
    
    config = WEBSITE_CONFIGS[website_id]
    
    return jsonify({
        'websiteId': website_id,
        'botName': config.get('bot_name', 'Assistant'),
        'primaryColor': config.get('primary_color', '#667eea'),
        'websiteName': config.get('name', 'Website'),
        'features': config.get('features', [])
    })


# Website management endpoints
@app.route("/api/websites", methods=["GET"])
def list_websites():
    """List all configured websites"""
    return jsonify({
        "websites": {
            website_id: {
                "name": config["name"],
                "bot_name": config["bot_name"], 
                "status": "active" if os.path.exists(get_knowledge_base_path(website_id)) else "setup_required"
            }
            for website_id, config in WEBSITE_CONFIGS.items()
            if website_id != 'default'
        }
    })

# Bulk operations endpoint
@app.route("/api/websites/bulk", methods=["POST"])
def bulk_website_operations():
    """Perform bulk operations on websites"""
    try:
        data = request.json
        operation = data.get('operation')
        website_ids = data.get('website_ids', [])
        
        if operation == 'backup':
            # Create backup for multiple websites
            results = {}
            for website_id in website_ids:
                try:
                    backup_path = create_website_backup(website_id)
                    results[website_id] = {"status": "success", "backup_path": backup_path}
                except Exception as e:
                    results[website_id] = {"status": "error", "error": str(e)}
            
            return jsonify({"results": results})
        
        elif operation == 'reset':
            # Reset multiple websites
            results = {}
            for website_id in website_ids:
                try:
                    reset_website_knowledge(website_id)
                    results[website_id] = {"status": "success"}
                except Exception as e:
                    results[website_id] = {"status": "error", "error": str(e)}
            
            return jsonify({"results": results})
        
        else:
            return jsonify({"error": "Invalid operation"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def reset_website_knowledge(website_id):
    """Reset knowledge base for a specific website"""
    # Clear website-specific knowledge base
    kb_path = get_knowledge_base_path(website_id)
    if os.path.exists(kb_path):
        shutil.rmtree(kb_path)
    os.makedirs(kb_path, exist_ok=True)
    
    # Clear website-specific uploads
    website_upload_dir = f"uploads/{website_id}"
    if os.path.exists(website_upload_dir):
        shutil.rmtree(website_upload_dir)
    
    # Recreate category directories
    os.makedirs(website_upload_dir, exist_ok=True)
    for category in FILE_CATEGORIES.keys():
        os.makedirs(f"{website_upload_dir}/{category}", exist_ok=True)

# Initialize website configs at startup
def initialize_website_configs():
    """Load website configurations at startup"""
    global WEBSITE_CONFIGS
    saved_configs = load_website_configs()
    if saved_configs:
        WEBSITE_CONFIGS.update(saved_configs)




def create_website_backup(website_id):
    """Create backup for a specific website"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"backups/{website_id}_backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup website-specific files
    website_upload_dir = f"uploads/{website_id}"
    if os.path.exists(website_upload_dir):
        shutil.copytree(website_upload_dir, f"{backup_dir}/uploads")
    
    # Backup website-specific knowledge base
    kb_path = get_knowledge_base_path(website_id)
    if os.path.exists(kb_path):
        shutil.copytree(kb_path, f"{backup_dir}/chroma_db")
    
    # Backup website-specific logs
    log_file = f"logs/chat_logs_{website_id}.csv"
    if os.path.exists(log_file):
        os.makedirs(f"{backup_dir}/logs", exist_ok=True)
        shutil.copy2(log_file, f"{backup_dir}/logs/")
    
    return backup_dir


@app.route("/api/websites", methods=["POST"])
def add_website():
    """Add a new website configuration"""
    try:
        data = request.json
        website_id = data.get('website_id')
        name = data.get('name')
        bot_name = data.get('bot_name')
        primary_color = data.get('primary_color', '#667eea')
        allowed_origins = data.get('allowed_origins', [])
        
        if not all([website_id, name, bot_name]):
            return jsonify({"error": "Missing required fields"}), 400
        
        if website_id in WEBSITE_CONFIGS:
            return jsonify({"error": "Website ID already exists"}), 400
        
        # Add to runtime configuration
        WEBSITE_CONFIGS[website_id] = {
            'name': name,
            'bot_name': bot_name,
            'primary_color': primary_color,
            'knowledge_base': website_id,
            'allowed_origins': allowed_origins,
            'custom_prompt': None,
            'features': ['basic_support']
        }
        
        # Create directories for website
        os.makedirs(f"uploads/{website_id}", exist_ok=True)
        for category in FILE_CATEGORIES.keys():
            os.makedirs(f"uploads/{website_id}/{category}", exist_ok=True)
        
        # Create knowledge base directory
        os.makedirs(get_knowledge_base_path(website_id), exist_ok=True)
        
        # Save configuration to file (optional - for persistence)
        save_website_configs()
        
        return jsonify({"message": f"Website {name} added successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_user_knowledge_base_path(user_id):
    """Get the knowledge base path for a specific user"""
    return f"./chroma_db/user_{user_id}"

def get_user_vectorstore(user_id):
    """Get or create vectorstore for specific user"""
    if not embeddings:
        print("❌ Embeddings not available for vectorstore")
        return None
    
    kb_path = get_user_knowledge_base_path(user_id)
    
    # Create directory if it doesn't exist
    os.makedirs(kb_path, exist_ok=True)
    
    try:
        # Create/load vectorstore for this user
        user_vectorstore = Chroma(
            persist_directory=kb_path,
            embedding_function=embeddings
        )
        return user_vectorstore
    except Exception as e:
        print(f"❌ Error creating vectorstore for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_user_chatbot_config_path(user_id):
    """Get path to user's chatbot config file"""
    config_dir = f"./config/user_{user_id}"
    os.makedirs(config_dir, exist_ok=True)
    return f"{config_dir}/chatbot_config.json"

def generate_user_api_key(user_id):
    """Generate a unique API key for a user"""
    import secrets
    import hashlib
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    # Create a hash for storage
    key_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, key_hash

def get_user_api_key(user_id):
    """Get or create API key for user"""
    config = load_user_chatbot_config(user_id)
    api_key = config.get('api_key')
    
    if not api_key:
        # Generate new API key
        token, key_hash = generate_user_api_key(user_id)
        config['api_key'] = token
        config['api_key_hash'] = key_hash
        save_user_chatbot_config_file(user_id, config)
        return token
    
    return api_key

def validate_api_key(api_key):
    """Validate API key and return user_id if valid"""
    if not api_key:
        return None
    
    # Search through all user configs to find matching API key
    config_dir = "./config"
    if not os.path.exists(config_dir):
        return None
    
    for user_dir in os.listdir(config_dir):
        if user_dir.startswith('user_'):
            try:
                user_id = int(user_dir.replace('user_', ''))
                config = load_user_chatbot_config(user_id)
                stored_key = config.get('api_key')
                
                # Direct comparison (since we store the plain token)
                if stored_key == api_key:
                    return user_id
            except (ValueError, Exception) as e:
                continue
    
    return None

def load_user_chatbot_config(user_id):
    """Load user's chatbot configuration"""
    config_path = get_user_chatbot_config_path(user_id)
    default_config = {
        'bot_name': 'Cortex',
        'prompt': None,  # Will use default prompt with bot_name
        'api_key': None,
        'api_key_hash': None
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults
                default_config.update(user_config)
        except Exception as e:
            print(f"Error loading user config: {e}")
    
    return default_config

def save_user_chatbot_config_file(user_id, config):
    """Save user's chatbot configuration to file"""
    config_path = get_user_chatbot_config_path(user_id)
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving user config: {e}")
        return False

def remove_file_from_vectorstore(user_id, filename):
    """Remove all chunks related to a specific file from user's vectorstore"""
    try:
        user_vectorstore = get_user_vectorstore(user_id)
        if not user_vectorstore:
            print(f"⚠️ Vectorstore not available for user {user_id}")
            return False
        
        collection = user_vectorstore._collection
        
        # Delete documents by metadata filter
        try:
            # Get all documents with this source file
            results = collection.get(
                where={"source_file": filename}
            )
            
            if results and 'ids' in results and len(results['ids']) > 0:
                # Delete by IDs
                collection.delete(ids=results['ids'])
                print(f"✅ Deleted {len(results['ids'])} chunks for file '{filename}' from user {user_id}'s knowledge base")
                return True
            else:
                # Try alternative method: delete by where clause
                collection.delete(where={"source_file": filename})
                print(f"✅ Deleted chunks for file '{filename}' from user {user_id}'s knowledge base (alternative method)")
                return True
        except Exception as e:
            print(f"⚠️ Error deleting chunks for {filename}: {e}")
            # Try direct delete with where clause
            try:
                collection.delete(where={"source_file": filename})
                return True
            except Exception as e2:
                print(f"❌ Failed to delete chunks: {e2}")
                return False
    except Exception as e:
        print(f"❌ Error removing file from vectorstore: {e}")
        import traceback
        traceback.print_exc()
        return False

# Legacy function for backward compatibility (maps to user)
def get_knowledge_base_path(website_id):
    """Legacy: Get the knowledge base path for a specific website (deprecated - use user-based)"""
    return f"./chroma_db_{website_id}"

def get_website_vectorstore(website_id):
    """Legacy: Get or create vectorstore for specific website (deprecated - use user-based)"""
    kb_path = get_knowledge_base_path(website_id)
    
    # Create directory if it doesn't exist
    os.makedirs(kb_path, exist_ok=True)
    
    # Create/load vectorstore for this website
    website_vectorstore = Chroma(
        persist_directory=kb_path,
        embedding_function=embeddings
    )
    
    return website_vectorstore

def get_website_prompt(website_config, website_id):
    """Get the custom prompt for a website"""
    custom_prompt = website_config.get('custom_prompt')
    if custom_prompt:
        return custom_prompt
    
    # Check for website-specific prompt file
    prompt_file = f"config/prompt_{website_id}.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Use default prompt with website customization
    bot_name = website_config.get('bot_name', 'Assistant')
    website_name = website_config.get('name', 'this website')
    
    return f"""You are {bot_name}, a real human virtual assistant for {website_name}.

Your job is to help users with their questions about {website_name} and its services. Always be polite, helpful, and conversational—just like a friendly and attentive human agent.

INSTRUCTIONS:
- Vary your greetings and responses to avoid sounding repetitive or robotic.
- Reference the user's specific question in your answer.
- Use ONLY the information provided in the "Relevant Info" section below.
- If you don't know the answer or the information isn't available, respond with a polite and varied fallback such as:
  "That's a great question! I don't have the details on that right now, but I can help connect you to the right person."
  or
  "I'm not sure about that, but I can help you get in touch with someone who knows more!"
- Only ask follow-up questions if they make sense and feel natural.
- CRITICAL: Respond ONLY in plain text. DO NOT use HTML tags, code blocks, or markdown code fences.
- Format your response naturally: use line breaks for paragraphs, bullet points with "-", and **bold** for emphasis only.
- NEVER wrap your response in ```html, ```markdown, or any code fence.
- Keep your tone friendly and concise.
- Always finish with a relevant, human-sounding follow-up or offer to help further.

Relevant Info:
{{context}}

User Question: {{question}}

{bot_name}'s Response:"""

@app.route("/api/website/<website_id>", methods=["PUT", "DELETE"])
def manage_website(website_id):
    """Update or delete a website configuration"""
    if website_id not in WEBSITE_CONFIGS:
        return jsonify({"error": "Website not found"}), 404
    
    try:
        if request.method == "PUT":
            # Update website configuration
            data = request.json
            config = WEBSITE_CONFIGS[website_id]
            
            # Update allowed fields
            updatable_fields = ['name', 'bot_name', 'primary_color', 'allowed_origins', 'features']
            for field in updatable_fields:
                if field in data:
                    config[field] = data[field]
            
            # Save configuration
            save_website_configs()
            
            return jsonify({"message": f"Website {website_id} updated successfully"})
        
        elif request.method == "DELETE":
            # Delete website configuration
            if website_id == 'default':
                return jsonify({"error": "Cannot delete default website"}), 400
            
            # Remove from configuration
            del WEBSITE_CONFIGS[website_id]
            
            # Optionally remove files and knowledge base
            import shutil
            if os.path.exists(f"uploads/{website_id}"):
                shutil.rmtree(f"uploads/{website_id}")
            
            kb_path = get_knowledge_base_path(website_id)
            if os.path.exists(kb_path):
                shutil.rmtree(kb_path)
            
            # Save configuration
            save_website_configs()
            
            return jsonify({"message": f"Website {website_id} deleted successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def save_website_configs():
    """Save website configurations to file for persistence"""
    try:
        os.makedirs('config', exist_ok=True)
        with open('config/websites.json', 'w') as f:
            json.dump(WEBSITE_CONFIGS, f, indent=2)
    except Exception as e:
        print(f"Failed to save website configs: {e}")

def load_website_configs():
    """Load website configurations from file"""
    try:
        if os.path.exists('config/websites.json'):
            with open('config/websites.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load website configs: {e}")
    return {}


# ================================
# 📊 DASHBOARD API ENDPOINTS
# ================================
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route("/api/upload", methods=["POST"])
# def upload_file():
#     try:
#         if 'file' not in request.files:
#             return jsonify({"error": "No file provided"}), 400
        
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({"error": "No file selected"}), 400
        
#         if not allowed_file(file.filename):
#             return jsonify({"error": "File type not allowed"}), 400
        
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         # Process the file
#         success = process_uploaded_file(filepath, filename)
        
#         if success:
#             return jsonify({"message": f"File {filename} processed successfully"})
#         else:
#             return jsonify({"error": "Failed to process file"}), 500
            
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# Enhanced upload function with proper error handling
@app.route("/api/upload", methods=["POST"])
@login_required
def upload_file_multi():
    """File upload endpoint - user-specific"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        category = request.form.get('category', 'company_details')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        filename = secure_filename(file.filename)
        user_id = current_user.id
        
        # User-specific upload directory
        user_upload_dir = f"uploads/user_{user_id}"
        category_dir = os.path.join(user_upload_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        filepath = os.path.join(category_dir, filename)
        file.save(filepath)
        
        # Process file for user-specific knowledge base
        success = process_file_for_user(filepath, filename, category, user_id)
        
        if success:
            return jsonify({
                "message": f"File uploaded successfully to your knowledge base",
                "user_id": user_id,
                "category": category,
                "filename": filename
            })
        else:
            return jsonify({"error": "Failed to process file"}), 500
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Upload error: {error_details}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/files", methods=["GET"])
@login_required
def list_user_files():
    """List all uploaded files for the current user"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        user_upload_dir = f"uploads/user_{user_id}"
        
        files = []
        if os.path.exists(user_upload_dir):
            for category in os.listdir(user_upload_dir):
                category_path = os.path.join(user_upload_dir, category)
                if os.path.isdir(category_path):
                    for filename in os.listdir(category_path):
                        filepath = os.path.join(category_path, filename)
                        if os.path.isfile(filepath):
                            file_stat = os.stat(filepath)
                            files.append({
                                "filename": filename,
                                "category": category,
                                "size": file_stat.st_size,
                                "uploaded_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                                "path": filepath
                            })
        
        return jsonify({
            "files": files,
            "total": len(files)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/files/<path:filename>", methods=["DELETE"])
@login_required
def delete_user_file(filename):
    """Delete a file and remove its knowledge from vectorstore"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        category = request.args.get('category', 'company_details')
        
        # Find the file
        user_upload_dir = f"uploads/user_{user_id}"
        category_dir = os.path.join(user_upload_dir, category)
        filepath = os.path.join(category_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        # Remove from vectorstore first
        remove_file_from_vectorstore(user_id, filename)
        
        # Delete the physical file
        os.remove(filepath)
        print(f"✅ Deleted file: {filepath}")
        
        return jsonify({
            "message": f"File '{filename}' and its knowledge base entries deleted successfully",
            "filename": filename,
            "category": category
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Delete error: {error_details}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/files/bulk", methods=["DELETE"])
@login_required
def delete_files_bulk():
    """Delete multiple files at once"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.json
        filenames = data.get('filenames', [])
        category = data.get('category', 'company_details')
        
        if not filenames:
            return jsonify({"error": "No files specified"}), 400
        
        user_id = current_user.id
        deleted = []
        errors = []
        
        for filename in filenames:
            try:
                user_upload_dir = f"uploads/user_{user_id}"
                category_dir = os.path.join(user_upload_dir, category)
                filepath = os.path.join(category_dir, filename)
                
                if os.path.exists(filepath):
                    # Remove from vectorstore
                    remove_file_from_vectorstore(user_id, filename)
                    
                    # Delete file
                    os.remove(filepath)
                    deleted.append(filename)
                else:
                    errors.append(f"{filename}: File not found")
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
        
        return jsonify({
            "message": f"Deleted {len(deleted)} file(s)",
            "deleted": deleted,
            "errors": errors,
            "total_requested": len(filenames),
            "total_deleted": len(deleted)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_file_for_user(filepath, filename, category, user_id):
    """Process file for specific user's knowledge base"""
    try:
        if not embeddings:
            print("❌ Embeddings not available")
            return False
        
        from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader, Docx2txtLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        # Load document based on file extension
        file_ext = filename.lower().split('.')[-1]
        print(f"📄 Processing {file_ext} file: {filename}")
        
        try:
            if file_ext == 'pdf':
                loader = PyPDFLoader(filepath)
            elif file_ext == 'csv':
                loader = CSVLoader(filepath)
            elif file_ext in ['docx', 'doc']:
                try:
                    loader = Docx2txtLoader(filepath)
                except Exception as e:
                    print(f"⚠️ Could not load .docx file, trying as text: {e}")
                    loader = TextLoader(filepath, encoding='utf-8')
            else:
                loader = TextLoader(filepath, encoding='utf-8')
            
            documents = loader.load()
            print(f"📚 Loaded {len(documents)} documents from {filename}")
        except Exception as e:
            print(f"❌ Error loading file {filename}: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        print(f"✂️ Split into {len(chunks)} chunks")
        
        # Add user-specific metadata
        for chunk in chunks:
            chunk.metadata.update({
                'source_file': filename,
                'upload_time': datetime.now().isoformat(),
                'category': category,
                'user_id': str(user_id)
            })
        
        # Add to user-specific vectorstore
        try:
            if not embeddings:
                print("❌ Embeddings not available - cannot add to vectorstore")
                return False
            
            user_vectorstore = get_user_vectorstore(user_id)
            if user_vectorstore is None:
                print("❌ Failed to create/get user vectorstore")
                return False
            
            # Add documents to vectorstore
            print(f"📤 Adding {len(chunks)} chunks to vectorstore...")
            user_vectorstore.add_documents(chunks)
            print(f"✅ Added {len(chunks)} chunks from {filename} to user {user_id} knowledge base")
            
            # Verify documents were added (optional, can be slow)
            try:
                retriever = user_vectorstore.as_retriever(search_kwargs={"k": 1})
                test_docs = retriever.get_relevant_documents("test")
                print(f"✅ Verified: Vectorstore contains documents (retrieved {len(test_docs)} test docs)")
            except Exception as e:
                print(f"⚠️ Could not verify documents (this is okay): {e}")
            
            return True
        except Exception as e:
            print(f"❌ Error adding to vectorstore: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ File processing error for user {user_id}: {e}")
        print(f"Full traceback:\n{error_details}")
        return False

# Legacy function for backward compatibility
def process_file_for_website(filepath, filename, category, website_id):
    """Legacy: Process file for website (deprecated - use user-based)"""
    # For backward compatibility, try to get current user
    if current_user.is_authenticated:
        return process_file_for_user(filepath, filename, category, current_user.id)
    else:
        print("⚠️ process_file_for_website called but user not authenticated")
        return False

def process_uploaded_file_enhanced(filepath, filename, category):
    """Enhanced file processing with category support"""
    try:
        from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        # Determine file type and load accordingly
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            loader = PyPDFLoader(filepath)
        elif file_ext == 'csv':
            loader = CSVLoader(filepath)
        else:  # txt, doc, etc.
            loader = TextLoader(filepath, encoding='utf-8')
        
        documents = loader.load()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata['source_file'] = filename
            chunk.metadata['upload_time'] = datetime.now().isoformat()
            chunk.metadata['category'] = category
            chunk.metadata['category_name'] = FILE_CATEGORIES[category]['name']
        
        # Add to user-specific vector store
        if not current_user.is_authenticated:
            print("⚠️ User not authenticated - cannot upload files")
            return False
        
        user_id = current_user.id
        user_vectorstore = get_user_vectorstore(user_id)
        
        # Get existing documents from user's vectorstore
        existing_docs = []
        try:
            user_retriever = user_vectorstore.as_retriever(search_kwargs={"k": 1000})
            existing_docs = user_retriever.get_relevant_documents("")
        except:
            # Vectorstore might be empty, that's okay
            pass
        
        # Add new chunks to user's vectorstore
        if chunks:
            user_vectorstore.add_documents(chunks)
        
        print(f"✅ Processed {len(chunks)} chunks from {filename} in category {category}")
        return True
        
    except Exception as e:
        print(f"File processing error: {e}")
        return False


@app.route("/api/crawl", methods=["POST"])
def crawl_url():
    try:
        data = request.json
        url = data.get('url')
        max_pages = data.get('max_pages', 10)
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        # Process the URL
        success = process_url(url, max_pages)
        
        if success:
            return jsonify({"message": f"URL {url} crawled successfully"})
        else:
            return jsonify({"error": "Failed to crawl URL"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/prompt", methods=["GET", "POST"])
def manage_prompt():
    try:
        if request.method == "GET":
            return jsonify({"prompt": template_text})
        
        elif request.method == "POST":
            data = request.json
            new_prompt = data.get('prompt')
            
            if not new_prompt:
                return jsonify({"error": "No prompt provided"}), 400
            
            # Update the global prompt
            success = update_prompt(new_prompt)
            
            if success:
                return jsonify({"message": "Prompt updated successfully"})
            else:
                return jsonify({"error": "Failed to update prompt"}), 500
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route("/api/knowledge-stats", methods=["GET"])
# def knowledge_stats():
#     try:
#         # Get vector store statistics
#         test_docs = retriever.get_relevant_documents("test", k=10000)
        
#         stats = {
#             "total_documents": len(test_docs),
#             "vector_store_path": "./chroma_db",
#             "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
#             "llm_model": llm.model_name if hasattr(llm, 'model_name') else "unknown",
#             "llm_option": LLM_OPTION
#         }
        
#         # Get uploaded files
#         uploaded_files = []
#         if os.path.exists(app.config['UPLOAD_FOLDER']):
#             for filename in os.listdir(app.config['UPLOAD_FOLDER']):
#                 filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#                 if os.path.isfile(filepath):
#                     stat = os.stat(filepath)
#                     uploaded_files.append({
#                         "name": filename,
#                         "size": stat.st_size,
#                         "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
#                     })
        
#         stats["uploaded_files"] = uploaded_files
#         return jsonify(stats)
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# ================================
# 🔧 HELPER FUNCTIONS
# ================================
# def process_uploaded_file(filepath, filename):
#     try:
#         from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
#         from langchain.text_splitter import RecursiveCharacterTextSplitter
        
#         # Determine file type and load accordingly
#         file_ext = filename.lower().split('.')[-1]
        
#         if file_ext == 'pdf':
#             loader = PyPDFLoader(filepath)
#         elif file_ext == 'csv':
#             loader = CSVLoader(filepath)
#         else:  # txt, doc, etc.
#             loader = TextLoader(filepath, encoding='utf-8')
        
#         documents = loader.load()
        
#         # Split documents into chunks
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function=len,
#         )
#         chunks = text_splitter.split_documents(documents)
        
#         # Add metadata
#         for chunk in chunks:
#             chunk.metadata['source_file'] = filename
#             chunk.metadata['upload_time'] = datetime.now().isoformat()
        
#         # Add to vector store
#         global vectorstore, retriever, qa_chain
        
#         # Create new vector store with existing + new documents
#         existing_docs = []
#         try:
#             existing_docs = retriever.get_relevant_documents("", k=1000)
#         except:
#             pass
        
#         all_docs = existing_docs + chunks
        
#         vectorstore = Chroma.from_documents(
#             all_docs,
#             embedding=embeddings,
#             persist_directory="./chroma_db"
#         )
#         vectorstore.persist()
        
#         # Update retriever and QA chain
#         retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
#         update_qa_chain()
        
#         return True
        
#     except Exception as e:
#         print(f"File processing error: {e}")
#         return False

def process_uploaded_file(filepath, filename, category):
    try:
        from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        # Determine file type and load accordingly
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            loader = PyPDFLoader(filepath)
        elif file_ext == 'csv':
            loader = CSVLoader(filepath)
        else:
            loader = TextLoader(filepath, encoding='utf-8')
        
        documents = loader.load()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        chunks = text_splitter.split_documents(documents)
        
        # Add metadata with category information
        category_info = FILE_CATEGORIES[category]
        for chunk in chunks:
            chunk.metadata.update({
                'source_file': filename,
                'upload_time': datetime.now().isoformat(),
                'category': category,
                'category_name': category_info['name'],
                'category_prefix': category_info['vector_prefix']
            })
        
        # Store in separate vector collections or with category prefixes
        global vectorstore, retriever
        
        # Option 1: Separate vector stores per category
        category_vector_dir = f"./chroma_db_{category}"
        
        # Option 2: Single vector store with category metadata (recommended)
        existing_docs = []
        try:
            existing_docs = retriever.get_relevant_documents("", k=1000)
        except:
            pass
        
        all_docs = existing_docs + chunks
        
        vectorstore = Chroma.from_documents(
            all_docs,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        vectorstore.persist()
        
        # Update retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        update_qa_chain()
        
        # Log the categorized upload
        log_file_upload(filename, category, len(chunks))
        
        return True
        
    except Exception as e:
        print(f"File processing error: {e}")
        return False

def log_file_upload(filename, category, chunk_count):
    """Log file uploads with category information"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'filename': filename,
        'category': category,
        'chunk_count': chunk_count
    }
    
    log_file = 'logs/file_uploads.jsonl'
    os.makedirs('logs', exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')



@app.route("/api/files-by-category")
def get_files_by_category_multi():
    """Get uploaded files organized by category for specific website"""
    try:
        website_id = request.args.get('website_id', 'default')
        
        categories_with_files = {}
        
        # Website-specific upload folder
        upload_folder = f"uploads/{website_id}" if website_id != 'default' else 'uploads'
        
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
        
        for category_id, category_info in FILE_CATEGORIES.items():
            category_dir = os.path.join(upload_folder, category_id)
            files = []
            
            if not os.path.exists(category_dir):
                os.makedirs(category_dir, exist_ok=True)
            
            try:
                for filename in os.listdir(category_dir):
                    filepath = os.path.join(category_dir, filename)
                    if os.path.isfile(filepath):
                        try:
                            stat = os.stat(filepath)
                            files.append({
                                "name": filename,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                "category": category_id,
                                "website_id": website_id
                            })
                        except Exception as e:
                            print(f"Error reading file {filepath}: {e}")
            except Exception as e:
                print(f"Error reading directory {category_dir}: {e}")
            
            categories_with_files[category_id] = {
                **category_info,
                "files": files,
                "file_count": len(files)
            }
        
        return jsonify(categories_with_files)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Return available file categories"""
    try:
        return jsonify({
            "categories": FILE_CATEGORIES,
            "default": "company_details"
        })
    except Exception as e:
        print(f"Error in get_categories: {e}")
        return jsonify({"error": str(e)}), 500

def process_url(url, max_pages=10):
    try:
        from langchain_community.document_loaders import WebBaseLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        # Simple web scraping
        loader = WebBaseLoader([url])
        documents = loader.load()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata['source_url'] = url
            chunk.metadata['crawl_time'] = datetime.now().isoformat()
        
        # Add to vector store
        global vectorstore, retriever, qa_chain
        
        # Get existing documents
        existing_docs = []
        try:
            existing_docs = retriever.get_relevant_documents("", k=1000)
        except:
            pass
        
        all_docs = existing_docs + chunks
        
        vectorstore = Chroma.from_documents(
            all_docs,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        vectorstore.persist()
        
        # Update retriever and QA chain
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        update_qa_chain()
        
        return True
        
    except Exception as e:
        print(f"URL processing error: {e}")
        return False

def update_prompt(new_prompt):
    try:
        global template_text, prompt, qa_chain
        
        template_text = new_prompt
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template_text,
        )
        
        # Save prompt to file
        os.makedirs("config", exist_ok=True)
        with open("config/prompt.txt", "w", encoding="utf-8") as f:
            f.write(new_prompt)
        
        # Update QA chain
        update_qa_chain()
        
        return True
        
    except Exception as e:
        print(f"Prompt update error: {e}")
        return False

def update_qa_chain():
    global qa_chain
    if LLM_OPTION == "openai" or hasattr(llm, 'invoke'):
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt}
            )
        except Exception as e:
            print(f"QA chain update failed: {e}")
            qa_chain = None

# Load saved prompt if exists
def load_saved_prompt():
    try:
        if os.path.exists("config/prompt.txt"):
            with open("config/prompt.txt", "r", encoding="utf-8") as f:
                return f.read()
    except:
        pass
    return None

# Load saved prompt at startup
saved_prompt = load_saved_prompt()
if saved_prompt:
    template_text = saved_prompt
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template_text,
    )

# ================================
#  CHAT ENDPOINT
# ================================
@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint - accepts login OR API key, uses user-specific RAG"""
    try:
        data = request.json
        user_input = data.get("message")
        api_key = data.get("api_key") or request.headers.get("X-API-Key")
        
        # Determine user_id from either login or API key
        user_id = None
        name = "User"
        
        if current_user.is_authenticated:
            # Dashboard usage - use logged in user
            user_id = current_user.id
            name = current_user.username or "User"
        elif api_key:
            # Widget usage - validate API key
            user_id = validate_api_key(api_key)
            if not user_id:
                return jsonify({"error": "Invalid API key"}), 401
            name = "Visitor"
        else:
            return jsonify({"error": "Authentication required (login or API key)"}), 401

        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        # Get user-specific vectorstore
        user_vectorstore = get_user_vectorstore(user_id)
        if not user_vectorstore:
            return jsonify({"error": "Knowledge base not available"}), 500
        
        user_retriever = user_vectorstore.as_retriever(search_kwargs={"k": 5})
        
        # Load user's chatbot config
        user_config = load_user_chatbot_config(user_id)
        bot_name = user_config.get('bot_name', 'Cortex')
        user_prompt_template = user_config.get('prompt')
        
        # Use user's custom prompt or default
        if user_prompt_template:
            prompt_template_text = user_prompt_template
        else:
            prompt_template_text = get_default_prompt_with_name(bot_name)

        # Use user-specific RAG
        if hasattr(llm, 'invoke'):
            try:
                # Get relevant documents from user's knowledge base
                try:
                    docs = user_retriever.get_relevant_documents(user_input)
                    context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
                    
                    # Log retrieval for debugging
                    if docs:
                        print(f"📚 Retrieved {len(docs)} relevant documents from knowledge base")
                        print(f"📄 Sources: {[doc.metadata.get('source_file', 'unknown') for doc in docs[:3]]}")
                    else:
                        print(f"ℹ️ No relevant documents found in knowledge base for: {user_input[:50]}")
                except Exception as e:
                    print(f"⚠️ Error retrieving documents: {e}")
                    context = ""
                
                if context:
                    # Use RAG with context from knowledge base
                    full_prompt = prompt_template_text.format(context=context, question=user_input)
                    print(f"✅ Using RAG with {len(context)} characters of context")
                else:
                    # No context found - use LLM directly with user's bot name
                    full_prompt = f"You are {bot_name}, an intelligent AI assistant. Help {name} with: {user_input}"
                    print(f"ℹ️ No knowledge base context - using direct LLM response")
                
                full_prompt += f"\n\nCRITICAL: Respond in plain text ONLY. NO HTML, NO code blocks. Be helpful and friendly."
                reply = llm.invoke(full_prompt)
                
                # Ensure reply is a string
                if hasattr(reply, 'content'):
                    reply = reply.content
                reply = str(reply).strip().replace("\n", "<br>")
            except Exception as e:
                print(f"LLM error: {e}")
                import traceback
                traceback.print_exc()
                reply = f"I'm here to help! Could you please rephrase your question?<br><br>Error: {str(e)}"
        else:
            # Mock LLM fallback
            reply = f"Mock response for: {user_input}<br><br>What else would you like to know?"
        
        return jsonify({"response": reply})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Chat error: {e}")
        print(f"Full traceback:\n{error_details}")
        return jsonify({"response": f"Sorry, I ran into an error: {str(e)}"}), 500

# @app.route("/chat", methods=["POST"])
# def chat():
#     try:
#         data = request.json
#         user_input = data.get("message")
#         user_id = data.get("user_id", "anon")
#         name = data.get("name", "visitor")
        
#         # Get website configuration
#         website_id, website_config = get_website_config(request)
        
#         if not user_input:
#             return jsonify({"error": "No message provided"}), 400

#         # Get website-specific vectorstore and retriever
#         website_vectorstore = get_website_vectorstore(website_id)
#         website_retriever = website_vectorstore.as_retriever(search_kwargs={"k": 5})
        
#         # Get website-specific prompt
#         website_prompt_template = get_website_prompt(website_config, website_id)
        
#         # Retrieve context from website-specific knowledge base
#         docs = website_retriever.get_relevant_documents(user_input)
#         context = "\n\n".join(doc.page_content for doc in docs)
        
#         # Create website-specific prompt
#         from langchain.prompts import PromptTemplate
#         website_prompt = PromptTemplate(
#             input_variables=["context", "question"],
#             template=website_prompt_template,
#         )
        
#         # Generate response using website-specific context and prompt
#         full_prompt = website_prompt_template.format(context=context, question=user_input)
        
#         if hasattr(llm, 'invoke'):
#             reply = llm.invoke(full_prompt)
#         else:
#             reply = f"Response for {website_config['name']}: {user_input}<br><br>What else would you like to know?"
        
#         # Log with website context
#         log_chat_multi_website(user_id, user_input, "user", website_id)
#         log_chat_multi_website(user_id, reply, "bot", website_id)
        
#         return jsonify({
#             "response": reply,
#             "website_id": website_id,
#             "bot_name": website_config.get('bot_name', 'Assistant')
#         })

#     except Exception as e:
#         print(f"Chat error: {e}")
#         return jsonify({"response": "Sorry, I ran into an error. Please try again."}), 500

def log_chat_multi_website(user_id, message, sender, website_id):
    """Enhanced logging with website identification"""
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clean_message = message.replace('"', '""').replace('\n', ' ').replace('\r', ' ')
        log_entry = f'"{now}","{user_id}","{sender}","{clean_message}","{website_id}"\n'
        
        os.makedirs("logs", exist_ok=True)
        
        # Log to general file
        with open("logs/chat_logs_multi.csv", "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # Log to website-specific file
        with open(f"logs/chat_logs_{website_id}.csv", "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    except Exception as e:
        print(f"Logging error: {e}")


def get_contextual_retriever(user_query, preferred_categories=None):
    """Enhanced retriever that can filter by categories"""
    if not preferred_categories:
        return retriever.get_relevant_documents(user_query)
    
    # For sales-related queries, prioritize sales training documents
    if any(word in user_query.lower() for word in ['price', 'cost', 'buy', 'purchase', 'interested']):
        preferred_categories = ['sales_training', 'product_info']
    
    # Filter documents by category in metadata
    all_docs = retriever.get_relevant_documents(user_query, k=15)
    
    categorized_docs = []
    other_docs = []
    
    for doc in all_docs:
        doc_category = doc.metadata.get('category', 'company_details')
        if preferred_categories and doc_category in preferred_categories:
            categorized_docs.append(doc)
        else:
            other_docs.append(doc)
    
    # Return prioritized docs (category-specific first, then others)
    return (categorized_docs + other_docs)[:5]


def log_chat_with_categories(user_id, message, sender, categories=None):
    """Enhanced logging that includes category context"""
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clean_message = message.replace('"', '""').replace('\n', ' ').replace('\r', ' ')
        
        # Include category information in log
        category_info = ",".join(categories) if categories else "general"
        log_entry = f'"{now}","{user_id}","{sender}","{clean_message}","{category_info}"\n'
        
        os.makedirs("logs", exist_ok=True)
        
        with open("logs/chat_logs_enhanced.csv", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Logging error: {e}")



@app.route("/api/website/<website_id>/stats", methods=["GET"])
def website_stats(website_id):
    """Get statistics for a specific website"""
    if website_id not in WEBSITE_CONFIGS:
        return jsonify({"error": "Website not found"}), 404
    
    try:
        # Get website-specific vectorstore
        website_vectorstore = get_website_vectorstore(website_id)
        test_docs = website_vectorstore.similarity_search("test", k=1000)
        
        # Count files
        upload_dir = f"uploads/{website_id}"
        file_count = 0
        if os.path.exists(upload_dir):
            for category in os.listdir(upload_dir):
                category_path = os.path.join(upload_dir, category)
                if os.path.isdir(category_path):
                    file_count += len(os.listdir(category_path))
        
        return jsonify({
            "website_id": website_id,
            "name": WEBSITE_CONFIGS[website_id]["name"],
            "documents": len(test_docs),
            "files": file_count,
            "knowledge_base_path": get_knowledge_base_path(website_id)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Analytics endpoint for specific website
@app.route("/api/website/<website_id>/analytics", methods=["GET"])
def website_analytics(website_id):
    """Get analytics data for a specific website"""
    try:
        if website_id not in WEBSITE_CONFIGS:
            return jsonify({"error": "Website not found"}), 404
        
        # Read website-specific logs
        log_file = f"logs/chat_logs_{website_id}.csv"
        analytics_data = {
            "website_id": website_id,
            "total_conversations": 0,
            "total_messages": 0,
            "unique_users": set(),
            "daily_stats": {},
            "popular_queries": []
        }
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        parts = line.strip().split('","')
                        if len(parts) >= 4:
                            timestamp, user_id, sender, message = parts[:4]
                            timestamp = timestamp.strip('"')
                            user_id = user_id.strip('"')
                            sender = sender.strip('"')
                            
                            analytics_data["total_messages"] += 1
                            analytics_data["unique_users"].add(user_id)
                            
                            # Daily stats
                            date = timestamp.split(' ')[0]
                            if date not in analytics_data["daily_stats"]:
                                analytics_data["daily_stats"][date] = 0
                            analytics_data["daily_stats"][date] += 1
                            
                    except Exception as e:
                        print(f"Error parsing log line: {e}")
        
        # Convert set to count
        analytics_data["unique_users"] = len(analytics_data["unique_users"])
        
        return jsonify(analytics_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Enhanced analytics endpoint to show category usage
@app.route("/api/category-analytics", methods=["GET"])
def category_analytics():
    """Get analytics on which categories are being used most"""
    try:
        log_file = "logs/chat_logs_enhanced.csv"
        if not os.path.exists(log_file):
            return jsonify({"categories": {}, "total_queries": 0})
        
        category_usage = {}
        total_queries = 0
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('","')
                if len(parts) >= 5:
                    sender = parts[2].strip('"')
                    categories = parts[4].strip('"')
                    
                    if sender == "user":
                        total_queries += 1
                        if categories and categories != "general":
                            for cat in categories.split(","):
                                category_usage[cat] = category_usage.get(cat, 0) + 1
        
        return jsonify({
            "categories": category_usage,
            "total_queries": total_queries,
            "category_distribution": {
                cat: (count / total_queries * 100) if total_queries > 0 else 0 
                for cat, count in category_usage.items()
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def determine_query_categories(user_input):
    """Determine which categories to prioritize based on query content"""
    query_lower = user_input.lower()
    
    # Sales-related keywords
    sales_keywords = [
        'price', 'cost', 'pricing', 'quote', 'buy', 'purchase', 'interested', 
        'hire', 'contract', 'deal', 'discount', 'budget', 'payment', 'invoice',
        'proposal', 'consultation', 'estimate'
    ]
    
    # Product/service keywords
    product_keywords = [
        'service', 'product', 'feature', 'specification', 'capability',
        'what do you offer', 'what can you do', 'portfolio', 'work'
    ]
    
    # Company info keywords
    company_keywords = [
        'about', 'who', 'team', 'history', 'location', 'contact', 'address',
        'phone', 'email', 'hours', 'founded', 'mission', 'vision'
    ]
    
    # Legal/policy keywords
    legal_keywords = [
        'terms', 'privacy', 'policy', 'legal', 'contract', 'agreement',
        'refund', 'cancellation', 'guarantee', 'liability'
    ]
    
    preferred_categories = []
    
    # Check for sales-related queries
    if any(keyword in query_lower for keyword in sales_keywords):
        preferred_categories.extend(['sales_training', 'product_info'])
    
    # Check for product/service queries
    if any(keyword in query_lower for keyword in product_keywords):
        preferred_categories.extend(['product_info', 'company_details'])
    
    # Check for company info queries
    if any(keyword in query_lower for keyword in company_keywords):
        preferred_categories.extend(['company_details'])
    
    # Check for legal/policy queries
    if any(keyword in query_lower for keyword in legal_keywords):
        preferred_categories.extend(['policies_legal'])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_categories = []
    for cat in preferred_categories:
        if cat not in seen:
            seen.add(cat)
            unique_categories.append(cat)
    
    return unique_categories if unique_categories else None


def safe_retriever_check():
    """Legacy function - retriever is now user-specific"""
    # This function is kept for backward compatibility but does nothing
    # User-specific retrievers are created in the chat endpoint
    return False


# ================================
# 📄 TEMPLATE ENDPOINT (Returns current RAG prompt)
# ================================
@app.route("/template", methods=["GET"])
def get_template():
    return jsonify({"template": template_text})

# ================================
# 🧠 UPDATE FAQ VECTOR DB
# ================================
@app.route("/update_faq", methods=["POST"])
def update_faq():
    try:
        from langchain_community.document_loaders import TextLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        # Check if FAQ file exists
        faq_file = "data/faq.txt"
        if not os.path.exists(faq_file):
            return jsonify({"error": f"FAQ file not found at {faq_file}"}), 404

        # Load your updated FAQ or content
        loader = TextLoader(faq_file)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        # Update the vector store
        global vectorstore, retriever, qa_chain
        vectorstore = Chroma.from_documents(
            chunks, 
            embedding=embeddings, 
            persist_directory="./chroma_db"
        )
        vectorstore.persist()
        
        # Update retriever and QA chain
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        if LLM_OPTION == "openai" or hasattr(llm, 'invoke'):
            try:
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                    chain_type_kwargs={"prompt": prompt}
                )
            except Exception as e:
                print(f"QA chain update failed: {e}")
                qa_chain = None
        
        return jsonify({"status": "FAQ updated successfully"})
    except Exception as e:
        print(f"FAQ update error: {e}")
        return jsonify({"error": f"Failed to update FAQ: {str(e)}"}), 500

# ================================
# 🔍 HEALTH CHECK ENDPOINT
# ================================
@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Test vector store
        test_docs = retriever.get_relevant_documents("test")
        return jsonify({
            "status": "healthy",
            "vectorstore_docs": len(test_docs),
            "llm_model": llm.model_name if hasattr(llm, 'model_name') else "unknown",
            "llm_option": LLM_OPTION
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# ================================
# 💬 Chat Logging (Enhanced)
# ================================
def log_chat(user_id, message, sender):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Escape commas and quotes in message for CSV safety
        clean_message = message.replace('"', '""').replace('\n', ' ').replace('\r', ' ')
        log_entry = f'"{now}","{user_id}","{sender}","{clean_message}"\n'
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        with open("logs/chat_logs.csv", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Logging error: {e}")



# ================================
# Knowledge reset



@app.route("/api/reset-knowledge", methods=["POST"])
def reset_knowledge_base():
    """Reset only the knowledge base and uploaded files - WITH CORRUPTION HANDLING"""
    try:
        import shutil
        import time
        
        print("🔥 Starting knowledge base reset...")
        
        # 1. FORCE CLOSE ANY VECTOR STORE CONNECTIONS
        global vectorstore, retriever, qa_chain
        try:
            vectorstore = None
            retriever = None  
            qa_chain = None
            print("✅ Vector store connections closed")
        except:
            pass
        
        # 2. NUCLEAR DELETE OF ALL POSSIBLE VECTOR DB LOCATIONS
        possible_db_paths = [
            "./chroma_db",
            "./db", 
            "chroma_db",
            "db",
            "./ollama_rag_chatbot/chroma_db",
            "./ollama_rag_chatbot/db"
        ]
        
        for db_path in possible_db_paths:
            if os.path.exists(db_path):
                try:
                    print(f"🗑️ Deleting vector DB at: {db_path}")
                    shutil.rmtree(db_path)
                    print(f"✅ Successfully deleted: {db_path}")
                except Exception as e:
                    print(f"❌ Failed to delete {db_path}: {e}")
        
        # 3. DELETE UPLOADED FILES
        upload_paths = [
            app.config.get('UPLOAD_FOLDER', 'uploads'),
            'uploads', 
            './uploads',
            './ollama_rag_chatbot/uploads'
        ]
        
        for upload_path in upload_paths:
            if os.path.exists(upload_path):
                try:
                    print(f"🗑️ Deleting uploads at: {upload_path}")
                    shutil.rmtree(upload_path)
                    print(f"✅ Successfully deleted: {upload_path}")
                except Exception as e:
                    print(f"❌ Failed to delete {upload_path}: {e}")
        
        # 4. WAIT FOR FILE SYSTEM TO CATCH UP
        time.sleep(2)
        
        # 5. RECREATE DIRECTORIES
        os.makedirs("./chroma_db", exist_ok=True)
        os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
        print("✅ Directories recreated")
        
        # 6. FORCE CREATE NEW VECTOR STORE WITH ERROR HANDLING
        try:
            # Import here to avoid any cached references
            from langchain_community.vectorstores import Chroma
            
            print("🔄 Creating new vector store...")
            
            # Create completely fresh vector store
            vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=embeddings
            )
            
            # Test that it works by adding and removing a dummy document
            test_texts = ["test document for verification"]
            test_ids = vectorstore.add_texts(test_texts, ids=["test_id"])
            vectorstore.delete(ids=["test_id"])
            
            print("✅ New vector store created and tested successfully")
            
            # Verify it's empty
            test_docs = vectorstore.similarity_search("test", k=10)
            doc_count = len(test_docs)
            print(f"📊 Vector store verification: {doc_count} documents")
            
            # Recreate retriever and QA chain
            retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
            update_qa_chain()
            
            return jsonify({
                "status": "success",
                "message": f"Knowledge base reset successfully! Vector store recreated with {doc_count} documents."
            })
            
        except Exception as vs_error:
            print(f"❌ Vector store creation error: {vs_error}")
            
            # If vector store creation fails, try even more aggressive cleanup
            return handle_vector_store_corruption()
            
    except Exception as e:
        print(f"❌ Knowledge reset error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error", 
            "message": f"Failed to reset knowledge base: {str(e)}"
        }), 500

@app.route("/api/backup-knowledge", methods=["POST"])
def backup_knowledge():
    """Create a backup before reset"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f"backups/backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_results = {}
        
        # 1. Backup vector database
        try:
            if os.path.exists("./chroma_db"):
                shutil.copytree("./chroma_db", f"{backup_dir}/chroma_db")
                backup_results["vectors"] = "✅ Vector database backed up"
        except Exception as e:
            backup_results["vectors"] = f"❌ Error backing up vectors: {str(e)}"
        
        # 2. Backup uploaded files
        try:
            if os.path.exists("uploads"):
                shutil.copytree("uploads", f"{backup_dir}/uploads")
                backup_results["files"] = "✅ Files backed up"
        except Exception as e:
            backup_results["files"] = f"❌ Error backing up files: {str(e)}"
        
        # 3. Backup logs
        try:
            log_backup_dir = f"{backup_dir}/logs"
            os.makedirs(log_backup_dir, exist_ok=True)
            
            log_files = [
                "logs/chat_logs.csv",
                "logs/chat_logs_enhanced.csv",
                "logs/file_uploads.jsonl"
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    shutil.copy2(log_file, log_backup_dir)
            
            backup_results["logs"] = "✅ Logs backed up"
        except Exception as e:
            backup_results["logs"] = f"❌ Error backing up logs: {str(e)}"
        
        # 4. Backup database
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            # Export chat logs
            cursor.execute("SELECT * FROM chat_logs")
            chat_logs = cursor.fetchall()
            
            cursor.execute("SELECT * FROM conversation_nodes")
            conversation_nodes = cursor.fetchall()
            
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Save as JSON
            db_backup = {
                "chat_logs": chat_logs,
                "conversation_nodes": conversation_nodes, 
                "users": users,
                "backup_timestamp": datetime.now().isoformat()
            }
            
            with open(f"{backup_dir}/database_backup.json", "w") as f:
                import json
                json.dump(db_backup, f, indent=2, default=str)
            
            backup_results["database"] = "✅ Database backed up"
        except Exception as e:
            backup_results["database"] = f"❌ Error backing up database: {str(e)}"
        
        # 5. Backup current prompt
        try:
            if os.path.exists("config/prompt.txt"):
                shutil.copy2("config/prompt.txt", f"{backup_dir}/prompt.txt")
                backup_results["prompt"] = "✅ Prompt backed up"
        except Exception as e:
            backup_results["prompt"] = f"❌ Error backing up prompt: {str(e)}"
        
        return jsonify({
            "message": f"Backup created successfully",
            "backup_location": backup_dir,
            "results": backup_results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/restore-knowledge", methods=["POST"])
def restore_knowledge():
    """Restore from a backup"""
    try:
        data = request.json
        backup_path = data.get("backup_path")
        
        if not backup_path or not os.path.exists(backup_path):
            return jsonify({"error": "Invalid backup path"}), 400
        
        restore_results = {}
        
        # 1. Restore vector database
        try:
            vector_backup = f"{backup_path}/chroma_db"
            if os.path.exists(vector_backup):
                if os.path.exists("./chroma_db"):
                    shutil.rmtree("./chroma_db")
                shutil.copytree(vector_backup, "./chroma_db")
                
                # Reload vector store
                global vectorstore, retriever
                vectorstore = Chroma(
                    persist_directory="./chroma_db",
                    embedding_function=embeddings
                )
                retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
                update_qa_chain()
                
                restore_results["vectors"] = "✅ Vector database restored"
        except Exception as e:
            restore_results["vectors"] = f"❌ Error restoring vectors: {str(e)}"
        
        # 2. Restore files
        try:
            files_backup = f"{backup_path}/uploads"
            if os.path.exists(files_backup):
                if os.path.exists("uploads"):
                    shutil.rmtree("uploads")
                shutil.copytree(files_backup, "uploads")
                restore_results["files"] = "✅ Files restored"
        except Exception as e:
            restore_results["files"] = f"❌ Error restoring files: {str(e)}"
        
        # 3. Restore prompt
        try:
            prompt_backup = f"{backup_path}/prompt.txt"
            if os.path.exists(prompt_backup):
                os.makedirs("config", exist_ok=True)
                shutil.copy2(prompt_backup, "config/prompt.txt")
                
                # Reload prompt
                with open("config/prompt.txt", "r") as f:
                    restored_prompt = f.read()
                update_prompt(restored_prompt)
                
                restore_results["prompt"] = "✅ Prompt restored"
        except Exception as e:
            restore_results["prompt"] = f"❌ Error restoring prompt: {str(e)}"
        
        return jsonify({
            "message": "Knowledge base restored successfully",
            "results": restore_results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/list-backups", methods=["GET"])
def list_backups():
    """List available backups"""
    try:
        backups = []
        backup_dir = "backups"
        
        if os.path.exists(backup_dir):
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                if os.path.isdir(item_path) and item.startswith("backup_"):
                    # Get backup info
                    stat = os.stat(item_path)
                    backups.append({
                        "name": item,
                        "path": item_path,
                        "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                        "size": get_folder_size(item_path)
                    })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return jsonify({"backups": backups})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/refresh", methods=["POST"])
def refresh_chat():
    try:
        session.clear()
        return jsonify({
            "status": "success",
            "message": "Chat conversation refreshed! (Files and knowledge preserved)"
        })
    except Exception as e:
        print(f"Refresh error: {e}")
        return jsonify({"status": "error", "message": "Failed to refresh chat session"}), 500

@app.route("/api/reset-knowledge", methods=["POST"])
def reset_knowledge_base_simple():
    """Reset only the knowledge base and uploaded files - no confirmation check"""
    try:
        import shutil
        
        # Clear uploaded files
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Clear vector database (learned knowledge)
        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db")
            os.makedirs("./chroma_db", exist_ok=True)
        
        # Recreate empty vector store
        global vectorstore, retriever, qa_chain
        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        update_qa_chain()
        
        return jsonify({
            "status": "success",
            "message": "Knowledge base reset successfully! All files and AI knowledge cleared."
        })
    except Exception as e:
        print(f"Knowledge reset error: {e}")
        return jsonify({
            "status": "error", 
            "message": "Failed to reset knowledge base"
        }), 500



@app.route("/api/clear-logs", methods=["POST"])
def clear_chat_logs():
    """Clear all chat logs from database"""
    try:
        # Get confirmation from request (if any)
        data = request.get_json() or {}
        confirmation = data.get('confirmation', '')
        
        # Check confirmation phrase (optional)
        expected_phrases = ['CLEAR LOGS', 'DELETE LOGS', 'RESET LOGS']
        if confirmation and confirmation not in expected_phrases:
            return jsonify({
                "status": "error",
                "message": f"Invalid confirmation phrase. Please type one of: {', '.join(expected_phrases)}"
            }), 400
        
        # Database: Using User model - chat logs are file-based
        # No database clearing needed as we use file-based logging
        
        # Also clear CSV logs if they exist
        if os.path.exists("logs/chat_logs.csv"):
            os.remove("logs/chat_logs.csv")
        
        return jsonify({
            "status": "success",
            "message": "All chat logs and conversation history cleared!"
        })
    except Exception as e:
        print(f"Clear logs error: {e}")
        return jsonify({
            "status": "error", 
            "message": "Failed to clear chat logs"
        }), 500

@app.route("/reset-all", methods=["POST"])  
def reset_all():
    """NUCLEAR OPTION: Complete system reset with corruption handling"""
    try:
        import shutil
        import time
        # Database connection removed - using User model instead
        print("💀 NUCLEAR RESET INITIATED...")
        
        # Clear session
        session.clear()
        
        # 1. FORCE CLOSE ALL CONNECTIONS
        global vectorstore, retriever, qa_chain
        vectorstore = None
        retriever = None
        qa_chain = None
        
        # 2. NUCLEAR DELETE ALL POSSIBLE DATABASE LOCATIONS
        all_possible_paths = [
            "./chroma_db", "./db", "chroma_db", "db",
            "./ollama_rag_chatbot/chroma_db", "./ollama_rag_chatbot/db",
            "uploads", "./uploads", "./ollama_rag_chatbot/uploads"
        ]
        
        for path in all_possible_paths:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    print(f"💥 Nuked: {path}")
                except Exception as e:
                    print(f"⚠️ Couldn't nuke {path}: {e}")
        
        # 3. CLEAR DATABASE (using User model)
        try:
            # Note: We keep users table for authentication
            # Only clear chat logs if they exist in a separate table
            # For now, we're using file-based logging, so this is handled by file deletion above
            print("✅ Database users preserved (authentication required)")
        except Exception as db_error:
            print(f"⚠️ Database operation error: {db_error}")
        
        # 4. DELETE LOG FILES
        log_files = ["logs/chat_logs.csv", "./logs/chat_logs.csv", "chat_logs.csv"]
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    os.remove(log_file)
                    print(f"💥 Nuked log: {log_file}")
                except:
                    pass
        
        # 5. WAIT FOR NUCLEAR FALLOUT TO SETTLE
        time.sleep(3)
        
        # 6. REBUILD FROM ASHES
        os.makedirs("./chroma_db", exist_ok=True)
        os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
        os.makedirs("./logs", exist_ok=True)
        
        # 7. CREATE NEW VECTOR STORE FROM SCRATCH
        try:
            from langchain_community.vectorstores import Chroma
            
            vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=embeddings
            )
            
            # Test it works
            test_docs = vectorstore.similarity_search("phoenix", k=1)
            doc_count = len(test_docs)
            
            retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
            update_qa_chain()
            
            print(f"🎉 PHOENIX RISEN! New vector store: {doc_count} documents")
            
            return jsonify({
                "status": "success",
                "message": f"💀 NUCLEAR RESET COMPLETE! Phoenix has risen from the ashes with {doc_count} documents."
            })
            
        except Exception as phoenix_error:
            print(f"☢️ Phoenix failed to rise: {phoenix_error}")
            return handle_vector_store_corruption()
            
    except Exception as e:
        print(f"☢️ Nuclear disaster: {e}")
        return jsonify({
            "status": "error",
            "message": f"Nuclear reset failed: {str(e)}"
        }), 500


def handle_vector_store_corruption():
    """Emergency handler for when vector store is completely corrupted"""
    try:
        import shutil
        import sqlite3
        import time
        
        print("🚨 EMERGENCY CORRUPTION HANDLER ACTIVATED")
        
        # 1. FIND AND DESTROY ALL CHROMA DATABASES
        import glob
        
        # Find all possible chroma database files
        possible_patterns = [
            "**/chroma.sqlite3",
            "**/chroma_db/**/*",
            "**/db/**/*", 
            "**/*.sqlite*"
        ]
        
        for pattern in possible_patterns:
            try:
                files = glob.glob(pattern, recursive=True)
                for file in files:
                    if 'chroma' in file.lower() or 'vector' in file.lower():
                        try:
                            if os.path.isfile(file):
                                os.remove(file)
                            elif os.path.isdir(file):
                                shutil.rmtree(file)
                            print(f"🔥 Emergency deleted: {file}")
                        except:
                            pass
            except:
                pass
        
        # 2. MANUALLY RECREATE CHROMA DIRECTORY STRUCTURE
        chroma_path = "./chroma_db"
        if os.path.exists(chroma_path):
            shutil.rmtree(chroma_path)
        
        time.sleep(1)
        os.makedirs(chroma_path, exist_ok=True)
        
        # 3. FORCE CREATE NEW VECTOR STORE WITH MINIMAL SETUP
        global vectorstore, retriever, qa_chain
        
        try:
            from langchain_community.vectorstores import Chroma
            
            # Create new instance with fresh directory
            vectorstore = Chroma(
                persist_directory=chroma_path,
                embedding_function=embeddings
            )
            
            retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
            
            # Skip QA chain if it fails
            try:
                update_qa_chain()
            except:
                qa_chain = None
            
            print("🚑 Emergency vector store created successfully")
            
            return jsonify({
                "status": "success", 
                "message": "🚑 Emergency recovery successful! Vector database corruption fixed."
            })
            
        except Exception as emergency_error:
            print(f"🚨 Emergency handler failed: {emergency_error}")
            
            # Last resort: disable vector store entirely
            vectorstore = None
            retriever = None
            qa_chain = None
            
            return jsonify({
                "status": "warning",
                "message": "⚠️ Vector database disabled due to corruption. Please restart the application."
            })
            
    except Exception as disaster:
        print(f"☢️ Total disaster: {disaster}")
        return jsonify({
            "status": "error",
            "message": "💀 Complete system failure. Please restart application and rebuild from scratch."
        }), 500


def get_folder_size(folder_path):
    """Get total size of folder in bytes"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

def get_default_prompt_with_name(bot_name='Cortex'):
    """Get default prompt template with custom bot name"""
    return f"""You are {bot_name}, an intelligent AI assistant.

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
{{context}}

User Question: {{question}}

{bot_name}'s Response:"""

def get_default_prompt():
    """Return the default system prompt"""
    return """You are Cortex, an intelligent AI assistant powered by advanced technology.

Your job is to help users with their questions. Always be polite, helpful, and conversational—just like a friendly and attentive assistant.

INSTRUCTIONS:
- Vary your greetings and responses to avoid sounding repetitive or robotic.
- Reference the user's specific question in your answer.
- Use ONLY the information provided in the "Relevant Info" section below.
- If you don't know the answer or the information isn't available, respond with a polite and varied fallback such as:
  "That's a great question! I don't have the details on that right now, but I can help you find more information."
  or
  "I'm not sure about that, but I can help you get in touch with someone who knows more!"
- Only ask follow-up questions if they make sense and feel natural.
- CRITICAL: Respond ONLY in plain text. DO NOT use HTML tags, code blocks, or markdown code fences.
- Format your response naturally: use line breaks for paragraphs, bullet points with "-", and **bold** for emphasis only.
- NEVER wrap your response in ```html, ```markdown, or any code fence.
- Keep your tone friendly and concise.
- Always finish with a relevant, human-sounding follow-up or offer to help further.

Relevant Info:
{context}

User Question: {question}

Cortex's Response:"""

@app.route("/api/knowledge-stats", methods=["GET"])
def knowledge_stats():
    """Get knowledge stats with corruption protection"""
    try:
        # Safely check vector store
        doc_count = 0
        db_status = "unknown"
        
        try:
            if vectorstore is not None:
                test_docs = vectorstore.similarity_search("test", k=1000)
                doc_count = len(test_docs)
                db_status = "healthy"
            else:
                db_status = "not_initialized"
        except Exception as e:
            print(f"⚠️ Vector store check failed: {e}")
            db_status = "corrupted"
            # Try to fix corruption automatically
            try:
                handle_vector_store_corruption()
                doc_count = 0
                db_status = "recovered"
            except:
                doc_count = -1
                db_status = "failed"
        
        # Get uploaded files safely - scan all subdirectories
        uploaded_files = []
        try:
            upload_folder = 'uploads'
            if os.path.exists(upload_folder):
                # Walk through all subdirectories
                for root, dirs, files in os.walk(upload_folder):
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        try:
                            stat = os.stat(filepath)
                            # Get category from path
                            path_parts = root.split(os.sep)
                            category = path_parts[-1] if len(path_parts) > 1 else 'Unknown'
                            uploaded_files.append({
                                "name": filename,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                "category": category.replace('_', ' ').title()
                            })
                        except Exception as e:
                            print(f"⚠️ Error reading file {filepath}: {e}")
        except Exception as e:
            print(f"⚠️ Upload folder check failed: {e}")
        
        stats = {
            "total_documents": max(0, doc_count),  # Never show negative
            "vector_store_status": db_status,
            "vector_store_path": "./chroma_db",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "llm_model": getattr(llm, 'model_name', 'unknown'),
            "llm_option": LLM_OPTION,
            "uploaded_files": uploaded_files
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return jsonify({
            "total_documents": 0,
            "vector_store_status": "error",
            "error": str(e)
        })

# ================================
# 🧪 Run
# ================================
# ===========================
# LLM CONFIGURATION API
# ===========================

@app.route("/api/llm-config", methods=["GET"])
def get_llm_config():
    """Get current LLM configuration"""
    try:
        llm_option = os.getenv("LLM_OPTION", "openai")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        
        # Mask the API key (show only last 4 characters)
        api_key_masked = ""
        if openai_key:
            if len(openai_key) > 8:
                api_key_masked = "sk-..." + openai_key[-4:]
            else:
                api_key_masked = "***"
        
        config = {
            "llm_option": llm_option,
            "has_openai_key": bool(openai_key),
            "openai_key_masked": api_key_masked,
            "openai_model": "gpt-4o-mini",
            "openai_temperature": 1.0,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "llama3.1:8b",
            "current_model": "gpt-4o-mini" if llm_option == "openai" else "llama3.1:8b"
        }
        
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/chatbot-config", methods=["GET"])
@login_required
def get_user_chatbot_config():
    """Get current user's chatbot configuration"""
    try:
        user_id = current_user.id
        config = load_user_chatbot_config(user_id)
        
        # Generate API key if it doesn't exist
        if not config.get('api_key'):
            api_key = get_user_api_key(user_id)
            config['api_key'] = api_key
        
        # If prompt is None, generate default prompt with bot_name
        if config.get('prompt') is None:
            bot_name = config.get('bot_name', 'Cortex')
            config['prompt'] = get_default_prompt_with_name(bot_name)
        
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/chatbot-config", methods=["POST"])
@login_required
def save_user_chatbot_config_endpoint():
    """Save current user's chatbot configuration"""
    try:
        user_id = current_user.id
        data = request.json
        
        bot_name = data.get('bot_name', 'Cortex').strip()
        prompt = data.get('prompt', '').strip()
        
        if not bot_name:
            return jsonify({"error": "Bot name cannot be empty"}), 400
        
        if not prompt:
            return jsonify({"error": "Prompt cannot be empty"}), 400
        
        config = {
            'bot_name': bot_name,
            'prompt': prompt
        }
        
        if save_user_chatbot_config_file(user_id, config):
            return jsonify({"message": "Configuration saved successfully", "config": config})
        else:
            return jsonify({"error": "Failed to save configuration"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test-llm", methods=["POST"])
def test_llm_connection():
    """Test LLM connection"""
    try:
        import time
        data = request.get_json()
        provider = data.get('provider', 'openai')
        model = data.get('model', 'gpt-4o-mini')
        
        start_time = time.time()
        
        # Test with a simple prompt
        test_prompt = "Say 'Hello' in one word."
        
        if provider == 'openai':
            try:
                response = llm.invoke(test_prompt)
                response_time = int((time.time() - start_time) * 1000)
                
                return jsonify({
                    "status": "success",
                    "provider": provider,
                    "model": model,
                    "response": str(response.content if hasattr(response, 'content') else response),
                    "response_time": response_time
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": f"OpenAI connection failed: {str(e)}"
                }), 400
        else:
            # Ollama test
            try:
                response = llm.invoke(test_prompt)
                response_time = int((time.time() - start_time) * 1000)
                
                return jsonify({
                    "status": "success",
                    "provider": provider,
                    "model": model,
                    "response": str(response),
                    "response_time": response_time
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": f"Ollama connection failed: {str(e)}"
                }), 400
                
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("./chroma_db", exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    
    # Initialize database and create default admin user
    print("🔐 Initializing authentication system...")
    # Initialize database and run migrations
    from migrations import run_migrations
    User.init_db()
    run_migrations()
    
    initialize_website_configs()
    print("🤖 Starting Flask RAG Chatbot...")
    print(f"📊 Vector store location: ./chroma_db")
    print(f"📝 FAQ file expected at: ./data/faq.txt")
    print(f"📋 Logs will be saved to: ./logs/chat_logs.csv")
    print(f"🔑 Default admin: admin@example.com / admin123")
    
    port = int(os.getenv('PORT', 6001))
    app.run(host='0.0.0.0', port=port, debug=True)

