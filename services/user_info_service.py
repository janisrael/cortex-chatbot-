"""
User Info Service - Modular user information collection
Completely separate from conversation flow
"""
from models.conversation import Conversation
from datetime import datetime
import json


def store_user_info(conversation_id, name, email=None, phone=None):
    """Store user info in conversation metadata
    
    Args:
        conversation_id: Conversation ID
        name: User name (required)
        email: User email (optional)
        phone: User phone (optional)
    
    Returns:
        bool: Success status
    """
    if not name or not name.strip():
        return False
    
    # Capitalize name: first letter uppercase, rest lowercase
    name = name.strip()
    if len(name) > 0:
        name = name[0].upper() + name[1:].lower()
    
    conversation = Conversation.get_by_id(conversation_id)
    if not conversation:
        return False
    
    metadata = conversation.metadata or {}
    metadata['user_info'] = {
        'name': name,
        'email': email.strip() if email and isinstance(email, str) else None,
        'phone': phone.strip() if phone and isinstance(phone, str) else None,
        'collected_at': datetime.now().isoformat()
    }
    
    return conversation.update_metadata(metadata)


def get_user_info(conversation_id):
    """Get user info from conversation metadata
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        dict: User info {name, email, phone} or None
    """
    conversation = Conversation.get_by_id(conversation_id)
    if not conversation or not conversation.metadata:
        return None
    
    user_info = conversation.metadata.get('user_info')
    return user_info if user_info else None


def has_user_info(conversation_id):
    """Check if conversation has user info
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        bool: True if user info exists
    """
    user_info = get_user_info(conversation_id)
    return user_info is not None and user_info.get('name') is not None


def get_user_name_for_chat(conversation_id, default="User"):
    """Get user name for chatbot (with fallback)
    
    This is the ONLY function imported by chatbot_service
    
    Args:
        conversation_id: Conversation ID
        default: Default name if not found
    
    Returns:
        str: User name or default
    """
    user_info = get_user_info(conversation_id)
    if user_info and user_info.get('name'):
        return user_info['name']
    return default

