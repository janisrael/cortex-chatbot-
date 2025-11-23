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

