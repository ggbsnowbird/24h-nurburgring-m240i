#!/usr/bin/env python3
import sqlite3, json
from pathlib import Path

db = Path(__file__).parent.parent.parent.parent / "m240i_sector_times.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("""
    SELECT
        ref_car_no, ref_stint_no, ref_driver,
        ref_window_start, ref_window_end,
        comp_car_no, comp_car_drivers, comp_driver,
        laps_in_window,
        ROUND(best_laptime_sec,3) AS best_laptime_sec,
        ROUND(avg_laptime_sec,3)  AS avg_laptime_sec,
        rank_by_best, rank_by_avg
    FROM stint_ranking
    WHERE best_laptime_sec IS NOT NULL
      AND best_laptime_sec < 690
    ORDER BY ref_car_no, ref_stint_no, rank_by_best
""").fetchall()

print(json.dumps([dict(r) for r in rows]))
conn.close()
