// Dashboard Knowledge Management - Prompt and Stats

// ====================================
// KNOWLEDGE MANAGEMENT FUNCTIONS
// ====================================
async function initializeKnowledgeManagement() {
    try {
        await loadPrompt();
        await loadKnowledgeStats();
        setupKnowledgeEventListeners();
    } catch (error) {
        console.error('Failed to initialize knowledge management:', error);
    }
}

async function loadPrompt() {
    try {
        const response = await fetch('/api/prompt');
        const result = await response.json();
        const editor = document.getElementById('promptEditor');
        if (editor) {
            editor.value = result.prompt || '';
        }
    } catch (error) {
        console.error('Failed to load prompt:', error);
    }
}

async function loadKnowledgeStats() {
    try {
        const response = await fetch('/api/knowledge-stats-detailed');
        const stats = await response.json();
        
        const vectorCount = document.getElementById('vectorCount');
        const fileCount = document.getElementById('fileCount');
        const chatLogCount = document.getElementById('chatLogCount');
        const userCount = document.getElementById('userCount');
        const backupCount = document.getElementById('backupCount');
        
        if (vectorCount) vectorCount.textContent = stats.vector_documents || 0;
        if (fileCount) fileCount.textContent = (stats.files && stats.files.total_count) ? stats.files.total_count : 0;
        if (chatLogCount) chatLogCount.textContent = (stats.database && stats.database.chat_logs) ? stats.database.chat_logs : 0;
        if (userCount) userCount.textContent = (stats.database && stats.database.users) ? stats.database.users : 0;
        if (backupCount) backupCount.textContent = stats.backups || 0;
    } catch (error) {
        console.error('Failed to load knowledge stats:', error);
    }
}

function setupKnowledgeEventListeners() {
    // URL input enter key
    const urlInput = document.getElementById('urlInput');
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                if (typeof crawlUrl === 'function') {
                    crawlUrl();
                }
            }
        });
    }
}

async function savePrompt() {
    const promptEditor = document.getElementById('promptEditor');
    const savePromptBtn = document.getElementById('savePromptBtn');
    const promptLoading = document.getElementById('promptLoading');
    const promptSuccess = document.getElementById('promptSuccess');
    const promptError = document.getElementById('promptError');
    
    if (!promptEditor) return;
    
    const prompt = promptEditor.value.trim();
    
    if (!prompt) {
        if (promptError) {
            promptError.textContent = 'Prompt cannot be empty';
            promptError.style.display = 'block';
        }
        return;
    }
    
    if (promptSuccess) promptSuccess.style.display = 'none';
    if (promptError) promptError.style.display = 'none';
    
    if (savePromptBtn) savePromptBtn.disabled = true;
    if (promptLoading) promptLoading.style.display = 'block';
    
    try {
        const response = await fetch('/api/prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            if (promptSuccess) {
                promptSuccess.textContent = result.message;
                promptSuccess.style.display = 'block';
            }
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        if (promptError) {
            promptError.textContent = 'Failed to save prompt: ' + error.message;
            promptError.style.display = 'block';
        }
    }
    
    if (savePromptBtn) savePromptBtn.disabled = false;
    if (promptLoading) promptLoading.style.display = 'none';
}

function resetPrompt() {
    const defaultPrompt = 'You are Bob, a real human virtual assistant for SourceSelect.ca.\n\n' +
        'Your job is to help users with their questions about SourceSelect.ca and its services. Always be polite, helpful, and conversational—just like a friendly and attentive human agent.\n\n' +
        'INSTRUCTIONS:\n' +
        '- Vary your greetings and responses to avoid sounding repetitive or robotic.\n' +
        '- Reference the user\'s specific question in your answer.\n' +
        '- Use ONLY the information provided in the "Relevant Info" section below.\n' +
        '- If you don\'t know the answer or the information isn\'t available, respond with a polite and varied fallback such as:\n' +
        '  "That\'s a great question! I don\'t have the details on that right now, but I can help connect you to the right person."\n' +
        '  or\n' +
        '  "I\'m not sure about that, but I can help you get in touch with someone who knows more!"\n' +
        '- Only ask follow-up questions if they make sense and feel natural.\n' +
        '- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).\n' +
        '- Keep your tone friendly and concise.\n' +
        '- Always finish with a relevant, human-sounding follow-up or offer to help further.\n\n' +
        'Relevant Info:\n' +
        '{context}\n\n' +
        'User Question: {question}\n\n' +
        'Bob\'s Response:';
    
    const promptEditor = document.getElementById('promptEditor');
    if (promptEditor) {
        promptEditor.value = defaultPrompt;
    }
}

function testPrompt() {
    window.open('/', '_blank');
}

