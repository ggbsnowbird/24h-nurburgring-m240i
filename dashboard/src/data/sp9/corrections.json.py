#!/usr/bin/env python3
import sqlite3, json
from pathlib import Path

CLASS = 'SP9'
db = Path(__file__).parent.parent.parent.parent.parent / "nbr_sector_times.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("""
    SELECT car_no, stint_no,
           original_lap_start, corrected_lap_start,
           original_lap_end,   corrected_lap_end,
           original_day_time_start, corrected_day_time_start,
           original_best_laptime, corrected_best_laptime,
           reason, corrected_at
    FROM stint_corrections
    WHERE class = ?
    ORDER BY corrected_at DESC
""", (CLASS,)).fetchall()

print(json.dumps([dict(r) for r in rows]))
conn.close()
