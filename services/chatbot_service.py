"""Chatbot service - handles chat responses and RAG"""
from services.knowledge_service import get_user_vectorstore
from services.config_service import load_user_chatbot_config
from utils.prompts import get_default_prompt_with_name


def get_chatbot_response(user_id, message, llm, name="User"):
    """Get chatbot response using user's knowledge base and config"""
    # Try to get user-specific vectorstore (will create if doesn't exist)
    user_vectorstore = None
    user_retriever = None
    
    try:
        user_vectorstore = get_user_vectorstore(user_id)
        if user_vectorstore:
            # Try to create retriever - if it fails, we'll use direct LLM
            try:
                user_retriever = user_vectorstore.as_retriever(search_kwargs={"k": 5})
            except Exception as e:
                print(f"⚠️ Cannot create retriever, using direct LLM: {e}")
                user_retriever = None
    except Exception as e:
        print(f"⚠️ Vectorstore not available, using direct LLM: {e}")
        user_vectorstore = None
        user_retriever = None
    
    # Load user's chatbot config
    user_config = load_user_chatbot_config(user_id)
    bot_name = user_config.get('bot_name', 'Cortex')
    user_prompt_template = user_config.get('prompt')
    
    # Use user's custom prompt or default
    if user_prompt_template:
        prompt_template_text = user_prompt_template
    else:
        prompt_template_text = get_default_prompt_with_name(bot_name)
    
    # Replace {bot_name} placeholder with actual bot name (at runtime)
    prompt_template_text = prompt_template_text.replace('{bot_name}', bot_name)
    
    # Get relevant documents from user's knowledge base (if retriever is available)
    context = ""
    if user_retriever:
        try:
            docs = user_retriever.get_relevant_documents(message)
            context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
            
            # Log retrieval for debugging
            if docs:
                print(f"📚 Retrieved {len(docs)} relevant documents from knowledge base")
                print(f"📄 Sources: {[doc.metadata.get('source_file', 'unknown') for doc in docs[:3]]}")
            else:
                print(f"ℹ️ No relevant documents found in knowledge base for: {message[:50]}")
        except Exception as e:
            print(f"⚠️ Error retrieving documents: {e}")
            context = ""
    else:
        print(f"ℹ️ No retriever available - using direct LLM response")
    
    # Generate response
    if hasattr(llm, 'invoke'):
        try:
            if context:
                # Use RAG with context from knowledge base
                full_prompt = prompt_template_text.format(context=context, question=message)
                print(f"✅ Using RAG with {len(context)} characters of context")
            else:
                # No context found - use LLM directly with user's bot name
                full_prompt = f"You are {bot_name}, an intelligent AI assistant. Help {name} with: {message}"
                print(f"ℹ️ No knowledge base context - using direct LLM response")
            
            full_prompt += f"\n\nCRITICAL: Respond in plain text ONLY. NO HTML, NO code blocks. Be helpful and friendly."
            reply = llm.invoke(full_prompt)
            
            # Ensure reply is a string
            if hasattr(reply, 'content'):
                reply = reply.content
            reply = str(reply).strip().replace("\n", "<br>")
            
            return reply, None
        except Exception as e:
            print(f"LLM error: {e}")
            import traceback
            traceback.print_exc()
            return f"I'm here to help! Could you please rephrase your question?<br><br>Error: {str(e)}", None
    else:
        # Mock LLM fallback
        return f"Mock response for: {message}<br><br>What else would you like to know?", None

