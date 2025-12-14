"""Chat endpoint blueprint"""
from flask import Blueprint, request, jsonify
from flask_login import current_user
from services.chatbot_service import get_chatbot_response
from services.conversation_service import (
    get_or_create_conversation,
    add_message,
    generate_session_id
)
from utils.api_key import validate_api_key

chat_bp = Blueprint('chat', __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint - accepts login OR API key, uses user-specific RAG"""
    try:
        # Get llm from Flask g or app config
        from flask import g, current_app
        llm = getattr(g, 'llm', None) or current_app.config.get('LLM')
        
        data = request.json
        user_input = data.get("message")
        api_key = data.get("api_key") or request.headers.get("X-API-Key")
        conversation_id = data.get("conversation_id")
        session_id = data.get("session_id")
        
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

        # Get or create conversation
        conversation, is_new = get_or_create_conversation(
            user_id=user_id,
            session_id=session_id,
            conversation_id=conversation_id
        )
        
        if not conversation:
            return jsonify({"error": "Failed to create or retrieve conversation"}), 500
        
        # Save user message
        user_message = add_message(
            conversation_id=conversation.id,
            role="user",
            content=user_input
        )
        
        if not user_message:
            print(f"⚠️ Warning: Failed to save user message for conversation {conversation.id}")

        # Get chatbot response with conversation context
        reply, error = get_chatbot_response(
            user_id=user_id,
            message=user_input,
            system_llm=llm,
            name=name,
            conversation_id=conversation.id
        )
        
        if error:
            return jsonify({"error": error}), 500
        
        # Save assistant message
        assistant_message = add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=reply
        )
        
        if not assistant_message:
            print(f"⚠️ Warning: Failed to save assistant message for conversation {conversation.id}")
        
        # Return response with conversation info
        return jsonify({
            "response": reply,
            "conversation_id": conversation.id,
            "session_id": conversation.session_id,
            "is_new_conversation": is_new
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Chat error: {e}")
        print(f"Full traceback:\n{error_details}")
        return jsonify({"response": f"Sorry, I ran into an error: {str(e)}"}), 500


@chat_bp.route("/refresh", methods=["POST"])
def refresh_chat():
    """Refresh chat conversation - clears session but preserves files and knowledge"""
    try:
        from flask import session
        session.clear()
        return jsonify({
            "status": "success",
            "message": "Chat conversation refreshed! (Files and knowledge preserved)"
        })
    except Exception as e:
        print(f"Refresh error: {e}")
        return jsonify({"status": "error", "message": "Failed to refresh chat session"}), 500

