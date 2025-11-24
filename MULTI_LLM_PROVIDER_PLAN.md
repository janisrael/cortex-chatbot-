# Multi-LLM Provider Support Plan

## Overview
Implement support for multiple external LLM providers with easy switching, removing local LLM (Ollama) support entirely.

## Supported Providers

### 1. **OpenAI** (Default - Currently Using)
- **Status:** ✅ Already implemented
- **Models:** gpt-4o-mini, gpt-4o, gpt-4-turbo, gpt-3.5-turbo
- **Library:** `langchain-openai`
- **API Key:** `OPENAI_API_KEY`
- **Cost:** Pay-per-use
- **Best for:** General purpose, reliable, fast

### 2. **Anthropic Claude**
- **Status:** ⚠️ To implement
- **Models:** claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-haiku-20240307
- **Library:** `langchain-anthropic`
- **API Key:** `ANTHROPIC_API_KEY`
- **Cost:** Pay-per-use
- **Best for:** Long context, reasoning, analysis
- **Integration:** Very similar to OpenAI, easy to add

### 3. **Google Gemini**
- **Status:** ⚠️ To implement
- **Models:** gemini-pro, gemini-pro-vision, gemini-1.5-pro
- **Library:** `langchain-google-genai`
- **API Key:** `GOOGLE_API_KEY`
- **Cost:** Free tier available, then pay-per-use
- **Best for:** Multimodal, free tier option
- **Integration:** LangChain has official support

### 4. **DeepSeek**
- **Status:** ⚠️ To implement
- **Models:** deepseek-chat, deepseek-coder
- **Library:** `langchain-openai` (OpenAI-compatible API)
- **API Key:** `DEEPSEEK_API_KEY`
- **Cost:** Very affordable, competitive pricing
- **Best for:** Cost-effective alternative, coding tasks
- **Integration:** Uses OpenAI-compatible API, minimal code changes

### 5. **Llama (via Groq)**
- **Status:** ⚠️ To implement
- **Models:** llama-3.1-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768
- **Library:** `langchain-groq`
- **API Key:** `GROQ_API_KEY`
- **Cost:** Very fast, free tier available
- **Best for:** Fast inference, free tier option
- **Integration:** LangChain has official support

### 6. **Llama (via Together AI)**
- **Status:** ⚠️ Alternative option
- **Models:** meta-llama/Llama-3-70b-chat-hf, meta-llama/Llama-3-8b-chat-hf
- **Library:** `langchain-together`
- **API Key:** `TOGETHER_API_KEY`
- **Cost:** Pay-per-use, competitive
- **Best for:** Open-source models, flexibility
- **Integration:** LangChain has official support

## Architecture Design

### Unified LLM Interface

```python
# services/llm_service.py
class LLMProvider:
    """Unified interface for all LLM providers"""
    
    @staticmethod
    def get_llm(provider: str, model: str, api_key: str, **kwargs):
        """
        Factory method to get LLM instance based on provider
        
        Args:
            provider: 'openai', 'claude', 'gemini', 'deepseek', 'groq', 'together'
            model: Model name (e.g., 'gpt-4o-mini', 'claude-3-5-sonnet')
            api_key: Provider-specific API key
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LangChain LLM instance
        """
        if provider == 'openai':
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=model, api_key=api_key, **kwargs)
        
        elif provider == 'claude':
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=model, api_key=api_key, **kwargs)
        
        elif provider == 'gemini':
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, **kwargs)
        
        elif provider == 'deepseek':
            # Uses OpenAI-compatible API
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )
        
        elif provider == 'groq':
            from langchain_groq import ChatGroq
            return ChatGroq(model=model, groq_api_key=api_key, **kwargs)
        
        elif provider == 'together':
            from langchain_together import Together
            return Together(model=model, together_api_key=api_key, **kwargs)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
```

### Database Schema

```sql
-- Add to existing user config or create new table
CREATE TABLE user_llm_config (
    user_id INT PRIMARY KEY,
    provider VARCHAR(50) DEFAULT 'openai',
    model VARCHAR(100) DEFAULT 'gpt-4o-mini',
    api_key_encrypted TEXT,
    temperature DECIMAL(3,2) DEFAULT 0.3,
    max_tokens INT DEFAULT 2000,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Configuration Structure

```python
# config/llm_providers.py
LLM_PROVIDERS = {
    'openai': {
        'name': 'OpenAI',
        'models': {
            'gpt-4o-mini': {'name': 'GPT-4o Mini', 'cost': 'low', 'speed': 'fast'},
            'gpt-4o': {'name': 'GPT-4o', 'cost': 'medium', 'speed': 'fast'},
            'gpt-4-turbo': {'name': 'GPT-4 Turbo', 'cost': 'high', 'speed': 'medium'},
            'gpt-3.5-turbo': {'name': 'GPT-3.5 Turbo', 'cost': 'very_low', 'speed': 'very_fast'}
        },
        'api_key_env': 'OPENAI_API_KEY',
        'default_model': 'gpt-4o-mini',
        'requires_api_key': True
    },
    'claude': {
        'name': 'Anthropic Claude',
        'models': {
            'claude-3-5-sonnet-20241022': {'name': 'Claude 3.5 Sonnet', 'cost': 'medium', 'speed': 'fast'},
            'claude-3-opus-20240229': {'name': 'Claude 3 Opus', 'cost': 'high', 'speed': 'medium'},
            'claude-3-haiku-20240307': {'name': 'Claude 3 Haiku', 'cost': 'low', 'speed': 'very_fast'}
        },
        'api_key_env': 'ANTHROPIC_API_KEY',
        'default_model': 'claude-3-5-sonnet-20241022',
        'requires_api_key': True
    },
    'gemini': {
        'name': 'Google Gemini',
        'models': {
            'gemini-pro': {'name': 'Gemini Pro', 'cost': 'free_tier', 'speed': 'fast'},
            'gemini-1.5-pro': {'name': 'Gemini 1.5 Pro', 'cost': 'low', 'speed': 'medium'},
            'gemini-pro-vision': {'name': 'Gemini Pro Vision', 'cost': 'low', 'speed': 'medium'}
        },
        'api_key_env': 'GOOGLE_API_KEY',
        'default_model': 'gemini-pro',
        'requires_api_key': True
    },
    'deepseek': {
        'name': 'DeepSeek',
        'models': {
            'deepseek-chat': {'name': 'DeepSeek Chat', 'cost': 'very_low', 'speed': 'fast'},
            'deepseek-coder': {'name': 'DeepSeek Coder', 'cost': 'very_low', 'speed': 'fast'}
        },
        'api_key_env': 'DEEPSEEK_API_KEY',
        'default_model': 'deepseek-chat',
        'requires_api_key': True
    },
    'groq': {
        'name': 'Groq (Llama)',
        'models': {
            'llama-3.1-70b-versatile': {'name': 'Llama 3.1 70B', 'cost': 'free_tier', 'speed': 'very_fast'},
            'llama-3.1-8b-instant': {'name': 'Llama 3.1 8B', 'cost': 'free_tier', 'speed': 'very_fast'},
            'mixtral-8x7b-32768': {'name': 'Mixtral 8x7B', 'cost': 'free_tier', 'speed': 'very_fast'}
        },
        'api_key_env': 'GROQ_API_KEY',
        'default_model': 'llama-3.1-70b-versatile',
        'requires_api_key': True
    },
    'together': {
        'name': 'Together AI (Llama)',
        'models': {
            'meta-llama/Llama-3-70b-chat-hf': {'name': 'Llama 3 70B', 'cost': 'low', 'speed': 'medium'},
            'meta-llama/Llama-3-8b-chat-hf': {'name': 'Llama 3 8B', 'cost': 'very_low', 'speed': 'fast'}
        },
        'api_key_env': 'TOGETHER_API_KEY',
        'default_model': 'meta-llama/Llama-3-70b-chat-hf',
        'requires_api_key': True
    }
}
```

## Implementation Steps

### Phase 1: Remove Ollama & Heavy Dependencies
1. Remove Ollama code from `app.py`
2. Remove Ollama UI from LLM Configuration tab
3. Remove Ollama API endpoints
4. Test with `requirements-prod.txt`
5. Verify everything still works

### Phase 2: Create Unified LLM Service
1. Create `services/llm_service.py` with factory pattern
2. Update `app.py` to use unified service
3. Update `services/chatbot_service.py` to use unified service
4. Test with OpenAI (should work as before)

### Phase 3: Add Provider Support
1. Install provider libraries:
   ```bash
   pip install langchain-anthropic langchain-google-genai langchain-groq langchain-together
   ```
2. Implement each provider in `llm_service.py`
3. Add provider configuration to `config/llm_providers.py`
4. Test each provider individually

### Phase 4: Update UI
1. Remove Ollama tab from LLM Configuration
2. Add provider dropdown (OpenAI, Claude, Gemini, DeepSeek, Groq, Together)
3. Add model dropdown (dynamically populated based on provider)
4. Add API key input (per provider, encrypted storage)
5. Add model info (cost, speed indicators)
6. Add "Test Connection" button

### Phase 5: Database Migration
1. Create `user_llm_config` table
2. Migrate existing OpenAI configs
3. Add encryption for API keys
4. Update API endpoints

### Phase 6: Testing & Documentation
1. Test all providers
2. Test switching between providers
3. Test API key validation
4. Document provider setup
5. Add cost comparison guide

## Code Changes Required

### Minimal Changes Needed

1. **app.py** - Replace Ollama with unified service
2. **services/llm_service.py** - NEW: Unified LLM factory
3. **services/chatbot_service.py** - Use unified service
4. **blueprints/api.py** - Update LLM config endpoints
5. **templates/components/dashboard_llm_tab.html** - Update UI
6. **static/v2/js/dashboard-llm.js** - Update JavaScript
7. **migrations.py** - Add user_llm_config table

### No Changes Needed

- `services/knowledge_service.py` - Already uses embeddings (unchanged)
- `services/chatbot_service.py` - Only LLM initialization changes
- Widget code - No changes
- RAG pipeline - No changes

## Provider Comparison

| Provider | Free Tier | Cost | Speed | Best For |
|----------|-----------|------|-------|----------|
| **OpenAI** | ❌ | Medium | Fast | General purpose, reliable |
| **Claude** | ❌ | Medium-High | Fast | Long context, reasoning |
| **Gemini** | ✅ | Low (after free) | Fast | Multimodal, free tier |
| **DeepSeek** | ❌ | Very Low | Fast | Cost-effective, coding |
| **Groq** | ✅ | Free tier | Very Fast | Fast inference, free tier |
| **Together** | ❌ | Low | Medium | Open-source models |

## API Key Management

### System-Level (Default)
- Stored in environment variables
- Used when user doesn't provide their own key
- Fallback option

### User-Level (Optional)
- Users can provide their own API keys
- Encrypted in database
- Allows users to use their own credits
- Better for cost management

## Security Considerations

1. **API Key Encryption**
   - Use `cryptography` library
   - Encrypt at rest
   - Decrypt only when needed

2. **Rate Limiting**
   - Per-user rate limits
   - Per-provider rate limits
   - Prevent abuse

3. **Key Validation**
   - Test API key on save
   - Show validation status
   - Handle invalid keys gracefully

## Cost Optimization

1. **Smart Defaults**
   - Use cheapest model by default
   - Allow users to upgrade

2. **Model Recommendations**
   - Show cost/speed indicators
   - Recommend based on use case

3. **Usage Tracking**
   - Track tokens per provider
   - Show usage statistics
   - Cost estimation

## Testing Strategy

1. **Unit Tests**
   - Test each provider initialization
   - Test model switching
   - Test error handling

2. **Integration Tests**
   - Test end-to-end chat flow
   - Test with each provider
   - Test API key validation

3. **Performance Tests**
   - Compare response times
   - Compare costs
   - Load testing

## Migration Path

1. **Phase 1:** Remove Ollama (no breaking changes)
2. **Phase 2:** Add unified service (backward compatible)
3. **Phase 3:** Add new providers (optional, users can stick with OpenAI)
4. **Phase 4:** Update UI (gradual rollout)

## Dependencies to Add

```txt
# Add to requirements-prod.txt
langchain-anthropic==0.3.0
langchain-google-genai==2.0.0
langchain-groq==0.1.0
langchain-together==0.1.0
cryptography==43.0.0  # For API key encryption
```

## Estimated Implementation Time

- **Phase 1 (Remove Ollama):** 2-3 hours
- **Phase 2 (Unified Service):** 3-4 hours
- **Phase 3 (Add Providers):** 4-6 hours
- **Phase 4 (Update UI):** 4-6 hours
- **Phase 5 (Database):** 2-3 hours
- **Phase 6 (Testing):** 4-6 hours

**Total:** ~20-28 hours

## Benefits

1. **Flexibility:** Users can choose best provider for their needs
2. **Cost Optimization:** Users can use free tiers or cheaper options
3. **Reliability:** Fallback options if one provider is down
4. **Future-Proof:** Easy to add new providers
5. **User Control:** Users can use their own API keys

## Next Steps

1. Review and approve this plan
2. Start with Phase 1 (Remove Ollama locally)
3. Test thoroughly
4. Proceed with remaining phases

