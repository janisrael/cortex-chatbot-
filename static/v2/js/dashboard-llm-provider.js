// ===========================
// LLM PROVIDER SELECTION
// Handles provider and model selection
// ===========================

// Provider configurations with available models
const LLM_PROVIDERS = {
    openai: {
        name: 'OpenAI',
        icon: 'smart_toy', // Material icon for OpenAI
        hasFreeTier: false,
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
        icon: 'psychology', // Material icon for Claude
        hasFreeTier: false,
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
        icon: 'auto_awesome', // Material icon for Gemini
        hasFreeTier: true,
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
        icon: 'explore', // Material icon for DeepSeek
        hasFreeTier: false,
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
        icon: 'bolt', // Material icon for Groq (fast)
        hasFreeTier: true,
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
        icon: 'hub', // Material icon for Together AI
        hasFreeTier: false,
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
        
        // Set API key (load user's saved key)
        const apiKeyField = document.getElementById('llmApiKey');
        if (apiKeyField) {
            // Load the actual API key value (not masked)
            if (apiKey && apiKey.trim().length > 0) {
                apiKeyField.value = apiKey;
                console.log('✅ Loaded user API key (length: ' + apiKey.length + ')');
            } else {
                apiKeyField.value = '';
                console.log('ℹ️ No user API key saved, using system default');
            }
        }
        
        // Update provider info box
        const providerConfig = LLM_PROVIDERS[provider];
        if (providerConfig) {
            updateProviderInfo(providerConfig);
        }
        
        // Update active LLM status display
        updateActiveLLMStatus(provider, model);
        
        // Setup clear button after loading config
        setupApiKeyClearButton();
    } catch (error) {
        console.error('Failed to load LLM provider config:', error);
    }
}

// Update active LLM status display (logo/icon, provider name, model)
function updateActiveLLMStatus(provider, model) {
    const providerConfig = LLM_PROVIDERS[provider];
    if (!providerConfig) {
        console.warn('Provider config not found for:', provider);
        return;
    }
    
    // Try to load provider logo (SVG first, then PNG)
    const logoImg = document.getElementById('activeLLMLogo');
    const iconElement = document.getElementById('activeLLMIcon');
    
    if (logoImg && iconElement) {
        // Only try PNG since we don't have SVG files
        const logoPng = `/static/img/providers/${provider}-logo.png`;
        
        // Create image to test if PNG file exists
        const testImg = new Image();
        testImg.onload = function() {
            // Logo found - show image, hide icon
            logoImg.src = this.src;
            logoImg.style.display = 'block';
            logoImg.alt = `${providerConfig.name} Logo`;
            iconElement.style.display = 'none';
            console.log(`✅ Loaded logo: ${this.src}`);
        };
        testImg.onerror = function() {
            // No logo found - show Material Icon fallback
            logoImg.style.display = 'none';
            iconElement.style.display = 'block';
            iconElement.textContent = providerConfig.icon || 'smart_toy';
            console.log(`ℹ️ Logo not found, using Material Icon: ${providerConfig.icon}`);
        };
        testImg.src = logoPng;
    }
    
    // Update provider name
    const providerElement = document.getElementById('activeLLMProvider');
    if (providerElement) {
        providerElement.textContent = providerConfig.name || provider;
    }
    
    // Update model name
    const modelElement = document.getElementById('activeLLMModel');
    if (modelElement) {
        // Find the model label from the models array
        const modelInfo = providerConfig.models?.find(m => m.value === model);
        const modelLabel = modelInfo ? modelInfo.label : model;
        modelElement.textContent = modelLabel;
    }
    
    console.log(`✅ Updated active LLM status: ${providerConfig.name} / ${model}`);
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
// Now includes connection test before saving
async function saveLLMProviderConfig() {
    const saveBtn = document.getElementById('saveLLMProviderBtn');
    if (!saveBtn) return;
    
    const originalText = saveBtn.innerHTML;
    const originalDisabled = saveBtn.disabled;
    
    try {
        // Get form values
        const provider = document.getElementById('llmProvider')?.value || 'openai';
        let model = document.getElementById('llmModel')?.value;
        
        // If no model selected, use default for provider
        if (!model && LLM_PROVIDERS[provider]) {
            model = LLM_PROVIDERS[provider].defaultModel;
        }
        
        if (!model) {
            throw new Error('No model selected. Please select a model first.');
        }
        
        const apiKey = document.getElementById('llmApiKey')?.value || '';
        
        // STEP 1: Test Connection
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">hourglass_empty</span> Checking connection...';
        hideAlert('llmSuccess');
        hideAlert('llmError');
        
        console.log('🔍 Testing connection before save...');
        const testResult = await testLLMConnectionSilent(provider, model, apiKey);
        
        if (!testResult.success) {
            // Test failed - show error and don't save
            const errorMsg = testResult.error || 'Connection test failed';
            console.error('❌ Connection test failed:', errorMsg);
            
            if (typeof showErrorNotification === 'function') {
                showErrorNotification(errorMsg);
            } else {
                showAlert('llmError', errorMsg);
            }
            return; // Exit - don't save
        }
        
        console.log('✅ Connection test passed, proceeding to save...');
        
        // STEP 2: Save Configuration (test passed)
        saveBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">save</span> Saving...';
        
        // Prepare API key for save
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
            credentials: 'same-origin',
            body: JSON.stringify(configData)
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Server returned non-JSON response. Status: ${response.status}.`);
        }
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to save provider settings');
        }
        
        // Success!
        console.log('✅ Settings saved successfully');
        if (typeof showSuccessNotification === 'function') {
            showSuccessNotification('LLM provider settings saved successfully!');
        } else {
            showAlert('llmSuccess', 'LLM provider settings saved successfully!');
        }
        
        // Reload configuration to update UI
        await loadLLMProviderConfig();
        
        // Update active LLM status display immediately
        updateActiveLLMStatus(provider, model);
        
        // Update llmConfig object used by updateLLMStatus() and overview
        // This ensures the status indicators show the correct model (not system default)
        if (typeof llmConfig !== 'undefined') {
            llmConfig.effective_provider = provider;
            llmConfig.effective_model = model;
            console.log(`✅ Updated llmConfig: ${provider} / ${model}`);
        }
        
        // Update status indicators
        if (typeof updateLLMStatus === 'function') {
            updateLLMStatus();
        }
        
        // Refresh overview stats to show updated model
        if (typeof loadStats === 'function') {
            await loadStats();
        }
        
    } catch (error) {
        console.error('Failed to save LLM provider config:', error);
        let errorMsg = `Unable to save settings: ${error.message}`;
        
        // Handle JSON parse errors
        if (error.message.includes('JSON') || error.message.includes('Unexpected token')) {
            errorMsg = 'Unable to save settings: Server returned an invalid response. Please check your login status and try again.';
        }
        
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMsg);
        } else {
            showAlert('llmError', errorMsg);
        }
    } finally {
        // Always restore button
        if (saveBtn) {
            saveBtn.disabled = originalDisabled;
            saveBtn.innerHTML = originalText;
        }
    }
}

// Test LLM connection silently (no UI updates, returns result)
// Used by saveLLMProviderConfig() to validate before saving
async function testLLMConnectionSilent(provider, model, apiKey) {
    try {
        // Prepare API key - don't send if masked or too short
        let apiKeyToSend = null;
        if (apiKey && !apiKey.includes('...') && apiKey.length >= 10) {
            apiKeyToSend = apiKey;
        }
        
        // Call test API
        const response = await fetch('/api/test-llm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                provider: provider,
                model: model,
                api_key: apiKeyToSend
            })
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            return { success: false, error: 'Server returned invalid response. Please check your login status.' };
        }
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            return { success: true, result: result };
        } else {
            // Extract error message from API response
            const errorMsg = result.error || result.message || 'Connection test failed';
            return { success: false, error: errorMsg };
        }
    } catch (error) {
        // Handle network errors or other exceptions
        let errorMsg = error.message;
        
        // Clean up error message
        if (errorMsg.includes('JSON') || errorMsg.includes('Unexpected token')) {
            errorMsg = 'Server returned an invalid response. Please check your login status and try again.';
        }
        
        return { success: false, error: errorMsg };
    }
}

// Test LLM provider connection (with UI updates)
async function testLLMProvider() {
    console.log('🧪 ========== testLLMProvider() CALLED ==========');
    console.log('🧪 Function execution started at:', new Date().toISOString());
    
    const testBtn = document.getElementById('testLLMProviderBtn');
    if (!testBtn) {
        console.error('❌ Test button not found');
        if (typeof showErrorNotification === 'function') {
            showErrorNotification('Test button not found. Please refresh the page.');
        } else {
            alert('Test button not found. Please refresh the page.');
        }
        return;
    }
    console.log('✅ Test button found:', testBtn);
    
    const originalText = testBtn.innerHTML;
    
    testBtn.disabled = true;
    testBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">hourglass_empty</span> Testing...';
    hideAlert('llmSuccess');
    hideAlert('llmError');
    
    try {
        // Get values from form
        const providerSelect = document.getElementById('llmProvider');
        const modelSelect = document.getElementById('llmModel');
        const apiKeyInput = document.getElementById('llmApiKey');
        
        if (!providerSelect || !modelSelect) {
            throw new Error('Provider or Model dropdown not found');
        }
        
        const provider = providerSelect.value || 'openai';
        let model = modelSelect.value;
        
        // If no model selected, use default for provider
        if (!model && LLM_PROVIDERS[provider]) {
            model = LLM_PROVIDERS[provider].defaultModel;
        }
        
        if (!model) {
            throw new Error('No model selected. Please select a model first.');
        }
        
        const apiKey = apiKeyInput?.value || '';
        
        // Log what we're testing
        console.log('🧪 Testing LLM Connection:');
        console.log('  Provider:', provider);
        console.log('  Model:', model);
        console.log('  API Key provided:', apiKey ? (apiKey.includes('...') ? 'Masked (using system default)' : `Yes (${apiKey.length} chars)`) : 'No (using system default)');
        
        // Prepare API key - don't send if masked or too short
        let apiKeyToSend = null;
        if (apiKey && !apiKey.includes('...') && apiKey.length >= 10) {
            apiKeyToSend = apiKey;
        }
        
        // Use the same test endpoint as the main test
        const response = await fetch('/api/test-llm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                provider: provider,
                model: model,
                api_key: apiKeyToSend
            })
        });
        
        console.log('📡 Response status:', response.status);
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Server returned non-JSON response. Status: ${response.status}. Please check if you're logged in.`);
        }
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            console.log('✅ Test successful:', result);
            const message = `Connection successful! Provider: ${provider}, Model: ${result.model}${result.response_time ? `, Response time: ${result.response_time}ms` : ''}`;
            
            // Always show floating notification (toast)
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message);
                console.log('✅ Success notification shown');
            } else {
                console.warn('⚠️ showSuccessNotification not available, using showAlert');
                showAlert('llmSuccess', message);
            }
        } else {
            console.error('❌ Test failed:', result);
            // Extract error message from API response
            const errorMsg = result.error || result.message || 'Unknown error occurred';
            // Create a user-friendly error that will be caught and displayed in toast
            const friendlyError = new Error(errorMsg);
            friendlyError.apiError = true; // Flag to indicate this is from API
            throw friendlyError;
        }
        
    } catch (error) {
        console.error('❌ LLM provider test failed:', error);
        let errorMsg = error.message;
        
        // Try to extract error from response if it's a fetch error
        if (error.message && error.message.includes('Connection failed:')) {
            // Extract the actual error message after "Connection failed: "
            const match = error.message.match(/Connection failed: (.+)/);
            if (match && match[1]) {
                errorMsg = match[1];
            }
        }
        
        // Handle JSON parse errors
        if (error.message.includes('JSON') || error.message.includes('Unexpected token')) {
            errorMsg = 'Connection test failed: Server returned an invalid response. Please check your login status and try again.';
        }
        
        // Clean up error message - remove redundant prefixes
        if (errorMsg.startsWith('Connection test failed: ')) {
            errorMsg = errorMsg.replace('Connection test failed: ', '');
        }
        if (errorMsg.startsWith('Connection failed: ')) {
            errorMsg = errorMsg.replace('Connection failed: ', '');
        }
        
        // Always show floating notification (toast) with user-friendly message
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMsg);
            console.log('✅ Error notification shown:', errorMsg);
        } else {
            console.warn('⚠️ showErrorNotification not available, using showAlert');
            showAlert('llmError', errorMsg);
        }
    } finally {
        const testBtn = document.getElementById('testLLMProviderBtn');
        if (testBtn) {
            testBtn.disabled = false;
            testBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">science</span> Test Connection';
        }
        console.log('🧪 ========== testLLMProvider() FINISHED ==========');
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
    
    // Populate provider dropdown with free tier labels
    if (providerSelect.options.length <= 1) { // Only populate if not already populated
        // Clear existing options (keep first one if it's a placeholder)
        const currentValue = providerSelect.value;
        providerSelect.innerHTML = '';
        
        // Add options from LLM_PROVIDERS
        Object.keys(LLM_PROVIDERS).forEach(providerKey => {
            const provider = LLM_PROVIDERS[providerKey];
            const option = document.createElement('option');
            option.value = providerKey;
            
            // Add "(free tier)" label if provider has free tier
            if (provider.hasFreeTier) {
                option.textContent = `${provider.name} (free tier)`;
            } else {
                option.textContent = provider.name;
            }
            
            // Mark default provider
            if (providerKey === 'openai') {
                option.textContent += ' (Default)';
            }
            
            providerSelect.appendChild(option);
        });
        
        // Restore previous selection if it exists
        if (currentValue && LLM_PROVIDERS[currentValue]) {
            providerSelect.value = currentValue;
        } else {
            providerSelect.value = 'openai';
        }
    }
    
    // Set default provider if not set
    if (!providerSelect.value) {
        providerSelect.value = 'openai';
        console.log('✅ Set default provider to openai');
    }
    
    // Populate models for the current provider
    console.log('📋 Calling onProviderChange()...');
    onProviderChange();
    
    // Setup API key clear button
    setupApiKeyClearButton();
    
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

// Clear API key input
function clearApiKeyInput() {
    const apiKeyInput = document.getElementById('llmApiKey');
    const clearBtn = document.getElementById('llmApiKeyClear');
    
    if (apiKeyInput) {
        apiKeyInput.value = '';
        apiKeyInput.focus();
    }
    
    if (clearBtn) {
        clearBtn.style.display = 'none';
    }
}

// Show/hide clear button based on input value
function setupApiKeyClearButton() {
    const apiKeyInput = document.getElementById('llmApiKey');
    const clearBtn = document.getElementById('llmApiKeyClear');
    
    if (!apiKeyInput || !clearBtn) return;
    
    // Show/hide clear button based on input value
    function toggleClearButton() {
        if (apiKeyInput.value && apiKeyInput.value.length > 0) {
            clearBtn.style.display = 'flex';
        } else {
            clearBtn.style.display = 'none';
        }
    }
    
    // Check on input
    apiKeyInput.addEventListener('input', toggleClearButton);
    
    // Check on load
    toggleClearButton();
}

// Make functions globally accessible for onclick handlers
// Assign immediately to ensure availability when dashboard-overview.js calls it
if (typeof window !== 'undefined') {
    window.initializeLLMProvider = initializeLLMProvider;
    window.clearApiKeyInput = clearApiKeyInput;
    window.onProviderChange = onProviderChange;
    window.updateActiveLLMStatus = updateActiveLLMStatus;
    console.log('✅ LLM provider functions assigned to window');
}

// Make the real test function globally accessible (MUST be after function definition)
// Store reference to original function to avoid infinite loop
const originalTestLLMProvider = testLLMProvider;
window.testLLMProvider = function() {
    console.log('🔧 window.testLLMProvider wrapper called');
    if (typeof originalTestLLMProvider === 'function') {
        return originalTestLLMProvider();
    } else {
        console.error('❌ testLLMProvider function not found!');
        if (typeof showErrorNotification === 'function') {
            showErrorNotification('Test function not loaded. Please refresh the page.');
        } else {
            alert('Test function not loaded. Please refresh the page.');
        }
    }
};

console.log('✅ testLLMProvider function registered globally:', typeof window.testLLMProvider);
console.log('✅ Direct testLLMProvider function:', typeof testLLMProvider);

// Debug function - can be called directly from console (renamed to avoid conflict)
window.debugLLMProvider = function() {
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
        setTimeout(() => {
            tryInitialize();
            setupApiKeyClearButton();
        }, 100);
    });
} else {
    console.log('📄 DOM already loaded, trying to initialize...');
    setTimeout(() => {
        tryInitialize();
        setupApiKeyClearButton();
    }, 100);
}

