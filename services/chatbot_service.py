"""Chatbot service - handles chat responses and RAG"""
import re

from services.knowledge_service import get_user_vectorstore
from services.config_service import load_user_chatbot_config
from services.llm_service import LLMProvider
from services.conversation_service import build_conversation_context
from services.user_info_service import get_user_name_for_chat
from utils.prompts import get_default_prompt_with_name


def _replace_bot_name(prompt_text: str, bot_name: str) -> str:
    """Replace any hardcoded 'Cortex' tokens with the current bot name."""
    if not prompt_text or not bot_name:
        return prompt_text

    # Replace possessive first to avoid partial overlaps
    prompt_text = re.sub(r"\bCortex's\b", f"{bot_name}'s", prompt_text)
    # Replace any remaining standalone occurrences (case-sensitive, boundary-aware)
    prompt_text = re.sub(r"\bCortex\b", bot_name, prompt_text)
    # Replace placeholder tokens
    prompt_text = prompt_text.replace('{bot_name}', bot_name)
    # Fallback: replace any remaining case-insensitive occurrences (safety net)
    if bot_name.lower() != 'cortex':
        prompt_text = re.sub(r"cortex", bot_name, prompt_text, flags=re.IGNORECASE)
    return prompt_text


def get_chatbot_response(user_id, message, system_llm=None, name="User", conversation_id=None):
    """Get chatbot response using user's knowledge base and config
    
    Args:
        user_id: User ID for isolation
        message: User's message
        system_llm: System-level LLM (fallback if user config fails)
        name: User's name (default: "User")
        conversation_id: Optional conversation ID for maintaining context
    
    Returns:
        tuple: (response_text, error_message)
    """
    if conversation_id:
        name = get_user_name_for_chat(conversation_id, default=name)
    
    # Load user's chatbot config
    user_config = load_user_chatbot_config(user_id)
    bot_name = user_config.get('bot_name', 'Cortex')
    user_prompt_template = user_config.get('prompt')
    
    # Log prompt status for debugging
    print(f" User {user_id} prompt status:")
    print(f"   - Has prompt: {user_prompt_template is not None}")
    print(f"   - Prompt length: {len(user_prompt_template) if user_prompt_template else 0}")
    print(f"   - Prompt preview: {user_prompt_template[:100] if user_prompt_template else 'None'}...")
    
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
        print(f" Using user LLM: {llm_provider} / {llm_model}")
    except Exception as e:
        print(f" Failed to create user LLM ({llm_provider}/{llm_model}), using system LLM: {e}")
        llm = system_llm if system_llm else LLMProvider.get_default_llm()
    
    # Try to get user-specific vectorstore (will create if doesn't exist)
    user_vectorstore = None
    user_retriever = None
    
    try:
        user_vectorstore = get_user_vectorstore(user_id)
        if user_vectorstore:
            # Try to create retriever - if it fails, we'll use direct LLM
            # Increased k to 30 for better retrieval, especially for FILE documents
            # Priority order handled in retrieval
            try:
                user_retriever = user_vectorstore.as_retriever(search_kwargs={"k": 30})
            except Exception as e:
                print(f" Cannot create retriever, using direct LLM: {e}")
                user_retriever = None
    except Exception as e:
        print(f" Vectorstore not available, using direct LLM: {e}")
        user_vectorstore = None
        user_retriever = None
    
    # Use user's custom prompt or default
    if user_prompt_template:
        prompt_template_text = user_prompt_template
        print(f" Using user's custom prompt (length: {len(prompt_template_text)})")
    else:
        prompt_template_text = get_default_prompt_with_name(bot_name)
        print(f" No custom prompt found, using default prompt")
    
    # Normalize bot name usage in the prompt (handles placeholders and hardcoded names)
    prompt_template_text = _replace_bot_name(prompt_template_text, bot_name)
    
    # Get relevant documents from user's knowledge base (if retriever is available)
    # Priority order: FAQ > Crawl > File Upload
    context = ""
    if user_retriever:
        try:
            # Use invoke() instead of get_relevant_documents() for LangChain 0.3.x
            if hasattr(user_retriever, 'invoke'):
                docs = user_retriever.invoke(message)
            else:
                # Fallback for older LangChain versions
                docs = user_retriever.get_relevant_documents(message)
            
            # Apply priority ordering: FAQ > Crawl > File Upload
            if docs:
                # Separate by source type
                # Note: Accept both 'crawl' and 'web_crawl' for backward compatibility
                faq_docs = [d for d in docs if d.metadata.get('source_type') == 'faq']
                crawl_docs = [d for d in docs if d.metadata.get('source_type') in ['crawl', 'web_crawl']]
                file_docs = [d for d in docs if d.metadata.get('source_type') == 'file_upload']
                other_docs = [d for d in docs if d.metadata.get('source_type') not in ['faq', 'crawl', 'web_crawl', 'file_upload']]
                
                # Phase 2: Improved prioritization for FILE documents
                # Reorder: FAQ first, then crawl, then file, then others
                prioritized_docs = faq_docs + crawl_docs + file_docs + other_docs
                
                # Phase 2: Ensure FILE documents are included if they exist
                # If we have FILE documents but they're not in top 8, include at least one
                if file_docs and len(prioritized_docs) > 8:
                    top_docs = prioritized_docs[:7]
                    # Check if any FILE docs are already in top 7
                    has_file = any(d.metadata.get('source_type') == 'file_upload' for d in top_docs)
                    if not has_file and file_docs:
                        # Replace last doc with first FILE doc to ensure FILE content is included
                        top_docs = top_docs[:6] + [file_docs[0]]
                    prioritized_docs = top_docs
                else:
                    # Limit to top 8 for context (keep some for diversity)
                    prioritized_docs = prioritized_docs[:8]
                
                context = "\n\n".join([doc.page_content for doc in prioritized_docs]) if prioritized_docs else ""
                
                # Log retrieval for debugging
                print(f" Retrieved {len(docs)} documents, prioritized to {len(prioritized_docs)}")
                print(f" Breakdown: FAQ={len(faq_docs)}, Crawl={len(crawl_docs)}, File={len(file_docs)}, Other={len(other_docs)}")
                print(f" Top sources: {[doc.metadata.get('source_file', 'unknown')[:30] for doc in prioritized_docs[:3]]}")
            else:
                print(f"ℹ No relevant documents found in knowledge base for: {message[:50]}")
        except Exception as e:
            print(f" Error retrieving documents: {e}")
            import traceback
            traceback.print_exc()
            context = ""
    else:
        print(f"ℹ No retriever available - using direct LLM response")
    
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
            
            # Build conversation history context if conversation_id is provided
            conversation_context = ""
            if conversation_id:
                conversation_context = build_conversation_context(conversation_id, max_messages=10)
                if conversation_context:
                    print(f" Using conversation history ({len(conversation_context)} chars)")
            
            # Build the full prompt with knowledge base context and conversation history
            if context:
                # Use RAG with context from knowledge base
                base_prompt = prompt_template_text.format(context=context, question=message)
                print(f" Using RAG with {len(context)} characters of context")
            else:
                # No context found - use LLM directly with user's bot name
                base_prompt = f"User ({name}) asks: {message}"
                print(f"ℹ No knowledge base context - using direct LLM response")
            
            # Combine system prompt, conversation history, and base prompt
            full_prompt = system_prompt
            
            # Add conversation history if available with explicit instructions
            if conversation_context:
                full_prompt += f"\n\n--- CONVERSATION CONTEXT ---"
                full_prompt += f"\nYou are having an ongoing conversation with the user. Below is the previous conversation history."
                full_prompt += f"\nIMPORTANT: Use this context to understand references like 'their', 'it', 'that', 'they', etc."
                full_prompt += f"\nIf the user says 'their phone number' and the previous conversation was about Person 1, they are referring to Person 1's phone number."
                full_prompt += f"\n\nPrevious Conversation History:\n{conversation_context}"
                full_prompt += f"\n--- END CONVERSATION CONTEXT ---\n"
            
            # Add user name instruction if name is provided (not default "User")
            if name and name != "User":
                full_prompt += f"\n\nIMPORTANT: The user's name is {name}. When appropriate, address them by name at the beginning of your response (e.g., '{name}, I can assist you...')."
            
            # Add knowledge base context and current question
            full_prompt += f"\n{base_prompt}"
            
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
            reply = str(reply).strip()
            
            # Clean up excessive newlines (more than 2 consecutive)
            import re
            reply = re.sub(r'\n{3,}', '\n\n', reply)
            
            # Convert newlines to <br> for HTML display
            reply = reply.replace("\n", "<br>")
            
            return reply, None
        except Exception as e:
            print(f"LLM error: {e}")
            import traceback
            traceback.print_exc()
            return f"I'm here to help! Could you please rephrase your question?<br><br>Error: {str(e)}", None
    else:
        # Mock LLM fallback
        return f"Mock response for: {message}<br><br>What else would you like to know?", None

