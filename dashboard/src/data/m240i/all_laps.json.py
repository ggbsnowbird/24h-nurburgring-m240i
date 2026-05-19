#!/usr/bin/env python3
import sqlite3, json
from pathlib import Path
from datetime import datetime, timezone, timedelta

CEST = timedelta(hours=2)
CLASS = 'M240i'

db = Path(__file__).parent.parent.parent.parent.parent / "nbr_sector_times.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("""
    SELECT sub.* FROM (
        SELECT
            lt.car_no, lt.lap_no, lt.lap_time, lt.lap_day_time,
            s.driver_name,
            CASE
                WHEN LENGTH(lt.lap_time)-LENGTH(REPLACE(lt.lap_time,':',''))=1
                THEN CAST(SUBSTR(lt.lap_time,1,INSTR(lt.lap_time,':')-1) AS REAL)*60
                     + CAST(SUBSTR(lt.lap_time,INSTR(lt.lap_time,':')+1) AS REAL)
                ELSE NULL
            END AS lap_sec
        FROM live_timing_laps lt
        JOIN stints s ON s.car_no=lt.car_no AND s.class=lt.class
                     AND lt.lap_no > s.lap_start
                     AND lt.lap_no <= s.lap_end
        WHERE lt.lap_day_time IS NOT NULL
          AND lt.class = ?
        ORDER BY lt.lap_day_time
    ) sub WHERE sub.lap_sec IS NOT NULL AND sub.lap_sec < 690
""", (CLASS,)).fetchall()

data = []
for r in rows:
    dt_utc = datetime.strptime(r['lap_day_time'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)
    dt_cest = dt_utc + CEST
    data.append({
        'car_no':   r['car_no'],
        'lap_no':   r['lap_no'],
        'driver':   r['driver_name'],
        'day_time': dt_cest.strftime('%Y-%m-%dT%H:%M:%S'),
        'lap_sec':  round(r['lap_sec'], 3),
        'lap_time': r['lap_time']
    })

print(json.dumps(data))
conn.close()
