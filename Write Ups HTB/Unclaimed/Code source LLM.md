```js
const log = document.getElementById("log"),
  q = document.getElementById("q"),
  sendBtn = document.getElementById("sendBtn");
const welcome =
  "Welcome to HTB Airlines TracerBot. I can look up lost or delayed baggage records.\n\nTry: *status for tag HTB0012345* or *scan history for tag HTB0067890*.";
function esc(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
function md(s) {
  let x = esc(s);
  const B = [];
  const stash = (h) => {
    B.push(h);
    return "%%B" + (B.length - 1) + "%%";
  };
  x = x.replace(/```([\s\S]*?)```/g, (m, c) =>
    stash(
      "<pre><code>" + c.replace(/^\n/, "").replace(/\n$/, "") + "</code></pre>",
    ),
  );
  x = x.replace(
    /(^|\n)(\|[^\n]*\|)\n(\|[ :\-|]+\|)\n((?:\|[^\n]*\|(?:\n|$))*)/g,
    (m, pre, head, sep, body) => {
      const cells = (r) =>
        r
          .trim()
          .replace(/^\|/, "")
          .replace(/\|$/, "")
          .split("|")
          .map((c) => c.trim());
      const th =
        "<tr>" +
        cells(head)
          .map((c) => "<th>" + c + "</th>")
          .join("") +
        "</tr>";
      const tb = body
        .trim()
        .split("\n")
        .filter((l) => l.trim())
        .map(
          (r) =>
            "<tr>" +
            cells(r)
              .map((c) => "<td>" + c + "</td>")
              .join("") +
            "</tr>",
        )
        .join("");
      return (
        pre +
        stash(
          "<table><thead>" + th + "</thead><tbody>" + tb + "</tbody></table>",
        )
      );
    },
  );
  x = x.replace(/`([^`]+)`/g, "<code>$1</code>");
  x = x.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  x = x.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  x =
    '<div class="md"><p>' +
    x.replace(/\n{2,}/g, "</p><p>").replace(/\n/g, "<br>") +
    "</p></div>";
  x = x.replace(/%%B(\d+)%%/g, (m, i) => "</p>" + B[i] + "<p>");
  return x.replace(/<p>(<br>)*<\/p>/g, "");
}
function add(cls, html) {
  const d = document.createElement("div");
  d.className = "msg " + cls;
  d.innerHTML = html;
  log.appendChild(d);
  window.scrollTo(0, document.body.scrollHeight);
  return d;
}
function addBot(text) {
  add("b", md(text || "No response."));
}
function addThinking() {
  return add(
    "b",
    '<span class="thinking">TracerBot is working <span class="dot"></span><span class="dot"></span><span class="dot"></span></span>',
  );
}
function newChat() {
  log.innerHTML = "";
  add("b welcome", md(welcome));
  q.value = "";
  q.focus();
}
async function send() {
  const m = q.value.trim();
  if (!m) return;
  add("u", esc(m));
  q.value = "";
  sendBtn.disabled = true;
  const bubble = addThinking();
  try {
    const r = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ msg: m }),
    });
    const j = await r.json();
    bubble.remove();
    addBot(j.reply || j.error);
  } catch (e) {
    bubble.remove();
    addBot(String(e));
  } finally {
    sendBtn.disabled = false;
    q.focus();
  }
}
q.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) send();
});
newChat();
```