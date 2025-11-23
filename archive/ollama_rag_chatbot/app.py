# from flask import Flask, request, jsonify, render_template, session, send_from_directory
# from flask_cors import CORS
# import os
# from datetime import datetime
# import re
# import shutil
# import json
# import time

# import mysql.connector
# from db_config import DB_CONFIG

# # Updated imports for dashboard functionality
# try:
#     from langchain_community.vectorstores import Chroma  # ✅ Correct import
# except ImportError:
#     from langchain.vectorstores import Chroma  # Fallback (legacy)

# from langchain_community.embeddings import HuggingFaceEmbeddings  # ✅ Updated
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from werkzeug.utils import secure_filename
# import hashlib
# from urllib.parse import urlparse

# # App setup
# app = Flask(__name__)
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "admin123")
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# app.config['UPLOAD_FOLDER'] = 'uploads'
# CORS(app)

# # Create upload directory
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # Allowed file extensions
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'csv'}

# # 🎯 Suggested messages for the UI
# SUGGESTED_MESSAGES = [
#     "What services do you offer?",
#     "How can I contact support?",
#     "What are your business hours?",
#     "Tell me about your pricing",
#     "How do I get started?"
# ]

# # Website configuration - Enhanced with LLM-specific settings
# WEBSITE_CONFIGS = {
#     'sourceselect.ca': {
#         'name': 'SourceSelect',
#         'bot_name': 'Bob',
#         'primary_color': '#667eea',
#         'knowledge_base': 'sourceselect',
#         'allowed_origins': ['https://sourceselect.ca', 'https://www.sourceselect.ca'],
#         'custom_prompt': None,  # Uses default if None
#         'features': ['sales_tracking', 'lead_generation', 'analytics'],
#         'llm_config': {  # Website-specific LLM settings
#             'provider': 'openai',
#             'model': 'gpt-4o-mini',
#             'temperature': 1.0
#         }
#     },
#     'example-business.com': {
#         'name': 'Example Business',
#         'bot_name': 'Alex',
#         'primary_color': '#28a745',
#         'knowledge_base': 'example_business',
#         'allowed_origins': ['https://example-business.com'],
#         'custom_prompt': 'You are Alex, a helpful assistant for Example Business...',
#         'features': ['basic_support'],
#         'llm_config': {
#             'provider': 'ollama',
#             'model': 'llama3.1:8b',
#             'temperature': 0.7
#         }
#     },
#     'default': {
#         'name': 'AI Assistant',
#         'bot_name': 'Assistant',
#         'primary_color': '#6c757d',
#         'knowledge_base': 'default',
#         'allowed_origins': ['*'],
#         'llm_config': {
#             'provider': 'openai',
#             'model': 'gpt-4o-mini',
#             'temperature': 1.0
#         }
#     }
# }

# # File categories configuration
# FILE_CATEGORIES = {
#     'company_details': {
#         'name': 'Company Details',
#         'description': 'Business information, services, team details, contact info',
#         'vector_prefix': 'company_',
#         'color': '#007bff'
#     },
#     'sales_training': {
#         'name': 'Sales Training',
#         'description': 'Sales scripts, objection handling, conversation examples',
#         'vector_prefix': 'sales_',
#         'color': '#28a745'
#     },
#     'product_info': {
#         'name': 'Product Information', 
#         'description': 'Product specs, pricing, features, documentation',
#         'vector_prefix': 'product_',
#         'color': '#ffc107'
#     },
#     'policies_legal': {
#         'name': 'Policies & Legal',
#         'description': 'Terms of service, privacy policy, legal documents',
#         'vector_prefix': 'legal_',
#         'color': '#dc3545'
#     }
# }

# # ================================
# # 🔐 ENHANCED LLM CONFIGURATION MANAGEMENT
# # ================================

# def load_llm_config():
#     """Load global LLM configuration with fallback to environment variables"""
#     config_file = "config/llm_config.json"
    
#     default_config = {
#         "global_provider": os.getenv("LLM_PROVIDER", "openai"),
#         "openai": {
#             "api_key": os.getenv("OPENAI_API_KEY", ""),
#             "models": {
#                 "gpt-4o-mini": {"temperature": 1.0},
#                 "gpt-4o": {"temperature": 0.7},
#                 "gpt-4": {"temperature": 0.7},
#                 "gpt-3.5-turbo": {"temperature": 0.9}
#             },
#             "default_model": "gpt-4o-mini"
#         },
#         "ollama": {
#             "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
#             "models": {
#                 "llama3.1:8b": {"temperature": 0.7},
#                 "llama3.1:70b": {"temperature": 0.7},
#                 "mistral": {"temperature": 0.8},
#                 "codellama": {"temperature": 0.5}
#             },
#             "default_model": "llama3.1:8b"
#         },
#         "website_overrides": {}  # Per-website LLM configurations
#     }
    
#     try:
#         os.makedirs("config", exist_ok=True)
#         if os.path.exists(config_file):
#             with open(config_file, 'r') as f:
#                 saved_config = json.load(f)
#                 # Merge saved config with defaults
#                 for key in default_config:
#                     if key in saved_config:
#                         if isinstance(default_config[key], dict):
#                             default_config[key].update(saved_config[key])
#                         else:
#                             default_config[key] = saved_config[key]
#     except Exception as e:
#         print(f"Warning: Could not load LLM config file: {e}")
    
#     return default_config

# def save_llm_config(config):
#     """Save LLM configuration to file"""
#     config_file = "config/llm_config.json"
#     try:
#         os.makedirs("config", exist_ok=True)
#         with open(config_file, 'w') as f:
#             json.dump(config, f, indent=2)
#         return True
#     except Exception as e:
#         print(f"Error saving LLM config: {e}")
#         return False

# def get_effective_llm_config(website_id=None):
#     """Get effective LLM configuration for a specific website or global"""
#     global_config = load_llm_config()
    
#     # Check for website-specific override
#     if website_id and website_id in global_config.get("website_overrides", {}):
#         website_override = global_config["website_overrides"][website_id]
#         return {
#             "provider": website_override.get("provider", global_config["global_provider"]),
#             "model": website_override.get("model"),
#             "temperature": website_override.get("temperature"),
#             "config": global_config
#         }
    
#     # Check WEBSITE_CONFIGS for default
#     if website_id and website_id in WEBSITE_CONFIGS:
#         website_config = WEBSITE_CONFIGS[website_id].get("llm_config", {})
#         return {
#             "provider": website_config.get("provider", global_config["global_provider"]),
#             "model": website_config.get("model"),
#             "temperature": website_config.get("temperature"),
#             "config": global_config
#         }
    
#     # Return global default
#     provider = global_config["global_provider"]
#     provider_config = global_config[provider]
#     default_model = provider_config["default_model"]
    
#     return {
#         "provider": provider,
#         "model": default_model,
#         "temperature": provider_config["models"][default_model]["temperature"],
#         "config": global_config
#     }

# def create_llm_instance(website_id=None):
#     """Create LLM instance based on website-specific or global configuration"""
#     effective_config = get_effective_llm_config(website_id)
#     provider = effective_config["provider"]
#     model = effective_config["model"]
#     temperature = effective_config["temperature"]
    
#     if provider == "openai":
#         try:
#             from langchain_openai import ChatOpenAI
#             api_key = effective_config["config"]["openai"]["api_key"] or os.getenv("OPENAI_API_KEY")
            
#             if not api_key:
#                 print(f"⚠️ OpenAI API key not found for website {website_id}")
#                 return create_mock_llm(), "mock"
            
#             llm = ChatOpenAI(
#                 model=model,
#                 temperature=temperature,
#                 openai_api_key=api_key
#             )
#             print(f"🤖 Using OpenAI model: {model} for website {website_id or 'global'}")
#             return llm, "openai"
            
#         except Exception as e:
#             print(f"Failed to initialize OpenAI for {website_id}: {e}")
#             return create_mock_llm(), "mock"
    
#     elif provider == "ollama":
#         try:
#             from langchain_community.llms import Ollama
#             base_url = effective_config["config"]["ollama"]["base_url"]
            
#             llm = Ollama(
#                 model=model,
#                 temperature=temperature,
#                 base_url=base_url
#             )
#             print(f"🤖 Using Ollama model: {model} for website {website_id or 'global'}")
#             return llm, "ollama"
            
#         except Exception as e:
#             print(f"Failed to initialize Ollama for {website_id}: {e}")
#             return create_mock_llm(), "mock"
    
#     return create_mock_llm(), "mock"

# def create_mock_llm():
#     """Create mock LLM for fallback"""
#     class MockLLM:
#         def invoke(self, prompt):
#             return "I'm a mock response. Please configure a valid LLM provider in the dashboard."
        
#         @property
#         def model_name(self):
#             return "mock-llm"
    
#     return MockLLM()

# # Global LLM instances cache
# llm_instances = {}

# def get_llm_for_website(website_id):
#     """Get or create LLM instance for specific website"""
#     if website_id not in llm_instances:
#         llm, provider = create_llm_instance(website_id)
#         llm_instances[website_id] = {"llm": llm, "provider": provider}
    
#     return llm_instances[website_id]["llm"], llm_instances[website_id]["provider"]

# # Initialize default LLM - Enhanced fallback logic
# try:
#     default_config = get_effective_llm_config()
#     llm, LLM_OPTION = create_llm_instance()
# except Exception as e:
#     print(f"LLM initialization failed: {e}")
#     # Fallback to ollama
#     try:
#         from langchain_community.llms import Ollama
#         llm = Ollama(
#             model="llama3.1:8b",
#             temperature=0.7,
#             base_url="http://localhost:11434"
#         )
#         LLM_OPTION = "ollama"
#         print(f"🤖 Using Ollama fallback: llama3.1:8b")
#     except ImportError:
#         print("❌ Ollama not available. Install with: pip install langchain-community")
#         llm = create_mock_llm()
#         LLM_OPTION = "mock"
#         print("🤖 Using Mock LLM (for testing only)")

# # 🔍 Embeddings & Vector DB setup
# embeddings = HuggingFaceEmbeddings()

# # ✅ Chroma vector store (no `.persist()` needed)
# vectorstore = Chroma(
#     persist_directory="./chroma_db",
#     embedding_function=embeddings
# )

# # RAG prompt template - Load from file or use default
# def load_saved_prompt():
#     try:
#         if os.path.exists("config/prompt.txt"):
#             with open("config/prompt.txt", "r", encoding="utf-8") as f:
#                 return f.read()
#     except:
#         pass
#     return None

# saved_prompt = load_saved_prompt()
# template_text = saved_prompt if saved_prompt else """
# You are Bob, a real human virtual assistant for SourceSelect.ca.

# Your job is to help users with their questions about SourceSelect.ca and its services. Always be polite, helpful, and conversational—just like a friendly and attentive human agent.

# INSTRUCTIONS:
# - Vary your greetings and responses to avoid sounding repetitive or robotic.
# - Reference the user's specific question in your answer.
# - Use ONLY the information provided in the "Relevant Info" section below.
# - If you don't know the answer or the information isn't available, respond with a polite and varied fallback such as:
#   "That's a great question! I don't have the details on that right now, but I can help connect you to the right person."
#   or
#   "I'm not sure about that, but I can help you get in touch with someone who knows more!"
# - Only ask follow-up questions if they make sense and feel natural.
# - Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
# - Keep your tone friendly and concise.
# - Always finish with a relevant, human-sounding follow-up or offer to help further.

# Relevant Info:
# {context}

# User Question: {question}

# Bob's Response:
# """

# prompt = PromptTemplate(
#     input_variables=["context", "question"],
#     template=template_text,
# )

# retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# # QA chains cache
# qa_chains = {}

# def get_qa_chain_for_website(website_id):
#     """Get or create QA chain for specific website"""
#     if website_id not in qa_chains:
#         llm, provider = get_llm_for_website(website_id)
        
#         if provider != "mock" and hasattr(llm, 'invoke'):
#             try:
#                 qa_chain = RetrievalQA.from_chain_type(
#                     llm=llm,
#                     chain_type="stuff",
#                     retriever=retriever,
#                     chain_type_kwargs={"prompt": prompt}
#                 )
#                 qa_chains[website_id] = qa_chain
#                 print(f"✅ QA Chain created for website {website_id}")
#             except Exception as e:
#                 print(f"❌ QA Chain creation failed for {website_id}: {e}")
#                 qa_chains[website_id] = None
#         else:
#             qa_chains[website_id] = None
    
#     return qa_chains[website_id]

# def update_qa_chain():
#     """Update QA chain with current LLM and prompt"""
#     global qa_chain
#     if LLM_OPTION != "mock" and hasattr(llm, 'invoke'):
#         try:
#             qa_chain = RetrievalQA.from_chain_type(
#                 llm=llm,
#                 chain_type="stuff",
#                 retriever=retriever,
#                 chain_type_kwargs={"prompt": prompt}
#             )
#             print("✅ QA Chain updated successfully")
#         except Exception as e:
#             print(f"❌ QA Chain update failed: {e}")
#             qa_chain = None
#     else:
#         qa_chain = None
#         print("⚠️ Using mock LLM - QA chain not created")

# # Create default QA chain
# qa_chain = get_qa_chain_for_website('default')

# def initialize_website_configs():
#     """Initialize website configurations from database"""
#     try:
#         # Add your database initialization logic here if needed
#         print("✅ Website configurations initialized")
#     except Exception as e:
#         print(f"⚠️ Website config initialization failed: {e}")

# def get_knowledge_base_path(website_id):
#     """Get the knowledge base path for a specific website"""
#     return f"./chroma_db_{website_id}"

# def get_website_vectorstore(website_id):
#     """Get or create website-specific vector store"""
#     kb_path = get_knowledge_base_path(website_id)
#     try:
#         website_vectorstore = Chroma(
#             persist_directory=kb_path,
#             embedding_function=embeddings
#         )
#         return website_vectorstore
#     except Exception as e:
#         print(f"Error creating vectorstore for {website_id}: {e}")
#         # Fallback to global vectorstore
#         return vectorstore

# # ================================
# # 🌐 WEB UI ROUTES
# # ================================

# @app.route("/website-a")
# def website():
#     return render_template("website_a.html")

# @app.route("/")
# def index():
#     session.clear()
#     return render_template("index.html", suggested=SUGGESTED_MESSAGES)

# @app.route("/widget")
# def widget_multi():
#     """Serve widget with website-specific configuration"""
#     website_id = request.args.get('website_id', 'default')
    
#     if website_id not in WEBSITE_CONFIGS:
#         website_id = 'default'
    
#     config = WEBSITE_CONFIGS[website_id]
    
#     # Pass website-specific config to template
#     return render_template("widget.html", 
#                          suggested=SUGGESTED_MESSAGES,
#                          website_id=website_id,
#                          bot_name=config.get('bot_name', 'Assistant'),
#                          primary_color=config.get('primary_color', '#667eea'),
#                          website_name=config.get('name', 'Website'))

# @app.route("/embed.js")
# def serve_embed_script_multi():
#     """Serve website-specific embed script"""
#     website_id = request.args.get('website_id', 'default')
    
#     if website_id not in WEBSITE_CONFIGS:
#         website_id = 'default'
    
#     config = WEBSITE_CONFIGS[website_id]
    
#     # Generate dynamic embed script with website-specific config
#     embed_script = f"""
# (function() {{
#     window.CHATBOT_CONFIG = {{
#         apiBaseUrl: '{request.host_url.rstrip('/')}',
#         websiteId: '{website_id}',
#         botName: '{config.get('bot_name', 'Assistant')}',
#         primaryColor: '{config.get('primary_color', '#667eea')}',
#         websiteName: '{config.get('name', 'Website')}'
#     }};
    
#     // Load the main embed script
#     const script = document.createElement('script');
#     script.src = '{request.host_url.rstrip('/')}/static/embed.js';
#     script.defer = true;
#     document.head.appendChild(script);
# }})();
# """
    
#     return embed_script, 200, {'Content-Type': 'application/javascript'}

# @app.route("/dashboard")
# def dashboard():
#     return render_template("dashboard_v1.html")

# def get_website_config(request):
#     """Determine which website configuration to use based on request"""
#     origin = request.headers.get('Origin', '')
#     referer = request.headers.get('Referer', '')
#     website_id = request.args.get('website_id') or (request.json.get('website_id') if request.is_json else None)
#     host = request.headers.get('Host', '')
    
#     # Priority: explicit website_id > origin > referer > host > default
#     if website_id and website_id in WEBSITE_CONFIGS:
#         return website_id, WEBSITE_CONFIGS[website_id]
    
#     # Check origin/referer against allowed origins
#     for website_id, config in WEBSITE_CONFIGS.items():
#         if website_id == 'default':
#             continue
        
#         allowed_origins = config.get('allowed_origins', [])
#         if any(allowed_origin in origin or allowed_origin in referer for allowed_origin in allowed_origins):
#             return website_id, config
    
#     # Default fallback
#     return 'default', WEBSITE_CONFIGS['default']

# # ================================
# # 🤖 LLM MANAGEMENT API ENDPOINTS
# # ================================

# @app.route("/api/llm-config", methods=["GET"])
# def get_llm_config_api():
#     """Get current LLM configuration"""
#     try:
#         website_id = request.args.get('website_id', 'default')
#         effective_config = get_effective_llm_config(website_id)
#         global_config = effective_config["config"]
        
#         safe_config = {
#             "website_id": website_id,
#             "effective_provider": effective_config["provider"],
#             "effective_model": effective_config["model"],
#             "effective_temperature": effective_config["temperature"],
#             "global_provider": global_config["global_provider"],
#             "openai": {
#                 "has_api_key": bool(global_config["openai"]["api_key"]),
#                 "models": global_config["openai"]["models"],
#                 "default_model": global_config["openai"]["default_model"]
#             },
#             "ollama": {
#                 "base_url": global_config["ollama"]["base_url"],
#                 "models": global_config["ollama"]["models"],
#                 "default_model": global_config["ollama"]["default_model"]
#             },
#             "website_overrides": global_config.get("website_overrides", {}),
#             "available_websites": list(WEBSITE_CONFIGS.keys())
#         }
        
#         return jsonify(safe_config)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/api/llm-config", methods=["POST"])
# def update_llm_config_api():
#     """Update LLM configuration"""
#     try:
#         data = request.json
#         config_type = data.get("config_type", "global")  # "global" or "website"
#         website_id = data.get("website_id")
        
#         global_config = load_llm_config()
        
#         if config_type == "global":
#             # Update global configuration
#             if "global_provider" in data:
#                 global_config["global_provider"] = data["global_provider"]
            
#             if "openai" in data:
#                 openai_data = data["openai"]
#                 if "api_key" in openai_data and openai_data["api_key"]:
#                     global_config["openai"]["api_key"] = openai_data["api_key"]
#                 if "default_model" in openai_data:
#                     global_config["openai"]["default_model"] = openai_data["default_model"]
#                 if "models" in openai_data:
#                     global_config["openai"]["models"].update(openai_data["models"])
            
#             if "ollama" in data:
#                 ollama_data = data["ollama"]
#                 if "base_url" in ollama_data:
#                     global_config["ollama"]["base_url"] = ollama_data["base_url"]
#                 if "default_model" in ollama_data:
#                     global_config["ollama"]["default_model"] = ollama_data["default_model"]
#                 if "models" in ollama_data:
#                     global_config["ollama"]["models"].update(ollama_data["models"])
        
#         elif config_type == "website" and website_id:
#             # Update website-specific configuration
#             if "website_overrides" not in global_config:
#                 global_config["website_overrides"] = {}
            
#             override_data = {
#                 "provider": data.get("provider"),
#                 "model": data.get("model"),
#                 "temperature": data.get("temperature")
#             }
            
#             global_config["website_overrides"][website_id] = override_data
        
#         # Save configuration
#         if save_llm_config(global_config):
#             # Clear caches to force reload
#             global llm_instances, qa_chains
#             llm_instances.clear()
#             qa_chains.clear()
            
#             # Reinitialize default LLM
#             global llm, LLM_OPTION
#             llm, LLM_OPTION = create_llm_instance()
            
#             return jsonify({"message": "LLM configuration updated successfully"})
#         else:
#             return jsonify({"error": "Failed to save configuration"}), 500
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/api/llm-test", methods=["POST"])
# def test_llm_api():
#     """Test LLM configuration for specific website"""
#     try:
#         data = request.json
#         website_id = data.get("website_id", "default")
#         test_message = data.get("message", "Hello! Please confirm you're working.")
        
#         # Get website-specific LLM
#         llm, provider = get_llm_for_website(website_id)
#         qa_chain = get_qa_chain_for_website(website_id)
        
#         if qa_chain and hasattr(llm, 'invoke'):
#             response = qa_chain.invoke({"query": test_message})
#             reply = response["result"].strip()
#         elif hasattr(llm, 'invoke'):
#             reply = llm.invoke(test_message)
#         else:
#             reply = "LLM test failed - invalid configuration"
        
#         effective_config = get_effective_llm_config(website_id)
        
#         return jsonify({
#             "response": reply,
#             "website_id": website_id,
#             "provider": provider,
#             "config": {
#                 "model": effective_config["model"],
#                 "temperature": effective_config["temperature"]
#             }
#         })
        
#     except Exception as e:
#         return jsonify({"error": f"LLM test failed: {str(e)}"}), 500

# @app.route("/api/website-config", methods=["GET"])
# def get_website_config_api():
#     """Get configuration for a specific website (for widget)"""
#     website_id = request.args.get('website_id', 'default')
    
#     if website_id not in WEBSITE_CONFIGS:
#         website_id = 'default'
    
#     config = WEBSITE_CONFIGS[website_id]
    
#     return jsonify({
#         'websiteId': website_id,
#         'botName': config.get('bot_name', 'Assistant'),
#         'primaryColor': config.get('primary_color', '#667eea'),
#         'websiteName': config.get('name', 'Website'),
#         'features': config.get('features', [])
#     })

# # Website management endpoints
# @app.route("/api/websites", methods=["GET"])
# def list_websites():
#     """List all configured websites"""
#     return jsonify({
#         "websites": {
#             website_id: {
#                 "name": config["name"],
#                 "bot_name": config["bot_name"], 
#                 "status": "active" if os.path.exists(get_knowledge_base_path(website_id)) else "setup_required"
#             }
#             for website_id, config in WEBSITE_CONFIGS.items()
#             if website_id != 'default'
#         }
#     })

# # ================================
# # 📦 ENHANCED CHAT ENDPOINT
# # ================================

# @app.route("/chat", methods=["POST"])
# def chat_multi():
#     try:
#         data = request.json
#         user_input = data.get("message")
#         user_id = data.get("user_id", "anon")
#         name = data.get("name", "visitor")
        
#         # Get website configuration
#         website_id, website_config = get_website_config(request)
        
#         if not user_input:
#             return jsonify({"error": "No message provided"}), 400

#         # Get website-specific LLM and QA chain
#         llm, provider = get_llm_for_website(website_id)
#         qa_chain = get_qa_chain_for_website(website_id)
        
#         # Use custom prompt if available
#         bot_name = website_config.get('bot_name', 'Assistant')
#         website_name = website_config.get('name', 'Website')
        
#         enhanced_query = (
#             f"You are {bot_name}, a friendly assistant at {website_name}. "
#             f"You are helping a user named {name}. "
#             f"Always answer in raw HTML (e.g., <br>, <ul>), no Markdown. "
#             f"Always end your message with a helpful follow-up question. "
#             f"Question: {user_input}"
#         )

#         # Use the QA chain to get response
#         if qa_chain and hasattr(llm, 'invoke'):
#             # For proper LangChain LLMs with QA chain
#             response = qa_chain.invoke({"query": enhanced_query})
#             reply = response["result"].strip().replace("\n", "<br>")
#         else:
#             # For mock LLM or when QA chain failed - manual RAG
#             docs = retriever.get_relevant_documents(user_input)
#             context = "\n\n".join(doc.page_content for doc in docs)
            
#             # Use custom prompt if available
#             prompt_template = website_config.get('custom_prompt', template_text)
#             full_prompt = prompt_template.format(context=context, question=user_input)
#             full_prompt += f"\n\nYou are {bot_name} helping {name}. Always end with a follow-up question."
            
#             if hasattr(llm, 'invoke'):
#                 reply = llm.invoke(full_prompt)
#             else:
#                 reply = f"Mock response for: {user_input}<br><br>What else would you like to know?"
        
#         # Log the conversation with website context
#         log_chat(user_id, user_input, "user", website_id)
#         log_chat(user_id, reply, "bot", website_id)
        
#         return jsonify({"response": reply, "website_id": website_id})

#     except Exception as e:
#         print(f"Chat error: {e}")
#         return jsonify({"response": "Sorry, I ran into an error. Please try again."}), 500

# # ================================
# # 📁 FILE MANAGEMENT ENDPOINTS
# # ================================

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route("/api/upload", methods=["POST"])
# def upload_file_multi():
#     try:
#         # Get website configuration
#         website_id, website_config = get_website_config(request)
        
#         if 'file' not in request.files:
#             return jsonify({"error": "No file provided"}), 400
        
#         file = request.files['file']
#         category = request.form.get('category', 'company_details')
        
#         if file.filename == '':
#             return jsonify({"error": "No file selected"}), 400
        
#         if not allowed_file(file.filename):
#             return jsonify({"error": "File type not allowed"}), 400
        
#         filename = secure_filename(file.filename)
        
#         # Website-specific upload directory
#         website_upload_dir = f"uploads/{website_id}"
#         category_dir = os.path.join(website_upload_dir, category)
#         os.makedirs(category_dir, exist_ok=True)
        
#         filepath = os.path.join(category_dir, filename)
#         file.save(filepath)
        
#         # Process file for website-specific knowledge base
#         success = process_file_for_website(filepath, filename, category, website_id)
        
#         if success:
#             return jsonify({
#                 "message": f"File uploaded to {website_config['name']} knowledge base",
#                 "website_id": website_id,
#                 "category": category
#             })
#         else:
#             return jsonify({"error": "Failed to process file"}), 500
            
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# def process_file_for_website(filepath, filename, category, website_id):
#     """Process file for specific website's knowledge base"""
#     try:
#         from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
#         from langchain.text_splitter import RecursiveCharacterTextSplitter
        
#         # Load document
#         file_ext = filename.lower().split('.')[-1]
#         if file_ext == 'pdf':
#             loader = PyPDFLoader(filepath)
#         elif file_ext == 'csv':
#             loader = CSVLoader(filepath)
#         else:
#             loader = TextLoader(filepath, encoding='utf-8')
        
#         documents = loader.load()
        
#         # Split into chunks
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         chunks = text_splitter.split_documents(documents)
        
#         # Add website-specific metadata
#         for chunk in chunks:
#             chunk.metadata.update({
#                 'source_file': filename,
#                 'upload_time': datetime.now().isoformat(),
#                 'category': category,
#                 'website_id': website_id
#             })
        
#         # Add to website-specific vectorstore
#         website_vectorstore = get_website_vectorstore(website_id)
#         website_vectorstore.add_documents(chunks)
#         website_vectorstore.persist()
        
#         # Also add to global vectorstore for backward compatibility
#         global vectorstore, retriever
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
        
#         # Update retriever and clear QA chains to force reload
#         retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
#         global qa_chains
#         qa_chains.clear()
        
#         return True
        
#     except Exception as e:
#         print(f"File processing error for {website_id}: {e}")
#         return False

# @app.route("/api/crawl", methods=["POST"])
# def crawl_url():
#     try:
#         data = request.json
#         url = data.get('url')
#         max_pages = data.get('max_pages', 10)
#         website_id = data.get('website_id', 'default')
        
#         if not url:
#             return jsonify({"error": "No URL provided"}), 400
        
#         # Process the URL
#         success = process_url(url, max_pages, website_id)
        
#         if success:
#             return jsonify({"message": f"URL {url} crawled successfully for {website_id}"})
#         else:
#             return jsonify({"error": "Failed to crawl URL"}), 500
            
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# def process_url(url, max_pages=10, website_id='default'):
#     try:
#         from langchain_community.document_loaders import WebBaseLoader
#         from langchain.text_splitter import RecursiveCharacterTextSplitter
        
#         # Simple web scraping
#         loader = WebBaseLoader([url])
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
#             chunk.metadata['source_url'] = url
#             chunk.metadata['crawl_time'] = datetime.now().isoformat()
#             chunk.metadata['website_id'] = website_id
        
#         # Add to vector store
#         global vectorstore, retriever
        
#         # Get existing documents
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
#         global qa_chains
#         qa_chains.clear()
        
#         return True
        
#     except Exception as e:
#         print(f"URL processing error: {e}")
#         return False

# @app.route("/api/prompt", methods=["GET", "POST"])
# def manage_prompt():
#     try:
#         if request.method == "GET":
#             return jsonify({"prompt": template_text})
        
#         elif request.method == "POST":
#             data = request.json
#             new_prompt = data.get('prompt')
            
#             if not new_prompt:
#                 return jsonify({"error": "No prompt provided"}), 400
            
#             # Update the global prompt
#             success = update_prompt(new_prompt)
            
#             if success:
#                 return jsonify({"message": "Prompt updated successfully"})
#             else:
#                 return jsonify({"error": "Failed to update prompt"}), 500
                
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# def update_prompt(new_prompt):
#     try:
#         global template_text, prompt
        
#         template_text = new_prompt
#         prompt = PromptTemplate(
#             input_variables=["context", "question"],
#             template=template_text,
#         )
        
#         # Save prompt to file
#         os.makedirs("config", exist_ok=True)
#         with open("config/prompt.txt", "w", encoding="utf-8") as f:
#             f.write(new_prompt)
        
#         # Clear QA chains to force recreation with new prompt
#         global qa_chains
#         qa_chains.clear()
        
#         return True
        
#     except Exception as e:
#         print(f"Prompt update error: {e}")
#         return False

# # ================================
# # 📊 KNOWLEDGE MANAGEMENT & STATS
# # ================================

# @app.route("/api/knowledge-stats", methods=["GET"])
# def knowledge_stats():
#     try:
#         website_id = request.args.get('website_id', 'default')
        
#         # Get vector store statistics
#         try:
#             test_docs = retriever.get_relevant_documents("test", k=10000)
#             doc_count = len(test_docs)
#             db_status = "active"
#         except Exception as e:
#             print(f"Vector DB test failed: {e}")
#             doc_count = 0
#             db_status = "error"
        
#         # Get uploaded files safely
#         uploaded_files = []
#         try:
#             upload_folder = f"uploads/{website_id}"
#             if os.path.exists(upload_folder):
#                 for category in FILE_CATEGORIES.keys():
#                     category_path = os.path.join(upload_folder, category)
#                     if os.path.exists(category_path):
#                         for filename in os.listdir(category_path):
#                             filepath = os.path.join(category_path, filename)
#                             if os.path.isfile(filepath):
#                                 stat = os.stat(filepath)
#                                 uploaded_files.append({
#                                     "name": filename,
#                                     "category": category,
#                                     "size": stat.st_size,
#                                     "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
#                                 })
#         except Exception as e:
#             print(f"⚠️ Upload folder check failed: {e}")
        
#         # Get effective LLM config
#         effective_config = get_effective_llm_config(website_id)
        
#         stats = {
#             "website_id": website_id,
#             "total_documents": max(0, doc_count),
#             "vector_store_status": db_status,
#             "vector_store_path": "./chroma_db",
#             "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
#             "llm_provider": effective_config["provider"],
#             "llm_model": effective_config["model"],
#             "llm_temperature": effective_config["temperature"],
#             "llm_option": effective_config["provider"],  # For backward compatibility
#             "uploaded_files": uploaded_files,
#             "file_categories": FILE_CATEGORIES
#         }
        
#         return jsonify(stats)
        
#     except Exception as e:
#         print(f"❌ Stats error: {e}")
#         return jsonify({
#             "total_documents": 0,
#             "vector_store_status": "error",
#             "error": str(e)
#         })

# @app.route("/api/categories", methods=["GET"])
# def get_categories():
#     """Get available file categories"""
#     return jsonify({"categories": FILE_CATEGORIES})

# # ================================
# # 🗂️ BULK OPERATIONS & RESET SYSTEM
# # ================================

# @app.route("/api/websites/bulk", methods=["POST"])
# def bulk_website_operations():
#     """Perform bulk operations on websites"""
#     try:
#         data = request.json
#         operation = data.get('operation')
#         website_ids = data.get('website_ids', [])
        
#         if operation == 'backup':
#             # Create backup for multiple websites
#             results = {}
#             for website_id in website_ids:
#                 try:
#                     backup_path = create_website_backup(website_id)
#                     results[website_id] = {"status": "success", "backup_path": backup_path}
#                 except Exception as e:
#                     results[website_id] = {"status": "error", "error": str(e)}
            
#             return jsonify({"results": results})
        
#         elif operation == 'reset':
#             # Reset multiple websites
#             results = {}
#             for website_id in website_ids:
#                 try:
#                     reset_website_knowledge(website_id)
#                     results[website_id] = {"status": "success"}
#                 except Exception as e:
#                     results[website_id] = {"status": "error", "error": str(e)}
            
#             return jsonify({"results": results})
        
#         else:
#             return jsonify({"error": "Invalid operation"}), 400
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# def create_website_backup(website_id):
#     """Create backup for specific website"""
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#     backup_dir = f"backups/{website_id}_backup_{timestamp}"
#     os.makedirs(backup_dir, exist_ok=True)
    
#     # Backup website-specific files and knowledge base
#     try:
#         upload_dir = f"uploads/{website_id}"
#         if os.path.exists(upload_dir):
#             shutil.copytree(upload_dir, f"{backup_dir}/uploads")
        
#         kb_path = get_knowledge_base_path(website_id)
#         if os.path.exists(kb_path):
#             shutil.copytree(kb_path, f"{backup_dir}/knowledge_base")
        
#         return backup_dir
#     except Exception as e:
#         print(f"Backup error for {website_id}: {e}")
#         raise e

# def reset_website_knowledge(website_id):
#     """Reset knowledge base for a specific website"""
#     # Clear website-specific knowledge base
#     kb_path = get_knowledge_base_path(website_id)
#     if os.path.exists(kb_path):
#         shutil.rmtree(kb_path)
    
#     # Clear website-specific uploads
#     upload_path = f"uploads/{website_id}"
#     if os.path.exists(upload_path):
#         shutil.rmtree(upload_path)
    
#     # Clear from cache
#     if website_id in llm_instances:
#         del llm_instances[website_id]
#     if website_id in qa_chains:
#         del qa_chains[website_id]

# @app.route("/api/refresh-session", methods=["POST"])
# def refresh_chat_session():
#     """Refresh chat session without deleting knowledge"""
#     try:
#         session.clear()
#         return jsonify({
#             "status": "success",
#             "message": "Chat session refreshed successfully! (Files and knowledge preserved)"
#         })
#     except Exception as e:
#         print(f"Refresh error: {e}")
#         return jsonify({"status": "error", "message": "Failed to refresh chat session"}), 500

# @app.route("/api/reset-knowledge", methods=["POST"])
# def reset_knowledge_base():
#     """Reset knowledge base with corruption handling"""
#     try:
#         print("🔥 Starting knowledge base reset...")
        
#         # 1. FORCE CLOSE ANY VECTOR STORE CONNECTIONS
#         global vectorstore, retriever, qa_chain, qa_chains, llm_instances
#         try:
#             vectorstore = None
#             retriever = None  
#             qa_chain = None
#             qa_chains.clear()
#             llm_instances.clear()
#             print("✅ Vector store connections closed")
#         except:
#             pass
        
#         # 2. NUCLEAR DELETE OF ALL POSSIBLE VECTOR DB LOCATIONS
#         possible_db_paths = [
#             "./chroma_db",
#             "./db", 
#             "chroma_db",
#             "db",
#             "./ollama_rag_chatbot/chroma_db",
#             "./ollama_rag_chatbot/db"
#         ]
        
#         for db_path in possible_db_paths:
#             if os.path.exists(db_path):
#                 try:
#                     print(f"🗑️ Deleting vector DB at: {db_path}")
#                     shutil.rmtree(db_path)
#                     print(f"✅ Successfully deleted: {db_path}")
#                 except Exception as e:
#                     print(f"❌ Failed to delete {db_path}: {e}")
        
#         # 3. DELETE UPLOADED FILES
#         upload_paths = [
#             app.config.get('UPLOAD_FOLDER', 'uploads'),
#             'uploads', 
#             './uploads',
#             './ollama_rag_chatbot/uploads'
#         ]
        
#         for upload_path in upload_paths:
#             if os.path.exists(upload_path):
#                 try:
#                     print(f"🗑️ Deleting uploads at: {upload_path}")
#                     shutil.rmtree(upload_path)
#                     print(f"✅ Successfully deleted: {upload_path}")
#                 except Exception as e:
#                     print(f"❌ Failed to delete {upload_path}: {e}")
        
#         # 4. WAIT FOR FILE SYSTEM TO CATCH UP
#         time.sleep(2)
        
#         # 5. RECREATE DIRECTORIES
#         os.makedirs("./chroma_db", exist_ok=True)
#         os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
#         print("✅ Directories recreated")
        
#         # 6. FORCE CREATE NEW VECTOR STORE WITH ERROR HANDLING
#         try:
#             # Import here to avoid any cached references
#             from langchain_community.vectorstores import Chroma
            
#             print("🔄 Creating new vector store...")
            
#             # Create completely fresh vector store
#             vectorstore = Chroma(
#                 persist_directory="./chroma_db",
#                 embedding_function=embeddings
#             )
            
#             # Test that it works by adding and removing a dummy document
#             test_texts = ["test document for verification"]
#             test_ids = vectorstore.add_texts(test_texts, ids=["test_id"])
#             vectorstore.delete(ids=["test_id"])
            
#             print("✅ New vector store created and tested successfully")
            
#             # Verify it's empty
#             test_docs = vectorstore.similarity_search("test", k=10)
#             doc_count = len(test_docs)
#             print(f"📊 Vector store verification: {doc_count} documents")
            
#             # Recreate retriever and QA chain
#             retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
#             update_qa_chain()
            
#             return jsonify({
#                 "status": "success",
#                 "message": f"Knowledge base reset successfully! Vector store recreated with {doc_count} documents."
#             })
            
#         except Exception as vs_error:
#             print(f"❌ Vector store creation error: {vs_error}")
#             return handle_vector_store_corruption()
            
#     except Exception as e:
#         print(f"❌ Knowledge reset error: {e}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "status": "error", 
#             "message": f"Failed to reset knowledge base: {str(e)}"
#         }), 500

# def handle_vector_store_corruption():
#     """Handle severe vector store corruption"""
#     try:
#         print("🚨 Handling vector store corruption...")
        
#         # More aggressive cleanup
#         import subprocess
#         try:
#             # Try to force delete on Windows/Linux
#             if os.name == 'nt':  # Windows
#                 subprocess.run(['rmdir', '/s', '/q', 'chroma_db'], shell=True, check=False)
#             else:  # Unix-like
#                 subprocess.run(['rm', '-rf', 'chroma_db'], check=False)
#         except:
#             pass
        
#         # Wait longer
#         time.sleep(5)
        
#         # Try creating vector store again
#         os.makedirs("./chroma_db", exist_ok=True)
        
#         global vectorstore, retriever
#         vectorstore = Chroma(
#             persist_directory="./chroma_db",
#             embedding_function=embeddings
#         )
#         retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
#         return jsonify({
#             "status": "success",
#             "message": "Vector store corruption handled. Fresh knowledge base created."
#         })
        
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": f"Severe corruption detected. Manual intervention required: {str(e)}"
#         }), 500

# @app.route("/api/clear-logs", methods=["POST"])
# def clear_chat_logs():
#     """Clear all chat logs from database"""
#     try:
#         # Get confirmation from request (if any)
#         data = request.get_json() or {}
#         confirmation = data.get('confirmation', '')
        
#         # Check confirmation phrase (optional)
#         expected_phrases = ['CLEAR LOGS', 'DELETE LOGS', 'RESET LOGS']
#         if confirmation and confirmation not in expected_phrases:
#             return jsonify({
#                 "status": "error",
#                 "message": f"Invalid confirmation phrase. Please type one of: {', '.join(expected_phrases)}"
#             }), 400
        
#         from db_model import get_connection
        
#         conn = get_connection()
#         cursor = conn.cursor()
        
#         # Clear chat logs
#         cursor.execute("DELETE FROM chat_logs")
#         cursor.execute("DELETE FROM conversation_nodes")
        
#         conn.commit()
#         cursor.close()
#         conn.close()
        
#         # Also clear CSV logs if they exist
#         if os.path.exists("logs/chat_logs.csv"):
#             os.remove("logs/chat_logs.csv")
        
#         return jsonify({
#             "status": "success",
#             "message": "All chat logs and conversation history cleared!"
#         })
        
#     except Exception as e:
#         print(f"Log clearing error: {e}")
#         return jsonify({
#             "status": "error",
#             "message": f"Failed to clear logs: {str(e)}"
#         }), 500

# @app.route("/api/backup-knowledge", methods=["POST"])
# def backup_knowledge():
#     """Create a backup before reset"""
#     try:
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         backup_dir = f"backups/backup_{timestamp}"
#         os.makedirs(backup_dir, exist_ok=True)
        
#         backup_results = {}
        
#         # 1. Backup vector database
#         try:
#             if os.path.exists("./chroma_db"):
#                 shutil.copytree("./chroma_db", f"{backup_dir}/chroma_db")
#                 backup_results["vectors"] = "✅ Vector database backed up"
#         except Exception as e:
#             backup_results["vectors"] = f"❌ Error backing up vectors: {str(e)}"
        
#         # 2. Backup uploaded files
#         try:
#             if os.path.exists(app.config['UPLOAD_FOLDER']):
#                 shutil.copytree(app.config['UPLOAD_FOLDER'], f"{backup_dir}/uploads")
#                 backup_results["files"] = "✅ Files backed up"
#         except Exception as e:
#             backup_results["files"] = f"❌ Error backing up files: {str(e)}"
        
#         # 3. Backup configuration
#         try:
#             if os.path.exists("config"):
#                 shutil.copytree("config", f"{backup_dir}/config")
#                 backup_results["config"] = "✅ Config backed up"
#         except Exception as e:
#             backup_results["config"] = f"❌ Error backing up config: {str(e)}"
        
#         # 4. Backup logs
#         try:
#             if os.path.exists("logs"):
#                 shutil.copytree("logs", f"{backup_dir}/logs")
#                 backup_results["logs"] = "✅ Logs backed up"
#         except Exception as e:
#             backup_results["logs"] = f"❌ Error backing up logs: {str(e)}"
        
#         return jsonify({
#             "status": "success",
#             "message": f"Backup created at {backup_dir}",
#             "backup_path": backup_dir,
#             "details": backup_results
#         })
        
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": f"Backup failed: {str(e)}"
#         }), 500

# # ================================
# # 📄 TEMPLATE & LEGACY ENDPOINTS
# # ================================

# @app.route("/template", methods=["GET"])
# def get_template():
#     return jsonify({"template": template_text})

# @app.route("/update_faq", methods=["POST"])
# def update_faq():
#     try:
#         from langchain_community.document_loaders import TextLoader
#         from langchain.text_splitter import RecursiveCharacterTextSplitter

#         # Check if FAQ file exists
#         faq_file = "data/faq.txt"
#         if not os.path.exists(faq_file):
#             return jsonify({"error": f"FAQ file not found at {faq_file}"}), 404

#         # Load your updated FAQ or content
#         loader = TextLoader(faq_file)
#         documents = loader.load()

#         splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#         chunks = splitter.split_documents(documents)

#         # Update the vector store
#         global vectorstore, retriever, qa_chains
#         vectorstore = Chroma.from_documents(
#             chunks, 
#             embedding=embeddings, 
#             persist_directory="./chroma_db"
#         )
#         vectorstore.persist()
        
#         # Update retriever and clear QA chains
#         retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
#         qa_chains.clear()  # Force recreation with new data
        
#         return jsonify({"status": "FAQ updated successfully"})
#     except Exception as e:
#         print(f"FAQ update error: {e}")
#         return jsonify({"error": f"Failed to update FAQ: {str(e)}"}), 500

# @app.route("/health", methods=["GET"])
# def health_check():
#     try:
#         # Test vector store
#         test_docs = retriever.get_relevant_documents("test")
#         effective_config = get_effective_llm_config()
        
#         return jsonify({
#             "status": "healthy",
#             "vectorstore_docs": len(test_docs),
#             "llm_model": effective_config.get("model", "unknown"),
#             "llm_provider": effective_config.get("provider", "unknown"),
#             "llm_option": LLM_OPTION,
#             "websites_configured": len(WEBSITE_CONFIGS)
#         })
#     except Exception as e:
#         return jsonify({"status": "unhealthy", "error": str(e)}), 500

# # ================================
# # 💬 ENHANCED CHAT LOGGING
# # ================================

# def log_chat(user_id, message, sender, website_id=None):
#     try:
#         now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         # Escape commas and quotes in message for CSV safety
#         clean_message = message.replace('"', '""').replace('\n', ' ').replace('\r', ' ')
#         log_entry = f'"{now}","{user_id}","{sender}","{website_id or "default"}","{clean_message}"\n'
        
#         # Create logs directory if it doesn't exist
#         os.makedirs("logs", exist_ok=True)
        
#         with open("logs/chat_logs.csv", "a", encoding="utf-8") as f:
#             f.write(log_entry)
            
#         # Also log to database if available
#         try:
#             from db_model import log_chat as db_log_chat
#             db_log_chat(user_id, message, sender)
#         except ImportError:
#             pass  # DB logging not available
#         except Exception as e:
#             print(f"Database logging error: {e}")
            
#     except Exception as e:
#         print(f"Logging error: {e}")

# # ================================
# # 🧪 INITIALIZATION & STARTUP
# # ================================

# def initialize_application():
#     """Initialize the application with all components"""
#     try:
#         # Create necessary directories
#         os.makedirs("./chroma_db", exist_ok=True)
#         os.makedirs("./data", exist_ok=True)
#         os.makedirs("./logs", exist_ok=True)
#         os.makedirs("./config", exist_ok=True)
#         os.makedirs("./backups", exist_ok=True)
        
#         # Initialize website configurations
#         initialize_website_configs()
        
#         # Initialize vector store if empty
#         try:
#             test_docs = retriever.get_relevant_documents("test", k=1)
#             print(f"📊 Vector store contains {len(test_docs)} test documents")
#         except Exception as e:
#             print(f"⚠️ Vector store initialization issue: {e}")
        
#         # Verify LLM configuration
#         effective_config = get_effective_llm_config()
#         print(f"🤖 LLM Configuration: {effective_config['provider']} - {effective_config['model']}")
        
#         # Create default QA chain
#         update_qa_chain()
        
#         print("✅ Application initialization complete!")
#         return True
        
#     except Exception as e:
#         print(f"❌ Application initialization failed: {e}")
#         return False

# # ================================
# # 🧪 RUN APPLICATION
# # ================================

# if __name__ == "__main__":
#     print("🚀 Starting Advanced Multi-Website RAG Chatbot with LLM Management...")
#     print(f"📊 Vector store location: ./chroma_db")
#     print(f"📝 FAQ file expected at: ./data/faq.txt")
#     print(f"📋 Logs will be saved to: ./logs/chat_logs.csv")
#     print(f"🌐 Supporting websites: {list(WEBSITE_CONFIGS.keys())}")
#     print(f"🔧 Configuration directory: ./config/")
#     print(f"📦 Backup directory: ./backups/")
    
#     # Initialize application
#     if initialize_application():
#         print("🎉 Ready to serve requests!")
#         app.run(host='0.0.0.0', port=5000, debug=True)
#     else:
#         print("💥 Failed to initialize application. Check logs for details.")
#         exit(1)




from flask import Flask, request, jsonify, render_template, session, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import re
import shutil
import json
import time

import mysql.connector
from db_config import DB_CONFIG

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

# App setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "admin123")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
CORS(app)

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

# Website configuration - Enhanced with LLM-specific settings
WEBSITE_CONFIGS = {
    'sourceselect.ca': {
        'name': 'SourceSelect',
        'bot_name': 'Bob',
        'primary_color': '#667eea',
        'knowledge_base': 'sourceselect',
        'allowed_origins': ['https://sourceselect.ca', 'https://www.sourceselect.ca'],
        'custom_prompt': None,  # Uses default if None
        'features': ['sales_tracking', 'lead_generation', 'analytics'],
        'llm_config': {  # Website-specific LLM settings
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'temperature': 1.0
        }
    },
    'example-business.com': {
        'name': 'Example Business',
        'bot_name': 'Alex',
        'primary_color': '#28a745',
        'knowledge_base': 'example_business',
        'allowed_origins': ['https://example-business.com'],
        'custom_prompt': 'You are Alex, a helpful assistant for Example Business...',
        'features': ['basic_support'],
        'llm_config': {
            'provider': 'ollama',
            'model': 'llama3.1:8b',
            'temperature': 0.7
        }
    },
    'default': {
        'name': 'AI Assistant',
        'bot_name': 'Assistant',
        'primary_color': '#6c757d',
        'knowledge_base': 'default',
        'allowed_origins': ['*'],
        'llm_config': {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'temperature': 1.0
        }
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

# ================================
# 🔐 ENHANCED LLM CONFIGURATION MANAGEMENT
# ================================

def load_llm_config():
    """Load global LLM configuration with fallback to environment variables"""
    config_file = "config/llm_config.json"
    
    default_config = {
        "global_provider": os.getenv("LLM_PROVIDER", "openai"),
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "models": {
                "gpt-4o-mini": {"temperature": 1.0},
                "gpt-4o": {"temperature": 0.7},
                "gpt-4": {"temperature": 0.7},
                "gpt-3.5-turbo": {"temperature": 0.9}
            },
            "default_model": "gpt-4o-mini"
        },
        "ollama": {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "models": {
                "llama3.1:8b": {"temperature": 0.7},
                "llama3.1:70b": {"temperature": 0.7},
                "mistral": {"temperature": 0.8},
                "codellama": {"temperature": 0.5}
            },
            "default_model": "llama3.1:8b"
        },
        "website_overrides": {}  # Per-website LLM configurations
    }
    
    try:
        os.makedirs("config", exist_ok=True)
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                saved_config = json.load(f)
                # Merge saved config with defaults
                for key in default_config:
                    if key in saved_config:
                        if isinstance(default_config[key], dict):
                            default_config[key].update(saved_config[key])
                        else:
                            default_config[key] = saved_config[key]
    except Exception as e:
        print(f"Warning: Could not load LLM config file: {e}")
    
    return default_config

def save_llm_config(config):
    """Save LLM configuration to file"""
    config_file = "config/llm_config.json"
    try:
        os.makedirs("config", exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving LLM config: {e}")
        return False

def get_effective_llm_config(website_id=None):
    """Get effective LLM configuration for a specific website or global"""
    global_config = load_llm_config()
    
    # Check for website-specific override
    if website_id and website_id in global_config.get("website_overrides", {}):
        website_override = global_config["website_overrides"][website_id]
        provider = website_override.get("provider")
        
        # If provider is None, use global provider
        if provider is None:
            provider = global_config["global_provider"]
        
        effective_config = {
            "provider": provider,
            "model": website_override.get("model"),
            "temperature": website_override.get("temperature"),
            "config": global_config
        }
        
        # If model is None, use the provider's default model
        if effective_config["model"] is None:
            effective_config["model"] = global_config[provider]["default_model"]
        
        # If temperature is None, use the model's default temperature
        if effective_config["temperature"] is None and effective_config["model"]:
            model = effective_config["model"]
            if model in global_config[provider]["models"]:
                effective_config["temperature"] = global_config[provider]["models"][model]["temperature"]
        
        return effective_config
    
    # Check WEBSITE_CONFIGS for default
    if website_id and website_id in WEBSITE_CONFIGS:
        website_config = WEBSITE_CONFIGS[website_id].get("llm_config", {})
        provider = website_config.get("provider")
        
        # If provider is None, use global provider
        if provider is None:
            provider = global_config["global_provider"]
        
        effective_config = {
            "provider": provider,
            "model": website_config.get("model"),
            "temperature": website_config.get("temperature"),
            "config": global_config
        }
        
        # If model is None, use the provider's default model
        if effective_config["model"] is None:
            effective_config["model"] = global_config[provider]["default_model"]
        
        # If temperature is None, use the model's default temperature
        if effective_config["temperature"] is None and effective_config["model"]:
            model = effective_config["model"]
            if model in global_config[provider]["models"]:
                effective_config["temperature"] = global_config[provider]["models"][model]["temperature"]
        
        return effective_config
    
    # Return global default
    provider = global_config["global_provider"]
    provider_config = global_config[provider]
    default_model = provider_config["default_model"]
    
    return {
        "provider": provider,
        "model": default_model,
        "temperature": provider_config["models"][default_model]["temperature"],
        "config": global_config
    }

    
def create_llm_instance(website_id=None):
    """Create LLM instance based on website-specific or global configuration"""
    effective_config = get_effective_llm_config(website_id)
    provider = effective_config["provider"]
    model = effective_config["model"]
    temperature = effective_config["temperature"]
    
    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            api_key = effective_config["config"]["openai"]["api_key"] or os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                print(f"⚠️ OpenAI API key not found for website {website_id}")
                return create_mock_llm(), "mock"
            
            # Test the API key before creating the LLM instance
            try:
                import openai
                openai.api_key = api_key
                openai.models.list()  # Simple API call to test the key
            except Exception as api_error:
                print(f"❌ OpenAI API key validation failed: {api_error}")
                return create_mock_llm(), "mock"
            
            llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                openai_api_key=api_key
            )
            print(f"🤖 Using OpenAI model: {model} for website {website_id or 'global'}")
            return llm, "openai"
            
        except Exception as e:
            print(f"Failed to initialize OpenAI for {website_id}: {e}")
            return create_mock_llm(), "mock"
    
    elif provider == "ollama":
        try:
            from langchain_community.llms import Ollama
            base_url = effective_config["config"]["ollama"]["base_url"]
            
            # Test Ollama connection
            try:
                import requests
                response = requests.get(f"{base_url}/api/tags")
                if response.status_code != 200:
                    raise Exception(f"Ollama connection failed: {response.status_code}")
            except Exception as conn_error:
                print(f"❌ Ollama connection test failed: {conn_error}")
                return create_mock_llm(), "mock"
            
            llm = Ollama(
                model=model,
                temperature=temperature,
                base_url=base_url
            )
            print(f"🤖 Using Ollama model: {model} for website {website_id or 'global'}")
            return llm, "ollama"
            
        except Exception as e:
            print(f"Failed to initialize Ollama for {website_id}: {e}")
            return create_mock_llm(), "mock"
    
    return create_mock_llm(), "mock"

def create_mock_llm():
    """Create mock LLM for fallback"""
    class MockLLM:
        def invoke(self, prompt):
            return "I'm a mock response. Please configure a valid LLM provider in the dashboard."
        
        @property
        def model_name(self):
            return "mock-llm"
    
    return MockLLM()

# Global LLM instances cache
llm_instances = {}

def get_llm_for_website(website_id):
    """Get or create LLM instance for specific website"""
    if website_id not in llm_instances:
        llm, provider = create_llm_instance(website_id)
        llm_instances[website_id] = {"llm": llm, "provider": provider}
    
    return llm_instances[website_id]["llm"], llm_instances[website_id]["provider"]

# Initialize default LLM - Enhanced fallback logic
try:
    default_config = get_effective_llm_config()
    llm, LLM_OPTION = create_llm_instance()
except Exception as e:
    print(f"LLM initialization failed: {e}")
    # Fallback to ollama
    try:
        from langchain_community.llms import Ollama
        llm = Ollama(
            model="llama3.1:8b",
            temperature=0.7,
            base_url="http://localhost:11434"
        )
        LLM_OPTION = "ollama"
        print(f"🤖 Using Ollama fallback: llama3.1:8b")
    except ImportError:
        print("❌ Ollama not available. Install with: pip install langchain-community")
        llm = create_mock_llm()
        LLM_OPTION = "mock"
        print("🤖 Using Mock LLM (for testing only)")

# 🔍 Embeddings & Vector DB setup
embeddings = HuggingFaceEmbeddings()

# ✅ Chroma vector store (no `.persist()` needed)
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

# RAG prompt template - Load from file or use default
def load_saved_prompt():
    try:
        if os.path.exists("config/prompt.txt"):
            with open("config/prompt.txt", "r", encoding="utf-8") as f:
                return f.read()
    except:
        pass
    return None

saved_prompt = load_saved_prompt()
template_text = saved_prompt if saved_prompt else """
You are Bob, a real human virtual assistant for SourceSelect.ca.

Your job is to help users with their questions about SourceSelect.ca and its services. Always be polite, helpful, and conversational—just like a friendly and attentive human agent.

INSTRUCTIONS:
- Vary your greetings and responses to avoid sounding repetitive or robotic.
- Reference the user's specific question in your answer.
- Use ONLY the information provided in the "Relevant Info" section below.
- If you don't know the answer or the information isn't available, respond with a polite and varied fallback such as:
  "That's a great question! I don't have the details on that right now, but I can help connect you to the right person."
  or
  "I'm not sure about that, but I can help you get in touch with someone who knows more!"
- Only ask follow-up questions if they make sense and feel natural.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- Keep your tone friendly and concise.
- Always finish with a relevant, human-sounding follow-up or offer to help further.

Relevant Info:
{context}

User Question: {question}

Bob's Response:
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=template_text,
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# QA chains cache
qa_chains = {}

def get_qa_chain_for_website(website_id):
    """Get or create QA chain for specific website"""
    if website_id not in qa_chains:
        llm, provider = get_llm_for_website(website_id)
        
        if provider != "mock" and hasattr(llm, 'invoke'):
            try:
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                    chain_type_kwargs={"prompt": prompt}
                )
                qa_chains[website_id] = qa_chain
                print(f"✅ QA Chain created for website {website_id}")
            except Exception as e:
                print(f"❌ QA Chain creation failed for {website_id}: {e}")
                qa_chains[website_id] = None
        else:
            qa_chains[website_id] = None
    
    return qa_chains[website_id]

def update_qa_chain():
    """Update QA chain with current LLM and prompt"""
    global qa_chain
    if LLM_OPTION != "mock" and hasattr(llm, 'invoke'):
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt}
            )
            print("✅ QA Chain updated successfully")
        except Exception as e:
            print(f"❌ QA Chain update failed: {e}")
            qa_chain = None
    else:
        qa_chain = None
        print("⚠️ Using mock LLM - QA chain not created")

# Create default QA chain
qa_chain = get_qa_chain_for_website('default')

def initialize_website_configs():
    """Initialize website configurations from database"""
    try:
        # Add your database initialization logic here if needed
        print("✅ Website configurations initialized")
    except Exception as e:
        print(f"⚠️ Website config initialization failed: {e}")

def get_knowledge_base_path(website_id):
    """Get the knowledge base path for a specific website"""
    return f"./chroma_db_{website_id}"

def get_website_vectorstore(website_id):
    """Get or create website-specific vector store"""
    kb_path = get_knowledge_base_path(website_id)
    try:
        website_vectorstore = Chroma(
            persist_directory=kb_path,
            embedding_function=embeddings
        )
        return website_vectorstore
    except Exception as e:
        print(f"Error creating vectorstore for {website_id}: {e}")
        # Fallback to global vectorstore
        return vectorstore

# ================================
# 🌐 WEB UI ROUTES
# ================================

@app.route("/website-a")
def website():
    return render_template("website_a.html")

@app.route("/")
def index():
    session.clear()
    return render_template("index.html", suggested=SUGGESTED_MESSAGES)

@app.route("/widget")
def widget_multi():
    """Serve widget with website-specific configuration"""
    website_id = request.args.get('website_id', 'default')
    
    if website_id not in WEBSITE_CONFIGS:
        website_id = 'default'
    
    config = WEBSITE_CONFIGS[website_id]
    
    # Pass website-specific config to template
    return render_template("widget.html", 
                         suggested=SUGGESTED_MESSAGES,
                         website_id=website_id,
                         bot_name=config.get('bot_name', 'Assistant'),
                         primary_color=config.get('primary_color', '#667eea'),
                         website_name=config.get('name', 'Website'))

@app.route("/embed.js")
def serve_embed_script_multi():
    """Serve website-specific embed script"""
    website_id = request.args.get('website_id', 'default')
    
    if website_id not in WEBSITE_CONFIGS:
        website_id = 'default'
    
    config = WEBSITE_CONFIGS[website_id]
    
    # Generate dynamic embed script with website-specific config
    embed_script = f"""
(function() {{
    window.CHATBOT_CONFIG = {{
        apiBaseUrl: '{request.host_url.rstrip('/')}',
        websiteId: '{website_id}',
        botName: '{config.get('bot_name', 'Assistant')}',
        primaryColor: '{config.get('primary_color', '#667eea')}',
        websiteName: '{config.get('name', 'Website')}'
    }};
    
    // Load the main embed script
    const script = document.createElement('script');
    script.src = '{request.host_url.rstrip('/')}/static/embed.js';
    script.defer = true;
    document.head.appendChild(script);
}})();
"""
    
    return embed_script, 200, {'Content-Type': 'application/javascript'}

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard_v1.html")

def get_website_config(request):
    """Determine which website configuration to use based on request"""
    origin = request.headers.get('Origin', '')
    referer = request.headers.get('Referer', '')
    website_id = request.args.get('website_id') or (request.json.get('website_id') if request.is_json else None)
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

# ================================
# 🤖 LLM MANAGEMENT API ENDPOINTS
# ================================

@app.route("/api/llm-config", methods=["GET"])
def get_llm_config_api():
    """Get current LLM configuration"""
    try:
        website_id = request.args.get('website_id', 'default')
        effective_config = get_effective_llm_config(website_id)
        global_config = effective_config["config"]
        
        safe_config = {
            "website_id": website_id,
            "effective_provider": effective_config["provider"],
            "effective_model": effective_config["model"],
            "effective_temperature": effective_config["temperature"],
            "global_provider": global_config["global_provider"],
            "openai": {
                "has_api_key": bool(global_config["openai"]["api_key"]),
                "models": global_config["openai"]["models"],
                "default_model": global_config["openai"]["default_model"]
            },
            "ollama": {
                "base_url": global_config["ollama"]["base_url"],
                "models": global_config["ollama"]["models"],
                "default_model": global_config["ollama"]["default_model"]
            },
            "website_overrides": global_config.get("website_overrides", {}),
            "available_websites": list(WEBSITE_CONFIGS.keys())
        }
        
        return jsonify(safe_config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/llm-config", methods=["POST"])
def update_llm_config_api():
    """Update LLM configuration"""
    try:
        data = request.json
        config_type = data.get("config_type", "global")  # "global" or "website"
        website_id = data.get("website_id")
        
        global_config = load_llm_config()
        
        if config_type == "global":
            # Update global configuration
            if "global_provider" in data:
                global_config["global_provider"] = data["global_provider"]
            
            if "openai" in data:
                openai_data = data["openai"]
                if "api_key" in openai_data and openai_data["api_key"]:
                    global_config["openai"]["api_key"] = openai_data["api_key"]
                if "default_model" in openai_data:
                    global_config["openai"]["default_model"] = openai_data["default_model"]
                if "models" in openai_data:
                    global_config["openai"]["models"].update(openai_data["models"])
            
            if "ollama" in data:
                ollama_data = data["ollama"]
                if "base_url" in ollama_data:
                    global_config["ollama"]["base_url"] = ollama_data["base_url"]
                if "default_model" in ollama_data:
                    global_config["ollama"]["default_model"] = ollama_data["default_model"]
                if "models" in ollama_data:
                    global_config["ollama"]["models"].update(ollama_data["models"])
        
        elif config_type == "website" and website_id:
            # Update website-specific configuration
            if "website_overrides" not in global_config:
                global_config["website_overrides"] = {}
            
            override_data = {
                "provider": data.get("provider"),
                "model": data.get("model"),
                "temperature": data.get("temperature")
            }
            
            global_config["website_overrides"][website_id] = override_data
        
        # Save configuration
        if save_llm_config(global_config):
            # Clear caches to force reload
            global llm_instances, qa_chains
            llm_instances.clear()
            qa_chains.clear()
            
            # Reinitialize default LLM
            global llm, LLM_OPTION
            llm, LLM_OPTION = create_llm_instance()
            
            return jsonify({"message": "LLM configuration updated successfully"})
        else:
            return jsonify({"error": "Failed to save configuration"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/llm-test", methods=["POST"])
def test_llm_api():
    """Test LLM configuration for specific website"""
    try:
        data = request.json
        website_id = data.get("website_id", "default")
        test_message = data.get("message", "Hello! Please confirm you're working.")
        
        # Get website-specific LLM
        llm, provider = get_llm_for_website(website_id)
        qa_chain = get_qa_chain_for_website(website_id)
        
        if qa_chain and hasattr(llm, 'invoke'):
            response = qa_chain.invoke({"query": test_message})
            reply = response["result"].strip()
        elif hasattr(llm, 'invoke'):
            reply = llm.invoke(test_message)
        else:
            reply = "LLM test failed - invalid configuration"
        
        effective_config = get_effective_llm_config(website_id)
        
        return jsonify({
            "response": reply,
            "website_id": website_id,
            "provider": provider,
            "config": {
                "model": effective_config["model"],
                "temperature": effective_config["temperature"]
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"LLM test failed: {str(e)}"}), 500

@app.route("/api/website-config", methods=["GET"])
def get_website_config_api():
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

# ================================
# 📦 ENHANCED CHAT ENDPOINT
# ================================

@app.route("/chat", methods=["POST"])
def chat_multi():
    try:
        data = request.json
        user_input = data.get("message")
        user_id = data.get("user_id", "anon")
        name = data.get("name", "visitor")
        
        # Get website configuration
        website_id, website_config = get_website_config(request)
        
        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        # Get website-specific LLM and QA chain
        llm, provider = get_llm_for_website(website_id)
        qa_chain = get_qa_chain_for_website(website_id)
        
        # Use custom prompt if available
        bot_name = website_config.get('bot_name', 'Assistant')
        website_name = website_config.get('name', 'Website')
        
        enhanced_query = (
            f"You are {bot_name}, a friendly assistant at {website_name}. "
            f"You are helping a user named {name}. "
            f"Always answer in raw HTML (e.g., <br>, <ul>), no Markdown. "
            f"Always end your message with a helpful follow-up question. "
            f"Question: {user_input}"
        )

        # Use the QA chain to get response
        if qa_chain and hasattr(llm, 'invoke'):
            # For proper LangChain LLMs with QA chain
            response = qa_chain.invoke({"query": enhanced_query})
            reply = response["result"].strip().replace("\n", "<br>")
        else:
            # For mock LLM or when QA chain failed - manual RAG
            docs = retriever.get_relevant_documents(user_input)
            context = "\n\n".join(doc.page_content for doc in docs)
            
            # Use custom prompt if available
            prompt_template = website_config.get('custom_prompt', template_text)
            full_prompt = prompt_template.format(context=context, question=user_input)
            full_prompt += f"\n\nYou are {bot_name} helping {name}. Always end with a follow-up question."
            
            if hasattr(llm, 'invoke'):
                reply = llm.invoke(full_prompt)
            else:
                reply = f"Mock response for: {user_input}<br><br>What else would you like to know?"
        
        # Log the conversation with website context
        log_chat(user_id, user_input, "user", website_id)
        log_chat(user_id, reply, "bot", website_id)
        
        return jsonify({"response": reply, "website_id": website_id})

    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"response": "Sorry, I ran into an error. Please try again."}), 500

# ================================
# 📁 FILE MANAGEMENT ENDPOINTS
# ================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/upload", methods=["POST"])
def upload_file_multi():
    try:
        # Get website configuration
        website_id, website_config = get_website_config(request)
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        category = request.form.get('category', 'company_details')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        filename = secure_filename(file.filename)
        
        # Website-specific upload directory
        website_upload_dir = f"uploads/{website_id}"
        category_dir = os.path.join(website_upload_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        filepath = os.path.join(category_dir, filename)
        file.save(filepath)
        
        # Process file for website-specific knowledge base
        success = process_file_for_website(filepath, filename, category, website_id)
        
        if success:
            return jsonify({
                "message": f"File uploaded to {website_config['name']} knowledge base",
                "website_id": website_id,
                "category": category
            })
        else:
            return jsonify({"error": "Failed to process file"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_file_for_website(filepath, filename, category, website_id):
    """Process file for specific website's knowledge base"""
    try:
        from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        # Load document
        file_ext = filename.lower().split('.')[-1]
        if file_ext == 'pdf':
            loader = PyPDFLoader(filepath)
        elif file_ext == 'csv':
            loader = CSVLoader(filepath)
        else:
            loader = TextLoader(filepath, encoding='utf-8')
        
        documents = loader.load()
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        # Add website-specific metadata
        for chunk in chunks:
            chunk.metadata.update({
                'source_file': filename,
                'upload_time': datetime.now().isoformat(),
                'category': category,
                'website_id': website_id
            })
        
        # Add to website-specific vectorstore
        website_vectorstore = get_website_vectorstore(website_id)
        website_vectorstore.add_documents(chunks)
        website_vectorstore.persist()
        
        # Also add to global vectorstore for backward compatibility
        global vectorstore, retriever
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
        
        # Update retriever and clear QA chains to force reload
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        global qa_chains
        qa_chains.clear()
        
        return True
        
    except Exception as e:
        print(f"File processing error for {website_id}: {e}")
        return False

@app.route("/api/crawl", methods=["POST"])
def crawl_url():
    try:
        data = request.json
        url = data.get('url')
        max_pages = data.get('max_pages', 10)
        website_id = data.get('website_id', 'default')
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        # Process the URL
        success = process_url(url, max_pages, website_id)
        
        if success:
            return jsonify({"message": f"URL {url} crawled successfully for {website_id}"})
        else:
            return jsonify({"error": "Failed to crawl URL"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_url(url, max_pages=10, website_id='default'):
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
            chunk.metadata['website_id'] = website_id
        
        # Add to vector store
        global vectorstore, retriever
        
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
        global qa_chains
        qa_chains.clear()
        
        return True
        
    except Exception as e:
        print(f"URL processing error: {e}")
        return False

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

def update_prompt(new_prompt):
    try:
        global template_text, prompt
        
        template_text = new_prompt
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template_text,
        )
        
        # Save prompt to file
        os.makedirs("config", exist_ok=True)
        with open("config/prompt.txt", "w", encoding="utf-8") as f:
            f.write(new_prompt)
        
        # Clear QA chains to force recreation with new prompt
        global qa_chains
        qa_chains.clear()
        
        return True
        
    except Exception as e:
        print(f"Prompt update error: {e}")
        return False

# ================================
# 📊 KNOWLEDGE MANAGEMENT & STATS
# ================================

@app.route("/api/knowledge-stats", methods=["GET"])
def knowledge_stats():
    try:
        website_id = request.args.get('website_id', 'default')
        
        # Get vector store statistics
        try:
            test_docs = retriever.get_relevant_documents("test", k=10000)
            doc_count = len(test_docs)
            db_status = "active"
        except Exception as e:
            print(f"Vector DB test failed: {e}")
            doc_count = 0
            db_status = "error"
        
        # Get uploaded files safely
        uploaded_files = []
        try:
            upload_folder = f"uploads/{website_id}"
            if os.path.exists(upload_folder):
                for category in FILE_CATEGORIES.keys():
                    category_path = os.path.join(upload_folder, category)
                    if os.path.exists(category_path):
                        for filename in os.listdir(category_path):
                            filepath = os.path.join(category_path, filename)
                            if os.path.isfile(filepath):
                                stat = os.stat(filepath)
                                uploaded_files.append({
                                    "name": filename,
                                    "category": category,
                                    "size": stat.st_size,
                                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                                })
        except Exception as e:
            print(f"⚠️ Upload folder check failed: {e}")
        
        # Get effective LLM config
        effective_config = get_effective_llm_config(website_id)
        
        stats = {
            "website_id": website_id,
            "total_documents": max(0, doc_count),
            "vector_store_status": db_status,
            "vector_store_path": "./chroma_db",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "llm_provider": effective_config["provider"],
            "llm_model": effective_config["model"],
            "llm_temperature": effective_config["temperature"],
            "llm_option": effective_config["provider"],  # For backward compatibility
            "uploaded_files": uploaded_files,
            "file_categories": FILE_CATEGORIES
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return jsonify({
            "total_documents": 0,
            "vector_store_status": "error",
            "error": str(e)
        })

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Get available file categories"""
    return jsonify({"categories": FILE_CATEGORIES})

# ================================
# 🗂️ BULK OPERATIONS & RESET SYSTEM
# ================================

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

def create_website_backup(website_id):
    """Create backup for specific website"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"backups/{website_id}_backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup website-specific files and knowledge base
    try:
        upload_dir = f"uploads/{website_id}"
        if os.path.exists(upload_dir):
            shutil.copytree(upload_dir, f"{backup_dir}/uploads")
        
        kb_path = get_knowledge_base_path(website_id)
        if os.path.exists(kb_path):
            shutil.copytree(kb_path, f"{backup_dir}/knowledge_base")
        
        return backup_dir
    except Exception as e:
        print(f"Backup error for {website_id}: {e}")
        raise e

def reset_website_knowledge(website_id):
    """Reset knowledge base for a specific website"""
    # Clear website-specific knowledge base
    kb_path = get_knowledge_base_path(website_id)
    if os.path.exists(kb_path):
        shutil.rmtree(kb_path)
    
    # Clear website-specific uploads
    upload_path = f"uploads/{website_id}"
    if os.path.exists(upload_path):
        shutil.rmtree(upload_path)
    
    # Clear from cache
    if website_id in llm_instances:
        del llm_instances[website_id]
    if website_id in qa_chains:
        del qa_chains[website_id]

@app.route("/api/refresh-session", methods=["POST"])
def refresh_chat_session():
    """Refresh chat session without deleting knowledge"""
    try:
        session.clear()
        return jsonify({
            "status": "success",
            "message": "Chat session refreshed successfully! (Files and knowledge preserved)"
        })
    except Exception as e:
        print(f"Refresh error: {e}")
        return jsonify({"status": "error", "message": "Failed to refresh chat session"}), 500

@app.route("/api/reset-knowledge", methods=["POST"])
def reset_knowledge_base():
    """Reset knowledge base with corruption handling"""
    try:
        print("🔥 Starting knowledge base reset...")
        
        # 1. FORCE CLOSE ANY VECTOR STORE CONNECTIONS
        global vectorstore, retriever, qa_chain, qa_chains, llm_instances
        try:
            vectorstore = None
            retriever = None  
            qa_chain = None
            qa_chains.clear()
            llm_instances.clear()
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
            return handle_vector_store_corruption()
            
    except Exception as e:
        print(f"❌ Knowledge reset error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error", 
            "message": f"Failed to reset knowledge base: {str(e)}"
        }), 500

def handle_vector_store_corruption():
    """Handle severe vector store corruption"""
    try:
        print("🚨 Handling vector store corruption...")
        
        # More aggressive cleanup
        import subprocess
        try:
            # Try to force delete on Windows/Linux
            if os.name == 'nt':  # Windows
                subprocess.run(['rmdir', '/s', '/q', 'chroma_db'], shell=True, check=False)
            else:  # Unix-like
                subprocess.run(['rm', '-rf', 'chroma_db'], check=False)
        except:
            pass
        
        # Wait longer
        time.sleep(5)
        
        # Try creating vector store again
        os.makedirs("./chroma_db", exist_ok=True)
        
        global vectorstore, retriever
        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        return jsonify({
            "status": "success",
            "message": "Vector store corruption handled. Fresh knowledge base created."
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Severe corruption detected. Manual intervention required: {str(e)}"
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
        
        from db_model import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Clear chat logs
        cursor.execute("DELETE FROM chat_logs")
        cursor.execute("DELETE FROM conversation_nodes")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Also clear CSV logs if they exist
        if os.path.exists("logs/chat_logs.csv"):
            os.remove("logs/chat_logs.csv")
        
        return jsonify({
            "status": "success",
            "message": "All chat logs and conversation history cleared!"
        })
        
    except Exception as e:
        print(f"Log clearing error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to clear logs: {str(e)}"
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
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                shutil.copytree(app.config['UPLOAD_FOLDER'], f"{backup_dir}/uploads")
                backup_results["files"] = "✅ Files backed up"
        except Exception as e:
            backup_results["files"] = f"❌ Error backing up files: {str(e)}"
        
        # 3. Backup configuration
        try:
            if os.path.exists("config"):
                shutil.copytree("config", f"{backup_dir}/config")
                backup_results["config"] = "✅ Config backed up"
        except Exception as e:
            backup_results["config"] = f"❌ Error backing up config: {str(e)}"
        
        # 4. Backup logs
        try:
            if os.path.exists("logs"):
                shutil.copytree("logs", f"{backup_dir}/logs")
                backup_results["logs"] = "✅ Logs backed up"
        except Exception as e:
            backup_results["logs"] = f"❌ Error backing up logs: {str(e)}"
        
        return jsonify({
            "status": "success",
            "message": f"Backup created at {backup_dir}",
            "backup_path": backup_dir,
            "details": backup_results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Backup failed: {str(e)}"
        }), 500

# ================================
# 📄 TEMPLATE & LEGACY ENDPOINTS
# ================================

@app.route("/template", methods=["GET"])
def get_template():
    return jsonify({"template": template_text})

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
        global vectorstore, retriever, qa_chains
        vectorstore = Chroma.from_documents(
            chunks, 
            embedding=embeddings, 
            persist_directory="./chroma_db"
        )
        vectorstore.persist()
        
        # Update retriever and clear QA chains
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        qa_chains.clear()  # Force recreation with new data
        
        return jsonify({"status": "FAQ updated successfully"})
    except Exception as e:
        print(f"FAQ update error: {e}")
        return jsonify({"error": f"Failed to update FAQ: {str(e)}"}), 500

@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Test vector store
        test_docs = retriever.get_relevant_documents("test")
        effective_config = get_effective_llm_config()
        
        return jsonify({
            "status": "healthy",
            "vectorstore_docs": len(test_docs),
            "llm_model": effective_config.get("model", "unknown"),
            "llm_provider": effective_config.get("provider", "unknown"),
            "llm_option": LLM_OPTION,
            "websites_configured": len(WEBSITE_CONFIGS)
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# ================================
# 💬 ENHANCED CHAT LOGGING
# ================================

def log_chat(user_id, message, sender, website_id=None):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Escape commas and quotes in message for CSV safety
        clean_message = message.replace('"', '""').replace('\n', ' ').replace('\r', ' ')
        log_entry = f'"{now}","{user_id}","{sender}","{website_id or "default"}","{clean_message}"\n'
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        with open("logs/chat_logs.csv", "a", encoding="utf-8") as f:
            f.write(log_entry)
            
        # Also log to database if available
        try:
            from db_model import log_chat as db_log_chat
            db_log_chat(user_id, message, sender)
        except ImportError:
            pass  # DB logging not available
        except Exception as e:
            print(f"Database logging error: {e}")
            
    except Exception as e:
        print(f"Logging error: {e}")

# ================================
# 🧪 INITIALIZATION & STARTUP
# ================================

def initialize_application():
    """Initialize the application with all components"""
    try:
        # Create necessary directories
        os.makedirs("./chroma_db", exist_ok=True)
        os.makedirs("./data", exist_ok=True)
        os.makedirs("./logs", exist_ok=True)
        os.makedirs("./config", exist_ok=True)
        os.makedirs("./backups", exist_ok=True)
        
        # Initialize website configurations
        initialize_website_configs()
        
        # Initialize vector store if empty
        try:
            test_docs = retriever.get_relevant_documents("test", k=1)
            print(f"📊 Vector store contains {len(test_docs)} test documents")
        except Exception as e:
            print(f"⚠️ Vector store initialization issue: {e}")
        
        # Verify LLM configuration
        effective_config = get_effective_llm_config()
        print(f"🤖 LLM Configuration: {effective_config['provider']} - {effective_config['model']}")
        
        # Create default QA chain
        update_qa_chain()
        
        print("✅ Application initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Application initialization failed: {e}")
        return False

# ================================
# 🧪 RUN APPLICATION
# ================================

if __name__ == "__main__":
    print("🚀 Starting Advanced Multi-Website RAG Chatbot with LLM Management...")
    print(f"📊 Vector store location: ./chroma_db")
    print(f"📝 FAQ file expected at: ./data/faq.txt")
    print(f"📋 Logs will be saved to: ./logs/chat_logs.csv")
    print(f"🌐 Supporting websites: {list(WEBSITE_CONFIGS.keys())}")
    print(f"🔧 Configuration directory: ./config/")
    print(f"📦 Backup directory: ./backups/")
    
    # Initialize application
    if initialize_application():
        print("🎉 Ready to serve requests!")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("💥 Failed to initialize application. Check logs for details.")
        exit(1)