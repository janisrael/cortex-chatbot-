"""
Conversation Service - manages conversation lifecycle and history
"""
from models.conversation import Conversation
from models.message import Message
import uuid


def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())


def create_conversation(user_id, session_id=None, title=None):
    """Create a new conversation
    
    Args:
        user_id: User ID
        session_id: Optional session ID (generated if not provided)
        title: Optional conversation title (auto-generated if not provided)
    
    Returns:
        Conversation object or None
    """
    if not session_id:
        session_id = generate_session_id()
    
    conversation = Conversation.create(user_id, session_id, title)
    return conversation


def get_or_create_conversation(user_id, session_id=None, conversation_id=None):
    """Get existing conversation or create a new one
    
    Args:
        user_id: User ID
        session_id: Optional session ID
        conversation_id: Optional conversation ID (takes precedence)
    
    Returns:
        tuple: (Conversation object, is_new: bool)
    """
    # If conversation_id is provided, get that conversation
    if conversation_id:
        conversation = Conversation.get_by_id(conversation_id)
        if conversation and conversation.user_id == user_id:
            return conversation, False
        # If conversation doesn't exist or belongs to different user, create new
        return create_conversation(user_id, session_id), True
    
    # If session_id is provided, try to get active conversation
    if session_id:
        conversation = Conversation.get_by_session(user_id, session_id, active_only=True)
        if conversation:
            return conversation, False
    
    # Create new conversation
    if not session_id:
        session_id = generate_session_id()
    
    return create_conversation(user_id, session_id), True


def add_message(conversation_id, role, content, metadata=None):
    """Add a message to a conversation
    
    Args:
        conversation_id: Conversation ID
        role: 'user' or 'assistant'
        content: Message content
        metadata: Optional metadata (dict)
    
    Returns:
        Message object or None
    """
    message = Message.create(conversation_id, role, content, metadata)
    
    # Update conversation message count and timestamp
    if message:
        conversation = Conversation.get_by_id(conversation_id)
        if conversation:
            conversation.increment_message_count()
            
            # Auto-generate title from first user message if not set
            if not conversation.title and role == 'user':
                # Use first 50 chars of message as title
                title = content[:50].strip()
                if len(content) > 50:
                    title += "..."
                conversation.update_title(title)
    
    return message


def get_conversation_history(conversation_id, limit=20):
    """Get conversation history (recent messages)
    
    Args:
        conversation_id: Conversation ID
        limit: Maximum number of messages to return
    
    Returns:
        list: List of Message objects (chronological order)
    """
    return Message.get_recent_messages(conversation_id, limit)


def build_conversation_context(conversation_id, max_messages=10):
    """Build conversation context string for LLM prompt
    
    Args:
        conversation_id: Conversation ID
        max_messages: Maximum number of message pairs to include
    
    Returns:
        str: Formatted conversation context
    """
    import re
    
    def clean_html_tags(text):
        """Remove HTML tags from text and clean up formatting"""
        if not text:
            return ""
        # Replace <br> tags with newlines
        text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        # Remove other HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove markdown bold/italic markers (keep content)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove **bold**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove *italic*
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Clean up whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    messages = get_conversation_history(conversation_id, limit=max_messages * 2)
    
    if not messages:
        return ""
    
    # Build context with cleaner formatting
    context_parts = []
    turn_num = 1
    
    i = 0
    while i < len(messages):
        # Group user and assistant messages as conversation turns
        if messages[i].role == "user":
            user_msg = clean_html_tags(messages[i].content)
            context_parts.append(f"Turn {turn_num}:")
            context_parts.append(f"User: {user_msg}")
            
            # Look for corresponding assistant response
            if i + 1 < len(messages) and messages[i + 1].role == "assistant":
                assistant_msg = clean_html_tags(messages[i + 1].content)
                context_parts.append(f"Assistant: {assistant_msg}")
                i += 2
            else:
                i += 1
            turn_num += 1
            context_parts.append("")  # Empty line between turns
        else:
            # Skip orphaned assistant messages
            i += 1
    
    return "\n".join(context_parts).strip()


def end_conversation(conversation_id):
    """Mark conversation as inactive
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        bool: Success status
    """
    conversation = Conversation.get_by_id(conversation_id)
    if conversation:
        return conversation.end()
    return False


def get_user_conversations(user_id, limit=10, active_only=False):
    """Get user's conversations
    
    Args:
        user_id: User ID
        limit: Maximum number of conversations to return
        active_only: Only return active conversations
    
    Returns:
        list: List of Conversation objects
    """
    return Conversation.get_user_conversations(user_id, limit, active_only)


def delete_conversation(conversation_id, user_id):
    """Delete a conversation (with permission check)
    
    Args:
        conversation_id: Conversation ID
        user_id: User ID (for permission check)
    
    Returns:
        bool: Success status
    """
    conversation = Conversation.get_by_id(conversation_id)
    if conversation and conversation.user_id == user_id:
        return conversation.delete()
    return False


def get_conversation_with_messages(conversation_id, user_id, message_limit=20):
    """Get conversation with its messages (for API responses)
    
    Args:
        conversation_id: Conversation ID
        user_id: User ID (for permission check)
        message_limit: Maximum number of messages to include
    
    Returns:
        dict: Conversation data with messages, or None
    """
    conversation = Conversation.get_by_id(conversation_id)
    if not conversation or conversation.user_id != user_id:
        return None
    
    messages = get_conversation_history(conversation_id, limit=message_limit)
    
    return {
        'conversation': conversation.to_dict(),
        'messages': [msg.to_dict() for msg in messages]
    }

