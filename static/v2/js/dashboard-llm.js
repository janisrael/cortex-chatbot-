// ===========================
// CORTEX AI DASHBOARD - LLM CONFIGURATION
// LLM Provider Management & Configuration
// ===========================

async function loadLLMConfig() {
    try {
        // Fetch actual LLM config from backend
        const response = await fetch('/api/llm-config');
        const data = await response.json();
        
        llmConfig = {
            global_provider: data.llm_option || 'openai',
            openai: {
                has_api_key: data.has_openai_key || false,
                api_key_masked: data.openai_key_masked || '',
                default_model: data.openai_model || 'gpt-4o-mini',
                temperature: data.openai_temperature || 1.0
            },
            ollama: {
                base_url: data.ollama_url || 'http://localhost:11434',
                default_model: data.ollama_model || 'llama3.1:8b'
            },
            effective_provider: data.llm_option || 'openai',
            effective_model: data.current_model || 'gpt-4o-mini',
            website_overrides: {},
            is_fallback: false  // API call succeeded, not using fallback
        };
        
        populateLLMConfig();
        updateLLMStatus();
    } catch (error) {
        console.error('Failed to load LLM config:', error);
        // Fallback to default values if API fails
        llmConfig = {
            global_provider: 'openai',
            openai: {
                has_api_key: false,
                api_key_masked: '',
                default_model: 'gpt-4o-mini',
                temperature: 1.0
            },
            ollama: {
                base_url: 'http://localhost:11434',
                default_model: 'llama3.1:8b'
            },
            effective_provider: 'openai',
            effective_model: 'gpt-4o-mini',
            website_overrides: {},
            is_fallback: true  // Using fallback values
        };
        populateLLMConfig();
        updateLLMStatus();
    }
}

function populateLLMConfig() {
    // Global settings
    const globalProvider = document.getElementById('globalProvider');
    if (globalProvider) {
        globalProvider.value = llmConfig.global_provider || 'openai';
    }
    
    if (llmConfig.openai) {
        const openaiKey = document.getElementById('globalOpenaiKey');
        const openaiModel = document.getElementById('globalOpenaiDefaultModel');
        const ollamaUrl = document.getElementById('globalOllamaUrl');
        const ollamaModel = document.getElementById('globalOllamaDefaultModel');
        
        // Populate OpenAI API key (masked)
        if (openaiKey && llmConfig.openai.api_key_masked) {
            openaiKey.value = llmConfig.openai.api_key_masked;
            openaiKey.type = 'password'; // Set as password field
        }
        
        if (openaiModel) openaiModel.value = llmConfig.openai.default_model || 'gpt-4o-mini';
        if (ollamaUrl) ollamaUrl.value = llmConfig.ollama?.base_url || 'http://localhost:11434';
        if (ollamaModel) ollamaModel.value = llmConfig.ollama?.default_model || 'llama3.1:8b';
    }
    
    // Website-specific overrides
    const websiteOverride = llmConfig.website_overrides?.[currentWebsiteId];
    if (websiteOverride) {
        const websiteProvider = document.getElementById('websiteProvider');
        const websiteModel = document.getElementById('websiteModel');
        const websiteTemp = document.getElementById('websiteTemperature');
        
        if (websiteProvider) websiteProvider.value = websiteOverride.provider || '';
        if (websiteModel) websiteModel.value = websiteOverride.model || '';
        if (websiteTemp) websiteTemp.value = websiteOverride.temperature || '';
    } else {
        const websiteProvider = document.getElementById('websiteProvider');
        const websiteModel = document.getElementById('websiteModel');
        const websiteTemp = document.getElementById('websiteTemperature');
        
        if (websiteProvider) websiteProvider.value = '';
        if (websiteModel) websiteModel.value = '';
        if (websiteTemp) websiteTemp.value = '';
    }
    
    // Update global provider tabs
    selectGlobalProvider(llmConfig.global_provider || 'openai');
}

function selectGlobalProvider(provider) {
    // Update tabs
    document.querySelectorAll('.provider-tab').forEach(tab => tab.classList.remove('active'));
    const providerTab = document.getElementById(`global${provider.charAt(0).toUpperCase() + provider.slice(1)}Tab`);
    if (providerTab) providerTab.classList.add('active');
    
    // Show/hide config sections
    document.querySelectorAll('.provider-config').forEach(config => config.classList.remove('active'));
    const configSection = document.getElementById(`global${provider.charAt(0).toUpperCase() + provider.slice(1)}Config`);
    if (configSection) configSection.classList.add('active');
}

async function saveGlobalConfig() {
    const saveBtn = document.getElementById('saveGlobalBtn');
    if (!saveBtn) return;
    
    const originalText = saveBtn.textContent;
    
    saveBtn.disabled = true;
    saveBtn.textContent = '💾 Saving...';
    hideAlert('llmSuccess');
    hideAlert('llmError');
    
    try {
        const configData = {
            config_type: 'global',
            global_provider: document.getElementById('globalProvider')?.value,
            openai: {
                api_key: document.getElementById('globalOpenaiKey')?.value || undefined,
                default_model: document.getElementById('globalOpenaiDefaultModel')?.value
            },
            ollama: {
                base_url: document.getElementById('globalOllamaUrl')?.value,
                default_model: document.getElementById('globalOllamaDefaultModel')?.value
            }
        };
        
        // Simulate API call - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        showAlert('llmSuccess', 'Global LLM configuration saved successfully!');
        await loadLLMConfig();
        
    } catch (error) {
        console.error('Failed to save global config:', error);
        showAlert('llmError', 'Failed to save configuration: ' + error.message);
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = originalText;
        }
    }
}

async function saveWebsiteConfig() {
    const saveBtn = document.getElementById('saveWebsiteBtn');
    if (!saveBtn) return;
    
    const originalText = saveBtn.textContent;
    
    saveBtn.disabled = true;
    saveBtn.textContent = '💾 Saving...';
    hideAlert('llmSuccess');
    hideAlert('llmError');
    
    try {
        const configData = {
            config_type: 'website',
            website_id: currentWebsiteId,
            provider: document.getElementById('websiteProvider')?.value || null,
            model: document.getElementById('websiteModel')?.value || null,
            temperature: document.getElementById('websiteTemperature')?.value || null
        };
        
        // Simulate API call - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        showAlert('llmSuccess', `Configuration saved for ${websites[currentWebsiteId]?.name || currentWebsiteId}!`);
        await loadLLMConfig();
        
    } catch (error) {
        console.error('Failed to save website config:', error);
        showAlert('llmError', 'Failed to save configuration: ' + error.message);
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = originalText;
        }
    }
}

function updateLLMStatus() {
    // Update main LLM status element
    const statusElement = document.getElementById('llmStatus');
    if (statusElement) {
        const provider = llmConfig.effective_provider || 'unknown';
        const model = llmConfig.effective_model || 'unknown';
        
        let statusClass = 'status-active';
        let statusText = `Active: ${provider} (${model})`;
        
        if (provider === 'unknown') {
            statusClass = 'status-inactive';
            statusText = 'Not Configured';
        }
        
        statusElement.className = `status-indicator ${statusClass}`;
        statusElement.innerHTML = `
            <span class="status-dot ${statusClass === 'status-active' ? 'active' : 'inactive'}"></span>
            ${statusText}
        `;
    }
    
    // Update overview tab LLM status indicator (systemLLMStatus section)
    const systemLLMText = document.getElementById('systemLLMText');
    const systemLLMDot = document.getElementById('systemLLMDot');
    const systemLLMStatus = document.getElementById('systemLLMStatus');
    
    if (systemLLMText && systemLLMDot) {
        const provider = llmConfig.effective_provider || 'openai';
        const model = llmConfig.effective_model || 'gpt-4o-mini';
        const hasApiKey = llmConfig.openai?.has_api_key || false;
        const isFallback = llmConfig.is_fallback || false;
        
        if (isFallback) {
            // Show fallback status
            systemLLMText.textContent = `Fallback: ${provider.toUpperCase()}`;
            systemLLMText.style.color = '#ff9800'; // Orange text
            systemLLMDot.className = 'status-dot';
            systemLLMDot.style.backgroundColor = '#ff9800'; // Orange dot
            if (systemLLMStatus) {
                systemLLMStatus.className = 'status-indicator';
                systemLLMStatus.style.backgroundColor = '#5d5d5d'; // Dark gray background
            }
        } else if (hasApiKey || provider === 'ollama') {
            // Active configuration
            systemLLMText.textContent = `${provider.toUpperCase()}: ${model}`;
            systemLLMDot.className = 'status-dot active';
            systemLLMDot.style.backgroundColor = '#28a745';
            if (systemLLMStatus) {
                systemLLMStatus.className = 'status-indicator status-active';
                systemLLMStatus.style.color = '';
            }
        } else {
            // Not configured
            systemLLMText.textContent = 'Not Configured';
            systemLLMDot.className = 'status-dot';
            systemLLMDot.style.backgroundColor = '#dc3545';
            if (systemLLMStatus) {
                systemLLMStatus.className = 'status-indicator';
                systemLLMStatus.style.color = '#dc3545';
            }
        }
    }
    
    // Also update LLM tab status indicator (for backward compatibility)
    const llmStatusText = document.getElementById('llmStatusText');
    const llmStatusDot = document.getElementById('llmStatusDot');
    
    if (llmStatusText && llmStatusDot) {
        const provider = llmConfig.effective_provider || 'openai';
        const model = llmConfig.effective_model || 'gpt-4o-mini';
        
        llmStatusText.textContent = `${provider.toUpperCase()}: ${model}`;
        llmStatusDot.className = 'status-dot active';
        llmStatusDot.style.backgroundColor = '#28a745';
    }
}

async function testLLMConnection() {
    const testBtn = event.target;
    const originalText = testBtn.innerHTML;
    
    testBtn.disabled = true;
    testBtn.innerHTML = '⏳ Testing...';
    hideAlert('llmSuccess');
    hideAlert('llmError');
    
    try {
        console.log('Testing LLM connection...');
        
        const response = await fetch('/api/test-llm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                provider: llmConfig.effective_provider || 'openai',
                model: llmConfig.effective_model || 'gpt-4o-mini'
            })
        });
        
        const result = await response.json();
        console.log('Test result:', result);
        
        if (response.ok && result.status === 'success') {
            const message = `Connection successful! Model: ${result.model}, Response time: ${result.response_time}ms`;
            console.log('Success:', message);
            showAlert('llmSuccess', message);
            
            // Auto-hide success message after 5 seconds
            setTimeout(() => hideAlert('llmSuccess'), 5000);
        } else {
            const errorMsg = `Connection failed: ${result.error || 'Unknown error'}`;
            console.error('Error:', errorMsg);
            showAlert('llmError', errorMsg);
        }
        
    } catch (error) {
        const errorMsg = `Connection test failed: ${error.message}`;
        console.error('Exception:', errorMsg);
        showAlert('llmError', errorMsg);
    } finally {
        testBtn.disabled = false;
        testBtn.innerHTML = originalText;
    }
}

// Alias for backward compatibility
function testLLM() {
    testLLMConnection();
}
