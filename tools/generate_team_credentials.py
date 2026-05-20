#!/usr/bin/env python3
"""
Generate team credentials for the NBR dashboard.

Two credential levels are produced:
  TEAM — one per distinct team name (login = slugified team name)
  CAR  — one per car entry        (login = car number as string)

Idempotent: if teams_credentials.csv already exists, existing passwords are
preserved. Only new logins get fresh passwords.

Requires import_team_names.py to have been run first (team_name column in DB).

Outputs:
  <repo-root>/teams_credentials.csv  — distribute to teams, DO NOT commit
  dashboard/src/auth/auth-table.js   — SHA-256 lookup table, safe to commit

Usage:
  python3 tools/generate_team_credentials.py [--db /path/to/nbr_sector_times.db]
"""
import argparse
import csv
import hashlib
import random
import re
import string
import sqlite3
import sys
import unicodedata
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent

def find_db(hint=None) -> Path:
    if hint:
        p = Path(hint)
        if not p.exists():
            sys.exit(f"DB not found: {hint}")
        return p
    candidate = REPO_ROOT
    for _ in range(5):
        p = candidate / "nbr_sector_times.db"
        if p.exists():
            return p
        candidate = candidate.parent
    sys.exit(
        "Could not find nbr_sector_times.db. "
        "Pass --db /path/to/nbr_sector_times.db explicitly."
    )

CSV_OUT       = REPO_ROOT / "teams_credentials.csv"
AUTH_TABLE_JS = REPO_ROOT / "dashboard/src/auth/auth-table.js"

# ── Slug helpers ────────────────────────────────────────────────────────────────
_STRIP_WORDS = ["motorsport", "racing", "team", "gp"]

def slugify(name: str) -> str:
    """Human-readable slug from a team name.

    Steps:
      1. Normalise unicode → ASCII  (Mühlner→Muhlner, Dörr→Dorr)
      2. Lowercase
      3. Remove noise words (motorsport / racing / team / gp) as whole words
      4. Replace non-alphanumeric runs with hyphens
      5. Collapse and trim hyphens
    """
    nfkd = unicodedata.normalize("NFKD", name)
    s    = nfkd.encode("ascii", "ignore").decode("ascii").lower()
    for w in _STRIP_WORDS:
        s = re.sub(rf"\b{w}\b", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s

def team_login(team_name: str) -> str:
    return slugify(team_name)               # e.g. "adrenalin", "rowe"

def car_login(car_no: int) -> str:
    return str(car_no)                      # e.g. "652", "1", "911"

# ── Password / hash helpers ────────────────────────────────────────────────────
_RNG   = random.SystemRandom()
_CHARS = string.ascii_letters + string.digits

def make_password(length: int = 8) -> str:
    return "".join(_RNG.choice(_CHARS) for _ in range(length))

def sha256_key(login: str, password: str) -> str:
    return hashlib.sha256(f"{login}:{password}".encode()).hexdigest()

# ── Load existing credentials (idempotency) ─────────────────────────────────────
def load_existing() -> dict:
    """Returns {login: password} from CSV if it already exists."""
    if not CSV_OUT.exists():
        return {}
    with open(CSV_OUT, newline="", encoding="utf-8") as f:
        return {row["login"]: row["password"] for row in csv.DictReader(f)}

# ── DB ─────────────────────────────────────────────────────────────────────────
def get_cars(db: Path) -> list:
    """Returns list of (car_no, team_name, drivers, class).
    Falls back to NULL team_name if import_team_names.py has not been run.
    """
    conn = sqlite3.connect(db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(cars)")}
    if "team_name" not in cols:
        sys.exit(
            "Column team_name not found in cars table.\n"
            "Run: python3 tools/import_team_names.py --db <DB> first."
        )
    rows = conn.execute(
        "SELECT car_no, team_name, drivers, class FROM cars ORDER BY class, car_no"
    ).fetchall()
    conn.close()
    return rows

# ── Main ────────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", metavar="PATH", help="Path to nbr_sector_times.db")
    args = parser.parse_args()

    db       = find_db(args.db)
    print(f"Using DB: {db}")

    existing = load_existing()
    cars     = get_cars(db)

    # ── Build credential rows ─────────────────────────────────────────────────
    csv_rows   = []
    new_count  = 0

    def get_or_create(login: str) -> tuple:
        nonlocal new_count
        if login in existing:
            return existing[login], False
        pw = make_password()
        new_count += 1
        return pw, True

    # 1. TEAM level — one per distinct team name (ordered by class, team_name)
    seen_teams: dict = {}   # team_name → password (for dedup within a run)
    for car_no, team_name, drivers, cls in cars:
        if team_name is None:
            team_name = f"Car #{car_no}"  # fallback if import not run
        if team_name in seen_teams:
            continue
        login    = team_login(team_name)
        password, _ = get_or_create(login)
        seen_teams[team_name] = password
        csv_rows.append({
            "level":  "TEAM",
            "team":   team_name,
            "class":  cls,
            "car_no": "",
            "login":  login,
            "password": password,
        })

    # 2. CAR level — one per car
    for car_no, team_name, drivers, cls in cars:
        if team_name is None:
            team_name = f"Car #{car_no}"
        login    = car_login(car_no)
        display  = f"{team_name} · Car #{car_no}"
        password, _ = get_or_create(login)
        csv_rows.append({
            "level":  "CAR",
            "team":   display,
            "class":  cls,
            "car_no": car_no,
            "login":  login,
            "password": password,
        })

    # ── Write CSV ─────────────────────────────────────────────────────────────
    fieldnames = ["level", "team", "class", "car_no", "login", "password"]
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"Wrote {len(csv_rows)} entries to {CSV_OUT} ({new_count} new passwords)")

    # ── Write auth-table.js ───────────────────────────────────────────────────
    entries = []
    for row in csv_rows:
        key  = sha256_key(row["login"], row["password"])
        name = row["team"].replace('"', "'")
        entries.append(f'  "{key}": "{name}"')

    AUTH_TABLE_JS.parent.mkdir(parents=True, exist_ok=True)
    AUTH_TABLE_JS.write_text(
        "// Auto-generated by tools/generate_team_credentials.py — DO NOT EDIT BY HAND\n"
        "// REPLACE: Google Apps Script Web App URL\n"
        'export const WEBHOOK_URL = "";\n'
        "\n"
        "export const AUTH_TABLE = {\n"
        + ",\n".join(entries) + "\n"
        "};\n",
        encoding="utf-8",
    )
    print(f"Wrote auth table ({len(csv_rows)} entries) to {AUTH_TABLE_JS}")

if __name__ == "__main__":
    main()
