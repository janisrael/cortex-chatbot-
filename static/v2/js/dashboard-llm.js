// ===========================
// CORTEX AI DASHBOARD - LLM CONFIGURATION
// LLM Provider Management & Configuration
// ===========================

async function loadLLMConfig() {
    try {
        // Fetch both system LLM config and user-specific config
        const [systemResponse, userResponse] = await Promise.all([
            fetch('/api/llm-config'),
            fetch('/api/user/chatbot-config')
        ]);
        
        const systemData = await systemResponse.json();
        const userData = userResponse.ok ? await userResponse.json() : {};
        const userConfig = userData.config || userData || {};
        
        // Use user's saved provider and model if available, otherwise use system defaults
        const userProvider = userConfig.llm_provider;
        const userModel = userConfig.llm_model;
        
        llmConfig = {
            global_provider: systemData.llm_option || 'openai',
            openai: {
                has_api_key: systemData.has_openai_key || false,
                api_key_masked: systemData.openai_key_masked || '',
                default_model: systemData.openai_model || 'gpt-4o-mini',
                temperature: systemData.openai_temperature || 1.0
            },
            // Ollama removed - local LLM support removed
            // Use user's saved provider/model, fallback to system defaults
            effective_provider: userProvider || systemData.llm_option || 'openai',
            effective_model: userModel || systemData.current_model || 'gpt-4o-mini',
            // Website overrides removed (v2 uses user-based system)
            is_fallback: false  // API call succeeded, not using fallback
        };
        
        
        populateLLMConfig();
        updateLLMStatus();
        
        // Update active LLM status display if function exists
        if (typeof updateActiveLLMStatus === 'function') {
            updateActiveLLMStatus(llmConfig.effective_provider, llmConfig.effective_model);
        }
    } catch (error) {
        // Fallback to default values if API fails
        llmConfig = {
            global_provider: 'openai',
            openai: {
                has_api_key: false,
                api_key_masked: '',
                default_model: 'gpt-4o-mini',
                temperature: 1.0
            },
            // Ollama removed - local LLM support removed
            effective_provider: 'openai',
            effective_model: 'gpt-4o-mini',
            // Website overrides removed (v2 uses user-based system)
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
        // Populate OpenAI API key (masked)
        if (openaiKey && llmConfig.openai.api_key_masked) {
            openaiKey.value = llmConfig.openai.api_key_masked;
            openaiKey.type = 'password'; // Set as password field
        }
        
        if (openaiModel) openaiModel.value = llmConfig.openai.default_model || 'gpt-4o-mini';
        // Ollama fields removed
    }
    
    // Load advanced chatbot settings
    loadAdvancedSettings();
    
    // Provider tabs removed - only OpenAI supported
}

// selectGlobalProvider function removed - only OpenAI supported now

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
            // Ollama removed
        };
        
        // Simulate API call - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        showAlert('llmSuccess', 'Global LLM configuration saved successfully!');
        await loadLLMConfig();
        
    } catch (error) {
        showAlert('llmError', 'Failed to save configuration: ' + error.message);
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = originalText;
        }
    }
}

// Load advanced chatbot settings from user config
async function loadAdvancedSettings() {
    try {
        const response = await fetch('/api/user/chatbot-config');
        if (!response.ok) throw new Error('Failed to load config');
        
        const data = await response.json();
        const config = data.config || data; // Handle both formats
        
        // Populate advanced settings fields
        const tempField = document.getElementById('chatbotTemperature');
        const maxTokensField = document.getElementById('chatbotMaxTokens');
        const topPField = document.getElementById('chatbotTopP');
        const responseStyleField = document.getElementById('chatbotResponseStyle');
        const freqPenaltyField = document.getElementById('chatbotFrequencyPenalty');
        const presPenaltyField = document.getElementById('chatbotPresencePenalty');
        const systemInstructionsField = document.getElementById('chatbotSystemInstructions');
        
        if (tempField) tempField.value = config.temperature ?? 0.3;
        if (maxTokensField) maxTokensField.value = config.max_tokens ?? 2000;
        if (topPField) topPField.value = config.top_p ?? 1.0;
        if (responseStyleField) responseStyleField.value = config.response_style ?? 'balanced';
        if (freqPenaltyField) freqPenaltyField.value = config.frequency_penalty ?? 0.0;
        if (presPenaltyField) presPenaltyField.value = config.presence_penalty ?? 0.0;
        if (systemInstructionsField) systemInstructionsField.value = config.system_instructions ?? '';
    } catch (error) {
        // Use defaults if load fails
    }
}

// Save advanced chatbot settings
// Includes parameter validation before saving
async function saveAdvancedSettings() {
    const saveBtn = document.getElementById('saveAdvancedBtn');
    if (!saveBtn) return;
    
    const originalText = saveBtn.innerHTML;
    const originalDisabled = saveBtn.disabled;
    
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">save</span> Saving...';
    hideAlert('llmSuccess');
    hideAlert('llmError');
    
    try {
        // Get and validate parameters
        const temperature = parseFloat(document.getElementById('chatbotTemperature')?.value);
        const maxTokens = parseInt(document.getElementById('chatbotMaxTokens')?.value);
        const topP = parseFloat(document.getElementById('chatbotTopP')?.value);
        const frequencyPenalty = parseFloat(document.getElementById('chatbotFrequencyPenalty')?.value);
        const presencePenalty = parseFloat(document.getElementById('chatbotPresencePenalty')?.value);
        const responseStyle = document.getElementById('chatbotResponseStyle')?.value || 'balanced';
        const systemInstructions = document.getElementById('chatbotSystemInstructions')?.value || '';
        
        // Validate parameter ranges
        const errors = [];
        
        if (isNaN(temperature) || temperature < 0 || temperature > 2) {
            errors.push('Temperature must be between 0.0 and 2.0');
        }
        
        if (isNaN(maxTokens) || maxTokens < 50 || maxTokens > 4000) {
            errors.push('Max Tokens must be between 50 and 4000');
        }
        
        if (isNaN(topP) || topP < 0 || topP > 1) {
            errors.push('Top P must be between 0.0 and 1.0');
        }
        
        if (isNaN(frequencyPenalty) || frequencyPenalty < -2 || frequencyPenalty > 2) {
            errors.push('Frequency Penalty must be between -2.0 and 2.0');
        }
        
        if (isNaN(presencePenalty) || presencePenalty < -2 || presencePenalty > 2) {
            errors.push('Presence Penalty must be between -2.0 and 2.0');
        }
        
        // If validation errors, show them and don't save
        if (errors.length > 0) {
            const errorMsg = 'Invalid settings: ' + errors.join(', ');
            if (typeof showErrorNotification === 'function') {
                showErrorNotification(errorMsg);
            } else {
                showAlert('llmError', errorMsg);
            }
            return; // Exit - don't save
        }
        
        // All validations passed, prepare config data
        const configData = {
            temperature: temperature || 0.3,
            max_tokens: maxTokens || 2000,
            top_p: topP || 1.0,
            frequency_penalty: frequencyPenalty || 0.0,
            presence_penalty: presencePenalty || 0.0,
            response_style: responseStyle,
            system_instructions: systemInstructions
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
            throw new Error(result.error || 'Failed to save settings');
        }
        
        // Success!
        if (typeof showSuccessNotification === 'function') {
            showSuccessNotification('Advanced chatbot settings saved successfully!');
        } else {
            showAlert('llmSuccess', 'Advanced chatbot settings saved successfully!');
        }
        
        await loadAdvancedSettings();
        
    } catch (error) {
        let errorMsg = `Failed to save settings: ${error.message}`;
        
        // Handle JSON parse errors
        if (error.message.includes('JSON') || error.message.includes('Unexpected token')) {
            errorMsg = 'Failed to save settings: Server returned an invalid response. Please check your login status and try again.';
        }
        
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMsg);
        } else {
            showAlert('llmError', errorMsg);
        }
    } finally {
        if (saveBtn) {
            saveBtn.disabled = originalDisabled;
            saveBtn.innerHTML = originalText;
        }
    }
}

// Reset advanced settings to defaults
function resetAdvancedSettings() {
    if (!confirm('Reset all advanced settings to defaults? This will discard your current settings.')) {
        return;
    }
    
    document.getElementById('chatbotTemperature').value = 0.3;
    document.getElementById('chatbotMaxTokens').value = 2000;
    document.getElementById('chatbotTopP').value = 1.0;
    document.getElementById('chatbotResponseStyle').value = 'balanced';
    document.getElementById('chatbotFrequencyPenalty').value = 0.0;
    document.getElementById('chatbotPresencePenalty').value = 0.0;
    document.getElementById('chatbotSystemInstructions').value = '';
    
    showAlert('llmSuccess', 'Settings reset to defaults. Click "Save Advanced Settings" to apply.');
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
        } else if (hasApiKey) {
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
    const testBtn = document.getElementById('testLLMBtn') || (event && event.target);
    if (!testBtn) return;
    
    const originalText = testBtn.innerHTML;
    
    testBtn.disabled = true;
    testBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">hourglass_empty</span> Testing...';
    hideAlert('llmSuccess');
    hideAlert('llmError');
    
    try {
        
        // Get API key from provider settings if available
        const apiKeyField = document.getElementById('llmApiKey');
        let apiKey = null;
        if (apiKeyField && apiKeyField.value && !apiKeyField.value.includes('...')) {
            apiKey = apiKeyField.value;
        }
        
        const response = await fetch('/api/test-llm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                provider: llmConfig.effective_provider || 'openai',
                model: llmConfig.effective_model || 'gpt-4o-mini',
                api_key: apiKey  // Send API key if provided
            })
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Server returned non-JSON response. Status: ${response.status}. Please check if you're logged in.`);
        }
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            const message = `Connection successful! Model: ${result.model}${result.response_time ? `, Response time: ${result.response_time}ms` : ''}`;
            
            // Show floating notification
            if (typeof showSuccessNotification !== 'undefined') {
                showSuccessNotification(message);
            } else {
                showAlert('llmSuccess', message);
                setTimeout(() => hideAlert('llmSuccess'), 5000);
            }
        } else {
            const errorMsg = `Connection failed: ${result.error || result.message || 'Unknown error'}`;
            
            // Show floating notification
            if (typeof showErrorNotification !== 'undefined') {
                showErrorNotification(errorMsg);
            } else {
                showAlert('llmError', errorMsg);
            }
        }
        
    } catch (error) {
        let errorMsg = `Connection test failed: ${error.message}`;
        
        // Handle JSON parse errors
        if (error.message.includes('JSON') || error.message.includes('Unexpected token')) {
            errorMsg = 'Connection test failed: Server returned an invalid response. Please check your login status and try again.';
        }
        
        
        // Show floating notification
        if (typeof showErrorNotification !== 'undefined') {
            showErrorNotification(errorMsg);
        } else {
            showAlert('llmError', errorMsg);
        }
    } finally {
        testBtn.disabled = false;
        testBtn.innerHTML = originalText;
    }
}

// Alias for backward compatibility
function testLLM() {
    testLLMConnection();
}

