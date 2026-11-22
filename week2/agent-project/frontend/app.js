const CHAT_ENDPOINT = "http://127.0.0.1:8000/chat";
const messagesElement = document.querySelector("#messages");
const historyElement = document.querySelector("#chat-history");
const form = document.querySelector("#chat-form");
const textarea = document.querySelector("#question");
const sendButton = document.querySelector("#send-button");
const charCount = document.querySelector("#char-count");
const topbarCurrent = document.querySelector("#topbar-current");
const sidebar = document.querySelector("#sidebar");
const backdrop = document.querySelector("#sidebar-backdrop");

const suggestions = [
  {
    title: "Give me a quick introduction",
    description: "Summarize Faraz's background and strengths.",
    question: "Can you give me a brief introduction to Faraz?"
  },
  {
    title: "Explore technical skills",
    description: "See the skills and tools listed on the resume.",
    question: "What technical skills does Faraz have?"
  },
  {
    title: "Talk about experience",
    description: "Review roles, responsibilities, and experience.",
    question: "Tell me about Faraz's work experience."
  },
  {
    title: "Ask about projects",
    description: "Learn about projects included in the resume.",
    question: "Which projects has Faraz worked on?"
  }
];

let chats = [createChat()];
let activeChatId = chats[0].id;
let isSending = false;

function createChat() {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    title: "New conversation",
    messages: []
  };
}

function activeChat() {
  return chats.find((chat) => chat.id === activeChatId);
}

function renderHistory() {
  historyElement.replaceChildren();

  for (const chat of [...chats].reverse()) {
    const item = document.createElement("button");
    item.className = `history-item${chat.id === activeChatId ? " active" : ""}`;
    item.type = "button";
    item.textContent = chat.title;
    item.title = chat.title;
    item.addEventListener("click", () => {
      activeChatId = chat.id;
      render();
      closeSidebar();
    });
    historyElement.append(item);
  }
}

function createAssistantIcon() {
  const avatar = document.createElement("span");
  avatar.className = "assistant-avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.innerHTML = '<svg viewBox="0 0 24 24" fill="none"><path d="m12 2.8 2.6 6.6 6.6 2.6-6.6 2.6-2.6 6.6-2.6-6.6L2.8 12l6.6-2.6L12 2.8Z" fill="currentColor"/></svg>';
  return avatar;
}

function renderInlineMarkdown(element, text) {
  const tokenPattern = /(\*\*[^*]+?\*\*|`[^`]+?`|\*[^*]+?\*)/g;
  let lastIndex = 0;

  for (const match of text.matchAll(tokenPattern)) {
    element.append(document.createTextNode(text.slice(lastIndex, match.index)));
    const token = match[0];
    const tag = token.startsWith("**") ? "strong" : token.startsWith("`") ? "code" : "em";
    const node = document.createElement(tag);
    node.textContent = tag === "strong" ? token.slice(2, -2) : token.slice(1, -1);
    element.append(node);
    lastIndex = match.index + token.length;
  }
  element.append(document.createTextNode(text.slice(lastIndex)));
}

function isListLine(line) {
  return /^\s*(?:[-*+]\s+|\d+[.)]\s+)/.test(line);
}

function isTableStart(lines, index) {
  return index + 1 < lines.length
    && lines[index].includes("|")
    && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[index + 1])
    && lines[index + 1].includes("-");
}

function tableCells(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function renderAssistantText(container, text) {
  const lines = text.split(/\r?\n/);
  let index = 0;

  while (index < lines.length) {
    if (!lines[index].trim()) {
      index += 1;
      continue;
    }

    if (isTableStart(lines, index)) {
      const wrapper = document.createElement("div");
      wrapper.className = "answer-table-wrap";
      const table = document.createElement("table");
      table.className = "answer-table";
      const header = document.createElement("thead");
      const headerRow = document.createElement("tr");
      for (const cellText of tableCells(lines[index])) {
        const cell = document.createElement("th");
        renderInlineMarkdown(cell, cellText);
        headerRow.append(cell);
      }
      header.append(headerRow);
      table.append(header);
      index += 2;

      const body = document.createElement("tbody");
      while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
        const row = document.createElement("tr");
        for (const cellText of tableCells(lines[index])) {
          const cell = document.createElement("td");
          renderInlineMarkdown(cell, cellText);
          row.append(cell);
        }
        body.append(row);
        index += 1;
      }
      table.append(body);
      wrapper.append(table);
      container.append(wrapper);
      continue;
    }

    if (isListLine(lines[index])) {
      const ordered = /^\s*\d+[.)]\s+/.test(lines[index]);
      const list = document.createElement(ordered ? "ol" : "ul");
      while (index < lines.length && isListLine(lines[index])) {
        const item = document.createElement("li");
        renderInlineMarkdown(item, lines[index].replace(/^\s*(?:[-*+]\s+|\d+[.)]\s+)/, ""));
        list.append(item);
        index += 1;
      }
      container.append(list);
      continue;
    }

    const paragraphLines = [];
    while (
      index < lines.length
      && lines[index].trim()
      && !isListLine(lines[index])
      && !isTableStart(lines, index)
    ) {
      paragraphLines.push(lines[index].trim());
      index += 1;
    }
    const paragraph = document.createElement("p");
    renderInlineMarkdown(paragraph, paragraphLines.join(" "));
    container.append(paragraph);
  }
}

function renderMessage(message) {
  const row = document.createElement("article");
  row.className = `message ${message.role}${message.error ? " error" : ""}`;

  if (message.role === "user") {
    const bubble = document.createElement("div");
    bubble.className = "message-content";
    bubble.textContent = message.content;
    row.append(bubble);
    return row;
  }

  row.append(createAssistantIcon());
  const contentWrap = document.createElement("div");
  contentWrap.className = "message-content-wrap";

  const heading = document.createElement("div");
  heading.className = "message-heading";
  const name = document.createElement("strong");
  name.textContent = "Faraz AI";
  const timestamp = document.createElement("span");
  timestamp.textContent = "Just now";
  heading.append(name, timestamp);

  const content = document.createElement("div");
  content.className = "message-content";
  if (message.error) {
    content.textContent = message.content;
  } else {
    renderAssistantText(content, message.content);
  }
  contentWrap.append(heading, content);
  row.append(contentWrap);
  return row;
}

function renderWelcome() {
  const welcome = document.createElement("section");
  welcome.className = "welcome";
  welcome.innerHTML = `
    <div class="welcome-eyebrow">Your personal career assistant</div>
    <h1>Good questions.<br /><span>Clear answers.</span></h1>
    <p class="welcome-copy">
      Explore Faraz's experience, skills, and projects. Ask naturally and get
      thoughtful answers grounded in the resume.
    </p>
    <div class="suggestion-heading">Start with a question</div>
    <div class="suggestions"></div>
  `;

  const suggestionList = welcome.querySelector(".suggestions");
  for (const suggestion of suggestions) {
    const card = document.createElement("button");
    card.className = "suggestion-card";
    card.type = "button";
    const title = document.createElement("strong");
    title.textContent = suggestion.title;
    const description = document.createElement("span");
    description.textContent = suggestion.description;
    const arrow = document.createElement("span");
    arrow.className = "suggestion-arrow";
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "↗";
    card.append(title, description, arrow);
    card.addEventListener("click", () => {
      textarea.value = suggestion.question;
      updateComposer();
      form.requestSubmit();
    });
    suggestionList.append(card);
  }

  return welcome;
}

function renderTyping() {
  const row = document.createElement("article");
  row.className = "message assistant";
  row.setAttribute("aria-label", "Faraz AI is preparing a response");
  row.append(createAssistantIcon());

  const contentWrap = document.createElement("div");
  contentWrap.className = "message-content-wrap";
  const heading = document.createElement("div");
  heading.className = "message-heading";
  const name = document.createElement("strong");
  name.textContent = "Faraz AI";
  const status = document.createElement("span");
  status.textContent = "Reading resume and thinking";
  heading.append(name, status);

  const dots = document.createElement("div");
  dots.className = "typing-indicator";
  dots.innerHTML = "<span></span><span></span><span></span>";
  contentWrap.append(heading, dots);
  row.append(contentWrap);
  return row;
}

function render() {
  const chat = activeChat();
  if (!chat) return;

  topbarCurrent.textContent = chat.title;
  messagesElement.replaceChildren();
  if (chat.messages.length === 0) {
    messagesElement.append(renderWelcome());
  } else {
    for (const message of chat.messages) {
      messagesElement.append(renderMessage(message));
    }
    if (isSending) messagesElement.append(renderTyping());
    messagesElement.scrollTop = messagesElement.scrollHeight;
  }
  renderHistory();
}

function updateComposer() {
  const length = textarea.value.length;
  charCount.textContent = `${length} / 2000`;
  sendButton.disabled = length === 0 || !textarea.value.trim() || isSending;
  textarea.style.height = "auto";
  textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
}

function closeSidebar() {
  sidebar.classList.remove("open");
  backdrop.classList.remove("visible");
}

function addMessage(chat, message) {
  chat.messages.push(message);
  if (chat.messages.length === 1 && message.role === "user") {
    chat.title = message.content.length > 34
      ? `${message.content.slice(0, 34).trimEnd()}…`
      : message.content;
  }
}

async function sendMessage(question) {
  const chat = activeChat();
  if (!chat || isSending || !question.trim()) return;

  addMessage(chat, { role: "user", content: question.trim() });
  textarea.value = "";
  isSending = true;
  updateComposer();
  render();

  try {
    const response = await fetch(CHAT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question.trim() })
    });
    const responseText = await response.text();
    let data;
    try {
      data = responseText ? JSON.parse(responseText) : {};
    } catch {
      data = { detail: responseText };
    }

    if (!response.ok) {
      const detail = data.detail || data.message || `The server returned HTTP ${response.status}.`;
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    if (typeof data.answer !== "string" || !data.answer.trim()) {
      throw new Error("The server response did not include an answer.");
    }
    addMessage(chat, { role: "assistant", content: data.answer });
  } catch (error) {
    const detail = error instanceof TypeError
      ? "Could not connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
      : error.message;
    addMessage(chat, {
      role: "assistant",
      content: `I couldn't get an answer. ${detail}`,
      error: true
    });
  } finally {
    isSending = false;
    updateComposer();
    render();
    textarea.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(textarea.value);
});

textarea.addEventListener("input", updateComposer);
textarea.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    if (!sendButton.disabled) form.requestSubmit();
  }
});

document.querySelector("#new-chat").addEventListener("click", () => {
  const chat = createChat();
  chats.push(chat);
  activeChatId = chat.id;
  render();
  closeSidebar();
  textarea.focus();
});

document.querySelector("#menu-button").addEventListener("click", () => {
  sidebar.classList.add("open");
  backdrop.classList.add("visible");
});
document.querySelector("#sidebar-close").addEventListener("click", closeSidebar);
backdrop.addEventListener("click", closeSidebar);

document.querySelector("#share-button").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  const originalLabel = button.querySelector("span").textContent;
  try {
    const transcript = activeChat().messages
      .map((message) => `${message.role === "user" ? "You" : "Faraz AI"}:\n${message.content}`)
      .join("\n\n");
    if (!transcript) {
      button.querySelector("span").textContent = "No messages";
      window.setTimeout(() => {
        button.querySelector("span").textContent = originalLabel;
      }, 1400);
      return;
    }
    await navigator.clipboard.writeText(transcript);
    button.querySelector("span").textContent = "Copied";
    window.setTimeout(() => {
      button.querySelector("span").textContent = originalLabel;
    }, 1400);
  } catch {
    button.querySelector("span").textContent = "Unavailable";
    window.setTimeout(() => {
      button.querySelector("span").textContent = originalLabel;
    }, 1600);
  }
});

document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    document.querySelector("#new-chat").click();
  }
  if (event.key === "Escape") closeSidebar();
});

render();
updateComposer();
