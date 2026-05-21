---
title: Login Tracker
toc: false
sidebar: false
---

<style>
#gate  { text-align:center; margin-top:8rem; opacity:.3; font-size:.9em }
#wrap  { max-width:860px; margin:0 auto }
.hdr   { display:flex; align-items:baseline; gap:.8rem; margin-bottom:1rem }
.hdr h2{ font-size:1em; font-weight:800; text-transform:uppercase; letter-spacing:.5px; margin:0 }
.cnt   { font-size:.8em; opacity:.4 }
.rfr   { margin-left:auto; background:transparent; border:1px solid var(--theme-foreground-faint);
         color:inherit; padding:3px 10px; border-radius:4px; cursor:pointer;
         font-size:.78em; font-family:inherit }
.rfr:hover { border-color:#7eb8f7; color:#7eb8f7 }
.ts    { font-size:.75em; opacity:.3; margin-top:.5rem }
table  { width:100%; border-collapse:collapse; font-size:.87em }
th     { text-transform:uppercase; font-size:.7em; letter-spacing:.9px; opacity:.4;
         font-weight:700; padding:.45rem .7rem;
         border-bottom:1px solid var(--theme-foreground-faintest); text-align:left }
td     { padding:.5rem .7rem; border-bottom:1px solid var(--theme-background) }
tr:hover td { background:var(--theme-background-alt) }
.tm    { color:#7eb8f7; font-family:monospace; white-space:nowrap }
.nm    { font-weight:600 }
.ua    { opacity:.3; font-size:.78em; max-width:260px; overflow:hidden;
         text-overflow:ellipsis; white-space:nowrap }
.b     { font-size:.62em; font-weight:700; letter-spacing:.8px; padding:2px 5px;
         border-radius:3px; margin-right:4px }
.bt    { background:var(--nbr-green,#43632d); color:#b8d490 }
.bc    { background:var(--theme-foreground-faintest); color:var(--theme-foreground-muted) }
.empty { text-align:center; padding:3rem; opacity:.3; font-size:.9em }
.setup { background:var(--theme-background-alt);
         border-left:3px solid #f0a500; border-radius:6px;
         padding:1rem 1.2rem; font-size:.85em; line-height:1.8; margin:1rem 0 }
.setup code { background:var(--theme-background); padding:1px 5px; border-radius:3px; font-family:monospace }
</style>

```js
import { GIST_ID, GIST_TOKEN } from "./auth/gist-config.js";

const SECRET = "706-R9OXtji6lpGd";

const gate = document.getElementById("gate");
const wrap = document.getElementById("wrap");

if (location.hash !== "#" + SECRET) {
  gate.style.display = "block";
} else {
  wrap.style.display = "block";
  init();
}

function fmt(ts) {
  const d = new Date(+ts);
  return d.toLocaleDateString("fr-FR", { day:"2-digit", month:"2-digit", year:"2-digit" })
    + " " + d.toLocaleTimeString("fr-FR", { hour:"2-digit", minute:"2-digit", second:"2-digit" });
}

async function load() {
  const tbody = document.getElementById("tbody");
  const cnt   = document.getElementById("cnt");
  const ts    = document.getElementById("ts");

  if (!GIST_TOKEN) {
    tbody.innerHTML = `<tr><td colspan="3"><div class="setup">
      ⚙️ <strong>Token manquant.</strong> Une seule étape :<br>
      1. <a href="https://github.com/settings/tokens/new?scopes=gist&description=NBR+tracker" target="_blank">
         Créer un token GitHub</a> avec scope <code>gist</code><br>
      2. <code>gh secret set GIST_TOKEN --body "TON_TOKEN"</code><br>
      3. <code>git commit --allow-empty -m "ci: enable gist tracking" && git push</code>
    </div></td></tr>`;
    return;
  }

  ts.textContent = "Chargement…";
  try {
    const r    = await fetch(`https://api.github.com/gists/${GIST_ID}`,
                   { headers: { Authorization: `Bearer ${GIST_TOKEN}` } });
    const data = await r.json();
    const logs = JSON.parse(data.files["logins.json"].content || "[]").reverse();

    tbody.innerHTML = "";
    if (!logs.length) {
      tbody.innerHTML = '<tr><td colspan="3" class="empty">Aucune connexion enregistrée</td></tr>';
    } else {
      for (const e of logs) {
        const isCar = /·\s*(Car\s*)?#/i.test(e.team);
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="tm">${fmt(e.ts)}</td>
          <td class="nm"><span class="b ${isCar ? "bc" : "bt"}">${isCar ? "CAR" : "TEAM"}</span>${e.team}</td>
          <td class="ua">${e.ua || "—"}</td>`;
        tbody.appendChild(tr);
      }
    }
    cnt.textContent = logs.length + " connexion" + (logs.length > 1 ? "s" : "");
    ts.textContent  = "↻ " + new Date().toLocaleTimeString("fr-FR");
  } catch (err) {
    ts.textContent = "Erreur : " + err.message;
  }
}

function init() {
  load();
  setInterval(load, 30000);
  document.getElementById("rfr").onclick = load;
}
```

<div id="gate" style="display:none">⛔</div>

<div id="wrap" style="display:none">
  <div class="hdr">
    <h2>Login Tracker — NBR 2026</h2>
    <span id="cnt" class="cnt"></span>
    <button id="rfr" class="rfr">↻ Actualiser</button>
  </div>
  <table>
    <thead><tr><th>Heure</th><th>Équipe / Voiture</th><th>Navigateur</th></tr></thead>
    <tbody id="tbody"></tbody>
  </table>
  <div id="ts" class="ts"></div>
</div>
