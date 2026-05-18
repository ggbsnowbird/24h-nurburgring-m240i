#!/usr/bin/env python3
import sqlite3, json
from pathlib import Path
from datetime import datetime, timezone, timedelta

CEST = timedelta(hours=2)

db = Path(__file__).parent.parent.parent.parent / "m240i_sector_times.db"
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

rows = cur.execute("""
    SELECT s.car_no, s.stint_no, s.driver_name, s.driver_no,
           s.lap_start, s.lap_end, s.lap_count,
           s.day_time_start, s.day_time_end,
           s.best_laptime,
           ROUND(s.best_laptime_sec,3) AS best_laptime_sec,
           ROUND(s.avg_laptime_sec,3)  AS avg_laptime_sec,
           c.drivers AS car_drivers
    FROM stints s
    JOIN cars c ON c.car_no = s.car_no
    WHERE s.best_laptime_sec IS NOT NULL
      AND s.best_laptime_sec < 690
      AND s.day_time_start IS NOT NULL
    ORDER BY s.car_no, s.stint_no
""").fetchall()

out = []
for r in rows:
    d = dict(r)
    d['day_time_start'] = utc_to_cest(d['day_time_start'])
    d['day_time_end']   = utc_to_cest(d['day_time_end'])
    out.append(d)

print(json.dumps(out))
conn.close()
