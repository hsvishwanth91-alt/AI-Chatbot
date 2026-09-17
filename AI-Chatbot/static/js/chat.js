const form = document.querySelector("#chatForm");
const input = document.querySelector("#messageInput");
const messages = document.querySelector("#messages");
const sendButton = document.querySelector("#sendButton");
const clearButton = document.querySelector("#clearButton");
const typingIndicator = document.querySelector("#typingIndicator");

function scrollToLatest() {
  messages.scrollTop = messages.scrollHeight;
}

function setLoading(isLoading) {
  sendButton.disabled = isLoading;
  input.disabled = isLoading;
  typingIndicator.classList.toggle("hidden", !isLoading);
  if (!isLoading) {
    input.focus();
  }
}

function resizeInput() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 144)}px`;
}

function addMessage(role, text, isError = false) {
  const row = document.createElement("article");
  row.className = `message-row ${role}${isError ? " error" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = role === "user" ? "You" : "AI";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = text;

  row.append(avatar, bubble);
  messages.appendChild(row);
  scrollToLatest();
}

async function sendMessage(message) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "The assistant could not reply right now.");
  }
  return data.reply;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = input.value.trim();
  if (!message) {
    addMessage("assistant", "Please type a message before sending.", true);
    return;
  }

  addMessage("user", message);
  input.value = "";
  resizeInput();
  setLoading(true);

  try {
    const reply = await sendMessage(message);
    addMessage("assistant", reply);
  } catch (error) {
    addMessage("assistant", error.message, true);
  } finally {
    setLoading(false);
  }
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

input.addEventListener("input", resizeInput);

clearButton.addEventListener("click", async () => {
  await fetch("/api/clear", { method: "POST" }).catch(() => {});
  messages.innerHTML = "";
  addMessage(
    "assistant",
    "Chat cleared. Send a new message when you are ready."
  );
  input.focus();
});

resizeInput();
input.focus();
