(function () {
  "use strict";

  // Get the base URL from the script's src (where embed.js is loaded from)
  // This ensures the widget loads from the chatbot server, not the current website
  function getScriptBaseUrl() {
    const scripts = document.getElementsByTagName('script');
    for (let script of scripts) {
      if (script.src && script.src.includes('embed.js')) {
        try {
          const url = new URL(script.src);
          return url.origin; // Returns http://localhost:6001
        } catch (e) {
          // Fallback to window.location.origin if URL parsing fails
          return window.location.origin;
        }
      }
    }
    // Fallback to window.location.origin if script not found
    return window.location.origin;
  }

  const WIDGET_CONFIG = {
    apiBaseUrl: getScriptBaseUrl(), // Use the chatbot server URL, not the current website
    widgetUrl: "/widget",
    triggerButtonText: "",
    position: "bottom-right",
    primaryColor: "#3b82f6",
    zIndex: 999999,
  };

  if (window.BobotWidget) {
    console.warn("Bobot Widget already loaded");
    return;
  }

  class BobotWidget {
    constructor() {
      this.isOpen = false;
      this.widget = null;
      this.triggerButton = null;
      this.iframe = null;
      this.config = {};
      this.apiKey = null;
      this.initialize();
    }

    initialize() {
      const urlParams = new URLSearchParams(window.location.search);
      this.websiteId = urlParams.get("website_id") || "default";
      this.apiKey = urlParams.get("api_key") || urlParams.get("key") || this.getApiKeyFromScript();

      this.createStyles();
      this.createTriggerButton();
      this.createWidget();
      this.attachEventListeners();
    }

    getApiKeyFromScript() {
      const scripts = document.getElementsByTagName('script');
      for (let script of scripts) {
        if (script.src && script.src.includes('embed.js')) {
          const params = new URLSearchParams(script.src.split('?')[1] || '');
          const key = params.get('api_key') || params.get('key');
          if (key) return key;
        }
      }
      return null;
    }

    createStyles() {
      const styles = `
        /* Chatbase-style Widget Styles */
        .bobot-widget-trigger {
          position: fixed;
          ${this.getPositionStyles()}
          background: transparent !important;
          color: white;
          border: none;
          width: 60px;
          height: 60px;
          font-size: 24px;
          cursor: pointer;
          z-index: ${WIDGET_CONFIG.zIndex};
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0;
          animation: fadeInGlow 1.5s ease-out forwards;
        }
          
        .bobot-widget-trigger img {
          border-radius: 50%;
          width:60px;
          height: 60px;
        }

        @keyframes fadeInGlow {
          0% {
            opacity: 0;
            transform: scale(0.8);
          }
          50% {
            opacity: 0.7;
            transform: scale(1.05);
          }
          100% {
            opacity: 1;
            transform: scale(1);
          }
        }

        .bobot-widget-trigger::before {
          content: '';
          position: absolute;
          inset: -6px;
          border-radius: 50%;
          background: conic-gradient(from 0deg, #667eea, #764ba2, #f093fb, #4facfe, #00f2fe, #667eea);
          opacity: 0.6;
          transition: opacity 0.3s ease;
          animation: gradientRotate 3s linear infinite, pulseGlow 2s ease-in-out infinite;
          z-index: -1;
        }
        
        @keyframes pulseGlow {
          0%, 100% {
            opacity: 0.4;
            transform: scale(1);
          }
          50% {
            opacity: 0.8;
            transform: scale(1.1);
          }
        }

        .bobot-widget-trigger:hover::after {
          background: white;
        }


        .bobot-widget-trigger::after {
          content: '';
          position: absolute;
          inset: -3px;
          border-radius: 50%;
          z-index: -1;
          background: white;
        }

        @keyframes gradientRotate {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        .bobot-widget-trigger img {
          width: 100%;
          object-fit: cover;
          background: transparent;
          position: relative;
          z-index: 1;
        }

        .bobot-widget-trigger:hover {
          transform: translateY(-2px) scale(1.05);
        }

        .bobot-widget-trigger:hover::before {
          opacity: 1;
        }

        .bobot-widget-trigger:active {
          transform: translateY(-1px) scale(1.02);
        }

        .bobot-widget-container {
          position: fixed;
          ${this.getWidgetPositionStyles()}
          width: 380px;
          height: 600px;
          z-index: ${WIDGET_CONFIG.zIndex + 1};
          transform: scale(0.95) translateY(20px);
          opacity: 0;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          transform-origin: ${this.getTransformOrigin()};
          pointer-events: none;
        }

        .bobot-widget-container.open {
          transform: scale(1) translateY(0);
          opacity: 1;
          pointer-events: all;
        }

        .bobot-widget-iframe {
          width: 100%;
          height: 100%;
          border: none;
          border-radius: 20px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12), 0 8px 24px rgba(0, 0, 0, 0.08);
          background: white;
        }

        .bobot-widget-close {
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
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3), 0 2px 6px rgba(0, 0, 0, 0.1);
          z-index: ${WIDGET_CONFIG.zIndex + 2};
          transition: all 0.2s;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .bobot-widget-close:hover {
          background: #dc2626;
          transform: scale(1.1);
          box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4), 0 3px 8px rgba(0, 0, 0, 0.15);
        }

        /* Notification Badge - Hidden */
        .bobot-widget-badge {
          display: none !important;
        }

        /* Welcome Message */
        .bobot-welcome-message {
          position: fixed;
          ${this.getWelcomePositionStyles()}
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 16px;
          padding: 16px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
          max-width: 280px;
          z-index: ${WIDGET_CONFIG.zIndex - 1};
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          opacity: 0;
          transform: translateY(10px);
          transition: all 0.3s ease;
          pointer-events: none;
        }

        .bobot-welcome-message.show {
          opacity: 1;
          transform: translateY(0);
          pointer-events: all;
        }

        .bobot-welcome-message::after {
          content: '';
          position: absolute;
          bottom: -8px;
          right: 24px;
          width: 16px;
          height: 16px;
          background: white;
          border-right: 1px solid #e5e7eb;
          border-bottom: 1px solid #e5e7eb;
          transform: rotate(45deg);
        }

        .bobot-welcome-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }

        .bobot-welcome-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
        }

        .bobot-welcome-title {
          font-size: 14px;
          font-weight: 600;
          color: #111827;
          margin: 0;
        }

        .bobot-welcome-message p {
          margin: 0;
          font-size: 13px;
          color: #6b7280;
          line-height: 1.4;
        }

        .bobot-welcome-close {
          position: absolute;
          top: 8px;
          right: 8px;
          background: transparent;
          border: none;
          color: #9ca3af;
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          transition: color 0.2s;
        }

        .bobot-welcome-close:hover {
          color: #6b7280;
        }

        /* Responsive Styles */
        @media (max-width: 768px) {
          .bobot-widget-container {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100% !important;
            height: 100% !important;
            transform: translateY(100%);
            border-radius: 0 !important;
          }

          .bobot-widget-container.open {
            transform: translateY(0);
          }

          .bobot-widget-iframe {
            border-radius: 0 !important;
          }

          .bobot-widget-close {
            top: 16px;
            right: 16px;
            width: 36px;
            height: 36px;
            font-size: 18px;
          }

          .bobot-welcome-message {
            display: none;
          }
        }
      `;

      const styleSheet = document.createElement("style");
      styleSheet.textContent = styles;
      document.head.appendChild(styleSheet);
    }

    getPositionStyles() {
      switch (WIDGET_CONFIG.position) {
        case "bottom-left":
          return "bottom: 24px; left: 24px;";
        case "top-right":
          return "top: 24px; right: 24px;";
        case "top-left":
          return "top: 24px; left: 24px;";
        default:
          return "bottom: 24px; right: 24px;";
      }
    }

    getWidgetPositionStyles() {
      switch (WIDGET_CONFIG.position) {
        case "bottom-left":
          return "bottom: 100px; left: 24px;";
        case "top-right":
          return "top: 100px; right: 24px;";
        case "top-left":
          return "top: 100px; left: 24px;";
        default:
          return "bottom: 100px; right: 24px;";
      }
    }

    getWelcomePositionStyles() {
      switch (WIDGET_CONFIG.position) {
        case "bottom-left":
          return "bottom: 100px; left: 24px;";
        case "top-right":
          return "top: 100px; right: 24px;";
        case "top-left":
          return "top: 100px; left: 24px;";
        default:
          return "bottom: 100px; right: 104px;";
      }
    }

    getTransformOrigin() {
      switch (WIDGET_CONFIG.position) {
        case "bottom-left":
          return "bottom left";
        case "top-right":
          return "top right";
        case "top-left":
          return "top left";
        default:
          return "bottom right";
      }
    }

    createTriggerButton() {
      this.triggerButton = document.createElement("button");
      this.triggerButton.className = "bobot-widget-trigger";
      this.renderTriggerButtonContent();
      this.triggerButton.setAttribute("aria-label", "Open chat");
      this.triggerButton.addEventListener("click", () => this.toggleWidget());
      document.body.appendChild(this.triggerButton);

      // Badge removed - using glowing effect instead

      // Show welcome message after delay
      setTimeout(() => this.showWelcomeMessage(), 3000);
    }

    renderTriggerButtonContent() {
      if (!this.triggerButton) return;
      this.triggerButton.innerHTML = "";
      
      const avatarUrl = this.config?.avatarUrl;
      if (avatarUrl) {
        const img = document.createElement("img");
        img.src = avatarUrl;
        img.alt = this.config?.botName || "Open chat";
        this.triggerButton.appendChild(img);
        this.triggerButton.style.background = "transparent";
      } else {
        // No emoji, just empty button with gradient background
        this.triggerButton.textContent = "";
        this.triggerButton.style.background = `linear-gradient(135deg, ${WIDGET_CONFIG.primaryColor} 0%, #2563eb 100%)`;
      }
    }

    addNotificationBadge() {
      // Badge functionality removed - using glowing effect instead
    }

    showWelcomeMessage() {
      if (this.isOpen) return;

      const welcomeMessage = document.createElement("div");
      welcomeMessage.className = "bobot-welcome-message";
      // Use dynamic config or defaults
      const botName = window.CHATBOT_CONFIG?.botName || WIDGET_CONFIG.botName || 'Cortex';
      const websiteName = window.CHATBOT_CONFIG?.websiteName || WIDGET_CONFIG.websiteName || 'our website';
      
      welcomeMessage.innerHTML = `
        <button class="bobot-welcome-close" aria-label="Close message">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        <div class="bobot-welcome-header">
          <h3 class="bobot-welcome-title">${botName}</h3>
        </div>
        <p>Hi! I'm ${botName}, your intelligent AI assistant. How can I help you today?</p>
      `;

      document.body.appendChild(welcomeMessage);

      // Show with animation
      setTimeout(() => welcomeMessage.classList.add("show"), 100);

      // Auto-hide after 8 seconds
      setTimeout(() => this.hideWelcomeMessage(), 8000);

      // Close button functionality
      welcomeMessage.querySelector(".bobot-welcome-close").addEventListener("click", () => {
        this.hideWelcomeMessage();
      });

      // Click to open chat
      welcomeMessage.addEventListener("click", (e) => {
        if (!e.target.closest(".bobot-welcome-close")) {
          this.openWidget();
          this.hideWelcomeMessage();
        }
      });

      this.welcomeMessage = welcomeMessage;
    }

    hideWelcomeMessage() {
      if (this.welcomeMessage) {
        this.welcomeMessage.classList.remove("show");
        setTimeout(() => {
          if (this.welcomeMessage && this.welcomeMessage.parentNode) {
            this.welcomeMessage.remove();
          }
        }, 300);
      }
    }

    createWidget() {
      // Extract API key or website_id from URL parameters or script src
      const urlParams = new URLSearchParams(window.location.search);
      let apiKey = urlParams.get("api_key") || urlParams.get("key");
      
      // If no API key in URL, try to get it from the script tag
      if (!apiKey) {
        const scripts = document.getElementsByTagName('script');
        for (let script of scripts) {
          if (script.src && script.src.includes('embed.js')) {
            const scriptParams = new URLSearchParams(script.src.split('?')[1] || '');
            apiKey = scriptParams.get('api_key') || scriptParams.get('key');
            if (apiKey) break;
          }
        }
      }
      
      const websiteId = urlParams.get("website_id") || "default";

      this.widget = document.createElement("div");
      this.widget.className = "bobot-widget-container";

      const closeButton = document.createElement("button");
      closeButton.className = "bobot-widget-close";
      closeButton.innerHTML = "×";
      closeButton.setAttribute("aria-label", "Close chat");
      closeButton.addEventListener("click", () => this.closeWidget());

      this.iframe = document.createElement("iframe");
      this.iframe.className = "bobot-widget-iframe";

      // Build widget URL with API key (for user isolation)
      let widgetUrl = `${WIDGET_CONFIG.apiBaseUrl}${WIDGET_CONFIG.widgetUrl}`;
      const keyToUse = this.apiKey || apiKey;
      if (keyToUse) {
        widgetUrl += `?api_key=${encodeURIComponent(keyToUse)}`;
      } else {
        widgetUrl += `?website_id=${encodeURIComponent(websiteId)}`;
      }
      this.iframe.src = widgetUrl;

      this.iframe.allow = "microphone; camera";
      const botName = window.CHATBOT_CONFIG?.botName || WIDGET_CONFIG.botName || 'Cortex';
      this.iframe.setAttribute("title", `${botName} Chat Widget`);

      this.widget.appendChild(closeButton);
      this.widget.appendChild(this.iframe);
      document.body.appendChild(this.widget);

      // Store websiteId for later use
      this.websiteId = websiteId;
    }

    attachEventListeners() {
      // Close on outside click
      document.addEventListener("click", (e) => {
        if (
          this.isOpen &&
          !this.widget.contains(e.target) &&
          !this.triggerButton.contains(e.target)
        ) {
          this.closeWidget();
        }
      });

      // Close on Escape key
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && this.isOpen) {
          this.closeWidget();
        }
      });

      // Handle responsive behavior
      window.addEventListener("resize", () => {
        if (this.isOpen && window.innerWidth <= 768) {
          this.widget.style.transform = "translateY(0)";
        }
      });

      // Listen for messages from iframe
      window.addEventListener("message", (event) => {
        if (event.origin !== WIDGET_CONFIG.apiBaseUrl) return;

        // Handle iframe events (like closing)
        if (event.data.type === "close_widget") {
          this.closeWidget();
        }

        if (event.data.type === "widget_config") {
          this.applyWidgetConfig(event.data);
        }
      });
    }

    applyWidgetConfig(data) {
      this.config = this.config || {};
      if (data.botName) this.config.botName = data.botName;
      if (data.avatarUrl) this.config.avatarUrl = data.avatarUrl;
      if (data.primaryColor) {
        this.config.primaryColor = data.primaryColor;
        WIDGET_CONFIG.primaryColor = data.primaryColor;
      }
      this.renderTriggerButtonContent();
    }

    toggleWidget() {
      if (this.isOpen) {
        this.closeWidget();
      } else {
        this.openWidget();
      }
    }

    openWidget() {
      this.isOpen = true;
      this.widget.classList.add("open");
      this.triggerButton.style.transform = "scale(0.9)";
      this.hideWelcomeMessage();

      // Focus iframe after animation
      setTimeout(() => {
        if (this.iframe && this.iframe.contentWindow) {
          this.iframe.contentWindow.focus();
        }
      }, 300);

      this.dispatchEvent("bobot:widget:opened");
    }

    closeWidget() {
      this.isOpen = false;
      this.widget.classList.remove("open");
      this.triggerButton.style.transform = "scale(1)";

      this.dispatchEvent("bobot:widget:closed");
    }

    dispatchEvent(eventName, data = {}) {
      const event = new CustomEvent(eventName, {
        detail: { widget: this, ...data },
      });
      window.dispatchEvent(event);
    }

    show() {
      this.triggerButton.style.display = "flex";
    }

    hide() {
      this.triggerButton.style.display = "none";
      if (this.isOpen) {
        this.closeWidget();
      }
    }

    destroy() {
      if (this.widget) {
        this.widget.remove();
      }
      if (this.triggerButton) {
        this.triggerButton.remove();
      }
      if (this.welcomeMessage) {
        this.welcomeMessage.remove();
      }
      window.BobotWidget = null;
    }

    getState() {
      return {
        isOpen: this.isOpen,
        position: WIDGET_CONFIG.position,
        primaryColor: WIDGET_CONFIG.primaryColor,
      };
    }
  }

  function initWidget() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => {
        window.BobotWidget = new BobotWidget();
      });
    } else {
      window.BobotWidget = new BobotWidget();
    }
  }

  // Public API
  window.BobotWidgetAPI = {
    init: initWidget,
    show: () => window.BobotWidget?.show(),
    hide: () => window.BobotWidget?.hide(),
    toggle: () => window.BobotWidget?.toggleWidget(),
    destroy: () => window.BobotWidget?.destroy(),
    getState: () => window.BobotWidget?.getState() || null,
  };

  initWidget();

  console.log("✅ Bobot Widget (Chatbase Style) loaded successfully");
})();
