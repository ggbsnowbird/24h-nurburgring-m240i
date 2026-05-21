#!/usr/bin/env python3
"""
Generate dashboard/src/credentials.md from teams_credentials.csv.

The output file embeds credentials as a JS const — it is gitignored and must
be (re)generated locally whenever credentials change, then deployed.

Usage:
  python3 tools/generate_credentials_page.py [--csv /path/to/teams_credentials.csv]
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent
CSV_DEFAULT = REPO_ROOT / "teams_credentials.csv"
PAGE_OUT    = REPO_ROOT / "dashboard/src/credentials.md"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", metavar="PATH", default=str(CSV_DEFAULT))
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"CSV not found: {csv_path}\nRun generate_team_credentials.py first.")

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Build grouped structure: class -> team_name -> {team, cars[]}
    by_class = defaultdict(lambda: defaultdict(lambda: {"team": None, "cars": []}))
    for r in rows:
        raw = r["team"].split(" · Car #")[0]
        cls = r["class"]
        if r["level"] == "TEAM":
            by_class[cls][raw]["team"] = r
        else:
            by_class[cls][raw]["cars"].append(r)

    # Flatten into a structure the JS page can use
    sections = []
    for cls in ["M240i", "SP9"]:
        teams = []
        for team_name in sorted(by_class[cls].keys()):
            g = by_class[cls][team_name]
            cars = sorted(g["cars"], key=lambda x: int(x["car_no"]) if x["car_no"] else 0)
            teams.append({
                "name": team_name,
                "team": {"login": g["team"]["login"], "password": g["team"]["password"]} if g["team"] else None,
                "cars": [{"no": c["car_no"], "login": c["login"], "password": c["password"]} for c in cars],
            })
        sections.append({"class": cls, "teams": teams})

    data_json = json.dumps(sections, ensure_ascii=False, separators=(",", ":"))

    page = f'''\
---
title: Credentials
toc: false
sidebar: false
---

<style>
.creds-wrap{{max-width:820px;margin:0 auto}}
.creds-search{{width:100%;padding:.6rem .9rem;background:var(--theme-background-alt);border:1px solid var(--theme-foreground-faint);border-radius:6px;color:inherit;font-size:.9em;font-family:inherit;margin-bottom:1.5rem;box-sizing:border-box}}
.creds-search:focus{{outline:none;border-color:var(--nbr-green,#43632d)}}
.cls-title{{font-size:.85em;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;opacity:.45;margin:2rem 0 .6rem;padding-bottom:.35rem;border-bottom:1px solid var(--theme-foreground-faintest)}}
.team-block{{margin-bottom:.35rem;border-radius:6px;overflow:hidden;background:var(--theme-background-alt)}}
.cred-row{{display:flex;align-items:center;gap:.55rem;padding:.5rem .75rem;border-bottom:1px solid var(--theme-background);font-size:.87em}}
.cred-row:last-child{{border-bottom:none}}
.cred-row.is-team{{background:color-mix(in srgb,var(--nbr-green,#43632d) 18%,var(--theme-background-alt))}}
.cred-row.is-car{{padding-left:1.3rem}}
.bdg{{font-size:.6em;font-weight:700;letter-spacing:.9px;padding:2px 5px;border-radius:3px;flex-shrink:0;text-transform:uppercase}}
.bdg-team{{background:var(--nbr-green,#43632d);color:#b8d490}}
.bdg-car{{background:var(--theme-foreground-faintest);color:var(--theme-foreground-muted)}}
.cred-name{{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;opacity:.75}}
.pill{{font-family:var(--mono,monospace);cursor:pointer;padding:2px 7px;border-radius:4px;border:1px solid transparent;transition:background .12s,border-color .12s;flex-shrink:0;user-select:none;white-space:nowrap}}
.pill-login{{color:#7eb8f7}} .pill-pw{{color:#f0c040}}
.pill:hover{{background:var(--theme-foreground-faintest);border-color:var(--theme-foreground-faint)}}
.sep{{opacity:.25;flex-shrink:0}}
.toast{{position:fixed;bottom:1.4rem;left:50%;transform:translateX(-50%);background:var(--nbr-green,#43632d);color:#fff;padding:.45rem 1.1rem;border-radius:20px;font-size:.82em;opacity:0;transition:opacity .18s;pointer-events:none;z-index:999}}
.toast.on{{opacity:1}}
.team-block.hidden{{display:none}}
</style>

```js
const SECTIONS = {data_json};

function pill(text, cls) {{
  const el = document.createElement("span");
  el.className = "pill " + cls;
  el.textContent = text;
  el.title = "Copier";
  el.onclick = () => {{
    navigator.clipboard.writeText(text).then(() => {{
      const t = document.getElementById("creds-toast");
      t.classList.add("on");
      clearTimeout(t._tid);
      t._tid = setTimeout(() => t.classList.remove("on"), 1400);
    }});
  }};
  return el;
}}

function buildRow(name, loginStr, pw, isTeam) {{
  const row = document.createElement("div");
  row.className = "cred-row " + (isTeam ? "is-team" : "is-car");

  const bdg = document.createElement("span");
  bdg.className = "bdg " + (isTeam ? "bdg-team" : "bdg-car");
  bdg.textContent = isTeam ? "TEAM" : "CAR";

  const nameEl = document.createElement("span");
  nameEl.className = "cred-name";
  nameEl.textContent = name;

  const sep = document.createElement("span");
  sep.className = "sep";
  sep.textContent = "/";

  row.append(bdg, nameEl, pill(loginStr, "pill-login"), sep, pill(pw, "pill-pw"));
  return row;
}}

function render(query) {{
  const wrap = document.getElementById("creds-body");
  if (!wrap) return;
  wrap.innerHTML = "";
  const q = (query || "").toLowerCase();

  for (const sec of SECTIONS) {{
    const h = document.createElement("div");
    h.className = "cls-title";
    h.textContent = sec.class === "M240i" ? "M240i Racing Cup" : "SP9 / GT3";
    wrap.appendChild(h);

    for (const team of sec.teams) {{
      const block = document.createElement("div");
      block.className = "team-block";
      block.dataset.search = (team.name + " " +
        (team.team ? team.team.login : "") + " " +
        team.cars.map(c => c.no + " " + c.login).join(" ")).toLowerCase();

      if (team.team) block.appendChild(buildRow(team.name, team.team.login, team.team.password, true));
      for (const c of team.cars) {{
        block.appendChild(buildRow(team.name + " · #" + c.no, c.login, c.password, false));
      }}

      if (q && !block.dataset.search.includes(q)) block.classList.add("hidden");
      wrap.appendChild(block);
    }}
  }}
}}

document.addEventListener("DOMContentLoaded", () => {{
  render("");
  const inp = document.getElementById("creds-search");
  if (inp) inp.addEventListener("input", e => render(e.target.value));
}});
```

<div class="creds-wrap">
  <input id="creds-search" class="creds-search" type="search" placeholder="Rechercher une équipe, un numéro...">
  <div id="creds-body"></div>
</div>
<div class="toast" id="creds-toast">Copié ✓</div>
'''

    PAGE_OUT.parent.mkdir(parents=True, exist_ok=True)
    PAGE_OUT.write_text(page, encoding="utf-8")
    print(f"Generated {PAGE_OUT}  ({len(rows)} credentials)")


if __name__ == "__main__":
    main()
