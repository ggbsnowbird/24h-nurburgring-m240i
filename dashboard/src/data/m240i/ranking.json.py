#!/usr/bin/env python3
import sqlite3, json
from pathlib import Path
from datetime import datetime, timezone, timedelta

CEST = timedelta(hours=2)
VIEW = 'stint_ranking_m240i'

db = Path(__file__).parent.parent.parent.parent.parent / "nbr_sector_times.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def utc_to_cest(s):
    if not s: return None
    try:
        dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)
        return (dt + CEST).strftime('%Y-%m-%dT%H:%M:%S')
    except:
        return s

rows = cur.execute(f"""
    SELECT
        ref_car_no, ref_stint_no, ref_driver,
        ref_window_start, ref_window_end,
        comp_car_no, comp_car_drivers, comp_driver,
        laps_in_window,
        ROUND(best_laptime_sec,3) AS best_laptime_sec,
        ROUND(avg_laptime_sec,3)  AS avg_laptime_sec,
        rank_by_best, rank_by_avg
    FROM {VIEW}
    WHERE best_laptime_sec IS NOT NULL
      AND best_laptime_sec < 690
    ORDER BY ref_car_no, ref_stint_no, rank_by_best
""").fetchall()

out = []
for r in rows:
    d = dict(r)
    d['ref_window_start'] = utc_to_cest(d['ref_window_start'])
    d['ref_window_end']   = utc_to_cest(d['ref_window_end'])
    out.append(d)

print(json.dumps(out))
conn.close()
