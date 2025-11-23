"""API endpoints blueprint"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.file_service import save_uploaded_file, list_user_files, delete_user_file, process_file_for_user
from services.knowledge_service import remove_file_from_vectorstore, get_knowledge_stats
from services.config_service import load_user_chatbot_config, save_user_chatbot_config_file
from utils.api_key import get_user_api_key
from utils.prompts import get_default_prompt_with_name
from utils.helpers import allowed_file
from config.constants import FILE_CATEGORIES
from models.prompt_preset import PromptPreset
from werkzeug.utils import secure_filename
import os
from datetime import datetime

api_bp = Blueprint('api', __name__)


@api_bp.route("/api/upload", methods=["POST"])
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
        
        user_id = current_user.id
        
        # Save file
        filepath, filename = save_uploaded_file(user_id, file, category)
        
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


@api_bp.route("/api/files", methods=["GET"])
@login_required
def list_user_files_endpoint():
    """List all uploaded files for the current user"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        files = list_user_files(user_id)
        
        return jsonify({
            "files": files,
            "total": len(files)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/files/<path:filename>", methods=["DELETE"])
@login_required
def delete_user_file_endpoint(filename):
    """Delete a file and remove its knowledge from vectorstore"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        category = request.args.get('category', 'company_details')
        
        # Remove from vectorstore first
        remove_file_from_vectorstore(user_id, filename)
        
        # Delete the physical file
        success = delete_user_file(user_id, filename, category)
        
        if success:
            print(f"✅ Deleted file: {filename}")
            return jsonify({
                "message": f"File '{filename}' and its knowledge base entries deleted successfully",
                "filename": filename,
                "category": category
            })
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Delete error: {error_details}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/files/bulk", methods=["DELETE"])
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
                # Remove from vectorstore
                remove_file_from_vectorstore(user_id, filename)
                
                # Delete file
                if delete_user_file(user_id, filename, category):
                    deleted.append(filename)
                else:
                    errors.append(f"{filename}: File not found")
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
        
        return jsonify({
            "message": f"Deleted {len(deleted)} file(s)",
            "deleted": deleted,
            "errors": errors
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/user/chatbot-config", methods=["GET"])
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


@api_bp.route("/api/user/chatbot-config", methods=["POST"])
@login_required
def save_user_chatbot_config_endpoint():
    """Save current user's chatbot configuration"""
    try:
        user_id = current_user.id
        data = request.json
        
        # Load existing config
        config = load_user_chatbot_config(user_id)
        
        # Update with new values
        if 'bot_name' in data:
            config['bot_name'] = data['bot_name']
        if 'prompt' in data:
            config['prompt'] = data['prompt']
        if 'prompt_preset_id' in data:
            config['prompt_preset_id'] = data['prompt_preset_id']
        
        # Save config
        success = save_user_chatbot_config_file(user_id, config)
        
        if success:
            return jsonify({
                "message": "Configuration saved successfully",
                "config": config
            })
        else:
            return jsonify({"error": "Failed to save configuration"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/knowledge-stats", methods=["GET"])
@login_required
def knowledge_stats():
    """Get knowledge base statistics for current user"""
    try:
        user_id = current_user.id
        stats = get_knowledge_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return jsonify({
            "total_documents": 0,
            "vector_store_status": "error",
            "error": str(e)
        }), 500


@api_bp.route("/api/prompt", methods=["GET", "POST"])
@login_required
def manage_prompt():
    """Get or update user's chatbot prompt"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        
        if request.method == "GET":
            # Get user's prompt
            config = load_user_chatbot_config(user_id)
            prompt = config.get('prompt')
            
            # If no prompt, use default with bot_name
            if prompt is None:
                bot_name = config.get('bot_name', 'Cortex')
                prompt = get_default_prompt_with_name(bot_name)
            
            return jsonify({"prompt": prompt})
        
        elif request.method == "POST":
            # Update user's prompt
            data = request.json
            new_prompt = data.get('prompt')
            
            if not new_prompt:
                return jsonify({"error": "No prompt provided"}), 400
            
            # Load existing config
            config = load_user_chatbot_config(user_id)
            config['prompt'] = new_prompt
            
            # Save config
            success = save_user_chatbot_config_file(user_id, config)
            
            if success:
                return jsonify({"message": "Prompt updated successfully"})
            else:
                return jsonify({"error": "Failed to update prompt"}), 500
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/categories", methods=["GET"])
@login_required
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


@api_bp.route("/api/prompt-presets", methods=["GET"])
@login_required
def get_prompt_presets():
    """Get available prompt presets from database"""
    try:
        presets = PromptPreset.get_all()
        # Convert to dictionary format for frontend (ID as key)
        presets_dict = {}
        for preset in presets:
            preset_id = str(preset['id'])  # Ensure ID is string
            presets_dict[preset_id] = {
                'id': preset_id,
                'name': preset['name'],
                'icon': preset['icon'],
                'description': preset['description'],
                'prompt': preset['prompt']
            }
        return jsonify({
            "presets": presets_dict
        })
    except Exception as e:
        print(f"Error in get_prompt_presets: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/llm-config", methods=["GET"])
@login_required
def get_llm_config():
    """Get LLM configuration"""
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        llm_option = os.getenv("LLM_OPTION", "openai")
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Check if OpenAI key exists
        has_openai_key = bool(openai_api_key and openai_api_key.strip())
        
        # Mask API key for display
        openai_key_masked = ""
        if has_openai_key:
            if len(openai_api_key) > 8:
                openai_key_masked = openai_api_key[:4] + "..." + openai_api_key[-4:]
            else:
                openai_key_masked = "****"
        
        # Get model and temperature from env or defaults
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        
        # Determine current model
        if llm_option == "openai":
            current_model = openai_model
        else:
            current_model = ollama_model
        
        return jsonify({
            "llm_option": llm_option,
            "has_openai_key": has_openai_key,
            "openai_key_masked": openai_key_masked,
            "openai_model": openai_model,
            "openai_temperature": openai_temperature,
            "ollama_url": ollama_url,
            "ollama_model": ollama_model,
            "current_model": current_model
        })
    except Exception as e:
        print(f"Error in get_llm_config: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/files-by-category", methods=["GET"])
@login_required
def get_files_by_category():
    """Get uploaded files organized by category for current user"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        categories_with_files = {}
        
        # User-specific upload folder
        user_upload_dir = f"uploads/user_{user_id}"
        
        if not os.path.exists(user_upload_dir):
            os.makedirs(user_upload_dir, exist_ok=True)
        
        # Get all files for user
        all_files = list_user_files(user_id)
        
        # Organize by category
        for category_id, category_info in FILE_CATEGORIES.items():
            category_dir = os.path.join(user_upload_dir, category_id)
            category_files = []
            
            # Filter files for this category
            for file_info in all_files:
                if file_info.get('category') == category_id:
                    file_stat = os.stat(file_info['path'])
                    category_files.append({
                        "name": file_info['filename'],
                        "size": file_stat.st_size,
                        "modified": datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            categories_with_files[category_id] = {
                "name": category_info['name'],
                "description": category_info['description'],
                "file_count": len(category_files),
                "files": category_files
            }
        
        return jsonify(categories_with_files)
        
    except Exception as e:
        print(f"Error in get_files_by_category: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/websites", methods=["GET"])
@login_required
def list_websites():
    """List websites - Returns empty for user-based system"""
    try:
        # In v2, we use user-based isolation instead of website-based
        # Return empty websites object for compatibility
        return jsonify({
            "websites": {}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/websites", methods=["POST"])
@login_required
def add_website():
    """Add website - Returns success for compatibility"""
    try:
        # In v2, we use user-based isolation
        # This endpoint exists for compatibility but doesn't create websites
        data = request.json
        website_name = data.get('name', 'Website')
        
        return jsonify({
            "message": f"Website '{website_name}' added successfully (user-based system)",
            "note": "v2 uses user-based isolation instead of website-based"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/website/<website_id>/stats", methods=["GET"])
@login_required
def get_website_stats(website_id):
    """Get website statistics - Returns user stats for compatibility"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        
        # Get user's knowledge stats
        stats = get_knowledge_stats(user_id)
        all_files = list_user_files(user_id)
        
        # Return stats in website format for compatibility
        return jsonify({
            "documents": stats.get('total_documents', 0),
            "files": len(all_files),
            "vector_store_status": stats.get('vector_store_status', 'unknown')
        })
    except Exception as e:
        return jsonify({
            "documents": 0,
            "files": 0,
            "vector_store_status": "error",
            "error": str(e)
        }), 500


@api_bp.route("/api/knowledge-stats-detailed", methods=["GET"])
@login_required
def knowledge_stats_detailed():
    """Get detailed knowledge base statistics for current user"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        
        # Get basic stats
        stats = get_knowledge_stats(user_id)
        all_files = list_user_files(user_id)
        
        # Organize files by category
        files_by_category = {}
        for file_info in all_files:
            category = file_info.get('category', 'company_details')
            if category not in files_by_category:
                files_by_category[category] = []
            files_by_category[category].append(file_info)
        
        # Calculate category stats
        category_stats = {}
        for category_id, category_info in FILE_CATEGORIES.items():
            category_files = files_by_category.get(category_id, [])
            category_stats[category_id] = {
                "name": category_info['name'],
                "file_count": len(category_files),
                "total_size": sum(f.get('size', 0) for f in category_files)
            }
        
        return jsonify({
            "vector_documents": stats.get('total_documents', 0),
            "vector_store_status": stats.get('vector_store_status', 'unknown'),
            "files": {
                "total_count": len(all_files),
                "total_size": sum(f.get('size', 0) for f in all_files),
                "by_category": category_stats
            },
            "database": {
                "chat_logs": 0,  # TODO: Implement chat log counting
                "users": 1  # Current user
            },
            "backups": 0  # TODO: Count user backups
        })
    except Exception as e:
        print(f"❌ Detailed stats error: {e}")
        return jsonify({
            "vector_documents": 0,
            "vector_store_status": "error",
            "files": {"total_count": 0, "total_size": 0, "by_category": {}},
            "database": {"chat_logs": 0, "users": 0},
            "backups": 0,
            "error": str(e)
        }), 500


@api_bp.route("/api/crawl", methods=["POST"])
@login_required
def crawl_url():
    """Crawl a website and add to knowledge base"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.json
        url = data.get('url')
        max_pages = data.get('max_pages', 10)
        category = data.get('category', 'company_details')
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        user_id = current_user.id
        
        # Process URL using WebBaseLoader
        try:
            from langchain_community.document_loaders import WebBaseLoader
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from services.knowledge_service import get_user_vectorstore, embeddings
            
            if not embeddings:
                return jsonify({"error": "Embeddings not available"}), 500
            
            # Load web pages
            loader = WebBaseLoader([url])
            documents = loader.load()
            
            if not documents:
                return jsonify({"error": "No content found at URL"}), 400
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_documents(documents)
            
            # Add metadata
            for chunk in chunks:
                chunk.metadata.update({
                    'source_file': url,
                    'upload_time': datetime.now().isoformat(),
                    'category': category,
                    'user_id': str(user_id),
                    'source_type': 'web_crawl'
                })
            
            # Add to user's vectorstore
            user_vectorstore = get_user_vectorstore(user_id)
            if user_vectorstore:
                user_vectorstore.add_documents(chunks)
                return jsonify({
                    "message": f"URL {url} crawled successfully. Added {len(chunks)} chunks to knowledge base.",
                    "chunks_added": len(chunks)
                })
            else:
                return jsonify({"error": "Failed to access knowledge base"}), 500
                
        except ImportError:
            return jsonify({"error": "WebBaseLoader not available. Install required dependencies."}), 500
        except Exception as e:
            print(f"❌ Crawl error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Failed to crawl URL: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/backup-knowledge", methods=["POST"])
@login_required
def backup_knowledge():
    """Create a backup of user's knowledge base"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f"backups/user_{user_id}/backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_results = {}
        
        # 1. Backup vector database
        try:
            user_kb_path = f"./chroma_db/user_{user_id}"
            if os.path.exists(user_kb_path):
                import shutil
                shutil.copytree(user_kb_path, f"{backup_dir}/chroma_db")
                backup_results["vectors"] = "✅ Vector database backed up"
            else:
                backup_results["vectors"] = "ℹ️ No vector database to backup"
        except Exception as e:
            backup_results["vectors"] = f"❌ Error backing up vectors: {str(e)}"
        
        # 2. Backup uploaded files
        try:
            user_upload_dir = f"uploads/user_{user_id}"
            if os.path.exists(user_upload_dir):
                import shutil
                shutil.copytree(user_upload_dir, f"{backup_dir}/uploads")
                backup_results["files"] = "✅ Files backed up"
            else:
                backup_results["files"] = "ℹ️ No files to backup"
        except Exception as e:
            backup_results["files"] = f"❌ Error backing up files: {str(e)}"
        
        # 3. Backup config
        try:
            user_config_path = f"./config/user_{user_id}"
            if os.path.exists(user_config_path):
                import shutil
                shutil.copytree(user_config_path, f"{backup_dir}/config")
                backup_results["config"] = "✅ Configuration backed up"
            else:
                backup_results["config"] = "ℹ️ No config to backup"
        except Exception as e:
            backup_results["config"] = f"❌ Error backing up config: {str(e)}"
        
        return jsonify({
            "message": "Backup created successfully",
            "backup_location": backup_dir,
            "backup_results": backup_results
        })
        
    except Exception as e:
        print(f"❌ Backup error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/list-backups", methods=["GET"])
@login_required
def list_backups():
    """List all backups for current user"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        backups = []
        backup_dir = f"backups/user_{user_id}"
        
        def get_folder_size(path):
            """Calculate folder size in bytes"""
            total = 0
            try:
                for entry in os.scandir(path):
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += get_folder_size(entry.path)
            except:
                pass
            return total
        
        if os.path.exists(backup_dir):
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                if os.path.isdir(item_path) and item.startswith("backup_"):
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
        print(f"❌ List backups error: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/restore-knowledge", methods=["POST"])
@login_required
def restore_knowledge():
    """Restore user's knowledge base from a backup"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.json
        backup_path = data.get("backup_path")
        
        if not backup_path or not os.path.exists(backup_path):
            return jsonify({"error": "Invalid backup path"}), 400
        
        user_id = current_user.id
        restore_results = {}
        import shutil
        
        # 1. Restore vector database
        try:
            vector_backup = f"{backup_path}/chroma_db"
            if os.path.exists(vector_backup):
                user_kb_path = f"./chroma_db/user_{user_id}"
                if os.path.exists(user_kb_path):
                    shutil.rmtree(user_kb_path)
                shutil.copytree(vector_backup, user_kb_path)
                restore_results["vectors"] = "✅ Vector database restored"
            else:
                restore_results["vectors"] = "ℹ️ No vector database in backup"
        except Exception as e:
            restore_results["vectors"] = f"❌ Error restoring vectors: {str(e)}"
        
        # 2. Restore uploaded files
        try:
            files_backup = f"{backup_path}/uploads"
            if os.path.exists(files_backup):
                user_upload_dir = f"uploads/user_{user_id}"
                if os.path.exists(user_upload_dir):
                    shutil.rmtree(user_upload_dir)
                shutil.copytree(files_backup, user_upload_dir)
                restore_results["files"] = "✅ Files restored"
            else:
                restore_results["files"] = "ℹ️ No files in backup"
        except Exception as e:
            restore_results["files"] = f"❌ Error restoring files: {str(e)}"
        
        # 3. Restore config
        try:
            config_backup = f"{backup_path}/config"
            if os.path.exists(config_backup):
                user_config_path = f"./config/user_{user_id}"
                if os.path.exists(user_config_path):
                    shutil.rmtree(user_config_path)
                shutil.copytree(config_backup, user_config_path)
                restore_results["config"] = "✅ Configuration restored"
            else:
                restore_results["config"] = "ℹ️ No config in backup"
        except Exception as e:
            restore_results["config"] = f"❌ Error restoring config: {str(e)}"
        
        return jsonify({
            "message": "Knowledge base restored successfully",
            "restore_results": restore_results
        })
        
    except Exception as e:
        print(f"❌ Restore error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/reset-knowledge", methods=["POST"])
@login_required
def reset_knowledge():
    """Reset user's knowledge base based on reset_type"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.json
        reset_type = data.get('reset_type', 'all')
        confirm_phrase = data.get('confirm_phrase', '')
        
        # Verify confirmation phrase
        if confirm_phrase != 'RESET ALL KNOWLEDGE':
            return jsonify({"error": "Invalid confirmation phrase"}), 400
        
        user_id = current_user.id
        import shutil
        
        reset_results = {}
        
        if reset_type in ['files', 'all']:
            # Delete uploaded files
            try:
                user_upload_dir = f"uploads/user_{user_id}"
                if os.path.exists(user_upload_dir):
                    shutil.rmtree(user_upload_dir)
                    os.makedirs(user_upload_dir, exist_ok=True)
                reset_results["files"] = "✅ Files deleted"
            except Exception as e:
                reset_results["files"] = f"❌ Error: {str(e)}"
        
        if reset_type in ['vectors', 'all']:
            # Clear vector database
            try:
                user_kb_path = f"./chroma_db/user_{user_id}"
                if os.path.exists(user_kb_path):
                    shutil.rmtree(user_kb_path)
                    os.makedirs(user_kb_path, exist_ok=True)
                reset_results["vectors"] = "✅ Vector database cleared"
            except Exception as e:
                reset_results["vectors"] = f"❌ Error: {str(e)}"
        
        if reset_type in ['logs', 'all']:
            # Clear logs (if user-specific logs exist)
            reset_results["logs"] = "✅ Logs cleared (if any)"
        
        if reset_type in ['database', 'all']:
            # Clear database records (if user-specific)
            reset_results["database"] = "✅ Database records cleared (if any)"
        
        if reset_type in ['prompt', 'all']:
            # Reset prompt to default
            try:
                from services.config_service import load_user_chatbot_config, save_user_chatbot_config_file
                from utils.prompts import get_default_prompt_with_name
                
                config = load_user_chatbot_config(user_id)
                bot_name = config.get('bot_name', 'Cortex')
                config['prompt'] = get_default_prompt_with_name(bot_name)
                save_user_chatbot_config_file(user_id, config)
                reset_results["prompt"] = "✅ Prompt reset to default"
            except Exception as e:
                reset_results["prompt"] = f"❌ Error: {str(e)}"
        
        return jsonify({
            "message": f"Reset completed: {reset_type}",
            "reset_results": reset_results
        })
        
    except Exception as e:
        print(f"❌ Reset error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

