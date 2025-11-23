// Enhanced Multi-Website Embed Script
// Replace your static/embed.js with this version

(function () {
  "use strict";

  // Get configuration from global or URL parameters
  const config = window.CHATBOT_CONFIG || {};
  const urlParams = new URLSearchParams(window.location.search);

  // Multi-website configuration
  const WIDGET_CONFIG = {
    apiBaseUrl: config.apiBaseUrl || window.location.origin,
    websiteId: config.websiteId || urlParams.get("website_id") || getWebsiteIdFromDomain(),
    botName: config.botName || "Assistant",
    websiteName: config.websiteName || "Website",
    primaryColor: config.primaryColor || "#667eea",
    position: config.position || "bottom-right",
    zIndex: 999999,
  };

  // Prevent multiple widget loads
  if (window.ChatbotWidget && window.ChatbotWidget.websiteId === WIDGET_CONFIG.websiteId) {
    console.warn("Chatbot Widget already loaded for this website");
    return;
  }

  function getWebsiteIdFromDomain() {
    // Auto-detect website ID from current domain
    const hostname = window.location.hostname;
    const domainMappings = {
      "sourceselect.ca": "sourceselect",
      "www.sourceselect.ca": "sourceselect",
      "example-business.com": "example_business",
      "client-site.com": "client_site",
    };

    return domainMappings[hostname] || "default";
  }

  class ChatbotWidget {
    constructor() {
      this.isOpen = false;
      this.widget = null;
      this.triggerButton = null;
      this.iframe = null;
      this.websiteId = WIDGET_CONFIG.websiteId;
      this.init();
    }

    init() {
      this.loadWebsiteConfig().then(() => {
        this.createStyles();
        this.createTriggerButton();
        this.createWidget();
        this.attachEventListeners();
      });
    }

    async loadWebsiteConfig() {
      try {
        // Fetch website-specific configuration from server
        const response = await fetch(
          `${WIDGET_CONFIG.apiBaseUrl}/api/website-config?website_id=${this.websiteId}`
        );
        if (response.ok) {
          const serverConfig = await response.json();
          // Update config with server data
          Object.assign(WIDGET_CONFIG, serverConfig);
        }
      } catch (error) {
        console.warn("Could not load server config, using defaults:", error);
      }
    }

    createStyles() {
      const styles = `
        .chatbot-widget-trigger {
          position: fixed;
          ${this.getPositionStyles()}
          background: ${WIDGET_CONFIG.primaryColor};
          color: white;
          border: none;
          border-radius: 50px;
          padding: 12px 20px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
          z-index: ${WIDGET_CONFIG.zIndex};
          transition: all 0.3s ease;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .chatbot-widget-trigger:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
        }

        .chatbot-widget-container {
          position: fixed;
          ${this.getWidgetPositionStyles()}
          width: 350px;
          height: 500px;
          z-index: ${WIDGET_CONFIG.zIndex + 1};
          transform: scale(0) translateY(20px);
          opacity: 0;
          transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
          transform-origin: ${this.getTransformOrigin()};
        }

        .chatbot-widget-container.open {
          transform: scale(1) translateY(0);
          opacity: 1;
        }

        .chatbot-widget-iframe {
          width: 100%;
          height: 100%;
          border: none;
          border-radius: 12px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }

        .chatbot-widget-close {
          position: absolute;
          top: -10px;
          right: -10px;
          background: #ff4757;
          color: white;
          border: none;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          font-size: 12px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
          z-index: ${WIDGET_CONFIG.zIndex + 2};
        }

        .chatbot-widget-close:hover {
          background: #ff3742;
        }

        /* Website-specific branding */
        .chatbot-widget-branding {
          position: absolute;
          bottom: -30px;
          right: 0;
          font-size: 10px;
          color: #666;
          background: white;
          padding: 2px 8px;
          border-radius: 4px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        @media (max-width: 768px) {
          .chatbot-widget-container {
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

          .chatbot-widget-container.open {
            transform: translateY(0);
          }

          .chatbot-widget-iframe {
            border-radius: 0 !important;
          }

          .chatbot-widget-close {
            top: 20px;
            right: 20px;
            width: 32px;
            height: 32px;
            font-size: 16px;
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
          return "bottom: 20px; left: 20px;";
        case "top-right":
          return "top: 20px; right: 20px;";
        case "top-left":
          return "top: 20px; left: 20px;";
        default:
          return "bottom: 20px; right: 20px;";
      }
    }

    getWidgetPositionStyles() {
      switch (WIDGET_CONFIG.position) {
        case "bottom-left":
          return "bottom: 80px; left: 20px;";
        case "top-right":
          return "top: 80px; right: 20px;";
        case "top-left":
          return "top: 80px; left: 20px;";
        default:
          return "bottom: 80px; right: 20px;";
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
      this.triggerButton.className = "chatbot-widget-trigger";
      this.triggerButton.innerHTML = `💬 Chat with ${WIDGET_CONFIG.botName}`;
      this.triggerButton.addEventListener("click", () => this.toggleWidget());
      document.body.appendChild(this.triggerButton);
    }

    createWidget() {
      this.widget = document.createElement("div");
      this.widget.className = "chatbot-widget-container";

      const closeButton = document.createElement("button");
      closeButton.className = "chatbot-widget-close";
      closeButton.innerHTML = "×";
      closeButton.addEventListener("click", () => this.closeWidget());

      // Create iframe with website-specific parameters
      this.iframe = document.createElement("iframe");
      this.iframe.className = "chatbot-widget-iframe";
      this.iframe.src = this.buildIframeUrl();
      this.iframe.allow = "microphone; camera";

      // Add branding
      const branding = document.createElement("div");
      branding.className = "chatbot-widget-branding";
      branding.innerHTML = `Powered by ${WIDGET_CONFIG.websiteName}`;

      this.widget.appendChild(closeButton);
      this.widget.appendChild(this.iframe);
      this.widget.appendChild(branding);
      document.body.appendChild(this.widget);
    }

    buildIframeUrl() {
      const params = new URLSearchParams({
        website_id: this.websiteId,
        bot_name: WIDGET_CONFIG.botName,
        primary_color: WIDGET_CONFIG.primaryColor,
        embedded: "true",
      });

      return `${WIDGET_CONFIG.apiBaseUrl}/widget?${params.toString()}`;
    }

    attachEventListeners() {
      document.addEventListener("click", (e) => {
        if (
          this.isOpen &&
          !this.widget.contains(e.target) &&
          !this.triggerButton.contains(e.target)
        ) {
          this.closeWidget();
        }
      });

      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && this.isOpen) {
          this.closeWidget();
        }
      });

      // Listen for iframe messages (for website-specific config updates)
      window.addEventListener("message", (event) => {
        if (event.origin !== WIDGET_CONFIG.apiBaseUrl) return;

        if (event.data.type === "chatbot_config_update") {
          this.updateConfig(event.data.config);
        }
      });

      window.addEventListener("resize", () => {
        if (this.isOpen && window.innerWidth <= 768) {
          this.widget.style.transform = "translateY(0)";
        }
      });
    }

    updateConfig(newConfig) {
      // Update widget configuration dynamically
      Object.assign(WIDGET_CONFIG, newConfig);

      // Update trigger button text
      if (newConfig.botName) {
        this.triggerButton.innerHTML = `💬 Chat with ${newConfig.botName}`;
      }

      // Update colors
      if (newConfig.primaryColor) {
        this.triggerButton.style.background = newConfig.primaryColor;
      }
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
      this.triggerButton.style.display = "none";

      setTimeout(() => {
        if (this.iframe && this.iframe.contentWindow) {
          this.iframe.contentWindow.focus();
        }
      }, 300);

      this.dispatchEvent("chatbot:widget:opened");
    }

    closeWidget() {
      this.isOpen = false;
      this.widget.classList.remove("open");
      this.triggerButton.style.display = "block";

      this.dispatchEvent("chatbot:widget:closed");
    }

    dispatchEvent(eventName, data = {}) {
      const event = new CustomEvent(eventName, {
        detail: {
          widget: this,
          websiteId: this.websiteId,
          ...data,
        },
      });
      window.dispatchEvent(event);
    }

    show() {
      this.triggerButton.style.display = "block";
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
      window.ChatbotWidget = null;
    }

    getState() {
      return {
        isOpen: this.isOpen,
        websiteId: this.websiteId,
        position: WIDGET_CONFIG.position,
        primaryColor: WIDGET_CONFIG.primaryColor,
        botName: WIDGET_CONFIG.botName,
      };
    }
  }

  function initWidget() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => {
        window.ChatbotWidget = new ChatbotWidget();
      });
    } else {
      window.ChatbotWidget = new ChatbotWidget();
    }
  }

  // Global API for website-specific control
  window.ChatbotWidgetAPI = {
    init: initWidget,
    show: () => window.ChatbotWidget?.show(),
    hide: () => window.ChatbotWidget?.hide(),
    toggle: () => window.ChatbotWidget?.toggleWidget(),
    destroy: () => window.ChatbotWidget?.destroy(),
    getState: () => window.ChatbotWidget?.getState() || null,
    updateConfig: (config) => window.ChatbotWidget?.updateConfig(config),

    // Website-specific methods
    setWebsiteId: (websiteId) => {
      if (window.ChatbotWidget) {
        window.ChatbotWidget.websiteId = websiteId;
        window.ChatbotWidget.iframe.src = window.ChatbotWidget.buildIframeUrl();
      }
    },

    getWebsiteId: () => window.ChatbotWidget?.websiteId || null,
  };

  // Initialize the widget
  initWidget();

  console.log(`Chatbot Widget loaded for website: ${WIDGET_CONFIG.websiteId}`);
})();
