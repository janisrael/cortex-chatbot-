"""User chatbot configuration service"""
import os
import json
from utils.prompts import get_default_prompt_with_name


def get_user_chatbot_config_path(user_id):
    """Get path to user's chatbot config file"""
    config_dir = f"./config/user_{user_id}"
    os.makedirs(config_dir, exist_ok=True)
    return f"{config_dir}/chatbot_config.json"


def load_user_chatbot_config(user_id):
    """Load user's chatbot configuration"""
    config_path = get_user_chatbot_config_path(user_id)
    default_config = {
        'bot_name': 'Cortex',
        'prompt': None,  # Will use default prompt with bot_name
        'prompt_preset_id': None,  # ID of the preset user is using (user-specific)
        'api_key': None,
        'api_key_hash': None,
        # Advanced chatbot settings
        'temperature': 0.3,  # 0.0-2.0, controls creativity/randomness
        'max_tokens': 2000,  # Maximum response length
        'top_p': 1.0,  # 0.0-1.0, nucleus sampling
        'frequency_penalty': 0.0,  # -2.0 to 2.0, reduces repetition
        'presence_penalty': 0.0,  # -2.0 to 2.0, encourages new topics
        'response_style': 'balanced',  # concise, balanced, detailed, creative
        'system_instructions': '',  # Additional context for the LLM
        # LLM Provider settings
        'llm_provider': 'openai',  # openai, claude, gemini, deepseek, groq, together
        'llm_model': 'gpt-4o-mini',  # Provider-specific model
        'llm_api_key': None  # User's API key for selected provider (optional, uses system key if not provided)
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

