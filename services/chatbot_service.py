"""Chatbot service - handles chat responses and RAG"""
from services.knowledge_service import get_user_vectorstore
from services.config_service import load_user_chatbot_config
from services.llm_service import LLMProvider
from utils.prompts import get_default_prompt_with_name


def get_chatbot_response(user_id, message, system_llm=None, name="User"):
    """Get chatbot response using user's knowledge base and config
    
    Args:
        user_id: User ID for isolation
        message: User's message
        system_llm: System-level LLM (fallback if user config fails)
        name: User's name (default: "User")
    
    Returns:
        tuple: (response_text, error_message)
    """
    # Load user's chatbot config
    user_config = load_user_chatbot_config(user_id)
    bot_name = user_config.get('bot_name', 'Cortex')
    user_prompt_template = user_config.get('prompt')
    
    # Get user-specific LLM settings
    temperature = float(user_config.get('temperature', 0.3))
    max_tokens = int(user_config.get('max_tokens', 2000))
    top_p = float(user_config.get('top_p', 1.0))
    frequency_penalty = float(user_config.get('frequency_penalty', 0.0))
    presence_penalty = float(user_config.get('presence_penalty', 0.0))
    system_instructions = user_config.get('system_instructions', '')
    
    # Get user's selected provider and model
    llm_provider = user_config.get('llm_provider', 'openai')
    llm_model = user_config.get('llm_model', 'gpt-4o-mini')
    llm_api_key = user_config.get('llm_api_key')  # User's API key (optional)
    
    # Create user-specific LLM with their provider and settings
    try:
        llm = LLMProvider.get_llm(
            provider=llm_provider,
            model=llm_model,
            api_key=llm_api_key,  # Uses system default if None
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        print(f"✅ Using user LLM: {llm_provider} / {llm_model}")
    except Exception as e:
        print(f"⚠️ Failed to create user LLM ({llm_provider}/{llm_model}), using system LLM: {e}")
        llm = system_llm if system_llm else LLMProvider.get_default_llm()
    
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
            # Build system instructions
            system_prompt = f"You are {bot_name}, an intelligent AI assistant."
            if system_instructions:
                system_prompt += f"\n\nAdditional Instructions: {system_instructions}"
            
            # Apply response style
            response_style = user_config.get('response_style', 'balanced')
            style_instructions = {
                'concise': "Be brief and to the point. Keep responses under 100 words.",
                'balanced': "Provide balanced, informative responses. Be helpful and clear.",
                'detailed': "Provide comprehensive, detailed responses. Include examples when helpful.",
                'creative': "Be creative and engaging. Use storytelling when appropriate."
            }
            if response_style in style_instructions:
                system_prompt += f"\n\nResponse Style: {style_instructions[response_style]}"
            
            if context:
                # Use RAG with context from knowledge base
                full_prompt = prompt_template_text.format(context=context, question=message)
                print(f"✅ Using RAG with {len(context)} characters of context")
            else:
                # No context found - use LLM directly with user's bot name
                full_prompt = f"{system_prompt}\n\nUser ({name}) asks: {message}"
                print(f"ℹ️ No knowledge base context - using direct LLM response")
            
            # Add system prompt at the beginning
            full_prompt = f"{system_prompt}\n\n{full_prompt}"
            
            # Add instructions for including contact information and links
            full_prompt += f"\n\nCRITICAL INSTRUCTIONS:"
            full_prompt += f"\n- Respond in plain text ONLY. NO HTML, NO code blocks."
            full_prompt += f"\n- Be helpful and friendly."
            full_prompt += f"\n- When the knowledge base contains contact information (phone numbers, email addresses, physical addresses, website URLs, booking links), ALWAYS include them in your response."
            full_prompt += f"\n- If the user asks about reservations, bookings, or how to contact, provide the exact contact information from the knowledge base."
            full_prompt += f"\n- Include website links, phone numbers, and email addresses when available in the context."
            full_prompt += f"\n- Format contact information clearly (e.g., 'Phone: +1-555-1234', 'Email: info@example.com', 'Website: https://example.com')."
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

