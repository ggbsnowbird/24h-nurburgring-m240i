---
title: Login
toc: false
sidebar: false
---

```js
import { AUTH_TABLE, WEBHOOK_URL } from "./auth/auth-table.js";

async function sha256hex(str) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
}

const loginInput = html`<input type="text" autocomplete="username" placeholder="car-652"
  style="width:100%;box-sizing:border-box;padding:.65rem .9rem;
    border:1px solid var(--theme-foreground-faint);border-radius:4px;
    background:var(--theme-background-alt);font-size:.95em;
    font-family:inherit;color:inherit">`;

const passwordInput = html`<input type="password" autocomplete="current-password"
  style="width:100%;box-sizing:border-box;padding:.65rem .9rem;
    border:1px solid var(--theme-foreground-faint);border-radius:4px;
    background:var(--theme-background-alt);font-size:.95em;
    font-family:inherit;color:inherit">`;

const errorEl = html`<p style="display:none;color:#e53935;font-size:.85em;
  margin:.8rem 0 0;text-align:center">Identifiants incorrects.</p>`;

const submitBtn = html`<button type="submit"
  style="width:100%;padding:.75rem;background:var(--nbr-green,#43632d);color:#fff;
    border:none;border-radius:4px;font-weight:700;font-size:.95em;cursor:pointer;
    text-transform:uppercase;letter-spacing:.7px;font-family:inherit">
  Se connecter
</button>`;

const form = html`<form>
  <div style="margin-bottom:1.1rem">
    <label style="display:block;font-size:.77em;opacity:.55;margin-bottom:.35rem;
      text-transform:uppercase;letter-spacing:.6px">Login</label>
    ${loginInput}
  </div>
  <div style="margin-bottom:1.5rem">
    <label style="display:block;font-size:.77em;opacity:.55;margin-bottom:.35rem;
      text-transform:uppercase;letter-spacing:.6px">Mot de passe</label>
    ${passwordInput}
  </div>
  ${submitBtn}
  ${errorEl}
</form>`;

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const login    = loginInput.value.trim().toLowerCase();
  const password = passwordInput.value;
  if (!login || !password) return;

  const key      = await sha256hex(`${login}:${password}`);
  const teamName = AUTH_TABLE[key];

  if (teamName) {
    localStorage.setItem("nbr_team", teamName);
    const exp = new Date(Date.now() + 30 * 86400 * 1000).toUTCString();
    document.cookie = `nbr_team=${encodeURIComponent(teamName)};expires=${exp};path=/;SameSite=Lax`;
    if (WEBHOOK_URL) {
      fetch(WEBHOOK_URL, {
        method: "POST",
        keepalive: true,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ team: teamName, ts: Date.now(), ua: navigator.userAgent }),
      }).catch(() => {});
    }
    location.replace("/");
  } else {
    errorEl.style.display = "block";
    passwordInput.value = "";
    passwordInput.focus();
  }
});

display(html`<div style="max-width:360px;margin:5rem auto;padding:0 1.5rem">
  <div style="text-align:center;margin-bottom:2.5rem">
    <h1 style="font-size:1.35em;font-weight:800;margin:0 0 .4rem;letter-spacing:.3px">
      54th ADAC Ravenol 24h Nürburgring
    </h1>
    <p style="font-size:.82em;opacity:.45;margin:0">Accès équipes · Données pilotes</p>
  </div>
  ${form}
</div>`);
```
