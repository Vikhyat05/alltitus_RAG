// DOM Elements
const inputText = document.getElementById("input-text");
const sendButton = document.getElementById("send-button");
const messagesDiv = document.getElementById("messages");
const newChatButton = document.getElementById("new-chat-btn");

// Session ID (random UUID)
let sessionId = localStorage.getItem("session_id");
if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem("session_id", sessionId);
}

const suggestionChips = [
  "What is the overall deductible in 2500 Gold American Choice?",
  "Are there services covered before you meet your deductible?",
  "What is not included in the out-of-pocket limit?",
];

function showWelcomeMessage() {
  messagesDiv.innerHTML = `
    <div class="message welcome">
      <h1 class="welcome-title">Welcome to SecureShield Insurance Support</h1>
      <p class="welcome-subtitle">I'm your virtual insurance assistant, ready to help with claims, policies, coverage questions, and more. How can I assist you today?</p>
      <div class="suggestion-chips">
        ${suggestionChips
          .map((chip) => `<div class="suggestion-chip">${chip}</div>`)
          .join("")}
      </div>
    </div>
  `;

  document.querySelectorAll(".suggestion-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      inputText.value = chip.textContent;
      inputText.focus();
      checkInput();
    });
  });
}

showWelcomeMessage();

inputText.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height =
    (this.scrollHeight < 150 ? this.scrollHeight : 150) + "px";
  checkInput();
});

newChatButton.addEventListener("click", async () => {
  try {
    const response = await fetch(`/reset_chat?session_id=${sessionId}`, {
      method: "POST",
    });

    if (!response.ok) {
      console.error("Error resetting chat:", response.statusText);
    }
  } catch (error) {
    console.error("Failed to reset chat history:", error);
  }

  showWelcomeMessage();
  inputText.value = "";
  inputText.style.height = "auto";
  sendButton.disabled = true;
});

function checkInput() {
  sendButton.disabled = inputText.value.trim() === "";
}

inputText.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!sendButton.disabled) {
      sendButton.click();
    }
  }
});

function formatMessage(role, content) {
  const isUser = role === "user";
  const avatar = isUser
    ? '<i class="fas fa-user"></i>'
    : '<i class="fas fa-headset"></i>';
  const sender = isUser ? "You" : "Insurance Assistant";

  return `
    <div class="message ${role}">
      <div class="message-avatar">${avatar}</div>
      <div class="message-wrapper">
        <div class="message-sender">${sender}</div>
        <div class="message-content">${content}</div>
      </div>
    </div>
  `;
}

function appendMessage(role, text) {
  if (messagesDiv.querySelector(".welcome")) {
    messagesDiv.innerHTML = "";
  }

  const formattedContent =
    role === "assistant" && text ? marked.parse(text) : text;
  const messageHTML = formatMessage(role, formattedContent);

  const tempDiv = document.createElement("div");
  tempDiv.innerHTML = messageHTML;
  const messageEl = tempDiv.firstElementChild;

  messagesDiv.appendChild(messageEl);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  return messageEl.querySelector(".message-content");
}

function showTypingIndicator() {
  const typingIndicator = document.createElement("div");
  typingIndicator.className = "message assistant typing";
  typingIndicator.innerHTML = `
    <div class="message-avatar">
      <i class="fas fa-headset"></i>
    </div>
    <div class="message-wrapper">
      <div class="message-sender">Insurance Assistant</div>
      <div class="message-content">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  `;

  messagesDiv.appendChild(typingIndicator);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  return typingIndicator;
}

function removeTypingIndicator() {
  const typingIndicator = messagesDiv.querySelector(".typing");
  if (typingIndicator) typingIndicator.remove();
}

sendButton.onclick = async () => {
  const message = inputText.value.trim();
  if (!message) return;

  appendMessage("user", message);

  inputText.value = "";
  inputText.style.height = "auto";
  sendButton.disabled = true;

  const typingIndicator = showTypingIndicator();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    if (!response.ok) throw new Error(`HTTP error ${response.status}`);

    removeTypingIndicator();

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let assistantMsg = "";
    const el = appendMessage("assistant", "");

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      assistantMsg += chunk;
      el.innerHTML = marked.parse(assistantMsg);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  } catch (error) {
    console.error("Error:", error);
    removeTypingIndicator();
    appendMessage(
      "assistant",
      "I'm experiencing technical difficulties connecting to our support system. Please try again in a moment, or contact our customer service line for immediate assistance."
    );
  }

  sendButton.disabled = false;
};

inputText.focus();
checkInput();
