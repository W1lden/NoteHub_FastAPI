const prejoin = document.getElementById("prejoin");
const chat = document.getElementById("chat");
const nicknameForm = document.getElementById("nickname-form");
const nicknameInput = document.getElementById("nickname");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message");
const historyBox = document.getElementById("history");

let ws = null;

function renderEvent(obj) {
  const div = document.createElement("div");
  if (obj.type === "system") {
    div.className = "sys";
    div.textContent = `[${new Date(obj.timestamp).toLocaleTimeString()}] ${obj.text}`;
  } else {
    div.className = "msg";
    div.innerHTML = `<b>${obj.nickname}</b>: ${escapeHtml(obj.text)} <span class="t">${new Date(obj.timestamp).toLocaleTimeString()}</span>`;
  }
  historyBox.appendChild(div);
  historyBox.scrollTop = historyBox.scrollHeight;
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
}

nicknameForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const nick = nicknameInput.value.trim();
  if (!nick) return;
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/anon-chat?nickname=${encodeURIComponent(nick)}`);
  ws.onopen = () => {
    prejoin.style.display = "none";
    chat.style.display = "block";
    messageInput.focus();
  };
  ws.onmessage = (ev) => {
    try {
      const obj = JSON.parse(ev.data);
      renderEvent(obj);
    } catch {
      try {
        const obj = JSON.parse(new TextDecoder("utf-8").decode(ev.data));
        renderEvent(obj);
      } catch {}
    }
  };
  ws.onclose = () => {
    const div = document.createElement("div");
    div.className = "sys";
    div.textContent = "Соединение закрыто";
    historyBox.appendChild(div);
  };
});

messageForm.addEventListener("submit", (e) => {
  e.preventDefault();
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  const text = messageInput.value.trim();
  if (!text) return;
  ws.send(text);
  messageInput.value = "";
  messageInput.focus();
});
