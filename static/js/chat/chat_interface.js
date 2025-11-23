// Chat Interface JavaScript - Extracted from index.html

const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');

// Generate random user ID for session
const userId = 'user_' + Math.random().toString(36).substr(2, 9);
const userName = 'Visitor';

messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendSuggestion(message) {
    messageInput.value = message;
    sendMessage();
}

function formatMessage(text) {
    // Convert **bold** to <strong>bold</strong>
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert lines starting with "- " to proper bullet points
    text = text.replace(/^- (.+)$/gm, '<li>$1</li>');
    
    // Wrap consecutive <li> elements in <ul>
    text = text.replace(/(<li>.*<\/li>\s*)+/gs, '<ul>$&</ul>');
    
    // Ensure <br> tags are preserved
    text = text.replace(/<br><br>/g, '</p><p>');
    
    return text;
}

function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = isUser ? content : formatMessage(content);
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
    typingIndicator.style.display = 'flex';
    chatMessages.appendChild(typingIndicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTyping() {
    typingIndicator.style.display = 'none';
    if (typingIndicator.parentNode) {
        typingIndicator.parentNode.removeChild(typingIndicator);
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Disable input
    messageInput.disabled = true;
    sendBtn.disabled = true;
    
    // Add user message
    addMessage(message, true);
    messageInput.value = '';

    // Show typing indicator
    showTyping();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: userId,
                name: userName,
                website_id: 'sourceselect',
            })
        });

        const data = await response.json();
        
        // Hide typing indicator
        hideTyping();
        
        if (data.response) {
            addMessage(data.response);
        } else {
            addMessage('Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        hideTyping();
        addMessage('Sorry, I encountered a connection error. Please try again.');
        console.error('Error:', error);
    }

    // Re-enable input
    messageInput.disabled = false;
    sendBtn.disabled = false;
    messageInput.focus();
}

async function refreshChat() {
    if (confirm("Refresh conversation? (Files and AI knowledge will be preserved)")) {
        try {
            // Show loading state
            const refreshBtn = document.getElementById('refreshBtn');
            const originalText = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '⏳';
            refreshBtn.disabled = true;
            
            const response = await fetch('/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Clear the chat messages display
                const chatMessages = document.getElementById('chatMessages');
                chatMessages.innerHTML = `
                    <div class="message bot">
                        <div class="message-content">
                            👋 Hi there! I'm Bobot AI, your helpful assistant for SourceSelect.ca. How can I help you today?
                        </div>
                    </div>
                `;
                
                // Clear the input field
                document.getElementById('messageInput').value = '';
                
                // Show success message
                addMessage('✅ ' + data.message, false);
                
                console.log('Chat refreshed successfully');
            } else {
                addMessage('❌ Failed to refresh: ' + data.message, false);
            }
        } catch (error) {
            addMessage('❌ Error refreshing chat: ' + error.message, false);
            console.error('Refresh error:', error);
        } finally {
            // Restore button state
            const refreshBtn = document.getElementById('refreshBtn');
            refreshBtn.innerHTML = '🔄';
            refreshBtn.disabled = false;
        }
    }
}

function addStatusMessage(content, isSuccess = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isSuccess ? 'bot' : 'bot'}`;
    messageDiv.style.opacity = '0.8';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;
    contentDiv.style.fontStyle = 'italic';
    contentDiv.style.backgroundColor = isSuccess ? '#d4edda' : '#f8d7da';
    contentDiv.style.color = isSuccess ? '#155724' : '#721c24';
    
    messageDiv.appendChild(contentDiv);
    
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
