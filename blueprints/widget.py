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
            welcome_message = appearance_dict.get('welcome_message')
        else:
            # Defaults
            primary_color = '#0891b2'
            contrast_text = '#ffffff'
            suggested = SUGGESTED_MESSAGES if 'SUGGESTED_MESSAGES' in locals() else []
            avatar = {'type': 'preset', 'value': 'avatar_1', 'fallback': 'ui-avatars'}
            short_info = 'Your friendly assistant'
            welcome_message = None
        
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
        welcome_message = None
    
    # Default welcome message if not set
    if 'welcome_message' not in locals() or not welcome_message:
        welcome_message = f"Hi there! I'm {bot_name}, your helpful assistant. How can I help you today?"
    
    # Ensure welcome_message is always a string (not None)
    if not welcome_message:
        welcome_message = f"Hi there! I'm {bot_name}, your helpful assistant. How can I help you today?"
    
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
                         short_info=short_info,
                         welcome_message=welcome_message)


@widget_bp.route("/embed.js")
def serve_embed_script_multi():
    """Serve user-specific embed script (1 chatbot per user) - requires API key - Uses iframe approach"""
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
    
    # Get the base URL from the script's src (where embed.js is loaded from)
    base_url = request.host_url.rstrip('/')
    
    # Load user's config for widget config
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
    
    # Generate iframe-based embed script (plug-and-play)
    embed_script = f"""
(function () {{
  "use strict";

  // Get the base URL from the script's src (where embed.js is loaded from)
  function getScriptBaseUrl() {{
    const scripts = document.getElementsByTagName('script');
    for (let script of scripts) {{
      if (script.src && script.src.includes('embed.js')) {{
        try {{
          const url = new URL(script.src);
          return url.origin;
        }} catch (e) {{
          return window.location.origin;
        }}
      }}
    }}
    return window.location.origin;
  }}

  const WIDGET_CONFIG = {{
    apiBaseUrl: getScriptBaseUrl(),
    widgetUrl: "/widget",
    triggerButtonText: "💬",
    position: "bottom-right",
    primaryColor: "{primary_color}",
    zIndex: 999999,
  }};

  if (window.BobotWidget) {{
    console.warn("Bobot Widget already loaded");
    return;
  }}

  class BobotWidget {{
    constructor() {{
      this.isOpen = false;
      this.widget = null;
      this.triggerButton = null;
      this.iframe = null;
      this.config = {{}};
      this.apiKey = "{api_key}";
      this.initialize();
    }}

    initialize() {{
      this.createStyles();
      this.createTriggerButton();
      this.createWidget();
      this.attachEventListeners();
    }}

    createStyles() {{
      const styles = `
        .bobot-widget-trigger {{
          position: fixed;
          bottom: 24px;
          right: 24px;
          background: transparent !important;
          color: white;
          border: none;
          width: 60px;
          height: 60px;
          font-size: 24px;
          cursor: pointer;
          z-index: ${{WIDGET_CONFIG.zIndex}};
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
        }}

        .bobot-widget-trigger::before {{
          content: '';
          position: absolute;
          inset: -6px;
          border-radius: 50%;
          background: conic-gradient(from 0deg, #667eea, #764ba2, #f093fb, #4facfe, #00f2fe, #667eea);
          opacity: 0;
          transition: opacity 0.3s ease;
          animation: gradientRotate 3s linear infinite;
          z-index: -1;
        }}

        .bobot-widget-trigger::after {{
          content: '';
          position: absolute;
          inset: -3px;
          border-radius: 50%;
          z-index: -1;
          background: white;
        }}

        @keyframes gradientRotate {{
          from {{ transform: rotate(0deg); }}
          to {{ transform: rotate(360deg); }}
        }}

        .bobot-widget-trigger img {{
          width: 100%;
          object-fit: cover;
          background: transparent;
          position: relative;
          z-index: 1;
        }}

        .bobot-widget-trigger:hover {{
          transform: translateY(-2px) scale(1.05);
        }}

        .bobot-widget-trigger:hover::before {{
          opacity: 1;
        }}

        .bobot-widget-container {{
          position: fixed;
          bottom: 100px;
          right: 24px;
          width: 380px;
          height: 600px;
          z-index: ${{WIDGET_CONFIG.zIndex + 1}};
          transform: scale(0.95) translateY(20px);
          opacity: 0;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          transform-origin: bottom right;
          pointer-events: none;
        }}

        .bobot-widget-container.open {{
          transform: scale(1) translateY(0);
          opacity: 1;
          pointer-events: all;
        }}

        .bobot-widget-iframe {{
          width: 100%;
          height: 100%;
          border: none;
          border-radius: 20px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12), 0 8px 24px rgba(0, 0, 0, 0.08);
          background: white;
        }}

        .bobot-widget-close {{
          position: absolute;
          top: -8px;
          right: -8px;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 50%;
          width: 28px;
          height: 28px;
          font-size: 14px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
          z-index: ${{WIDGET_CONFIG.zIndex + 2}};
          transition: all 0.2s;
        }}

        .bobot-widget-close:hover {{
          background: #dc2626;
          transform: scale(1.1);
        }}

        @media (max-width: 768px) {{
          .bobot-widget-container {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100% !important;
            height: 100% !important;
            transform: translateY(100%);
            border-radius: 0 !important;
          }}

          .bobot-widget-container.open {{
            transform: translateY(0);
          }}

          .bobot-widget-iframe {{
            border-radius: 0 !important;
          }}
        }}
      `;

      const styleSheet = document.createElement("style");
      styleSheet.textContent = styles;
      document.head.appendChild(styleSheet);
    }}

    createTriggerButton() {{
      this.triggerButton = document.createElement("button");
      this.triggerButton.className = "bobot-widget-trigger";
      this.renderTriggerButtonContent();
      this.triggerButton.setAttribute("aria-label", "Open chat");
      this.triggerButton.addEventListener("click", () => this.toggleWidget());
      document.body.appendChild(this.triggerButton);
    }}

    renderTriggerButtonContent() {{
      if (!this.triggerButton) return;
      this.triggerButton.innerHTML = "";
      
      const avatarUrl = this.config?.avatarUrl;
      if (avatarUrl) {{
        const img = document.createElement("img");
        img.src = avatarUrl;
        img.alt = this.config?.botName || "Open chat";
        this.triggerButton.appendChild(img);
        this.triggerButton.style.background = "transparent";
      }} else {{
        this.triggerButton.textContent = WIDGET_CONFIG.triggerButtonText;
        this.triggerButton.style.background = `linear-gradient(135deg, ${{WIDGET_CONFIG.primaryColor}} 0%, #2563eb 100%)`;
      }}
    }}

    createWidget() {{
      this.widget = document.createElement("div");
      this.widget.className = "bobot-widget-container";

      const closeButton = document.createElement("button");
      closeButton.className = "bobot-widget-close";
      closeButton.innerHTML = "×";
      closeButton.setAttribute("aria-label", "Close chat");
      closeButton.addEventListener("click", () => this.closeWidget());

      this.iframe = document.createElement("iframe");
      this.iframe.className = "bobot-widget-iframe";
      this.iframe.src = `${{WIDGET_CONFIG.apiBaseUrl}}${{WIDGET_CONFIG.widgetUrl}}?api_key=${{encodeURIComponent(this.apiKey)}}`;
      this.iframe.allow = "microphone; camera";
      this.iframe.setAttribute("title", "{bot_name} Chat Widget");

      this.widget.appendChild(closeButton);
      this.widget.appendChild(this.iframe);
      document.body.appendChild(this.widget);
    }}

    attachEventListeners() {{
      // Close on outside click
      document.addEventListener("click", (e) => {{
        if (
          this.isOpen &&
          !this.widget.contains(e.target) &&
          !this.triggerButton.contains(e.target)
        ) {{
          this.closeWidget();
        }}
      }});

      // Close on Escape key
      document.addEventListener("keydown", (e) => {{
        if (e.key === "Escape" && this.isOpen) {{
          this.closeWidget();
        }}
      }});

      // Listen for messages from iframe
      window.addEventListener("message", (event) => {{
        if (event.origin !== WIDGET_CONFIG.apiBaseUrl) return;

        if (event.data.type === "close_widget") {{
          this.closeWidget();
        }}

        if (event.data.type === "widget_config") {{
          this.applyWidgetConfig(event.data);
        }}
      }});
    }}

    applyWidgetConfig(data) {{
      this.config = this.config || {{}};
      if (data.botName) this.config.botName = data.botName;
      if (data.avatarUrl) this.config.avatarUrl = data.avatarUrl;
      if (data.primaryColor) {{
        this.config.primaryColor = data.primaryColor;
        WIDGET_CONFIG.primaryColor = data.primaryColor;
      }}
      this.renderTriggerButtonContent();
    }}

    toggleWidget() {{
      if (this.isOpen) {{
        this.closeWidget();
      }} else {{
        this.openWidget();
      }}
    }}

    openWidget() {{
      this.isOpen = true;
      this.widget.classList.add("open");
      this.triggerButton.style.transform = "scale(0.9)";
    }}

    closeWidget() {{
      this.isOpen = false;
      this.widget.classList.remove("open");
      this.triggerButton.style.transform = "scale(1)";
    }}

    show() {{
      this.triggerButton.style.display = "flex";
    }}

    hide() {{
      this.triggerButton.style.display = "none";
      if (this.isOpen) {{
        this.closeWidget();
      }}
    }}

    destroy() {{
      if (this.widget) {{
        this.widget.remove();
      }}
      if (this.triggerButton) {{
        this.triggerButton.remove();
      }}
      window.BobotWidget = null;
    }}
  }}

  function initWidget() {{
    if (document.readyState === "loading") {{
      document.addEventListener("DOMContentLoaded", () => {{
        window.BobotWidget = new BobotWidget();
      }});
    }} else {{
      window.BobotWidget = new BobotWidget();
    }}
  }}

  // Public API
  window.BobotWidgetAPI = {{
    init: initWidget,
    show: () => window.BobotWidget?.show(),
    hide: () => window.BobotWidget?.hide(),
    toggle: () => window.BobotWidget?.toggleWidget(),
    destroy: () => window.BobotWidget?.destroy(),
    getState: () => window.BobotWidget?.getState() || null,
  }};

  initWidget();
  console.log("✅ Cortex Widget loaded successfully");
}})();
"""
    
    return embed_script, 200, {'Content-Type': 'application/javascript'}

