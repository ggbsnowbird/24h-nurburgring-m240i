// Auth guard utilities — enforcement happens via inline script in observablehq.config.js head

export function getTeam() {
  return localStorage.getItem("nbr_team");
}

export function logout() {
  localStorage.removeItem("nbr_team");
  document.cookie = "nbr_team=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Lax";
  location.replace("/login");
}

export function renderAuthBadge() {
  const team = getTeam();
  if (!team) return null;

  const el = document.createElement("div");
  el.style.cssText =
    "display:flex;align-items:center;gap:.7rem;font-size:.82em;margin-bottom:1rem;" +
    "padding:.45rem .9rem;background:var(--theme-background-alt);" +
    "border-radius:4px;border-left:3px solid var(--nbr-green,#43632d)";

  const label = document.createElement("span");
  label.innerHTML = `Connecté : <strong style="color:var(--nbr-gold,#f0c040)">${team}</strong>`;

  const btn = document.createElement("button");
  btn.textContent = "Déconnexion";
  btn.style.cssText =
    "margin-left:auto;padding:2px 8px;font-size:.8em;cursor:pointer;" +
    "border:1px solid currentColor;border-radius:3px;background:transparent;font-family:inherit";
  btn.addEventListener("click", logout);

  el.append(label, btn);
  return el;
}
