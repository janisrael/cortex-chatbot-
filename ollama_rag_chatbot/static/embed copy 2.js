(function () {
  "use strict";

  // Configuration
  const WIDGET_CONFIG = {
    apiBaseUrl: window.location.origin,
    widgetUrl: "/widget",
    triggerButtonText: "💬 Chat",
    position: "bottom-right",
    primaryColor: "#667eea",
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
      this.init();
    }

    init() {
      this.createStyles();
      this.createTriggerButton();
      this.createWidget();
      this.attachEventListeners();
    }

    createStyles() {
      const styles = `
              .bobot-widget-trigger {
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

              .bobot-widget-trigger:hover {
                  transform: translateY(-2px);
                  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
              }

              .bobot-widget-container {
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

              .bobot-widget-container.open {
                  transform: scale(1) translateY(0);
                  opacity: 1;
              }

              .bobot-widget-iframe {
                  width: 100%;
                  height: 100%;
                  border: none;
                  border-radius: 12px;
                  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
              }

              .bobot-widget-close {
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

              .bobot-widget-close:hover {
                  background: #ff3742;
              }

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
      this.triggerButton.className = "bobot-widget-trigger";
      this.triggerButton.textContent = WIDGET_CONFIG.triggerButtonText;
      this.triggerButton.addEventListener("click", () => this.toggleWidget());
      document.body.appendChild(this.triggerButton);
    }

    createWidget() {
      this.widget = document.createElement("div");
      this.widget.className = "bobot-widget-container";

      const closeButton = document.createElement("button");
      closeButton.className = "bobot-widget-close";
      closeButton.innerHTML = "×";
      closeButton.addEventListener("click", () => this.closeWidget());

      this.iframe = document.createElement("iframe");
      this.iframe.className = "bobot-widget-iframe";
      this.iframe.src = WIDGET_CONFIG.apiBaseUrl + WIDGET_CONFIG.widgetUrl;
      this.iframe.allow = "microphone; camera";

      this.widget.appendChild(closeButton);
      this.widget.appendChild(this.iframe);
      document.body.appendChild(this.widget);
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

      window.addEventListener("resize", () => {
        if (this.isOpen && window.innerWidth <= 768) {
          this.widget.style.transform = "translateY(0)";
        }
      });
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

      this.dispatchEvent("bobot:widget:opened");
    }

    closeWidget() {
      this.isOpen = false;
      this.widget.classList.remove("open");
      this.triggerButton.style.display = "block";

      this.dispatchEvent("bobot:widget:closed");
    }

    dispatchEvent(eventName, data = {}) {
      const event = new CustomEvent(eventName, {
        detail: { widget: this, ...data },
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

  window.BobotWidgetAPI = {
    init: initWidget,
    show: () => window.BobotWidget?.show(),
    hide: () => window.BobotWidget?.hide(),
    toggle: () => window.BobotWidget?.toggleWidget(),
    destroy: () => window.BobotWidget?.destroy(),
    getState: () => window.BobotWidget?.getState() || null,
  };

  initWidget();

  console.log("Widget loaded successfully");
})();

// New embed.js with full widget rendering from script only

// (function () {
//   "use strict";

//   const WIDGET_CONFIG = {
//     apiBaseUrl: window.location.origin,
//     widgetUrl: "/widget",
//     triggerButtonText: "Chat with us",
//     position: "bottom-right",
//     primaryColor: "#667eea",
//     zIndex: 999999,
//     title: "Chat with Bobot AI",
//   };

//   if (window.BobotWidget) {
//     console.warn("Bobot Widget already loaded");
//     return;
//   }

//   class BobotWidget {
//     constructor() {
//       this.isOpen = false;
//       this.widget = null;
//       this.triggerButton = null;
//       this.init();
//     }

//     init() {
//       this.createStyles();
//       this.createTriggerButton();
//       this.createWidget();
//       this.attachEvents();
//     }

//     createStyles() {
//       const style = document.createElement("style");
//       style.textContent = `
//         .bobot-widget-trigger {
//           position: fixed;
//           ${this.getPositionStyles()}
//           background: ${WIDGET_CONFIG.primaryColor};
//           color: white;
//           border: none;
//           border-radius: 50px;
//           padding: 12px 20px;
//           font-size: 14px;
//           font-weight: 600;
//           cursor: pointer;
//           z-index: ${WIDGET_CONFIG.zIndex};
//           box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
//           font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
//         }
//         .bobot-widget-container {
//           position: fixed;
//           ${this.getWidgetPositionStyles()}
//           width: 350px;
//           height: 500px;
//           background: white;
//           border-radius: 12px;
//           box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
//           display: none;
//           flex-direction: column;
//           overflow: hidden;
//           z-index: ${WIDGET_CONFIG.zIndex + 1};
//           font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
//         }
//         .bobot-widget-header {
//           background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
//           color: white;
//           padding: 15px;
//           text-align: center;
//           font-size: 16px;
//           font-weight: 600;
//         }
//         .bobot-widget-messages {
//           flex: 1;
//           padding: 15px;
//           overflow-y: auto;
//           background: #f8f9fa;
//         }
//         .bobot-message {
//           margin-bottom: 12px;
//           display: flex;
//           flex-direction: column;
//         }
//         .bobot-message-content {
//           max-width: 80%;
//           padding: 8px 12px;
//           border-radius: 12px;
//           font-size: 13px;
//           line-height: 1.4;
//         }
//         .bobot-message.user .bobot-message-content {
//           background: #667eea;
//           color: white;
//           align-self: flex-end;
//           border-bottom-right-radius: 3px;
//         }
//         .bobot-message.bot .bobot-message-content {
//           background: #e9ecef;
//           color: #333;
//           align-self: flex-start;
//           border-bottom-left-radius: 3px;
//         }
//         .bobot-widget-input {
//           display: flex;
//           padding: 12px;
//           background: white;
//           border-top: 1px solid #eee;
//           gap: 8px;
//         }
//         .bobot-widget-input input {
//           flex: 1;
//           padding: 8px 12px;
//           border: 1px solid #ddd;
//           border-radius: 18px;
//           font-size: 13px;
//         }
//         .bobot-widget-input button {
//           background: #667eea;
//           color: white;
//           border: none;
//           padding: 8px 16px;
//           border-radius: 18px;
//           font-size: 13px;
//           cursor: pointer;
//         }
//       `;
//       document.head.appendChild(style);
//     }

//     getPositionStyles() {
//       switch (WIDGET_CONFIG.position) {
//         case "bottom-left":
//           return "bottom: 20px; left: 20px;";
//         case "top-right":
//           return "top: 20px; right: 20px;";
//         case "top-left":
//           return "top: 20px; left: 20px;";
//         default:
//           return "bottom: 20px; right: 20px;";
//       }
//     }

//     getWidgetPositionStyles() {
//       switch (WIDGET_CONFIG.position) {
//         case "bottom-left":
//           return "bottom: 70px; left: 20px;";
//         case "top-right":
//           return "top: 70px; right: 20px;";
//         case "top-left":
//           return "top: 70px; left: 20px;";
//         default:
//           return "bottom: 70px; right: 20px;";
//       }
//     }

//     createTriggerButton() {
//       this.triggerButton = document.createElement("button");
//       this.triggerButton.className = "bobot-widget-trigger";
//       this.triggerButton.textContent = WIDGET_CONFIG.triggerButtonText;
//       this.triggerButton.onclick = () => this.toggleWidget();
//       document.body.appendChild(this.triggerButton);
//     }

//     createWidget() {
//       this.widget = document.createElement("div");
//       this.widget.className = "bobot-widget-container";

//       this.widget.innerHTML = `
//         <div class="bobot-widget-header">${WIDGET_CONFIG.title}</div>
//         <div class="bobot-widget-messages" id="bobotMessages"></div>
//         <div class="bobot-widget-input">
//           <input type="text" id="bobotInput" placeholder="Ask me anything..." />
//           <button id="bobotSend">Send</button>
//         </div>
//       `;

//       document.body.appendChild(this.widget);
//     }

//     attachEvents() {
//       const input = () => document.getElementById("bobotInput");
//       const sendBtn = () => document.getElementById("bobotSend");
//       const msgBox = () => document.getElementById("bobotMessages");

//       sendBtn().onclick = () => this.handleSend(input().value);
//       input().addEventListener("keypress", (e) => {
//         if (e.key === "Enter") this.handleSend(input().value);
//       });
//     }

//     handleSend(text) {
//       const input = document.getElementById("bobotInput");
//       if (!text.trim()) return;
//       this.addMessage(text, true);
//       input.value = "";
//       fetch(WIDGET_CONFIG.apiBaseUrl + "/chat", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message: text, user_id: "widget_user" }),
//       })
//         .then((res) => res.json())
//         .then((data) => {
//           if (data.response) this.addMessage(data.response, false);
//           else this.addMessage("Sorry, something went wrong.", false);
//         })
//         .catch((err) => {
//           console.error("Widget Error", err);
//           this.addMessage("Connection error. Please try again.", false);
//         });
//     }

//     addMessage(text, isUser) {
//       const msgBox = document.getElementById("bobotMessages");
//       const msg = document.createElement("div");
//       msg.className = `bobot-message ${isUser ? "user" : "bot"}`;
//       msg.innerHTML = `<div class="bobot-message-content">${text}</div>`;
//       msgBox.appendChild(msg);
//       msgBox.scrollTop = msgBox.scrollHeight;
//     }

//     toggleWidget() {
//       if (this.widget.style.display === "flex") {
//         this.widget.style.display = "none";
//       } else {
//         this.widget.style.display = "flex";
//       }
//     }
//   }

//   function initWidget() {
//     if (document.readyState === "loading") {
//       document.addEventListener("DOMContentLoaded", () => new BobotWidget());
//     } else {
//       new BobotWidget();
//     }
//   }

//   initWidget();
// })();
