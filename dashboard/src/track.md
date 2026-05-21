---
title: Login Tracker
toc: false
sidebar: false
---

<style>
#tracker-wrap { max-width: 860px; margin: 0 auto }
#tracker-gate { text-align: center; margin-top: 8rem; opacity: .35; font-size: .9em }
table { width: 100%; border-collapse: collapse; font-size: .87em }
th { text-transform: uppercase; font-size: .7em; letter-spacing: .9px; opacity: .4;
     font-weight: 700; padding: .45rem .7rem; border-bottom: 1px solid var(--theme-foreground-faintest); text-align: left }
td { padding: .5rem .7rem; border-bottom: 1px solid var(--theme-background) }
tr:hover td { background: var(--theme-background-alt) }
.t-time  { color: #7eb8f7; font-family: monospace; white-space: nowrap }
.t-team  { font-weight: 600 }
.t-ua    { opacity: .3; font-size: .78em; max-width: 240px; overflow: hidden;
           text-overflow: ellipsis; white-space: nowrap }
.bdg     { font-size: .62em; font-weight: 700; letter-spacing: .8px; padding: 2px 5px;
           border-radius: 3px; margin-right: 4px; vertical-align: middle }
.bdg-team{ background: var(--nbr-green, #43632d); color: #b8d490 }
.bdg-car { background: var(--theme-foreground-faintest); color: var(--theme-foreground-muted) }
.hdr     { display: flex; align-items: baseline; gap: 1rem; margin-bottom: 1rem }
.hdr h2  { font-size: 1em; font-weight: 800; text-transform: uppercase; letter-spacing: .5px; margin: 0 }
.count   { font-size: .8em; opacity: .4 }
.refresh { background: transparent; border: 1px solid var(--theme-foreground-faint);
           color: inherit; padding: 3px 10px; border-radius: 4px; cursor: pointer;
           font-size: .78em; font-family: inherit; margin-left: auto }
.refresh:hover { border-color: #7eb8f7; color: #7eb8f7 }
.ts-info { font-size: .78em; opacity: .35; margin-top: .6rem }
.setup   { background: var(--theme-background-alt);
           border-left: 3px solid #f0a500; border-radius: 6px;
           padding: 1rem 1.2rem; font-size: .85em; line-height: 1.8 }
.setup code { background: var(--theme-background); padding: 1px 5px;
              border-radius: 3px; font-family: monospace }
</style>

```js
import { WEBHOOK_URL } from "./auth/auth-table.js";

// ── Auth gate — requires correct URL hash ──────────────────────────────────
const SECRET_HASH = "706-R9OXtji6lpGd";
const gate   = document.getElementById("tracker-gate");
const wrap   = document.getElementById("tracker-wrap");
const tbody  = document.getElementById("t-body");
const countEl = document.getElementById("t-count");
const tsEl   = document.getElementById("t-ts");

function hasAccess() {
  return location.hash === "#" + SECRET_HASH;
}

// ── Helpers ────────────────────────────────────────────────────────────────
function fmt(raw) {
  const d = new Date(raw);
  if (isNaN(d)) return String(raw);
  return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit", year: "2-digit" })
    + " " + d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function isCar(name) { return /·\s*(Car\s*)?#/i.test(name); }

function row(entry) {
  const tr = document.createElement("tr");
  const level = isCar(entry.team) ? "car" : "team";
  tr.innerHTML = `
    <td class="t-time">${fmt(entry.ts)}</td>
    <td class="t-team">
      <span class="bdg bdg-${level}">${level.toUpperCase()}</span>${entry.team}
    </td>
    <td class="t-ua">${entry.ua || "—"}</td>`;
  return tr;
}

// ── Fetch & render ─────────────────────────────────────────────────────────
async function load() {
  if (!WEBHOOK_URL) return;
  try {
    const res  = await fetch(WEBHOOK_URL);
    const data = await res.json();
    const sorted = [...data].reverse();
    tbody.innerHTML = "";
    for (const e of sorted) tbody.appendChild(row(e));
    countEl.textContent = sorted.length + " connexion" + (sorted.length > 1 ? "s" : "");
    tsEl.textContent    = "Mis à jour " + new Date().toLocaleTimeString("fr-FR");
  } catch (err) {
    tsEl.textContent = "Erreur : " + err.message;
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
if (!hasAccess()) {
  gate.style.display = "block";
} else {
  wrap.style.display = "block";
  if (!WEBHOOK_URL) {
    tbody.innerHTML = `<tr><td colspan="3">
      <div class="setup">
        ⚙️ <strong>WEBHOOK_URL non configurée.</strong><br>
        1. Crée un Google Sheet avec un onglet <code>Logins</code><br>
        2. Extensions → Apps Script → colle le code ci-dessous → Déployer → Web App<br>
        &nbsp;&nbsp;&nbsp;<em>Execute as: Me · Who has access: Anyone</em><br>
        3. Copie l'URL de déploiement dans <code>dashboard/src/auth/auth-table.js</code> → <code>WEBHOOK_URL</code>
      </div>
    </td></tr>`;
  } else {
    load();
    setInterval(load, 30000);
  }
}
```

<div id="tracker-gate" style="display:none">⛔ Accès refusé</div>

<div id="tracker-wrap" style="display:none">
  <div class="hdr">
    <h2>Login Tracker</h2>
    <span id="t-count" class="count"></span>
    <button class="refresh" onclick="load()">↻</button>
  </div>
  <table>
    <thead>
      <tr><th>Heure</th><th>Équipe / Voiture</th><th>Navigateur</th></tr>
    </thead>
    <tbody id="t-body"></tbody>
  </table>
  <div id="t-ts" class="ts-info"></div>
</div>
