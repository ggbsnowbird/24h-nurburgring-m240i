#!/usr/bin/env python3
"""
One-shot migration: add team_name column to the cars table and populate it.

Usage:
  python3 tools/import_team_names.py --db /path/to/nbr_sector_times.db [--dry-run]
"""
import argparse
import sqlite3
import sys
from pathlib import Path

# ── Team name mapping (car_no → team_name) ────────────────────────────────────
# Sources: gt-report.com, wikipedia, planetf1.com (May 2026)
# ⚠ Cars 19, 75 and 992 had discrepancies between the online entry list and the
#   drivers stored in the DB — verify / correct these three before running.
TEAM_NAMES = {
    # ── M240i Racing Cup ────────────────────────────────────────────────────
    195: "Adrenalin Motorsport",
    650: "Adrenalin Motorsport",
    651: "Adrenalin Motorsport",
    652: "Adrenalin Motorsport",
    653: "Adrenalin Motorsport",
    658: "JJ Motorsport",
    665: "WS Racing",
    667: "Breakell Racing",
    669: "Keeevin Motorsport",
    670: "WS Racing",
    677: "asBest Racing",
    # ── SP9 / GT3 ───────────────────────────────────────────────────────────
    1:   "ROWE RACING",
    3:   "Mercedes-AMG Team Verstappen Racing",
    4:   "Goroyan RT by Car Collection",
    5:   "Black Falcon Team EAE",
    7:   "Konrad Motorsport",
    8:   "JUTA Racing",
    11:  "SR Motorsport by Schnitzelalm",
    16:  "Scherer Sport PHX",
    17:  "Dunlop Motorsport",
    18:  "Lionspeed GP",
    19:  "Max Kruse Racing",             # ⚠ verify
    24:  "Lionspeed GP",
    26:  "PROsport Racing",
    30:  "Hankook Competition",
    32:  "Toyo Tires with Ring Racing",
    33:  "KKrämer Racing",
    34:  "Walkenhorst Motorsport",
    35:  "Walkenhorst Motorsport",
    37:  "PROsport Racing",
    39:  "Walkenhorst Motorsport",
    44:  "Falken Motorsports",
    45:  "Realize Kondo Racing with Rinaldi",
    47:  "KCMG",
    48:  "LOSCH Motorsport by Black Falcon",
    54:  "Dinamic GT",
    55:  "Dinamic GT",
    64:  "HRT Ford Racing",
    65:  "HRT Ford Racing",
    67:  "HRT Ford Racing",
    69:  "Dörr Motorsport",
    71:  "JUTA Racing",
    75:  "Max Kruse Racing",             # ⚠ verify
    77:  "Schubert Motorsport",
    80:  "Mercedes-AMG Team RAVENOL",
    84:  "Red Bull Team ABT",
    86:  "High Class Racing",
    99:  "ROWE RACING",
    123: "Mühlner Motorsport",
    130: "Red Bull Team ABT",
    786: "Renazzo Motorsport",
    911: "Manthey Racing",
    992: "Manthey Team eFuel",           # ⚠ verify (DB drivers: Griesemann)
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, metavar="PATH",
                        help="Path to nbr_sector_times.db")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done, without writing")
    args = parser.parse_args()

    db = Path(args.db)
    if not db.exists():
        sys.exit(f"DB not found: {db}")

    conn = sqlite3.connect(db)
    cur  = conn.cursor()

    # ── 1. Add column (idempotent) ────────────────────────────────────────────
    existing_cols = {row[1] for row in cur.execute("PRAGMA table_info(cars)")}
    if "team_name" not in existing_cols:
        if args.dry_run:
            print("[dry-run] ALTER TABLE cars ADD COLUMN team_name TEXT")
        else:
            cur.execute("ALTER TABLE cars ADD COLUMN team_name TEXT")
            print("Added column team_name to cars")
    else:
        print("Column team_name already exists — skipping ALTER")

    # ── 2. Update each car ────────────────────────────────────────────────────
    db_car_nos = {row[0] for row in cur.execute("SELECT car_no FROM cars")}
    missing = db_car_nos - set(TEAM_NAMES)
    if missing:
        print(f"⚠ No team_name mapping for car_no(s): {sorted(missing)}"
              " — these will be left NULL")

    updated = 0
    for car_no, team_name in TEAM_NAMES.items():
        if car_no not in db_car_nos:
            print(f"  [skip] car_no {car_no} not in DB")
            continue
        if args.dry_run:
            print(f"  [dry-run] SET team_name='{team_name}' WHERE car_no={car_no}")
        else:
            cur.execute("UPDATE cars SET team_name=? WHERE car_no=?",
                        (team_name, car_no))
            updated += 1

    if not args.dry_run:
        conn.commit()
        print(f"Updated {updated} rows.")
    conn.close()

    if not args.dry_run:
        print("Done. Run generate_team_credentials.py to regenerate credentials.")


if __name__ == "__main__":
    main()
