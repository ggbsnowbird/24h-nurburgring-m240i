#!/usr/bin/env python3
import sqlite3, json, sys
from pathlib import Path

db = Path(__file__).parent.parent.parent.parent / "m240i_sector_times.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("""
    SELECT s.car_no, s.stint_no, s.driver_name, s.driver_no,
           s.lap_start, s.lap_end, s.lap_count,
           s.day_time_start, s.day_time_end,
           s.best_laptime, ROUND(s.best_laptime_sec,3) AS best_laptime_sec,
           ROUND(s.avg_laptime_sec,3) AS avg_laptime_sec,
           c.drivers AS car_drivers
    FROM stints s
    JOIN cars c ON c.car_no = s.car_no
    WHERE s.best_laptime_sec IS NOT NULL AND s.best_laptime_sec < 1200
    ORDER BY s.car_no, s.stint_no
""").fetchall()

print(json.dumps([dict(r) for r in rows]))
conn.close()
