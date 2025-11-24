// ===========================
// LLM PROVIDER SELECTION
// Handles provider and model selection
// ===========================

// Provider configurations with available models
const LLM_PROVIDERS = {
    openai: {
        name: 'OpenAI',
        description: 'Industry-leading AI with excellent performance, reliability, and broad capabilities. Best for general-purpose chatbots.',
        strengths: 'Excellent for virtual assistants and customer support chatbots. Provides reliable, natural conversations with strong language understanding and fast response times. Great for businesses that need a polished, professional chatbot experience.',
        models: [
            { value: 'gpt-4o-mini', label: 'GPT-4o Mini (Recommended)' },
            { value: 'gpt-4o', label: 'GPT-4o' },
            { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
            { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' }
        ],
        apiKeyEnv: 'OPENAI_API_KEY',
        defaultModel: 'gpt-4o-mini'
    },
    claude: {
        name: 'Anthropic Claude',
        description: 'Advanced AI focused on safety, helpfulness, and long-context understanding. Excellent for detailed analysis and reasoning.',
        strengths: 'Perfect for intelligent virtual assistants that need to handle complex queries and maintain long conversations. Excellent reasoning capabilities make it ideal for technical support chatbots, educational assistants, and chatbots that need to reference extensive documentation or context.',
        models: [
            { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
            { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
            { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku' }
        ],
        apiKeyEnv: 'ANTHROPIC_API_KEY',
        defaultModel: 'claude-3-5-sonnet-20241022'
    },
    gemini: {
        name: 'Google Gemini',
        description: 'Google\'s powerful AI with free tier available. Great for multimodal tasks and cost-effective solutions.',
        strengths: 'Ideal for cost-effective chatbot deployments with a free tier option. Great for multilingual chatbots and applications that need to process images alongside text. Perfect for startups and businesses looking for a budget-friendly yet capable virtual assistant solution.',
        models: [
            { value: 'gemini-pro', label: 'Gemini Pro' },
            { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
            { value: 'gemini-pro-vision', label: 'Gemini Pro Vision' }
        ],
        apiKeyEnv: 'GOOGLE_API_KEY',
        defaultModel: 'gemini-pro'
    },
    deepseek: {
        name: 'DeepSeek',
        description: 'Highly cost-effective AI with excellent performance. Great for budget-conscious deployments without sacrificing quality.',
        strengths: 'Excellent choice for technical support chatbots and developer-focused virtual assistants. Very affordable while maintaining good performance, making it perfect for businesses that need cost-effective chatbot solutions without compromising on quality. Great for handling technical queries and code-related questions.',
        models: [
            { value: 'deepseek-chat', label: 'DeepSeek Chat' },
            { value: 'deepseek-coder', label: 'DeepSeek Coder' }
        ],
        apiKeyEnv: 'DEEPSEEK_API_KEY',
        defaultModel: 'deepseek-chat'
    },
    groq: {
        name: 'Groq (Llama)',
        description: 'Ultra-fast inference with free tier. Open-source Llama models running on specialized hardware for maximum speed.',
        strengths: 'Perfect for real-time chatbots that require instant responses. The ultra-fast inference makes it ideal for live chat applications, customer service bots, and interactive virtual assistants where low latency is critical. Free tier available makes it great for testing and small-scale deployments.',
        models: [
            { value: 'llama-3.1-70b-versatile', label: 'Llama 3.1 70B' },
            { value: 'llama-3.1-8b-instant', label: 'Llama 3.1 8B' },
            { value: 'mixtral-8x7b-32768', label: 'Mixtral 8x7B' }
        ],
        apiKeyEnv: 'GROQ_API_KEY',
        defaultModel: 'llama-3.1-70b-versatile'
    },
    together: {
        name: 'Together AI (Llama)',
        description: 'Access to open-source Llama models with competitive pricing. Good balance of performance and cost for open-source models.',
        strengths: 'Great for businesses that prefer open-source solutions and want flexibility in model selection. Good balance of performance and cost, making it suitable for general-purpose chatbots and virtual assistants. Ideal for developers who want to experiment with different model sizes and configurations.',
        models: [
            { value: 'meta-llama/Llama-3-70b-chat-hf', label: 'Llama 3 70B' },
            { value: 'meta-llama/Llama-3-8b-chat-hf', label: 'Llama 3 8B' }
        ],
        apiKeyEnv: 'TOGETHER_API_KEY',
        defaultModel: 'meta-llama/Llama-3-70b-chat-hf'
    }
};

// Load provider and model from user config
async function loadLLMProviderConfig() {
    try {
        const response = await fetch('/api/user/chatbot-config');
        if (!response.ok) throw new Error('Failed to load config');
        
        const data = await response.json();
        const config = data.config || data;
        
        const provider = config.llm_provider || 'openai';
        const model = config.llm_model || LLM_PROVIDERS[provider].defaultModel;
        const apiKey = config.llm_api_key || '';
        
        // Set provider dropdown
        const providerSelect = document.getElementById('llmProvider');
        if (providerSelect) {
            providerSelect.value = provider;
            onProviderChange(); // This will populate models
        }
        
        // Set model dropdown
        const modelSelect = document.getElementById('llmModel');
        if (modelSelect) {
            modelSelect.value = model;
        }
        
        // Set API key (masked if exists)
        const apiKeyField = document.getElementById('llmApiKey');
        if (apiKeyField) {
            if (apiKey && apiKey.length > 8) {
                apiKeyField.value = apiKey.substring(0, 4) + '...' + apiKey.substring(apiKey.length - 4);
            } else {
                apiKeyField.value = '';
            }
        }
        
        // Update provider info box
        const providerConfig = LLM_PROVIDERS[provider];
        if (providerConfig) {
            updateProviderInfo(providerConfig);
        }
    } catch (error) {
        console.error('Failed to load LLM provider config:', error);
    }
}

// Handle provider change - update available models and info box
function onProviderChange() {
    console.log('🔄 onProviderChange called');
    
    const providerSelect = document.getElementById('llmProvider');
    const modelSelect = document.getElementById('llmModel');
    
    if (!providerSelect) {
        console.error('❌ llmProvider element not found in onProviderChange');
        return;
    }
    
    if (!modelSelect) {
        console.error('❌ llmModel element not found in onProviderChange');
        return;
    }
    
    const selectedProvider = providerSelect.value || 'openai';
    console.log('📌 Selected provider:', selectedProvider);
    
    // Check if LLM_PROVIDERS is defined
    if (typeof LLM_PROVIDERS === 'undefined') {
        console.error('❌ LLM_PROVIDERS is not defined!');
        console.error('This usually means the script failed to load or there was a syntax error.');
        return;
    }
    
    console.log('Available providers:', Object.keys(LLM_PROVIDERS));
    
    const providerConfig = LLM_PROVIDERS[selectedProvider];
    
    if (!providerConfig) {
        console.error('❌ Unknown provider:', selectedProvider);
        console.log('Available providers:', Object.keys(LLM_PROVIDERS));
        return;
    }
    
    console.log('✅ Provider config found:', providerConfig);
    console.log('Provider config keys:', Object.keys(providerConfig));
    
    // Check if models array exists
    if (!providerConfig.hasOwnProperty('models')) {
        console.error('❌ Provider config has no "models" property');
        console.error('Full config:', JSON.stringify(providerConfig, null, 2));
        return;
    }
    
    if (!Array.isArray(providerConfig.models)) {
        console.error('❌ Provider config "models" is not an array:', typeof providerConfig.models);
        console.error('Models value:', providerConfig.models);
        return;
    }
    
    if (providerConfig.models.length === 0) {
        console.warn('⚠️ Provider config has empty models array');
    }
    
    console.log('📋 Models to add:', providerConfig.models.length);
    
    // Clear and populate model dropdown
    if (!modelSelect) {
        console.error('❌ modelSelect is null/undefined, cannot populate models');
        return;
    }
    
    modelSelect.innerHTML = '';
    
    // Verify modelSelect is still valid after clearing
    if (!modelSelect || !modelSelect.appendChild) {
        console.error('❌ modelSelect became invalid after clearing innerHTML');
        return;
    }
    
    providerConfig.models.forEach((model, index) => {
        if (!model || !model.value || !model.label) {
            console.warn(`⚠️ Skipping invalid model at index ${index}:`, model);
            return;
        }
        
        const option = document.createElement('option');
        option.value = model.value;
        option.textContent = model.label;
        if (model.value === providerConfig.defaultModel) {
            option.selected = true;
            console.log('✅ Set default model:', model.value);
        }
        
        try {
            modelSelect.appendChild(option);
            console.log(`  ✓ Added model ${index + 1}: ${model.value} - ${model.label}`);
        } catch (e) {
            console.error(`❌ Failed to add model ${index + 1}:`, e);
        }
    });
    
    // Safely get model count - with extra validation
    let finalModelCount = 0;
    if (modelSelect) {
        // Verify it's actually a select element
        if (modelSelect.tagName && modelSelect.tagName.toLowerCase() === 'select') {
            if (modelSelect.options && Array.isArray(modelSelect.options)) {
                finalModelCount = modelSelect.options.length;
            } else if (modelSelect.options && typeof modelSelect.options.length === 'number') {
                finalModelCount = modelSelect.options.length;
            } else {
                console.error('❌ modelSelect.options is not accessible');
                console.error('modelSelect type:', typeof modelSelect);
                console.error('modelSelect.tagName:', modelSelect.tagName);
                console.error('modelSelect.options:', modelSelect.options);
            }
        } else {
            console.error('❌ modelSelect is not a select element!');
            console.error('modelSelect:', modelSelect);
            console.error('modelSelect.tagName:', modelSelect?.tagName);
        }
    } else {
        console.error('❌ modelSelect is null/undefined');
    }
    
    console.log(`✅ Populated ${finalModelCount} models`);
    
    if (finalModelCount === 0) {
        console.warn('⚠️ No models were added to dropdown!');
        console.warn('This might be normal if models array was empty');
    }
    
    // Update API key placeholder
    const apiKeyField = document.getElementById('llmApiKey');
    if (apiKeyField) {
        apiKeyField.placeholder = `Leave empty to use system ${providerConfig.apiKeyEnv} or provide your own`;
    }
    
    // Update provider info box
    updateProviderInfo(providerConfig);
}

// Update provider info box with description and strengths
function updateProviderInfo(providerConfig) {
    const infoBox = document.getElementById('providerInfoBox');
    const infoName = document.getElementById('providerInfoName');
    const infoDescription = document.getElementById('providerInfoDescription');
    const infoStrengths = document.getElementById('providerInfoStrengths');
    
    if (!infoBox || !infoName || !infoDescription || !infoStrengths) return;
    
    // Update name
    infoName.textContent = providerConfig.name;
    
    // Update description
    infoDescription.textContent = providerConfig.description || '';
    
    // Update strengths (single paragraph)
    if (providerConfig.strengths) {
        infoStrengths.innerHTML = '<strong>Best for Chatbots:</strong> ' + providerConfig.strengths;
    } else {
        infoStrengths.innerHTML = '';
    }
    
    // Show the info box
    infoBox.style.display = 'block';
}

// Save LLM provider configuration
async function saveLLMProviderConfig() {
    const saveBtn = document.getElementById('saveLLMProviderBtn');
    if (!saveBtn) return;
    
    const originalText = saveBtn.innerHTML;
    
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">save</span> Saving...';
    hideAlert('llmSuccess');
    hideAlert('llmError');
    
    try {
        const provider = document.getElementById('llmProvider')?.value || 'openai';
        const model = document.getElementById('llmModel')?.value || LLM_PROVIDERS[provider].defaultModel;
        const apiKey = document.getElementById('llmApiKey')?.value || '';
        
        // If API key looks masked (contains ...), don't send it
        const apiKeyToSave = apiKey.includes('...') ? null : (apiKey || null);
        
        const configData = {
            llm_provider: provider,
            llm_model: model,
            llm_api_key: apiKeyToSave
        };
        
        const response = await fetch('/api/user/chatbot-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to save provider settings');
        }
        
        showAlert('llmSuccess', 'LLM provider settings saved successfully!');
        await loadLLMProviderConfig();
        
    } catch (error) {
        console.error('Failed to save LLM provider config:', error);
        showAlert('llmError', 'Failed to save settings: ' + error.message);
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalText;
        }
    }
}

// Test LLM provider connection
async function testLLMProvider() {
    const testBtn = document.getElementById('testLLMProviderBtn');
    if (!testBtn) return;
    
    const originalText = testBtn.innerHTML;
    
    testBtn.disabled = true;
    testBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">science</span> Testing...';
    hideAlert('llmSuccess');
    hideAlert('llmError');
    
    try {
        const provider = document.getElementById('llmProvider')?.value || 'openai';
        const model = document.getElementById('llmModel')?.value || LLM_PROVIDERS[provider].defaultModel;
        const apiKey = document.getElementById('llmApiKey')?.value || '';
        
        // Test endpoint (we'll need to create this)
        const response = await fetch('/api/test-llm-provider', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                provider: provider,
                model: model,
                api_key: apiKey.includes('...') ? null : apiKey
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Connection test failed');
        }
        
        const result = await response.json();
        showAlert('llmSuccess', `✅ Connection successful! ${result.message || 'Provider is working correctly.'}`);
        
    } catch (error) {
        console.error('LLM provider test failed:', error);
        showAlert('llmError', 'Connection test failed: ' + error.message);
    } finally {
        if (testBtn) {
            testBtn.disabled = false;
            testBtn.innerHTML = originalText;
        }
    }
}

// Initialize on page load
function initializeLLMProvider() {
    console.log('🔧 initializeLLMProvider called');
    
    // First, populate models for default provider (OpenAI) if dropdowns exist
    const providerSelect = document.getElementById('llmProvider');
    const modelSelect = document.getElementById('llmModel');
    
    console.log('Provider select found:', !!providerSelect);
    console.log('Model select found:', !!modelSelect);
    
    if (!providerSelect) {
        console.error('❌ llmProvider element not found!');
        return;
    }
    
    if (!modelSelect) {
        console.error('❌ llmModel element not found!');
        return;
    }
    
    // Set default provider if not set
    if (!providerSelect.value) {
        providerSelect.value = 'openai';
        console.log('✅ Set default provider to openai');
    }
    
    // Populate models for the current provider
    console.log('📋 Calling onProviderChange()...');
    onProviderChange();
    
    // Check if models were populated
    setTimeout(() => {
        const modelSelectCheck = document.getElementById('llmModel');
        if (!modelSelectCheck) {
            console.error('❌ modelSelect element not found in timeout check');
            return;
        }
        
        let modelCount = 0;
        if (modelSelectCheck.options && typeof modelSelectCheck.options.length === 'number') {
            modelCount = modelSelectCheck.options.length;
        }
        
        console.log(`📊 Model dropdown now has ${modelCount} options`);
        if (modelCount === 0) {
            console.error('❌ Models still not populated!');
        } else {
            console.log('✅ Models successfully populated!');
        }
    }, 100);
    
    // Then load user's saved config (which may override the default)
    loadLLMProviderConfig();
}

// Make initializeLLMProvider globally accessible for switchTab
window.initializeLLMProvider = initializeLLMProvider;
window.onProviderChange = onProviderChange;

// Test function - can be called directly from console
window.testLLMProvider = function() {
    console.log('🧪 Testing LLM Provider initialization...');
    console.log('LLM_PROVIDERS available:', typeof LLM_PROVIDERS !== 'undefined');
    console.log('OpenAI config:', LLM_PROVIDERS?.openai);
    
    const providerSelect = document.getElementById('llmProvider');
    const modelSelect = document.getElementById('llmModel');
    
    console.log('Provider select:', providerSelect);
    console.log('Model select:', modelSelect);
    
    if (providerSelect && modelSelect) {
        console.log('✅ Both elements found!');
        console.log('Current provider value:', providerSelect.value);
        
        // Safely get current model count
        let currentCount = 0;
        if (modelSelect.options && typeof modelSelect.options.length === 'number') {
            currentCount = modelSelect.options.length;
        }
        console.log('Current model options:', currentCount);
        
        // Try to populate
        if (typeof onProviderChange === 'function') {
            console.log('🔄 Calling onProviderChange...');
            onProviderChange();
            
            // Safely check again after call
            const modelSelectAfter = document.getElementById('llmModel');
            let afterCount = 0;
            if (modelSelectAfter && modelSelectAfter.options && typeof modelSelectAfter.options.length === 'number') {
                afterCount = modelSelectAfter.options.length;
            }
            console.log('After call, model options:', afterCount);
        }
    } else {
        console.error('❌ Elements not found!');
    }
};

// Wait for DOM to be ready
function tryInitialize() {
    const providerSelect = document.getElementById('llmProvider');
    const modelSelect = document.getElementById('llmModel');
    
    if (providerSelect && modelSelect) {
        console.log('✅ Elements found, initializing...');
        initializeLLMProvider();
    } else {
        console.log('⏳ Elements not ready yet, retrying...');
        setTimeout(tryInitialize, 200);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('📄 DOM loaded, trying to initialize...');
        setTimeout(tryInitialize, 100);
    });
} else {
    console.log('📄 DOM already loaded, trying to initialize...');
    setTimeout(tryInitialize, 100);
}

