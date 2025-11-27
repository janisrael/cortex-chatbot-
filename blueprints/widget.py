"""Widget and demo blueprint"""
from flask import Blueprint, request, render_template, send_from_directory, jsonify, url_for
from flask_login import login_required, current_user
from services.config_service import load_user_chatbot_config
from utils.api_key import validate_api_key
from config.constants import SUGGESTED_MESSAGES
from models.chatbot_appearance import ChatbotAppearance
from urllib.parse import quote
import json
import os

widget_bp = Blueprint('widget', __name__)


def _build_widget_config(user_id):
    """Assemble widget/appearance config for a user"""
    user_config = load_user_chatbot_config(user_id)
    bot_name = user_config.get('bot_name', 'Cortex')
    website_name = bot_name
    
    primary_color = '#0891b2'
    primary_color_obj = None
    contrast_text = '#ffffff'
    short_info = 'Your friendly assistant'
    avatar = {
        'type': 'preset',
        'value': 'avatar_1',
        'fallback': 'ui-avatars',
        'src': '/static/img/avatar/avatar_1.png'
    }
    suggested = list(SUGGESTED_MESSAGES)
    
    appearance = ChatbotAppearance.get_by_user(user_id)
    if appearance:
        appearance_dict = ChatbotAppearance.to_dict(appearance)
        primary_color_obj = appearance_dict.get('primary_color')
        if isinstance(primary_color_obj, dict):
            primary_color = primary_color_obj.get('value', '#0891b2')
            contrast_text = primary_color_obj.get('contrast_text', '#ffffff')
        elif isinstance(primary_color_obj, str):
            primary_color = primary_color_obj
            primary_color_obj = None
            contrast_text = '#ffffff'
        else:
            primary_color_obj = None
        
        suggested_raw = appearance_dict.get('suggested_messages', [])
        if suggested_raw and isinstance(suggested_raw, list):
            processed = [msg.get('text', msg) if isinstance(msg, dict) else msg for msg in suggested_raw]
            suggested = processed or suggested
        
        avatar = appearance_dict.get('avatar', avatar)
        short_info = appearance_dict.get('short_info', short_info)
    
    avatar_url = None
    if avatar:
        avatar_value = avatar.get('value')
        if avatar.get('type') == 'preset' and avatar_value:
            avatar_url = url_for('static', filename=f"img/avatar/{avatar_value}.png", _external=True)
        elif avatar.get('src'):
            src_value = avatar['src']
            if src_value.startswith('http'):
                avatar_url = src_value
            else:
                avatar_url = request.host_url.rstrip('/') + src_value
    
    if not avatar_url:
        # Extract hex color from primary_color (handle gradients)
        hex_color = '0891b2'  # default
        if isinstance(primary_color, str):
            if primary_color.startswith('#'):
                hex_color = primary_color.replace('#', '')[:6] or '0891b2'
            elif 'linear-gradient' in primary_color:
                # Extract first hex color from gradient
                import re
                hex_match = re.search(r'#([0-9A-Fa-f]{6})', primary_color)
                if hex_match:
                    hex_color = hex_match.group(1)
        avatar_url = (
            f"https://ui-avatars.com/api/?name={quote(bot_name)}"
            f"&background={hex_color}&color=fff&size=64&rounded=true"
        )
    
    return {
        'bot_name': bot_name,
        'website_name': website_name,
        'primary_color': primary_color,
        'primary_color_obj': primary_color_obj,
        'contrast_text': contrast_text,
        'avatar': avatar,
        'avatar_url': avatar_url,
        'short_info': short_info,
        'suggested_messages': suggested
    }


@widget_bp.route("/demo")
@login_required
def demo_chatbox():
    """Demo page showing the floating chatbox widget with user's chatbot config"""
    try:
        user_id = current_user.id
        config = load_user_chatbot_config(user_id)
        bot_name = config.get('bot_name', 'Cortex')
        
        # Get user's API key
        from utils.api_key import get_user_api_key
        api_key = get_user_api_key(user_id)
        
        # Render the new widget preview template with user's API key
        return render_template("widget/preview.html", 
                             bot_name=bot_name,
                             api_key=api_key,
                             user=current_user)
    except Exception as e:
        print(f"Error loading demo: {e}")
        # Fallback to old demo if error
        try:
            from utils.api_key import get_user_api_key
            api_key = get_user_api_key(current_user.id)
            return render_template("widget/preview.html", 
                                 bot_name='Cortex',
                                 api_key=api_key,
                                 user=current_user)
        except:
            return send_from_directory('templates/widget', 'demo.html')


@widget_bp.route("/feedback")
@login_required
def feedback():
    """Feedback and bug report page"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template("widget/feedback.html", user=current_user)


@widget_bp.route("/widget")
def widget_multi():
    """Serve widget with user-specific configuration (1 chatbot per user) - requires API key"""
    # Get API key from query parameter
    api_key = request.args.get('api_key') or request.args.get('key')
    
    if not api_key:
        return "Error: API key is required", 400
    
    # Validate API key and get user_id
    user_id = validate_api_key(api_key)
    
    if not user_id:
        return "Error: Invalid API key", 401
    
    # Load user's config
    try:
        user_config = load_user_chatbot_config(user_id)
        bot_name = user_config.get('bot_name', 'Cortex')
        
        # Load appearance config from database
        from models.chatbot_appearance import ChatbotAppearance
        appearance = ChatbotAppearance.get_by_user(user_id)
        
        if appearance:
            appearance_dict = ChatbotAppearance.to_dict(appearance)
            # Get primary color (handle both string and object format)
            primary_color_obj = appearance_dict.get('primary_color')
            if isinstance(primary_color_obj, dict):
                primary_color = primary_color_obj.get('value', '#0891b2')
                contrast_text = primary_color_obj.get('contrast_text', '#ffffff')
            elif isinstance(primary_color_obj, str):
                primary_color = primary_color_obj
                contrast_text = '#ffffff'  # Default contrast for string colors
            else:
                primary_color = '#0891b2'
                contrast_text = '#ffffff'
            
            # Get suggested messages
            suggested = appearance_dict.get('suggested_messages', [])
            if not suggested or not isinstance(suggested, list):
                from config.constants import SUGGESTED_MESSAGES
                suggested = SUGGESTED_MESSAGES
            else:
                # Convert to list of strings if needed
                suggested = [msg.get('text', msg) if isinstance(msg, dict) else msg for msg in suggested]
            
            # Get avatar
            avatar = appearance_dict.get('avatar', {})
            short_info = appearance_dict.get('short_info', 'Your friendly assistant')
        else:
            # Defaults
            primary_color = '#0891b2'
            contrast_text = '#ffffff'
            suggested = SUGGESTED_MESSAGES if 'SUGGESTED_MESSAGES' in locals() else []
            avatar = {'type': 'preset', 'value': 'avatar_1', 'fallback': 'ui-avatars'}
            short_info = 'Your friendly assistant'
        
        website_name = bot_name  # Use bot name as website name
    except Exception as e:
        print(f"Error loading user config for widget: {e}")
        import traceback
        traceback.print_exc()
        bot_name = 'Cortex'
        primary_color = '#667eea'
        website_name = 'Website'
        from config.constants import SUGGESTED_MESSAGES
        suggested = SUGGESTED_MESSAGES
        avatar = {'type': 'preset', 'value': 'avatar_1', 'fallback': 'ui-avatars'}
        short_info = 'Your friendly assistant'
    
    # Pass user-specific config to template - use embeddable widget
    return render_template("widget/widget_embed.html", 
                         bot_name=bot_name,
                         primary_color=primary_color,
                         primary_color_obj=primary_color_obj if 'primary_color_obj' in locals() else None,
                         contrast_text=contrast_text if 'contrast_text' in locals() else '#ffffff',
                         website_name=website_name,
                         api_key=api_key,
                         suggested=suggested,
                         avatar=avatar,
                         short_info=short_info)


@widget_bp.route("/embed.js")
def serve_embed_script_multi():
    """Serve user-specific embed script (1 chatbot per user) - requires API key"""
    # Get API key from query parameter
    api_key = request.args.get('api_key') or request.args.get('key')
    
    if not api_key:
        # Return error script if no API key provided
        return """
(function() {
    console.error('Chatbot Error: API key is required. Please get your embed script from the dashboard.');
})();
""", 200, {'Content-Type': 'application/javascript'}
    
    # Validate API key and get user_id
    user_id = validate_api_key(api_key)
    
    if not user_id:
        # Return error script if API key is invalid
        return """
(function() {
    console.error('Chatbot Error: Invalid API key. Please check your embed script.');
})();
""", 200, {'Content-Type': 'application/javascript'}
    
    # Load user's config
    try:
        user_config = load_user_chatbot_config(user_id)
        bot_name = user_config.get('bot_name', 'Cortex')
        
        # Load appearance config from database
        from models.chatbot_appearance import ChatbotAppearance
        appearance = ChatbotAppearance.get_by_user(user_id)
        
        if appearance:
            appearance_dict = ChatbotAppearance.to_dict(appearance)
            # Get primary color (handle both string and object format)
            primary_color_obj = appearance_dict.get('primary_color')
            if isinstance(primary_color_obj, dict):
                primary_color = primary_color_obj.get('value', '#0891b2')
            elif isinstance(primary_color_obj, str):
                primary_color = primary_color_obj
            else:
                primary_color = '#0891b2'
            
            # Get avatar
            avatar = appearance_dict.get('avatar', {})
            short_info = appearance_dict.get('short_info', 'Your friendly assistant')
        else:
            # Defaults
            primary_color = '#0891b2'
            avatar = {'type': 'preset', 'value': 'avatar_1', 'fallback': 'ui-avatars'}
            short_info = 'Your friendly assistant'
        
        website_name = bot_name
    except Exception as e:
        print(f"Error loading user config for embed: {e}")
        import traceback
        traceback.print_exc()
        bot_name = 'Cortex'
        primary_color = '#667eea'
        website_name = 'Website'
        avatar = {'type': 'preset', 'value': 'avatar_1', 'fallback': 'ui-avatars'}
        short_info = 'Your friendly assistant'
    
    config = {
        'bot_name': bot_name,
        'primary_color': primary_color,
        'name': website_name,
        'avatar': avatar,
        'short_info': short_info
    }
    
    # Generate dynamic embed script with user-specific config
    embed_script = f"""
// Define sendSuggestion IMMEDIATELY at the top level (synchronous)
window.sendSuggestion = window.sendSuggestion || function(message) {{
    console.log('sendSuggestion called with:', message);
    
    function trySend() {{
        const inputField = document.getElementById('chatbot-input');
        const sendBtn = document.getElementById('chatbot-send-btn');
        
        if (!inputField) {{
            console.log('Input field not found, retrying in 50ms...');
            setTimeout(trySend, 50);
            return;
        }}
        
        inputField.value = message;
        console.log('Input field set to:', message);
        
        // Try to click send button
        if (sendBtn) {{
            console.log('Clicking send button');
            sendBtn.click();
        }} else {{
            console.log('Send button not found, trying Enter key');
            // Fallback: trigger Enter key
            const event = new KeyboardEvent('keypress', {{
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
                bubbles: true
            }});
            inputField.dispatchEvent(event);
        }}
    }}
    
    trySend();
}};
console.log('✅ sendSuggestion function defined globally (SYNCHRONOUS)');

(function() {{
    window.CHATBOT_CONFIG = {{
        apiBaseUrl: '{request.host_url.rstrip('/')}',
        apiKey: '{api_key}',
        botName: '{config.get('bot_name', 'Assistant')}',
        primaryColor: '{config.get('primary_color', '#667eea')}',
        avatar: {config.get('avatar', {})},
        shortInfo: '{config.get('short_info', 'Your friendly assistant')}',
        websiteName: '{config.get('name', 'Website')}'
    }};
    
    // sendSuggestion is already defined above at top level (outside IIFE)
    // It's available immediately when the script loads
    
    // Load the widget HTML
    fetch('{request.host_url.rstrip('/')}/widget?api_key={api_key}')
        .then(response => response.text())
        .then(html => {{
            const widgetContainer = document.createElement('div');
            widgetContainer.id = 'ai-chatbot-widget';
            widgetContainer.innerHTML = html;
            document.body.appendChild(widgetContainer);
            console.log('✅ Widget HTML injected');
            
            // Execute any script tags in the injected HTML
            const scripts = widgetContainer.querySelectorAll('script');
            scripts.forEach(function(oldScript) {{
                const newScript = document.createElement('script');
                Array.from(oldScript.attributes).forEach(attr => {{
                    newScript.setAttribute(attr.name, attr.value);
                }});
                newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                oldScript.parentNode.replaceChild(newScript, oldScript);
            }});
            
            console.log('✅ Scripts executed, sendSuggestion available:', typeof window.sendSuggestion);
            
            // Attach event listeners to suggested buttons using event delegation
            // This works even if buttons are added dynamically
            document.addEventListener('click', function(e) {{
                if (e.target && e.target.classList.contains('suggested-btn')) {{
                    const message = e.target.getAttribute('data-suggestion') || e.target.textContent.trim();
                    console.log('Suggested button clicked:', message);
                    if (window.sendSuggestion && typeof window.sendSuggestion === 'function') {{
                        window.sendSuggestion(message);
                    }} else {{
                        console.error('sendSuggestion not available when button clicked');
                    }}
                }}
            }});
            console.log('✅ Event delegation attached for suggested buttons');
            
            // Initialize widget after HTML is injected
            setTimeout(function() {{
                const config = window.CHATBOT_CONFIG;
                const toggleBtn = document.getElementById('chatbot-toggle-btn');
                const closeBtn = document.getElementById('chatbot-close-btn');
                const chatbotWindow = document.getElementById('chatbot-window');
                const messagesDiv = document.getElementById('chatbot-messages');
                const inputField = document.getElementById('chatbot-input');
                const sendBtn = document.getElementById('chatbot-send-btn');
                
                if (!toggleBtn || !chatbotWindow) {{
                    console.error('Chatbot elements not found');
                    return;
                }}
                
                let isOpen = false;
                
                toggleBtn.addEventListener('click', function() {{
                    isOpen = !isOpen;
                    chatbotWindow.style.display = isOpen ? 'flex' : 'none';
                }});
                
                if (closeBtn) {{
                    closeBtn.addEventListener('click', function() {{
                        isOpen = false;
                        chatbotWindow.style.display = 'none';
                    }});
                }}
                
                function addMessage(text, isBot) {{
                    if (!messagesDiv) return;
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message ' + (isBot ? 'bot' : 'user');
                    messageDiv.style.cssText = 'display: flex; flex-direction: column; gap: 8px; align-items: ' + (isBot ? 'flex-start' : 'flex-end') + '; animation: fadeIn 0.3s ease-out;';
                    
                    // Format text (convert <br> to actual breaks)
                    const formattedText = text.replace(/<br>/g, '<br>').replace(/\\n/g, '<br>');
                    
                    if (isBot) {{
                        const botName = config.botName || 'Assistant';
                        const avatarUrl = `https://ui-avatars.com/api/?name=${{encodeURIComponent(botName)}}&background=${{config.primaryColor.substring(1)}}&color=fff&size=24`;
                        messageDiv.innerHTML = `
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                                <img src="${{avatarUrl}}" alt="Bot Avatar" style="width: 24px; height: 24px; border-radius: 50%;">
                                <span style="font-size: 14px; font-weight: 500; color: #18181b;">${{botName}}</span>
                            </div>
                            <div style="max-width: min(calc(100% - 40px), 65ch); padding: 12px 16px; border-radius: 20px; font-size: 14px; line-height: 1.6; word-wrap: break-word; background: #f4f4f5; color: #27272a; border-bottom-left-radius: 6px;">${{formattedText}}</div>
                        `;
                    }} else {{
                        messageDiv.innerHTML = `
                            <div style="max-width: min(calc(100% - 40px), 65ch); padding: 12px 16px; border-radius: 20px; font-size: 14px; line-height: 1.6; word-wrap: break-word; background: ${{config.primaryColor}}; color: white; border-bottom-right-radius: 6px;">${{formattedText}}</div>
                        `;
                    }}
                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }}
                
                function showTyping() {{
                    const typingIndicator = document.getElementById('typing-indicator');
                    if (typingIndicator) {{
                        typingIndicator.style.display = 'flex';
                        messagesDiv.appendChild(typingIndicator);
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    }}
                }}
                
                function hideTyping() {{
                    const typingIndicator = document.getElementById('typing-indicator');
                    if (typingIndicator) {{
                        typingIndicator.style.display = 'none';
                        if (typingIndicator.parentNode === messagesDiv) {{
                            messagesDiv.removeChild(typingIndicator);
                        }}
                    }}
                }}
                
                async function sendMessage() {{
                    if (!inputField || !sendBtn) return;
                    const message = inputField.value.trim();
                    if (!message) return;
                    
                    addMessage(message, false);
                    inputField.value = '';
                    sendBtn.disabled = true;
                    
                    showTyping();
                    
                    try {{
                        const response = await fetch(config.apiBaseUrl + '/chat', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                message: message,
                                api_key: config.apiKey
                            }})
                        }});
                        
                        const data = await response.json();
                        hideTyping();
                        addMessage(data.response || 'Sorry, I encountered an error.', true);
                    }} catch (error) {{
                        hideTyping();
                        addMessage('Sorry, I encountered a connection error.', true);
                        console.error('Chatbot error:', error);
                    }}
                    
                    sendBtn.disabled = false;
                }}
                
                // Make sendMessage available globally
                window.chatbotSendMessage = sendMessage;
                
                // Update sendSuggestion to use local variables (better version)
                const originalSendSuggestion = window.sendSuggestion;
                window.sendSuggestion = function(message) {{
                    console.log('sendSuggestion (enhanced) called with:', message);
                    if (inputField && typeof sendMessage === 'function') {{
                        // Use local variables for better performance
                        inputField.value = message;
                        sendMessage();
                    }} else {{
                        // Fallback to original if elements not ready
                        console.log('Using fallback sendSuggestion (elements not ready)');
                        if (originalSendSuggestion) {{
                            originalSendSuggestion(message);
                        }}
                    }}
                }};
                console.log('✅ sendSuggestion enhanced with local variables');
                
                // Event delegation is already set up above, but we can also attach direct listeners
                // as a backup (event delegation should handle it, but this ensures it works)
                const widgetContainer = document.getElementById('ai-chatbot-widget');
                const suggestedButtons = widgetContainer ? widgetContainer.querySelectorAll('.suggested-btn') : document.querySelectorAll('.suggested-btn');
                console.log('Found suggested buttons:', suggestedButtons.length);
                
                suggestedButtons.forEach(function(btn) {{
                    btn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        e.stopPropagation();
                        const message = btn.getAttribute('data-suggestion') || btn.textContent.trim();
                        console.log('Direct listener: Button clicked, message:', message);
                        if (message && window.sendSuggestion) {{
                            window.sendSuggestion(message);
                        }}
                    }});
                }});
                console.log('✅ Direct event listeners attached to suggested buttons');
                
                if (sendBtn) {{
                    sendBtn.addEventListener('click', sendMessage);
                }}
                if (inputField) {{
                    inputField.addEventListener('keypress', function(e) {{
                        if (e.key === 'Enter') sendMessage();
                    }});
                }}
            }}, 100);
        }})
        .catch(error => {{
            console.error('Error loading chatbot widget:', error);
        }});
}})();
"""
    
    return embed_script, 200, {'Content-Type': 'application/javascript'}

