"""Conversation management endpoints"""
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from services.conversation_service import (
    get_user_conversations,
    get_conversation_with_messages,
    delete_conversation,
    end_conversation,
    create_conversation
)
from services.user_info_service import store_user_info
from utils.api_key import validate_api_key

conversations_bp = Blueprint('conversations', __name__)


@conversations_bp.route("/conversations/test", methods=["GET"])
def test_route():
    """Test route to verify blueprint is registered"""
    return jsonify({"status": "ok", "message": "Conversations blueprint is working"})


def get_user_id_from_request():
    """Get user_id from either login or API key"""
    if current_user.is_authenticated:
        return current_user.id
    
    # For GET requests, request.json might be None, so check headers first
    api_key = request.headers.get("X-API-Key")
    if not api_key and request.is_json and request.json:
        api_key = request.json.get("api_key")
    
    if api_key:
        user_id = validate_api_key(api_key)
        return user_id
    
    return None


@conversations_bp.route("/conversations", methods=["GET"])
def list_conversations():
    """List user's conversations"""
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        # Get query parameters
        limit = request.args.get("limit", 10, type=int)
        active_only = request.args.get("active_only", "false").lower() == "true"
        
        conversations = get_user_conversations(user_id, limit=limit, active_only=active_only)
        
        return jsonify({
            "conversations": [conv.to_dict() for conv in conversations]
        })
    except Exception as e:
        print(f"Error listing conversations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@conversations_bp.route("/conversations", methods=["POST"])
def create_new_conversation():
    """Create a new conversation"""
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.json or {}
        session_id = data.get("session_id")
        title = data.get("title")
        
        conversation = create_conversation(user_id, session_id, title)
        
        if not conversation:
            return jsonify({"error": "Failed to create conversation"}), 500
        
        return jsonify({
            "conversation": conversation.to_dict()
        }), 201
    except Exception as e:
        print(f"Error creating conversation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@conversations_bp.route("/conversations/<int:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    """Get conversation with messages"""
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        message_limit = request.args.get("message_limit", 20, type=int)
        
        result = get_conversation_with_messages(conversation_id, user_id, message_limit)
        
        if not result:
            return jsonify({"error": "Conversation not found"}), 404
        
        return jsonify(result)
    except Exception as e:
        print(f"Error getting conversation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@conversations_bp.route("/conversations/<int:conversation_id>", methods=["DELETE"])
def delete_conversation_endpoint(conversation_id):
    """Delete a conversation"""
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        success = delete_conversation(conversation_id, user_id)
        
        if not success:
            return jsonify({"error": "Conversation not found or permission denied"}), 404
        
        return jsonify({
            "status": "success",
            "message": "Conversation deleted"
        })
    except Exception as e:
        print(f"Error deleting conversation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@conversations_bp.route("/conversations/<int:conversation_id>/end", methods=["POST"])
def end_conversation_endpoint(conversation_id):
    """End (deactivate) a conversation"""
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        # Verify conversation belongs to user
        result = get_conversation_with_messages(conversation_id, user_id, message_limit=1)
        if not result:
            return jsonify({"error": "Conversation not found"}), 404
        
        success = end_conversation(conversation_id)
        
        if not success:
            return jsonify({"error": "Failed to end conversation"}), 500
        
        return jsonify({
            "status": "success",
            "message": "Conversation ended"
        })
    except Exception as e:
        print(f"Error ending conversation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@conversations_bp.route("/conversations/<int:conversation_id>/user-info", methods=["POST", "OPTIONS"])
def store_user_info_endpoint(conversation_id):
    """Store user information for a conversation"""
    print(f"🔍 store_user_info_endpoint called: conversation_id={conversation_id}, method={request.method}")
    
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response
    
    try:
        user_id = get_user_id_from_request()
        print(f"🔍 User ID from request: {user_id}")
        if not user_id:
            print("❌ No user_id found")
            return jsonify({"error": "Authentication required"}), 401
        
        # Verify conversation belongs to user
        result = get_conversation_with_messages(conversation_id, user_id, message_limit=1)
        print(f"🔍 Conversation lookup result: {result is not None}")
        if not result:
            print(f"❌ Conversation {conversation_id} not found for user {user_id}")
            return jsonify({"error": "Conversation not found or access denied"}), 404
        
        data = request.json or {}
        name = (data.get("name") or "").strip()
        email_str = data.get("email")
        phone_str = data.get("phone")
        email = email_str.strip() if email_str and isinstance(email_str, str) else None
        phone = phone_str.strip() if phone_str and isinstance(phone_str, str) else None
        
        if not name:
            return jsonify({"error": "Name is required"}), 400
        
        # Capitalize name: first letter uppercase, rest lowercase
        if len(name) > 0:
            name = name[0].upper() + name[1:].lower()
        
        success = store_user_info(conversation_id, name, email, phone)
        
        if not success:
            return jsonify({"error": "Failed to store user info"}), 500
        
        return jsonify({
            "status": "success",
            "message": "User info stored"
        })
    except Exception as e:
        print(f"Error storing user info: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

