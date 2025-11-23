
(function () {
  if (window.hasOwnProperty('sourceSelectWidget')) return;

  const RATE_LIMIT_COOLDOWN = 1000;
  let lastClickTime = 0;
  let userInfoCaptured = false;
  let hasSentFirstMessage = false;

  // Load external CSS
  const styleLink = document.createElement("link");
  styleLink.rel = "stylesheet";
  styleLink.href = "/static/chat-widget.css";
  document.head.appendChild(styleLink);

  // Load Emoji Picker
  const emojiScript = document.createElement("script");
  emojiScript.src = "https://cdn.jsdelivr.net/npm/@joeattardi/emoji-button@4.6.4/dist/emoji-button.js";
  document.head.appendChild(emojiScript);

  // Create chat button
  const chatButton = document.createElement('div');
  chatButton.id = 'chat-button';
  chatButton.innerHTML = '💬';
  document.body.appendChild(chatButton);

  // Create chat container
  const chatDiv = document.createElement('div');
  chatDiv.id = 'chat';
  document.body.appendChild(chatDiv);

  // Inject chat UI
  chatDiv.innerHTML = `
    <div id="chat-window">
      <div class="msg bot">
        <div class="bot-msg-wrapper">
          <img src="https://backend.chatbase.co/storage/v1/object/public/chatbots-profile-pictures/f295df57-57e4-4b10-824d-e5659916d586/i91yeOUDGtHiX4ImHr8tA.jpg?width=24&height=24&quality=50" alt="Bot Avatar">
          <span>Bobot:</span>
        </div>
        <div class="user-msg-wrapper">Hi! Good Day, What can I help you with?</div>
      </div>
    </div>
    <div id="suggested-buttons" style="margin: 10px 0;"></div>
    <div class="msg-container">
      <button id="emoji-btn">😊</button>
      <input id="msg" placeholder="Ask me something..." />
      <button id="sendBtn">Send</button>
    </div>
  `;

  const chatWindow = chatDiv.querySelector('#chat-window');
  const buttonContainer = chatDiv.querySelector('#suggested-buttons');

  // Initialize emoji picker AFTER emoji script loads and UI is built
  emojiScript.onload = () => {
    setTimeout(() => {
      const EmojiButton = window.EmojiButton;
      const emojiBtn = chatDiv.querySelector('#emoji-btn');
      const input = chatDiv.querySelector('#msg');

      if (!emojiBtn || !input || !EmojiButton) {
        console.warn('Emoji Picker: Missing elements or EmojiButton not loaded');
        return;
      }

      const picker = new EmojiButton({
        position: 'top-start',
        autoHide: true,
        zIndex: 999999
      });

      emojiBtn.addEventListener('click', () => {
        console.log('Emoji button clicked');
        picker.togglePicker(emojiBtn);
      });

      picker.on('emoji', emoji => {
        input.value += emoji;
        input.focus();
      });
    }, 100);
  };

  function appendMessage(sender, text) {
    const msg = document.createElement('div');
    msg.className = 'msg ' + sender;
  
    // Clean up the response message by removing excess line breaks and spaces
    text = text.replace(/(\s{2,}|\n)/g, ' '); // Replace multiple spaces or newlines with a single space
  
    // Avoid extra <br> tags in bot's message
    text = text.replace(/<br\s*\/?>/g, ''); // Remove all <br> tags
  
    msg.innerHTML = sender === 'bot'
      ? `<div class="bot-msg-wrapper">
             <img src="https://backend.chatbase.co/storage/v1/object/public/chatbots-profile-pictures/f295df57-57e4-4b10-824d-e5659916d586/i91yeOUDGtHiX4ImHr8tA.jpg?width=24&height=24&quality=50" alt="Bot Avatar">
             <span>Bobot:</span>
           </div>
           <div class="user-msg-wrapper">${text}</div>`
      : `<div class="user-msg-wrapper">${text}</div>`;
  
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }
  
  // function appendMessage(sender, text) {
  //   const msg = document.createElement('div');
  //   msg.className = 'msg ' + sender;
  //   msg.innerHTML = sender === 'bot'
  //     ? `<div class="bot-msg-wrapper">
  //          <img src="https://backend.chatbase.co/storage/v1/object/public/chatbots-profile-pictures/f295df57-57e4-4b10-824d-e5659916d586/i91yeOUDGtHiX4ImHr8tA.jpg?width=24&height=24&quality=50" alt="Bot Avatar">
  //          <span>Bobot:</span>
  //        </div>
  //        <div class="user-msg-wrapper">${text}</div>`
  //     : `<div class="user-msg-wrapper">${text}</div>`;

  //   chatWindow.appendChild(msg);
  //   chatWindow.scrollTop = chatWindow.scrollHeight;
  // }

  function renderSuggestedButtons(buttons) {
    buttonContainer.innerHTML = '';
    buttons.forEach(text => {
      const btn = document.createElement('button');
      btn.innerText = text;
      btn.className = 'suggested-button';
      btn.onclick = () => {
        const currentTime = Date.now();
        if (currentTime - lastClickTime < RATE_LIMIT_COOLDOWN) {
          console.log("Please wait before clicking again.");
          return;
        }
        lastClickTime = currentTime;
        buttonContainer.innerHTML = '';
        simulateUserMessage(text);
      };
      buttonContainer.appendChild(btn);
    });
  }

  function simulateUserMessage(msg) {
    chatDiv.querySelector('#msg').value = msg;
    sendMessage();
  }

  function showTypingIndicator() {
    const typing = document.createElement('div');
    typing.className = 'bot-typing';
    typing.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
    chatWindow.appendChild(typing);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function removeTypingIndicator() {
    const typing = chatWindow.querySelector('.bot-typing');
    if (typing) typing.remove();
  }

  function showInlineFormMessage() {
    const msg = document.createElement('div');
    msg.className = 'msg bot';
    msg.innerHTML = `
      <div class="bot-msg-wrapper">
        <img src="https://backend.chatbase.co/storage/v1/object/public/chatbots-profile-pictures/f295df57-57e4-4b10-824d-e5659916d586/i91yeOUDGtHiX4ImHr8tA.jpg?width=24&height=24&quality=50" alt="Bot Avatar">
        <span>Bobot:</span>
      </div>
      <div class="user-msg-wrapper">
        Hello! It's great to hear from you. Before we dive in, please provide your name, email, and phone:
      </div>
      <form id="inline-user-info-form" style="margin-top: 10px;">
        <input type="text" id="user-name" placeholder="Your Name" required />
        <input type="email" id="user-email" placeholder="Your Email" required />
        <input type="text" id="user-phone" placeholder="Your Phone" required />
        <button type="submit">Submit</button>
      </form>
    `;
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    msg.querySelector('#inline-user-info-form').addEventListener('submit', function (e) {
      e.preventDefault();
      const name = msg.querySelector('#user-name').value;
      const email = msg.querySelector('#user-email').value;
      const phone = msg.querySelector('#user-phone').value;

      sessionStorage.setItem("chat_user_name", name);
      sessionStorage.setItem("chat_user_email", email);
      sessionStorage.setItem("chat_user_phone", phone);
      userInfoCaptured = true;
      msg.querySelector('#inline-user-info-form').style.display = 'none';

      appendMessage("bot", `Thanks ${name}, how can I assist you further?`);
      renderSuggestedButtons([
        "What is SourceSelect?",
        "How can I contact SourceSelect?",
        "What services do you offer?",
        "Can you help with branding?",
        "Do you offer web development?"
      ]);
    });
  }

  function sendMessage() {
    const input = chatDiv.querySelector('#msg');
    const message = input.value.trim();
    if (!message) return;

    appendMessage("user", message);
    input.value = '';

    if (!hasSentFirstMessage) {
      hasSentFirstMessage = true;
      showInlineFormMessage();
      return;
    }

    if (!userInfoCaptured) return;

    showTypingIndicator();

    fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        name: sessionStorage.getItem("chat_user_name"),
        email: sessionStorage.getItem("chat_user_email"),
        phone: sessionStorage.getItem("chat_user_phone")
      })
    })
      .then(resp => resp.json())
      .then(data => {
        removeTypingIndicator();
        appendMessage("bot", data.response);
        if (data.suggested_buttons) {
          renderSuggestedButtons(data.suggested_buttons);
        } else {
          buttonContainer.innerHTML = '';
        }
      })
      .catch(() => {
        removeTypingIndicator();
        appendMessage("bot", "Oops! Something went wrong.");
      });
  }

  chatDiv.querySelector('#sendBtn').addEventListener('click', sendMessage);
  chatDiv.querySelector('#msg').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });

  chatButton.addEventListener('click', function () {
    const isOpen = chatDiv.style.display === 'block';
    chatDiv.style.display = isOpen ? 'none' : 'block';
  });

  window.sourceSelectWidget = true;
})();
