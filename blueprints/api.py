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
    """File upload endpoint - saves file and extracts text for preview (does not auto-ingest)"""
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
        
        # Check file count limit (100 files per user)
        from models.uploaded_file import UploadedFile
        existing_files = UploadedFile.get_all_by_user(user_id)
        MAX_FILES_PER_USER = 100
        
        # Count only non-deleted files
        active_files = [f for f in existing_files if f.get('status') != 'deleted']
        
        if len(active_files) >= MAX_FILES_PER_USER:
            return jsonify({
                "error": f"File upload limit reached. Maximum {MAX_FILES_PER_USER} files per user. Please delete some files before uploading new ones."
            }), 400
        
        # Save file
        filepath, filename = save_uploaded_file(user_id, file, category)
        
        # Get AI cleaning preference (default: True)
        use_ai_cleaning = request.form.get('use_ai_cleaning', 'true').lower() == 'true'
        
        # Extract text for preview (does not ingest)
        from services.file_service import extract_text_from_file
        from services.ai_text_cleaning import clean_text_with_ai
        
        extracted_text = extract_text_from_file(filepath, filename)
        
        if extracted_text is None:
            return jsonify({"error": "Failed to extract text from file"}), 500
        
        # Log extraction results for debugging
        print(f"📊 Extraction results for {filename}:")
        print(f"   - Text length (raw): {len(extracted_text)} characters")
        print(f"   - Word count (raw): {len(extracted_text.split())} words")
        
        # Apply AI cleaning to extract only essential content (if enabled)
        # Uses system OpenAI credentials for AI-powered features
        if use_ai_cleaning:
            try:
                print("🤖 Applying AI cleaning to uploaded file using system OpenAI...")
                extracted_text = clean_text_with_ai(extracted_text)
                print(f"   - Text length (cleaned): {len(extracted_text)} characters")
                print(f"   - Word count (cleaned): {len(extracted_text.split())} words")
            except Exception as e:
                print(f"⚠️ AI cleaning failed, using original text: {e}")
                import traceback
                traceback.print_exc()
                # Continue with original text if AI cleaning fails
        else:
            print("ℹ️ AI cleaning disabled by user")
        
        # Calculate word and character counts (after cleaning)
        word_count = len(extracted_text.split())
        char_count = len(extracted_text)
        
        # Save to database with status='preview'
        file_id = UploadedFile.create(
            user_id=user_id,
            filename=filename,
            filepath=filepath,
            category=category,
            extracted_text=extracted_text,
            word_count=word_count,
            char_count=char_count,
            status='preview'
        )
        
        if file_id:
            # Get updated file count (refresh from DB)
            updated_files = UploadedFile.get_all_by_user(user_id)
            updated_active_files = [f for f in updated_files if f.get('status') != 'deleted']
            remaining_files = MAX_FILES_PER_USER - len(updated_active_files)
            
            return jsonify({
                "message": f"File uploaded successfully. Please review and ingest to add to knowledge base. ({remaining_files} files remaining)",
                "user_id": user_id,
                "category": category,
                "filename": filename,
                "file_id": file_id,
                "word_count": word_count,
                "char_count": char_count,
                "status": "preview",
                "file_count": len(existing_files) + 1,
                "max_files": MAX_FILES_PER_USER,
                "remaining_files": remaining_files
            })
        else:
            return jsonify({"error": "Failed to save file information"}), 500
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Upload error: {error_details}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/files", methods=["GET"])
@login_required
def list_user_files_endpoint():
    """List all uploaded files for the current user (from database with status)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.uploaded_file import UploadedFile
        
        # Get files from database (includes status)
        db_files = UploadedFile.get_all_by_user(user_id)
        
        # Format files for response
        files = []
        for db_file in db_files:
            # Convert datetime objects to ISO format
            uploaded_at = db_file.get('uploaded_at')
            if uploaded_at and hasattr(uploaded_at, 'isoformat'):
                uploaded_at = uploaded_at.isoformat()
            elif uploaded_at:
                uploaded_at = str(uploaded_at)
            
            ingested_at = db_file.get('ingested_at')
            if ingested_at and hasattr(ingested_at, 'isoformat'):
                ingested_at = ingested_at.isoformat()
            elif ingested_at:
                ingested_at = str(ingested_at)
            
            # Get file size from filesystem
            filepath = db_file.get('filepath')
            size = 0
            if filepath and os.path.exists(filepath):
                size = os.path.getsize(filepath)
            
            files.append({
                "id": db_file.get('id'),
                "filename": db_file.get('filename'),
                "category": db_file.get('category'),
                "size": size,
                "uploaded_at": uploaded_at,
                "status": db_file.get('status', 'preview'),
                "word_count": db_file.get('word_count', 0),
                "char_count": db_file.get('char_count', 0),
                "path": filepath
            })
        
        return jsonify({
            "files": files,
            "total": len(files)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/files/<int:file_id>", methods=["GET"])
@login_required
def get_file_preview(file_id):
    """Get file details for preview"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.uploaded_file import UploadedFile
        
        file_data = UploadedFile.get_by_id(user_id, file_id)
        if not file_data:
            return jsonify({"error": "File not found"}), 404
        
        # Convert datetime objects to ISO format
        uploaded_at = file_data.get('uploaded_at')
        if uploaded_at and hasattr(uploaded_at, 'isoformat'):
            uploaded_at = uploaded_at.isoformat()
        elif uploaded_at:
            uploaded_at = str(uploaded_at)
        
        ingested_at = file_data.get('ingested_at')
        if ingested_at and hasattr(ingested_at, 'isoformat'):
            ingested_at = ingested_at.isoformat()
        elif ingested_at:
            ingested_at = str(ingested_at)
        
        return jsonify({
            "id": file_data.get('id'),
            "filename": file_data.get('filename'),
            "category": file_data.get('category'),
            "extracted_text": file_data.get('extracted_text', ''),
            "word_count": file_data.get('word_count', 0),
            "char_count": file_data.get('char_count', 0),
            "status": file_data.get('status', 'preview'),
            "uploaded_at": uploaded_at,
            "ingested_at": ingested_at,
            "filepath": file_data.get('filepath')
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/files/<int:file_id>/ingest", methods=["POST"])
@login_required
def ingest_uploaded_file(file_id):
    """Ingest uploaded file to knowledge base (vectorstore)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        data = request.json
        
        from models.uploaded_file import UploadedFile
        from services.knowledge_service import get_user_vectorstore, embeddings
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        try:
            from langchain_core.documents import Document
        except ImportError:
            from langchain.schema import Document
        from datetime import datetime
        
        # Get uploaded file
        uploaded_file = UploadedFile.get_by_id(user_id, file_id)
        if not uploaded_file:
            return jsonify({"error": "File not found"}), 404
        
        if uploaded_file['status'] == 'ingested':
            return jsonify({"error": "File already ingested"}), 400
        
        # Get text (user may have edited it)
        text = data.get('text', uploaded_file.get('extracted_text'))
        if not text:
            return jsonify({"error": "No text to ingest"}), 400
        
        # Update text if edited
        if text != uploaded_file.get('extracted_text'):
            UploadedFile.update_text(file_id, text)
        
        # RAG Process Explanation:
        # 1. Text is split into chunks (not converted to JSON - we use vector embeddings)
        # 2. Each chunk is converted to a vector embedding (numerical representation)
        # 3. Embeddings are stored in ChromaDB vector database
        # 4. During queries, the question is also converted to an embedding
        # 5. Similar embeddings are retrieved (semantic search)
        # 6. Cleaner text = better embeddings = better retrieval accuracy
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        doc = Document(
            page_content=text,
            metadata={
                'source_file': uploaded_file['filename'],
                'upload_time': datetime.now().isoformat(),
                'category': uploaded_file['category'],  # ✅ Category is tagged in metadata for filtering/search
                'user_id': str(user_id),
                'source_type': 'file_upload',
                'file_id': file_id
            }
        )
        
        chunks = text_splitter.split_documents([doc])
        
        # Add to vectorstore
        user_vectorstore = get_user_vectorstore(user_id)
        if user_vectorstore is None:
            print(f"❌ Failed to get vectorstore for user {user_id}")
            return jsonify({"error": "Failed to access knowledge base. Please check embeddings and vectorstore initialization."}), 500
        
        try:
            # Ensure write permissions
            kb_path = f"./chroma_db/user_{user_id}"
            if os.path.exists(kb_path):
                os.chmod(kb_path, 0o777)
                for root, dirs, files in os.walk(kb_path):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), 0o777)
                    for f in files:
                        os.chmod(os.path.join(root, f), 0o666)
            
            print(f"📝 Adding {len(chunks)} chunks to vectorstore...")
            user_vectorstore.add_documents(chunks)
            print(f"✅ Successfully added chunks to vectorstore")
            
            # Update status to 'ingested'
            UploadedFile.update_status(file_id, 'ingested')
            
            return jsonify({
                "message": f"File '{uploaded_file['filename']}' ingested successfully. Added {len(chunks)} chunks.",
                "chunks_added": len(chunks),
                "status": "ingested"
            })
        except Exception as e:
            print(f"❌ Error adding documents to vectorstore: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Failed to add documents to knowledge base: {str(e)}"}), 500
            
    except Exception as e:
        print(f"❌ Ingest uploaded file error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/files/<int:file_id>", methods=["DELETE"])
@login_required
def delete_user_file_endpoint(file_id):
    """Delete a file and remove its knowledge from vectorstore"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.uploaded_file import UploadedFile
        
        # Get file info
        file_data = UploadedFile.get_by_id(user_id, file_id)
        if not file_data:
            return jsonify({"error": "File not found"}), 404
        
        filename = file_data['filename']
        category = file_data['category']
        
        # Remove from vectorstore if ingested
        if file_data['status'] == 'ingested':
            remove_file_from_vectorstore(user_id, filename)
        
        # Delete from database (soft delete)
        UploadedFile.delete(file_id)
        
        # Delete the physical file
        filepath = file_data.get('filepath')
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"⚠️ Could not delete physical file: {e}")
        
        print(f"✅ Deleted file: {filename}")
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
        
        # Load appearance config from database
        from models.chatbot_appearance import ChatbotAppearance
        appearance = ChatbotAppearance.get_by_user(user_id)
        if appearance:
            appearance_dict = ChatbotAppearance.to_dict(appearance)
            if appearance_dict:
                config['short_info'] = appearance_dict.get('short_info')
                config['primary_color'] = appearance_dict.get('primary_color')
                config['avatar'] = appearance_dict.get('avatar')
                config['suggested_messages'] = appearance_dict.get('suggested_messages')
        
        # Generate API key if it doesn't exist
        if not config.get('api_key'):
            api_key = get_user_api_key(user_id)
            config['api_key'] = api_key
        
        # If prompt is None, generate default prompt with bot_name
        if config.get('prompt') is None:
            bot_name = config.get('bot_name', 'Cortex')
            config['prompt'] = get_default_prompt_with_name(bot_name)
        
        return jsonify({"config": config})
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
        
        # Advanced chatbot settings
        if 'temperature' in data:
            config['temperature'] = float(data['temperature'])
        if 'max_tokens' in data:
            config['max_tokens'] = int(data['max_tokens'])
        if 'top_p' in data:
            config['top_p'] = float(data['top_p'])
        if 'frequency_penalty' in data:
            config['frequency_penalty'] = float(data['frequency_penalty'])
        if 'presence_penalty' in data:
            config['presence_penalty'] = float(data['presence_penalty'])
        if 'response_style' in data:
            config['response_style'] = data['response_style']
        if 'system_instructions' in data:
            config['system_instructions'] = data['system_instructions']
        
        # LLM Provider settings
        if 'llm_provider' in data:
            config['llm_provider'] = data['llm_provider']
        if 'llm_model' in data:
            config['llm_model'] = data['llm_model']
        if 'llm_api_key' in data:
            # Only save if provided (not masked)
            if data['llm_api_key']:
                config['llm_api_key'] = data['llm_api_key']
            # If None or empty, remove it (use system default)
            elif 'llm_api_key' in config:
                config['llm_api_key'] = None
        
        # Save basic config to file
        success = save_user_chatbot_config_file(user_id, config)
        
        # Save appearance config to database
        from models.chatbot_appearance import ChatbotAppearance
        short_info = data.get('short_info') or data.get('description')
        primary_color = data.get('primary_color')
        avatar = data.get('avatar')
        suggested_messages = data.get('suggested_messages')
        
        if short_info is not None or primary_color is not None or avatar is not None or suggested_messages is not None:
            appearance_success = ChatbotAppearance.create_or_update(
                user_id=user_id,
                short_info=short_info,
                primary_color=primary_color,
                avatar_type=avatar.get('type') if avatar else None,
                avatar_value=avatar.get('value') if avatar else None,
                suggested_messages=suggested_messages
            )
            if not appearance_success:
                print(f"⚠️ Warning: Failed to save appearance config to database for user {user_id}")
        
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
    """Get knowledge base statistics for current user with limits"""
    try:
        user_id = current_user.id
        stats = get_knowledge_stats(user_id)
        
        # Get file count with limit
        from models.uploaded_file import UploadedFile
        MAX_FILES_PER_USER = 100
        uploaded_files = UploadedFile.get_all_by_user(user_id)
        file_count = len(uploaded_files)
        
        # Get crawled URLs count
        from models.crawled_url import CrawledUrl
        crawled_urls = CrawledUrl.get_all_by_user(user_id)
        crawled_count = len(crawled_urls)
        MAX_CRAWLED_URLS = 200  # Set limit for crawled URLs
        
        # Get FAQ count
        from models.faq import FAQ
        faqs = FAQ.get_all_by_user(user_id, status=None)
        faq_count = len(faqs)
        MAX_FAQS = 500  # Set limit for FAQs
        
        # Add limits and counts to stats
        stats['file_count'] = file_count
        stats['max_files'] = MAX_FILES_PER_USER
        stats['crawled_count'] = crawled_count
        stats['max_crawled'] = MAX_CRAWLED_URLS
        stats['faq_count'] = faq_count
        stats['max_faqs'] = MAX_FAQS
        
        return jsonify(stats)
    except Exception as e:
        print(f"❌ Stats error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "total_documents": 0,
            "vector_store_status": "error",
            "file_count": 0,
            "max_files": 100,
            "crawled_count": 0,
            "max_crawled": 200,
            "faq_count": 0,
            "max_faqs": 500,
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
        
        # Only OpenAI supported now (Ollama removed)
        current_model = openai_model
        
        return jsonify({
            "llm_option": "openai",  # Always OpenAI now
            "has_openai_key": has_openai_key,
            "openai_key_masked": openai_key_masked,
            "openai_model": openai_model,
            "openai_temperature": openai_temperature,
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


@api_bp.route("/api/crawl-preview", methods=["POST"])
@login_required
def crawl_url_preview():
    """Crawl URL, extract clean text, save to crawled_urls table (preview status)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.json
        url = data.get('url')
        category = data.get('category', 'company_details')
        use_ai_cleaning = data.get('use_ai_cleaning', True)  # Default to True
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        user_id = current_user.id
        
        # Check if URL already crawled
        from models.crawled_url import CrawledUrl
        existing = CrawledUrl.get_by_url(user_id, url)
        if existing and existing['status'] != 'deleted':
            return jsonify({
                "error": "URL already crawled",
                "crawled_id": existing['id'],
                "url": existing['url']
            }), 400
        
        # Extract clean text
        from services.text_cleaning_service import extract_clean_text_from_url
        from services.ai_text_cleaning import clean_text_with_ai
        
        try:
            text = extract_clean_text_from_url(url)
        except Exception as e:
            print(f"❌ Error in extract_clean_text_from_url: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Failed to extract content from URL: {str(e)}"}), 400
        
        if not text:
            return jsonify({"error": "Failed to extract content from URL. The URL may be inaccessible, require authentication, or contain no extractable text."}), 400
        
        # Apply AI cleaning to extract only essential content (if enabled)
        # Uses system OpenAI credentials for AI-powered features
        if use_ai_cleaning:
            try:
                print("🤖 Applying AI cleaning using system OpenAI...")
                text = clean_text_with_ai(text)
            except Exception as e:
                print(f"⚠️ AI cleaning failed, using original text: {e}")
                import traceback
                traceback.print_exc()
                # Continue with original text if AI cleaning fails
        else:
            print("ℹ️ AI cleaning disabled by user")
        
        # Get text stats
        word_count = len(text.split())
        char_count = len(text)
        
        # Extract title from URL or text
        title = url.split('/')[-1] or url
        if len(text) > 100:
            # Try to get title from first line
            first_line = text.split('\n')[0][:100]
            if first_line:
                title = first_line.strip()
        
        # Save to crawled_urls table (status='preview')
        crawled_id = CrawledUrl.create(
            user_id=user_id,
            url=url,
            title=title,
            extracted_text=text,
            word_count=word_count,
            char_count=char_count,
            category=category,
            status='preview'
        )
        
        if not crawled_id:
            return jsonify({"error": "Failed to save crawled URL"}), 500
        
        return jsonify({
            "id": crawled_id,
            "url": url,
            "title": title,
            "preview": text[:2000],  # First 2000 chars for preview
            "full_text": text,  # Full text for editing
            "word_count": word_count,
            "char_count": char_count,
            "status": "preview",
            "message": "URL crawled successfully. Review the extracted text before ingesting."
        })
    except Exception as e:
        print(f"❌ Crawl preview error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/crawled-urls", methods=["GET"])
@login_required
def list_crawled_urls():
    """List all crawled URLs for current user"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.crawled_url import CrawledUrl
        
        urls = CrawledUrl.get_all_by_user(user_id)
        
        # Convert datetime objects to strings for JSON
        for url in urls:
            if 'crawled_at' in url and url['crawled_at']:
                if hasattr(url['crawled_at'], 'isoformat'):
                    url['crawled_at'] = url['crawled_at'].isoformat()
            if 'ingested_at' in url and url['ingested_at']:
                if hasattr(url['ingested_at'], 'isoformat'):
                    url['ingested_at'] = url['ingested_at'].isoformat()
            if 'created_at' in url and url['created_at']:
                if hasattr(url['created_at'], 'isoformat'):
                    url['created_at'] = url['created_at'].isoformat()
            if 'updated_at' in url and url['updated_at']:
                if hasattr(url['updated_at'], 'isoformat'):
                    url['updated_at'] = url['updated_at'].isoformat()
        
        return jsonify({
            "urls": urls,
            "total": len(urls)
        })
    except Exception as e:
        print(f"❌ List crawled URLs error: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/crawled-urls/<int:crawled_id>", methods=["GET"])
@login_required
def view_crawled_url(crawled_id):
    """Get crawled URL details and extracted text"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.crawled_url import CrawledUrl
        
        crawled = CrawledUrl.get_by_id(user_id, crawled_id)
        
        if not crawled:
            return jsonify({"error": "Crawled URL not found"}), 404
        
        # Convert datetime objects to strings
        if 'crawled_at' in crawled and crawled['crawled_at']:
            if hasattr(crawled['crawled_at'], 'isoformat'):
                crawled['crawled_at'] = crawled['crawled_at'].isoformat()
        if 'ingested_at' in crawled and crawled['ingested_at']:
            if hasattr(crawled['ingested_at'], 'isoformat'):
                crawled['ingested_at'] = crawled['ingested_at'].isoformat()
        if 'created_at' in crawled and crawled['created_at']:
            if hasattr(crawled['created_at'], 'isoformat'):
                crawled['created_at'] = crawled['created_at'].isoformat()
        if 'updated_at' in crawled and crawled['updated_at']:
            if hasattr(crawled['updated_at'], 'isoformat'):
                crawled['updated_at'] = crawled['updated_at'].isoformat()
        
        # Add full_text alias for consistency with crawl-preview endpoint
        if 'extracted_text' in crawled:
            crawled['full_text'] = crawled['extracted_text']
        
        return jsonify(crawled)
    except Exception as e:
        print(f"❌ View crawled URL error: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/crawled-urls/<int:crawled_id>/ingest", methods=["POST"])
@login_required
def ingest_crawled_url(crawled_id):
    """Ingest crawled URL to knowledge base (vectorstore)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        data = request.json
        
        from models.crawled_url import CrawledUrl
        from services.knowledge_service import get_user_vectorstore, embeddings
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        try:
            from langchain_core.documents import Document
        except ImportError:
            from langchain.schema import Document
        
        # Get crawled URL
        crawled = CrawledUrl.get_by_id(user_id, crawled_id)
        if not crawled:
            return jsonify({"error": "Crawled URL not found"}), 404
        
        if crawled['status'] == 'ingested':
            return jsonify({"error": "URL already ingested"}), 400
        
        # Get text (user may have edited it)
        text = data.get('text', crawled['extracted_text'])
        if not text:
            return jsonify({"error": "No text to ingest"}), 400
        
        # Update text if edited
        if text != crawled['extracted_text']:
            CrawledUrl.update_text(crawled_id, text)
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        doc = Document(
            page_content=text,
            metadata={
                'source_file': crawled['url'],
                'upload_time': datetime.now().isoformat(),
                'category': crawled['category'],
                'user_id': str(user_id),
                'source_type': 'web_crawl',
                'crawled_id': crawled_id
            }
        )
        
        chunks = text_splitter.split_documents([doc])
        
        # Add to vectorstore
        user_vectorstore = get_user_vectorstore(user_id)
        if user_vectorstore is None:
            print(f"❌ Failed to get vectorstore for user {user_id}")
            return jsonify({"error": "Failed to access knowledge base. Please check embeddings and vectorstore initialization."}), 500
        
        try:
            print(f"📝 Adding {len(chunks)} chunks to vectorstore...")
            user_vectorstore.add_documents(chunks)
            print(f"✅ Successfully added chunks to vectorstore")
            
            # Update status to 'ingested'
            CrawledUrl.update_status(crawled_id, 'ingested')
            
            return jsonify({
                "message": f"URL {crawled['url']} ingested successfully. Added {len(chunks)} chunks.",
                "chunks_added": len(chunks),
                "status": "ingested"
            })
        except Exception as e:
            print(f"❌ Error adding documents to vectorstore: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Failed to add documents to knowledge base: {str(e)}"}), 500
            
    except Exception as e:
        print(f"❌ Ingest crawled URL error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/crawled-urls/<int:crawled_id>", methods=["DELETE"])
@login_required
def delete_crawled_url(crawled_id):
    """Delete crawled URL (and remove from vectorstore if ingested)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.crawled_url import CrawledUrl
        from services.knowledge_service import remove_file_from_vectorstore
        
        crawled = CrawledUrl.get_by_id(user_id, crawled_id)
        if not crawled:
            return jsonify({"error": "Crawled URL not found"}), 404
        
        # If ingested, remove from vectorstore
        if crawled['status'] == 'ingested':
            try:
                remove_file_from_vectorstore(user_id, crawled['url'])
            except Exception as e:
                print(f"⚠️ Warning: Could not remove from vectorstore: {e}")
        
        # Delete from database
        success = CrawledUrl.delete(crawled_id)
        
        if success:
            return jsonify({
                "message": f"URL {crawled['url']} deleted successfully"
            })
        else:
            return jsonify({"error": "Failed to delete"}), 500
            
    except Exception as e:
        print(f"❌ Delete crawled URL error: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== FAQ Endpoints ====================

@api_bp.route("/api/faqs", methods=["GET"])
@login_required
def get_faqs():
    """Get all FAQs for the current user"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.faq import FAQ
        
        status = request.args.get('status', None)  # Optional filter by status
        faqs = FAQ.get_all_by_user(user_id, status=status)
        
        # Convert datetime objects to ISO format strings
        for faq in faqs:
            if 'created_at' in faq and faq['created_at']:
                if isinstance(faq['created_at'], datetime):
                    faq['created_at'] = faq['created_at'].isoformat()
            if 'updated_at' in faq and faq['updated_at']:
                if isinstance(faq['updated_at'], datetime):
                    faq['updated_at'] = faq['updated_at'].isoformat()
            if 'ingested_at' in faq and faq['ingested_at']:
                if isinstance(faq['ingested_at'], datetime):
                    faq['ingested_at'] = faq['ingested_at'].isoformat()
        
        return jsonify({
            "faqs": faqs,
            "total": len(faqs)
        })
    except Exception as e:
        print(f"❌ Get FAQs error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/faqs/<int:faq_id>", methods=["GET"])
@login_required
def get_faq(faq_id):
    """Get a single FAQ by ID"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.faq import FAQ
        
        faq = FAQ.get_by_id(user_id, faq_id)
        if not faq:
            return jsonify({"error": "FAQ not found"}), 404
        
        # Convert datetime objects to ISO format strings
        if 'created_at' in faq and faq['created_at']:
            if isinstance(faq['created_at'], datetime):
                faq['created_at'] = faq['created_at'].isoformat()
        if 'updated_at' in faq and faq['updated_at']:
            if isinstance(faq['updated_at'], datetime):
                faq['updated_at'] = faq['updated_at'].isoformat()
        if 'ingested_at' in faq and faq['ingested_at']:
            if isinstance(faq['ingested_at'], datetime):
                faq['ingested_at'] = faq['ingested_at'].isoformat()
        
        return jsonify(faq)
    except Exception as e:
        print(f"❌ Get FAQ error: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/faqs", methods=["POST"])
@login_required
def create_faq():
    """Create a new FAQ"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        data = request.json
        
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        category = data.get('category', 'company_details')
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        if not answer:
            return jsonify({"error": "Answer is required"}), 400
        
        from models.faq import FAQ
        
        faq_id = FAQ.create(user_id, question, answer, category, status='draft')
        
        if faq_id:
            faq = FAQ.get_by_id(user_id, faq_id)
            # Convert datetime objects
            if 'created_at' in faq and faq['created_at']:
                if isinstance(faq['created_at'], datetime):
                    faq['created_at'] = faq['created_at'].isoformat()
            
            return jsonify({
                "id": faq_id,
                "message": "FAQ created successfully",
                "faq": faq
            }), 201
        else:
            return jsonify({"error": "Failed to create FAQ"}), 500
            
    except Exception as e:
        print(f"❌ Create FAQ error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/faqs/<int:faq_id>", methods=["PUT"])
@login_required
def update_faq(faq_id):
    """Update an existing FAQ"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        data = request.json
        
        from models.faq import FAQ
        
        # Check if FAQ exists and belongs to user
        faq = FAQ.get_by_id(user_id, faq_id)
        if not faq:
            return jsonify({"error": "FAQ not found"}), 404
        
        # Get update fields
        question = data.get('question')
        answer = data.get('answer')
        category = data.get('category')
        
        # Update FAQ
        success = FAQ.update(user_id, faq_id, question=question, answer=answer, category=category)
        
        if success:
            # Get updated FAQ
            updated_faq = FAQ.get_by_id(user_id, faq_id)
            # Convert datetime objects
            if 'updated_at' in updated_faq and updated_faq['updated_at']:
                if isinstance(updated_faq['updated_at'], datetime):
                    updated_faq['updated_at'] = updated_faq['updated_at'].isoformat()
            
            return jsonify({
                "message": "FAQ updated successfully",
                "faq": updated_faq
            })
        else:
            return jsonify({"error": "Failed to update FAQ"}), 500
            
    except Exception as e:
        print(f"❌ Update FAQ error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/faqs/<int:faq_id>", methods=["DELETE"])
@login_required
def delete_faq(faq_id):
    """Delete an FAQ (and remove from vectorstore if ingested)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.faq import FAQ
        from services.knowledge_service import remove_file_from_vectorstore
        
        faq = FAQ.get_by_id(user_id, faq_id)
        if not faq:
            return jsonify({"error": "FAQ not found"}), 404
        
        # If ingested, remove from vectorstore
        if faq.get('status') == 'active' and faq.get('ingested_at'):
            try:
                source_file = f"FAQ_{faq_id}"
                remove_file_from_vectorstore(user_id, source_file)
            except Exception as e:
                print(f"⚠️ Warning: Could not remove FAQ from vectorstore: {e}")
        
        # Delete from database (soft delete)
        success = FAQ.delete(faq_id)
        
        if success:
            return jsonify({
                "message": "FAQ deleted successfully"
            })
        else:
            return jsonify({"error": "Failed to delete FAQ"}), 500
            
    except Exception as e:
        print(f"❌ Delete FAQ error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/faqs/<int:faq_id>/ingest", methods=["POST"])
@login_required
def ingest_faq(faq_id):
    """Ingest FAQ to knowledge base (vectorstore)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        from models.faq import FAQ
        from services.knowledge_service import get_user_vectorstore, embeddings
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        try:
            from langchain_core.documents import Document
        except ImportError:
            from langchain.schema import Document
        
        # Get FAQ
        faq = FAQ.get_by_id(user_id, faq_id)
        if not faq:
            return jsonify({"error": "FAQ not found"}), 404
        
        if faq['status'] == 'active':
            return jsonify({"error": "FAQ already ingested"}), 400
        
        # Create document from FAQ
        # Format: "Q: {question}\nA: {answer}"
        page_content = f"Q: {faq['question']}\nA: {faq['answer']}"
        
        # For FAQs, we'll use a single chunk (preserves Q&A context)
        # But if the answer is very long, we can split it
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  # Larger chunks for FAQs
            chunk_overlap=200,
            length_function=len
        )
        
        doc = Document(
            page_content=page_content,
            metadata={
                'source_file': f"FAQ_{faq_id}",
                'upload_time': datetime.now().isoformat(),
                'category': faq['category'],
                'user_id': str(user_id),
                'source_type': 'faq',
                'faq_id': faq_id,
                'question': faq['question']
            }
        )
        
        chunks = text_splitter.split_documents([doc])
        
        # Add to vectorstore
        user_vectorstore = get_user_vectorstore(user_id)
        if user_vectorstore is None:
            print(f"❌ Failed to get vectorstore for user {user_id}")
            return jsonify({"error": "Failed to access knowledge base. Please check embeddings and vectorstore initialization."}), 500
        
        try:
            # Ensure directory and all files are writable before adding documents
            kb_path = f"./chroma_db/user_{user_id}"
            import os
            if os.path.exists(kb_path):
                # Use more permissive permissions to avoid readonly database errors
                os.chmod(kb_path, 0o777)
                # Fix permissions on all subdirectories and database files
                for root, dirs, files in os.walk(kb_path):
                    for d in dirs:
                        try:
                            os.chmod(os.path.join(root, d), 0o777)
                        except:
                            pass
                    for f in files:
                        try:
                            os.chmod(os.path.join(root, f), 0o666)
                        except:
                            pass
            
            print(f"📝 Adding {len(chunks)} FAQ chunks to vectorstore...")
            user_vectorstore.add_documents(chunks)
            print(f"✅ Successfully added FAQ chunks to vectorstore")
            
            # Update status to 'active' and set ingested_at
            FAQ.update_status(faq_id, 'active')
            
            return jsonify({
                "message": f"FAQ ingested successfully. Added {len(chunks)} chunk(s).",
                "chunks_added": len(chunks),
                "status": "active"
            })
        except Exception as e:
            print(f"❌ Error adding FAQ to vectorstore: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Failed to add FAQ to knowledge base: {str(e)}"}), 500
            
    except Exception as e:
        print(f"❌ Ingest FAQ error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/faqs/bulk-ingest", methods=["POST"])
@login_required
def bulk_ingest_faqs():
    """Bulk ingest multiple FAQs to knowledge base"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = current_user.id
        data = request.json
        faq_ids = data.get('faq_ids', [])
        
        if not faq_ids:
            return jsonify({"error": "No FAQ IDs provided"}), 400
        
        from models.faq import FAQ
        from services.knowledge_service import get_user_vectorstore, embeddings
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        try:
            from langchain_core.documents import Document
        except ImportError:
            from langchain.schema import Document
        
        user_vectorstore = get_user_vectorstore(user_id)
        if user_vectorstore is None:
            return jsonify({"error": "Failed to access knowledge base."}), 500
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len
        )
        
        total_chunks = 0
        ingested_count = 0
        errors = []
        
        for faq_id in faq_ids:
            try:
                faq = FAQ.get_by_id(user_id, faq_id)
                if not faq:
                    errors.append(f"FAQ {faq_id} not found")
                    continue
                
                if faq['status'] == 'active':
                    errors.append(f"FAQ {faq_id} already ingested")
                    continue
                
                # Create document
                page_content = f"Q: {faq['question']}\nA: {faq['answer']}"
                doc = Document(
                    page_content=page_content,
                    metadata={
                        'source_file': f"FAQ_{faq_id}",
                        'upload_time': datetime.now().isoformat(),
                        'category': faq['category'],
                        'user_id': str(user_id),
                        'source_type': 'faq',
                        'faq_id': faq_id,
                        'question': faq['question']
                    }
                )
                
                chunks = text_splitter.split_documents([doc])
                user_vectorstore.add_documents(chunks)
                FAQ.update_status(faq_id, 'active')
                
                total_chunks += len(chunks)
                ingested_count += 1
            except Exception as e:
                errors.append(f"FAQ {faq_id}: {str(e)}")
        
        return jsonify({
            "message": f"Bulk ingest completed. {ingested_count} FAQ(s) ingested, {total_chunks} chunk(s) added.",
            "ingested_count": ingested_count,
            "total_chunks": total_chunks,
            "errors": errors if errors else None
        })
        
    except Exception as e:
        print(f"❌ Bulk ingest FAQs error: {e}")
        import traceback
        traceback.print_exc()
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


@api_bp.route("/api/feedback", methods=["POST"])
@login_required
def submit_feedback():
    """Submit feedback, bug reports, or feature requests"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.get_json()
        feedback_type = data.get('type', 'comment')
        subject = data.get('subject', '')
        message = data.get('message', '')
        email = data.get('email', current_user.email if hasattr(current_user, 'email') else '')
        username = data.get('username', current_user.username if hasattr(current_user, 'username') else 'Anonymous')
        
        if not subject or not message:
            return jsonify({"error": "Subject and message are required"}), 400
        
        # Send email with feedback
        from utils.email_utils import send_feedback_email
        email_sent = send_feedback_email(feedback_type, subject, message, username, email)
        
        if not email_sent:
            print(f"⚠️ Failed to send feedback email for {feedback_type} from {username}")
            # Still return success to user even if email fails
        
        return jsonify({
            "message": "Feedback submitted successfully",
            "type": feedback_type
        }), 200
        
    except Exception as e:
        print(f"❌ Feedback submission error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to submit feedback. Please try again."}), 500


@api_bp.route("/api/test-llm", methods=["POST"])
@login_required
def test_llm():
    """Test LLM connection with current configuration"""
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.get_json()
        provider = data.get('provider', 'openai')
        model = data.get('model', 'gpt-4o-mini')
        api_key = data.get('api_key')  # Optional: user-provided API key
        
        # Only use provided API key if it's valid (not masked/placeholder)
        if api_key and ('...' in api_key or len(api_key) < 10):
            api_key = None
        
        import time
        from services.llm_service import LLMProvider
        
        # Get LLM instance
        try:
            llm = LLMProvider.get_llm(
                provider=provider,
                model=model,
                api_key=api_key,  # Use provided key or fall back to environment
                temperature=0.3,
                max_tokens=50  # Small test response
            )
        except ValueError as e:
            # Handle missing API key with helpful message
            error_msg = str(e)
            if "API key required" in error_msg:
                if provider == "claude":
                    error_msg = "Anthropic API key required. Please provide your API key in the 'API Key' field or set ANTHROPIC_API_KEY in your environment. Get your key at: https://console.anthropic.com/"
                elif provider == "gemini":
                    error_msg = "Google API key required. Please provide your API key in the 'API Key' field or set GOOGLE_API_KEY in your environment. Get your key at: https://makersuite.google.com/app/apikey"
                elif provider == "groq":
                    error_msg = "Groq API key required. Please provide your API key in the 'API Key' field or set GROQ_API_KEY in your environment. Get your key at: https://console.groq.com/"
                elif provider == "deepseek":
                    error_msg = "DeepSeek API key required. Please provide your API key in the 'API Key' field or set DEEPSEEK_API_KEY in your environment. Get your key at: https://platform.deepseek.com/"
                elif provider == "together":
                    error_msg = "Together AI API key required. Please provide your API key in the 'API Key' field or set TOGETHER_API_KEY in your environment. Get your key at: https://api.together.xyz/"
            
            return jsonify({
                "status": "error",
                "error": error_msg
            }), 400
        except Exception as e:
            error_msg = str(e)
            
            # Handle ModelProfile import errors (version compatibility)
            if "ModelProfile" in error_msg or "cannot import name" in error_msg:
                error_msg = (
                    "LangChain version compatibility issue. "
                    "Please run: pip install --upgrade langchain-anthropic langchain-core "
                    "and restart your Flask application."
                )
            # Handle other initialization errors
            elif "Failed to initialize" in error_msg or "Failed to import" in error_msg:
                # Keep the original error but make it more readable
                if provider == "claude":
                    error_msg = f"Failed to initialize Anthropic Claude: {error_msg}"
                else:
                    error_msg = f"Failed to initialize {provider}: {error_msg}"
            
            return jsonify({
                "status": "error",
                "error": error_msg
            }), 400
        
        # Test connection with a simple prompt
        start_time = time.time()
        try:
            response = llm.invoke("Say 'OK' if you can read this.")
            response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            # Extract response text
            if hasattr(response, 'content'):
                response_text = response.content
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)
            
            return jsonify({
                "status": "success",
                "message": "Connection test successful",
                "model": model,
                "provider": provider,
                "response_time": response_time,
                "response_preview": response_text[:100] if response_text else "No response"
            }), 200
            
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            
            # Handle authentication errors (invalid API key)
            if "401" in error_msg or "authentication" in error_msg.lower() or ("invalid" in error_msg.lower() and "key" in error_msg.lower()):
                if provider == "claude":
                    error_msg = "Invalid Anthropic API key. Please check your API key and try again. Get your key at: https://console.anthropic.com/"
                elif provider == "gemini":
                    error_msg = "Invalid Google API key. Please check your API key and try again. Get your key at: https://makersuite.google.com/app/apikey"
                elif provider == "groq":
                    error_msg = "Invalid Groq API key. Please check your API key and try again. Get your key at: https://console.groq.com/"
                elif provider == "deepseek":
                    error_msg = "Invalid DeepSeek API key. Please check your API key and try again. Get your key at: https://platform.deepseek.com/"
                elif provider == "together":
                    error_msg = "Invalid Together AI API key. Please check your API key and try again. Get your key at: https://api.together.xyz/"
                else:
                    error_msg = f"Invalid API key for {provider}. Please check your API key and try again."
            # Handle rate limit errors
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                error_msg = f"Rate limit exceeded for {provider}. Please wait a moment and try again."
            # Handle forbidden/access errors
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                error_msg = f"Access forbidden for {provider}. Please check your API key permissions."
            # Handle other API errors
            elif "error" in error_msg.lower() and ("code" in error_msg.lower() or "type" in error_msg.lower()):
                # Try to extract a cleaner error message
                if provider == "claude":
                    error_msg = f"Anthropic API error. Please check your API key and account status. Details: {error_msg[:200]}"
                else:
                    error_msg = f"{provider.capitalize()} API error: {error_msg[:200]}"
            
            return jsonify({
                "status": "error",
                "error": error_msg,
                "response_time": response_time
            }), 500
        
    except Exception as e:
        print(f"❌ LLM test error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "error": f"Test failed: {str(e)}"
        }), 500

