"""API key generation and validation utilities"""
import os
import json
import secrets
import hashlib


def generate_user_api_key(user_id):
    """Generate a unique API key for a user"""
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    # Create a hash for storage
    key_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, key_hash


def get_user_api_key(user_id):
    """Get or create API key for user"""
    # Import here to avoid circular dependency
    from services.config_service import load_user_chatbot_config, save_user_chatbot_config_file
    
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
    """
    Validate API key and return user_id if valid
    
    Priority order:
    1. Database admin API keys (AdminAPIKey) - returns first admin user ID
    2. .env DEFAULT_API_KEY - returns first admin user ID
    3. .env FALLBACK_API_KEY - returns first admin user ID
    4. User config files (existing user API keys) - returns specific user_id
    
    Returns:
        user_id (int) if valid, None otherwise
    """
    if not api_key:
        return None
    
    # Helper function to get first admin user ID
    def get_first_admin_user_id():
        try:
            from models.user import User
            conn = User._get_db_connection()
            is_sqlite = User._is_sqlite(conn)
            try:
                if is_sqlite:
                    cursor = conn.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
                    result = cursor.fetchone()
                else:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
                    result = cursor.fetchone()
                    cursor.close()
                
                if result:
                    return result[0] if is_sqlite else result[0]
            finally:
                conn.close()
        except Exception as e:
            print(f"Error getting admin user: {e}")
        return None
    
    # 1. Check database admin API keys first
    try:
        from models.api_key import AdminAPIKey
        admin_key = AdminAPIKey.validate_key(api_key)
        if admin_key and admin_key.get('is_active'):
            admin_user_id = get_first_admin_user_id()
            if admin_user_id:
                return admin_user_id
    except Exception as e:
        print(f"Error checking admin API keys: {e}")
    
    # 2. Check .env DEFAULT_API_KEY
    default_key = os.getenv("DEFAULT_API_KEY", "")
    if default_key and default_key == api_key:
        admin_user_id = get_first_admin_user_id()
        if admin_user_id:
            return admin_user_id
    
    # 3. Check .env FALLBACK_API_KEY
    fallback_key = os.getenv("FALLBACK_API_KEY", "")
    if fallback_key and fallback_key == api_key:
        admin_user_id = get_first_admin_user_id()
        if admin_user_id:
            return admin_user_id
    
    # 4. Search through all user configs to find matching API key (existing behavior)
    config_dir = "./config"
    if not os.path.exists(config_dir):
        return None
    
    for user_dir in os.listdir(config_dir):
        if user_dir.startswith('user_'):
            try:
                user_id = int(user_dir.replace('user_', ''))
                # Import here to avoid circular dependency
                from services.config_service import load_user_chatbot_config
                config = load_user_chatbot_config(user_id)
                stored_key = config.get('api_key')
                
                # Direct comparison (since we store the plain token)
                if stored_key == api_key:
                    return user_id
            except (ValueError, Exception):
                continue
    
    return None
