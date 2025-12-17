// ===========================
// CORTEX AI DASHBOARD - PROMPT EDITOR
// Prompt Management & Editing
// ===========================

let currentPresetId = null;

// Load and display prompt presets
async function loadPresets() {
    try {
        const response = await fetch('/api/prompt-presets');
        if (!response.ok) {
            throw new Error('Failed to load presets');
        }
        
        const data = await response.json();
        const presets = data.presets || {};
        const presetGrid = document.getElementById('presetGrid');
        
        if (!presetGrid) return;
        
        presetGrid.innerHTML = '';
        
        // Render each preset as a card with radio button
        // Presets come as object with numeric keys, convert to array
        const presetsArray = Object.values(presets);
        
        // Store presets globally for later use
        globalPresets = presets;
        
        presetsArray.forEach(preset => {
            const presetId = preset.id || preset['id']; // Handle both string and numeric IDs
            const card = document.createElement('label');
            card.className = 'preset-card';
            card.dataset.presetId = presetId;
            
            card.innerHTML = `
                <input type="radio" name="preset-select" value="${presetId}" class="preset-radio" id="preset-${presetId}">
                <div class="preset-card-content">
                    <span class="material-icons-round preset-card-icon">${preset.icon}</span>
                    <div class="preset-card-name">${preset.name}</div>
                    <div class="preset-card-description">${preset.description}</div>
                </div>
            `;
            
            // Add change handler for radio button
            const radio = card.querySelector('.preset-radio');
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    applyPreset(presetId, presets);
                }
            });
            
            presetGrid.appendChild(card);
        });
    } catch (error) {
    }
}

// Apply a preset to the prompt editor (does NOT save - only updates UI)
function applyPreset(presetId, presets) {
    // Handle both string and numeric IDs
    const preset = presets[presetId] || presets[String(presetId)] || Object.values(presets).find(p => p.id == presetId);
    if (!preset) return;
    
    const promptEditor = document.getElementById('promptEditor');
    
    if (!promptEditor) return;
    
    // Keep {bot_name} placeholder in the prompt - don't replace it
    // It will be replaced at runtime when the prompt is used
    promptEditor.value = preset.prompt;
    
    // Update currentPresetId but DON'T save yet - user must click "Save Prompt"
    currentPresetId = presetId;
    
    // Update radio button state
    document.querySelectorAll('.preset-radio').forEach(radio => {
        radio.checked = false;
    });
    
    const selectedRadio = document.getElementById(`preset-${presetId}`);
    if (selectedRadio) {
        selectedRadio.checked = true;
        const selectedCard = selectedRadio.closest('.preset-card');
        if (selectedCard) {
            selectedCard.classList.add('active');
        }
    }
    
    // Remove active class from other cards
    document.querySelectorAll('.preset-card').forEach(card => {
        if (card.dataset.presetId !== presetId) {
            card.classList.remove('active');
        }
    });
    
    currentPresetId = presetId;
    
    // Show success message
    showAlert('promptSuccess', `"${preset.name}" preset applied! You can now customize it.`);
    hideAlert('promptError');
    
    // Scroll to prompt editor
    promptEditor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Store presets globally (for reference, but we keep {bot_name} placeholder)
let globalPresets = {};
let savedPrompt = null; // Store user's saved prompt for reset functionality

async function loadPrompt() {
    try {
        // Load user's chatbot config from API
        const config = (typeof getChatbotConfig === 'function')
            ? await getChatbotConfig()
            : await (await fetch('/api/user/chatbot-config')).json().then(d => d.config || d);
        
        // Load chatbot name
        const nameInput = document.getElementById('chatbotName');
        if (nameInput) {
            nameInput.value = config.bot_name || 'Cortex';
        }
        
        // Load welcome message
        const welcomeMessageInput = document.getElementById('welcomeMessage');
        if (welcomeMessageInput) {
            welcomeMessageInput.value = config.welcome_message || '';
        }
        
        const botName = config.bot_name || 'Cortex';
        
        // Normalize prompt text for display (replace Cortex/{bot_name} with actual bot name)
        const promptEditor = document.getElementById('promptEditor');
        if (promptEditor) {
            let displayPrompt = config.prompt || '';
            if (displayPrompt) {
                displayPrompt = displayPrompt.replace(/{bot_name}/g, botName);
                displayPrompt = displayPrompt.replace(/\bCortex's\b/g, `${botName}'s`);
                displayPrompt = displayPrompt.replace(/\bCortex\b/g, botName);
                promptEditor.value = displayPrompt;
            }
        }
        
        // Load presets first (needed to select default)
        await loadPresets();
        
        // Wait a bit for DOM to update after presets are loaded
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Get user's saved preset_id or default to Virtual Assistant
        // Handle both string and number IDs
        let presetIdToSelect = config.prompt_preset_id;
        if (presetIdToSelect !== null && presetIdToSelect !== undefined) {
            // Convert to string for comparison (preset IDs are stored as strings in HTML)
            presetIdToSelect = String(presetIdToSelect);
        }
        
        // If no preset_id saved, find Virtual Assistant preset (default for new users)
        if (!presetIdToSelect) {
            const vaPreset = Object.values(globalPresets).find(p => 
                p.name && p.name.toLowerCase().includes('virtual assistant')
            );
            if (vaPreset) {
                presetIdToSelect = vaPreset.id;
            } else {
                // Fallback: use first preset
                const firstPreset = Object.values(globalPresets)[0];
                if (firstPreset) {
                    presetIdToSelect = firstPreset.id;
                }
            }
        }
        
        // Select the preset radio button (user's saved preset, or Virtual Assistant if new)
        if (presetIdToSelect) {
            // Try multiple times in case DOM isn't ready yet
            let attempts = 0;
            const maxAttempts = 10;
            const selectPreset = () => {
                // Try both string and number ID formats
                let radio = document.getElementById(`preset-${presetIdToSelect}`);
                if (!radio) {
                    // Try with numeric ID
                    const numericId = parseInt(presetIdToSelect);
                    if (!isNaN(numericId)) {
                        radio = document.getElementById(`preset-${numericId}`);
                    }
                }
                
                if (radio) {
                    radio.checked = true;
                    const card = radio.closest('.preset-card');
                    if (card) {
                        card.classList.add('active');
                    }
                    currentPresetId = presetIdToSelect;
                    return true;
                }
                return false;
            };
            
            while (!selectPreset() && attempts < maxAttempts) {
                attempts++;
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            if (attempts >= maxAttempts) {
            }
        }
        
        // Load prompt (user's modified version, or preset template if new)
        const editor = document.getElementById('promptEditor');
        if (editor) {
            if (config.prompt) {
                // User has a saved prompt (their modified version)
                editor.value = config.prompt;
                savedPrompt = config.prompt; // Store for reset functionality
            } else if (presetIdToSelect) {
                // Try to find preset by string or number ID
                const preset = globalPresets[presetIdToSelect] || 
                              globalPresets[String(presetIdToSelect)] || 
                              Object.values(globalPresets).find(p => p.id == presetIdToSelect);
                
                if (preset) {
                    // No saved prompt, load the preset template
                    editor.value = preset.prompt;
                    savedPrompt = null; // No saved version yet
                } else {
                    editor.value = getDefaultPrompt(config.bot_name || 'Cortex');
                    savedPrompt = null;
                }
            } else {
                // Fallback to default prompt
                editor.value = getDefaultPrompt(config.bot_name || 'Cortex');
                savedPrompt = null;
            }
        }
    } catch (error) {
        // Fallback to default
        const nameInput = document.getElementById('chatbotName');
        const editor = document.getElementById('promptEditor');
        if (nameInput) nameInput.value = 'Cortex';
        if (editor) editor.value = getDefaultPrompt('Cortex');
    }
}

function getDefaultPrompt(botName) {
    return `You are ${botName}, an intelligent AI assistant.

Your job is to help users with their questions. Always be polite, helpful, and conversational.

INSTRUCTIONS:
- Vary your greetings and responses to avoid sounding repetitive or robotic.
- Reference the user's specific question in your answer.
- Use ONLY the information provided in the "Relevant Info" section below.
- If you don't know the answer or the information isn't available, respond with a polite fallback.
- Only ask follow-up questions if they make sense and feel natural.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- Keep your tone friendly and concise.
- Always finish with a relevant follow-up or offer to help further.

Relevant Info:
{context}

User Question: {question}

${botName}'s Response:`;
}

async function savePrompt() {
    const promptEditor = document.getElementById('promptEditor');
    const nameInput = document.getElementById('chatbotName');
    const savePromptBtn = document.getElementById('savePromptBtn');
    const promptLoading = document.getElementById('promptLoading');
    
    if (!promptEditor || !savePromptBtn) return;
    
    const prompt = promptEditor.value.trim();
    const botName = nameInput ? nameInput.value.trim() : 'Cortex';
    
    if (!prompt) {
        const errorMessage = 'Prompt cannot be empty';
        showAlert('promptError', errorMessage);
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 4000);
        }
        return;
    }
    
    if (!botName) {
        const errorMessage = 'Chatbot name cannot be empty';
        showAlert('promptError', errorMessage);
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 4000);
        }
        return;
    }
    
    hideAlert('promptSuccess');
    hideAlert('promptError');
    
    savePromptBtn.disabled = true;
    if (promptLoading) promptLoading.style.display = 'block';
    
    try {
        // Get welcome message
        const welcomeMessageInput = document.getElementById('welcomeMessage');
        const welcomeMessage = welcomeMessageInput ? welcomeMessageInput.value.trim() : '';
        
        // Save both prompt and the preset_id it came from (user-specific)
        const saveData = {
            bot_name: botName,
            prompt: prompt,
            prompt_preset_id: currentPresetId || null,  // Save which preset user is using
            welcome_message: welcomeMessage  // Always send, even if empty (to clear it)
        };
        
        const response = await fetch('/api/user/chatbot-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(saveData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save config');
        }
        
        const result = await response.json();
        const message = result.message || 'Configuration saved successfully';
        showAlert('promptSuccess', message);
        setTimeout(() => hideAlert('promptSuccess'), 3000);
        // Show toast notification
        if (typeof showSuccessNotification === 'function') {
            showSuccessNotification(message, 5000);
        }
        
        // Update saved prompt after successful save
        savedPrompt = prompt;
        
    } catch (error) {
        const errorMessage = `Failed to save: ${error.message}`;
        showAlert('promptError', errorMessage);
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        }
    }
    
    savePromptBtn.disabled = false;
    if (promptLoading) promptLoading.style.display = 'none';
}

function resetPrompt() {
    // Show confirmation popup
    const confirmMessage = 'Are you sure you want to reset the prompt?\n\n' +
        'This will restore the original preset template and discard any unsaved changes.';
    
    if (!confirm(confirmMessage)) {
        return; // User cancelled
    }
    
    // Reset to the original preset template (not user's saved modified version)
    const editor = document.getElementById('promptEditor');
    if (!editor) return;
    
    if (currentPresetId && globalPresets[currentPresetId]) {
        // Reset to original preset template
        const preset = globalPresets[currentPresetId];
        editor.value = preset.prompt;
        const message = 'Prompt reset to original preset template';
        showAlert('promptSuccess', message);
        setTimeout(() => hideAlert('promptSuccess'), 3000);
        // Show toast notification
        if (typeof showSuccessNotification === 'function') {
            showSuccessNotification(message, 5000);
        }
    } else {
        // Fallback: if no preset selected, use default prompt
        const nameInput = document.getElementById('chatbotName');
        const botName = nameInput ? nameInput.value.trim() || 'Cortex' : 'Cortex';
        const defaultPrompt = getDefaultPrompt(botName);
        editor.value = defaultPrompt;
        const message = 'Prompt reset to default';
        showAlert('promptSuccess', message);
        setTimeout(() => hideAlert('promptSuccess'), 3000);
        // Show toast notification
        if (typeof showSuccessNotification === 'function') {
            showSuccessNotification(message, 5000);
        }
    }
}

// ===========================
// FILE UPLOAD & CATEGORY MANAGEMENT
// ===========================

function setupCategoryTabs() {
    const categoryTabs = document.querySelectorAll('.category-tab');
    categoryTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const categoryId = this.dataset.category;
            selectCategory(categoryId, this);
        });
    });
    
    // Select first category by default
    if (categoryTabs.length > 0) {
        selectCategory(categoryTabs[0].dataset.category, categoryTabs[0]);
    }
}

function selectCategory(categoryId, element) {
    selectedCategory = categoryId;
    
    // Update active tab
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    element?.classList.add('active');
    
}

function setupFileUpload() {
    const fileUpload = document.getElementById('fileUpload');
    const fileInput = document.getElementById('fileInput');

    if (!fileUpload || !fileInput) return;

    // Click to browse
    fileUpload.addEventListener('click', () => fileInput.click());

    // Drag and drop
    fileUpload.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUpload.classList.add('dragover');
    });

    fileUpload.addEventListener('dragleave', () => {
        fileUpload.classList.remove('dragover');
    });

    fileUpload.addEventListener('drop', async (e) => {
        e.preventDefault();
        fileUpload.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        await handleFileUpload(files);
    });

    // File input change
    fileInput.addEventListener('change', async (e) => {
        const files = Array.from(e.target.files);
        await handleFileUpload(files);
    });
}

async function handleFileUpload(files) {
    
    const uploadBtn = document.getElementById('uploadBtn');
    const progressDiv = document.getElementById('uploadProgress');
    const progressBar = progressDiv?.querySelector('.progress-bar');
    
    if (!files.length) {
        return;
    }
    
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Uploading...';
    }
    
    if (progressDiv) progressDiv.style.display = 'block';
    
    // Upload files one by one
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        const formData = new FormData();
        formData.append('file', file);  // Changed from 'files' to 'file'
        formData.append('website_id', currentWebsiteId || 'default');
        formData.append('category', selectedCategory || 'company_details');
        
        try {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && progressBar) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressBar.style.width = percentComplete + '%';
                    progressBar.textContent = Math.round(percentComplete) + '%';
                }
            });
            
            xhr.addEventListener('load', () => {
                
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    
                    // Show processing message (use uploadSuccess for Knowledge Management tab)
                    showAlert('uploadSuccess', `Processing ${file.name}... Please wait.`);
                    
                    // Wait 2 seconds for file to be ingested into vectorstore
                    setTimeout(async () => {
                        showAlert('uploadSuccess', `Successfully uploaded: ${file.name}`);
                        // Reload stats and file list to show the new file
                        if (typeof loadStats === 'function') {
                            await loadStats();
                        }
                        if (typeof refreshFileList === 'function') {
                            await refreshFileList();
                        }
                    }, 2000);
                } else {
                    const error = JSON.parse(xhr.responseText);
                    showAlert('uploadError', `Upload failed: ${error.error || xhr.statusText}`);
                }
            });
            
            xhr.addEventListener('error', () => {
                showAlert('uploadError', `Upload failed: Network error for ${file.name}`);
            });
            
            xhr.open('POST', '/api/upload');
            xhr.send(formData);
            
            // Wait for upload to complete
            await new Promise((resolve) => {
                xhr.addEventListener('loadend', resolve);
            });
            
        } catch (error) {
            showAlert('promptError', `Upload failed: ${error.message}`);
        }
    }
    
    // Reset UI
    if (uploadBtn) {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload Files';
    }
    if (progressDiv) progressDiv.style.display = 'none';
    if (progressBar) {
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
    }
    
    // Clear file input
    const fileInput = document.getElementById('fileInput');
    if (fileInput) fileInput.value = '';
}

