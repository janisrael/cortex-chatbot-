// ===========================
// CORTEX AI DASHBOARD - PROMPT EDITOR
// Prompt Management & Editing
// ===========================

async function loadPrompt() {
    try {
        // Load user's chatbot config from API
        const response = await fetch('/api/user/chatbot-config');
        if (!response.ok) {
            throw new Error('Failed to load config');
        }
        
        const config = await response.json();
        
        // Load chatbot name
        const nameInput = document.getElementById('chatbotName');
        if (nameInput) {
            nameInput.value = config.bot_name || 'Cortex';
        }
        
        // Load prompt
        const editor = document.getElementById('promptEditor');
        if (editor) {
            editor.value = config.prompt || getDefaultPrompt(config.bot_name || 'Cortex');
        }
    } catch (error) {
        console.error('Failed to load prompt:', error);
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
        showAlert('promptError', 'Prompt cannot be empty');
        return;
    }
    
    if (!botName) {
        showAlert('promptError', 'Chatbot name cannot be empty');
        return;
    }
    
    hideAlert('promptSuccess');
    hideAlert('promptError');
    
    savePromptBtn.disabled = true;
    if (promptLoading) promptLoading.style.display = 'block';
    
    try {
        const response = await fetch('/api/user/chatbot-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                bot_name: botName,
                prompt: prompt
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save config');
        }
        
        const result = await response.json();
        showAlert('promptSuccess', result.message || 'Configuration saved successfully');
        setTimeout(() => hideAlert('promptSuccess'), 3000);
        
    } catch (error) {
        showAlert('promptError', `Failed to save: ${error.message}`);
    }
    
    savePromptBtn.disabled = false;
    if (promptLoading) promptLoading.style.display = 'none';
}

function resetPrompt() {
    const nameInput = document.getElementById('chatbotName');
    const botName = nameInput ? nameInput.value.trim() || 'Cortex' : 'Cortex';
    const defaultPrompt = getDefaultPrompt(botName);

    const editor = document.getElementById('promptEditor');
    if (editor) {
        editor.value = defaultPrompt;
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
    
    console.log(`Selected category: ${categoryId}`);
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
    console.log('handleFileUpload called with', files.length, 'files');
    console.log('Current website:', currentWebsiteId);
    console.log('Selected category:', selectedCategory);
    
    const uploadBtn = document.getElementById('uploadBtn');
    const progressDiv = document.getElementById('uploadProgress');
    const progressBar = progressDiv?.querySelector('.progress-bar');
    
    if (!files.length) {
        console.log('No files to upload');
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
        console.log(`Uploading file ${i + 1}/${files.length}:`, file.name);
        
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
                console.log('Upload response status:', xhr.status);
                console.log('Upload response:', xhr.responseText);
                
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
                console.error('Upload network error');
                showAlert('uploadError', `Upload failed: Network error for ${file.name}`);
            });
            
            xhr.open('POST', '/api/upload');
            xhr.send(formData);
            
            // Wait for upload to complete
            await new Promise((resolve) => {
                xhr.addEventListener('loadend', resolve);
            });
            
        } catch (error) {
            console.error('Upload error:', error);
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

