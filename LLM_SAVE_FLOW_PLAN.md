# LLM Provider Save Flow Improvement Plan

## Current Problem
1. "Save Provider Settings" saves configuration without testing connection
2. Invalid configurations (e.g., Anthropic without API key) are saved
3. System falls back to OpenAI, but overview still shows wrong provider
4. No validation before save

## Desired Flow

### User clicks "Save Provider Settings"
1. **Step 1: Test Connection**
   - Button shows: "Checking connection..." with hourglass icon
   - Call test connection API with current form values
   - If test fails:
     - Show error toast with user-friendly message
     - Restore button to "Save Provider Settings"
     - **DO NOT SAVE** - Exit function
   - If test succeeds:
     - Continue to Step 2

2. **Step 2: Save Configuration**
   - Button shows: "Saving..." with save icon
   - Save configuration to backend
   - If save fails:
     - Show error toast: "Unable to save settings: [error]"
     - Restore button
   - If save succeeds:
     - Show success toast: "LLM provider settings saved successfully!"
     - Reload configuration to update UI
     - Update overview LLM status
     - Restore button

## Implementation Plan

### 1. Extract Test Connection Logic
**File:** `static/v2/js/dashboard-llm-provider.js`

Create a reusable function that:
- Takes provider, model, apiKey as parameters
- Returns `{ success: boolean, error?: string, result?: object }`
- Does NOT update UI (no button state changes, no toasts)
- Only performs the test and returns result

```javascript
async function testLLMConnectionSilent(provider, model, apiKey) {
    // Returns { success: true/false, error?: string, result?: object }
    // No UI updates, just pure test logic
}
```

### 2. Modify saveLLMProviderConfig()
**File:** `static/v2/js/dashboard-llm-provider.js`

New flow:
```javascript
async function saveLLMProviderConfig() {
    // 1. Get form values
    // 2. Update button: "Checking connection..."
    // 3. Call testLLMConnectionSilent()
    // 4. If test fails:
    //    - Show error toast
    //    - Restore button
    //    - Return (don't save)
    // 5. If test succeeds:
    //    - Update button: "Saving..."
    //    - Save configuration
    //    - Show success toast
    //    - Reload config
    //    - Restore button
}
```

### 3. Button State Management
**States:**
- Default: "Save Provider Settings" (save icon)
- Testing: "Checking connection..." (hourglass icon)
- Saving: "Saving..." (save icon)
- Error: Restore to default
- Success: Restore to default

### 4. Error Messages
**Test Failure:**
- Use the same user-friendly messages from testLLMProvider()
- Examples:
  - "Anthropic API key required. Please provide your API key..."
  - "Invalid Anthropic API key. Please check your API key..."
  - "Rate limit exceeded for claude. Please wait..."

**Save Failure:**
- "Unable to save settings: [error message]"
- "Failed to save settings: Server returned an invalid response..."

### 5. Overview Update
**File:** `static/v2/js/dashboard-llm.js`

After successful save:
- Call `loadLLMProviderConfig()` (already does this)
- This should trigger `updateLLMStatus()` which updates overview
- Verify overview shows correct provider/model

### 6. Code Structure

```javascript
// Extract test logic (no UI updates)
async function testLLMConnectionSilent(provider, model, apiKey) {
    try {
        // Prepare API key
        let apiKeyToSend = null;
        if (apiKey && !apiKey.includes('...') && apiKey.length >= 10) {
            apiKeyToSend = apiKey;
        }
        
        // Call test API
        const response = await fetch('/api/test-llm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ provider, model, api_key: apiKeyToSend })
        });
        
        // Check response
        if (!response.headers.get('content-type')?.includes('application/json')) {
            return { success: false, error: 'Server returned invalid response' };
        }
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            return { success: true, result };
        } else {
            return { success: false, error: result.error || 'Connection test failed' };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Modified save function
async function saveLLMProviderConfig() {
    const saveBtn = document.getElementById('saveLLMProviderBtn');
    if (!saveBtn) return;
    
    const originalText = saveBtn.innerHTML;
    const originalDisabled = saveBtn.disabled;
    
    try {
        // Get form values
        const provider = document.getElementById('llmProvider')?.value || 'openai';
        const model = document.getElementById('llmModel')?.value || LLM_PROVIDERS[provider]?.defaultModel;
        const apiKey = document.getElementById('llmApiKey')?.value || '';
        
        if (!model) {
            throw new Error('No model selected. Please select a model first.');
        }
        
        // STEP 1: Test Connection
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">hourglass_empty</span> Checking connection...';
        hideAlert('llmSuccess');
        hideAlert('llmError');
        
        const testResult = await testLLMConnectionSilent(provider, model, apiKey);
        
        if (!testResult.success) {
            // Test failed - show error and don't save
            const errorMsg = testResult.error || 'Connection test failed';
            if (typeof showErrorNotification === 'function') {
                showErrorNotification(errorMsg);
            } else {
                showAlert('llmError', errorMsg);
            }
            return; // Exit - don't save
        }
        
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
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(configData)
        });
        
        // Check response
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
        if (typeof showSuccessNotification === 'function') {
            showSuccessNotification('LLM provider settings saved successfully!');
        } else {
            showAlert('llmSuccess', 'LLM provider settings saved successfully!');
        }
        
        // Reload configuration to update UI and overview
        await loadLLMProviderConfig();
        
        // Trigger overview update if needed
        if (typeof updateLLMStatus === 'function') {
            updateLLMStatus();
        }
        
    } catch (error) {
        console.error('Failed to save LLM provider config:', error);
        let errorMsg = `Unable to save settings: ${error.message}`;
        
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
```

## Testing Checklist

- [ ] Test with OpenAI (no API key - should use system default)
- [ ] Test with OpenAI (with API key)
- [ ] Test with Anthropic (no API key - should fail test, not save)
- [ ] Test with Anthropic (invalid API key - should fail test, not save)
- [ ] Test with Anthropic (valid API key - should test, then save)
- [ ] Test with Gemini (no API key - should fail test, not save)
- [ ] Test with Groq (no API key - should fail test, not save)
- [ ] Test with DeepSeek (no API key - should fail test, not save)
- [ ] Test with Together AI (no API key - should fail test, not save)
- [ ] Verify overview updates correctly after successful save
- [ ] Verify button states change correctly during process
- [ ] Verify error toasts show user-friendly messages
- [ ] Verify success toast shows after successful save

## Files to Modify

1. `static/v2/js/dashboard-llm-provider.js`
   - Add `testLLMConnectionSilent()` function
   - Modify `saveLLMProviderConfig()` function

2. No changes needed to:
   - `dashboard-llm.js` (already handles overview updates via `loadLLMProviderConfig()`)
   - `dashboard-overview.js` (gets data from config)
   - Backend API (already works correctly)

## Benefits

1. ✅ Prevents saving invalid configurations
2. ✅ User gets immediate feedback on connection issues
3. ✅ Overview always shows correct LLM status
4. ✅ Better UX with clear button states
5. ✅ Works for all providers consistently
6. ✅ No fallback confusion - only valid configs are saved

