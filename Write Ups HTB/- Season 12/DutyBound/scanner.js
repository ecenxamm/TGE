async function postJSON(url, body) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  let data = {};
  try { data = await r.json(); } catch (e) {}
  return { status: r.status, data };
}

function initCart() {
  document.querySelectorAll(".btn-add").forEach(function (b) {
    b.addEventListener("click", async function () {
      b.classList.add("added");
      const res = await postJSON("/cart/add", { sku: b.dataset.sku });
      const n = res.data && res.data.cart_size;
      if (typeof n !== "undefined") {
        const badge = document.getElementById("cart-badge");
        const barc = document.getElementById("bar-count");
        if (badge) badge.textContent = n;
        if (barc) barc.textContent = n;
      }
      setTimeout(function () { b.classList.remove("added"); }, 500);
    });
  });
}

function initScanner() {
  const btn = document.getElementById("scan-btn");
  const screen = document.getElementById("scanner-screen");
  const msg = document.getElementById("scanner-msg");
  const status = document.getElementById("scan-status");
 (!btn) return;
 if 
  btn.addEventListener("click", async function () {
    btn.disabled = true;
    status.innerHTML = "";
    screen.classList.add("scanning");
    msg.textContent = "Scanning…";

    const pending = postJSON("/checkout/boarding-pass/verify", { raw: "" });
    await new Promise(function (r) { setTimeout(r, 1400); });
    try { await pending; } catch (e) {}

    screen.classList.remove("scanning");
    msg.textContent = "No barcode detected";
    status.innerHTML =
      '<div class="scan-fail">Couldn’t detect a boarding pass. ' +
      "Please reposition it and try again.</div>";
    btn.disabled = false;
  });
}