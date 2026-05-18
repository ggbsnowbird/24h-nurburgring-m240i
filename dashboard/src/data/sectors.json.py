#!/usr/bin/env python3
"""
Per-stint sector ranking:
- Reference window = [day_time_start - 4min, day_time_end] of each stint
- Outlap excluded (lap_no > stint.lap_start)
- Laps > 690s excluded
- For each sector (1-9): rank all drivers by best sector time in window
"""
import sqlite3, json
from pathlib import Path

db = Path(__file__).parent.parent.parent.parent / "m240i_sector_times.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def to_sec(t):
    if not t: return None
    try:
        parts = t.split(':')
        if len(parts) == 1:
            return round(float(parts[0]), 3)
        elif len(parts) == 2:
            return round(float(parts[0]) * 60 + float(parts[1]), 3)
        elif len(parts) == 3:
            return round(float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2]), 3)
    except:
        return None

stints = cur.execute("""
    SELECT s.car_no, s.stint_no, s.driver_name,
           s.day_time_start, s.day_time_end, s.lap_start, s.lap_end
    FROM stints s
    WHERE s.best_laptime_sec IS NOT NULL
      AND s.best_laptime_sec < 690
      AND s.day_time_start IS NOT NULL
""").fetchall()

output = []
sector_cols = ['sector1_time','sector2_time','sector3_time',
               'sector4_time','sector5_time','sector6_time',
               'sector7_time','sector8_time','sector9_time']

for ref in stints:
    ref_car    = ref['car_no']
    ref_stint  = ref['stint_no']
    ref_driver = ref['driver_name']
    w_start    = ref['day_time_start']
    w_end      = ref['day_time_end']

    # Use 4-min lookback on window start
    laps = cur.execute("""
        SELECT l.car_no, l.lap_no,
               l.sector1_time, l.sector2_time, l.sector3_time,
               l.sector4_time, l.sector5_time, l.sector6_time,
               l.sector7_time, l.sector8_time, l.sector9_time,
               l.laptime,
               lt.lap_day_time, s.driver_name, c.drivers AS car_drivers,
               s.lap_start
        FROM laps l
        JOIN live_timing_laps lt ON lt.car_no=l.car_no AND lt.lap_no=l.lap_no
        JOIN stints s ON s.car_no=l.car_no
                     AND l.lap_no BETWEEN s.lap_start AND s.lap_end
        JOIN cars c ON c.car_no=l.car_no
        WHERE lt.lap_day_time >= DATETIME(?, '-4 minutes')
          AND lt.lap_day_time <= ?
          AND l.lap_no > s.lap_start
    """, (w_start, w_end)).fetchall()

    # Filter: overall lap < 690s
    laps = [lap for lap in laps if to_sec(lap['laptime']) is not None
            and to_sec(lap['laptime']) < 690]

    if not laps:
        continue

    # Per driver: best sector time
    best = {}  # (car, driver, sector_idx) -> (sec, car_drivers)
    for lap in laps:
        driver = lap['driver_name']
        car    = lap['car_no']
        for i, col in enumerate(sector_cols, 1):
            s_time = to_sec(lap[col])
            if s_time is None or s_time <= 0 or s_time > 200:
                continue
            key = (car, driver, i)
            if key not in best or s_time < best[key][0]:
                best[key] = (s_time, lap['car_drivers'])

    if not best:
        continue

    # Group by sector, rank
    sectors_drivers = {}
    for (car, driver, sector), (sec, car_drivers) in best.items():
        sectors_drivers.setdefault(sector, []).append({
            'comp_car_no': car, 'comp_driver': driver,
            'comp_car_drivers': car_drivers, 'sector_time_sec': sec
        })

    for sector, entries in sectors_drivers.items():
        entries_sorted = sorted(entries, key=lambda x: x['sector_time_sec'])
        best_time = entries_sorted[0]['sector_time_sec']
        for rank, e in enumerate(entries_sorted, 1):
            output.append({
                'ref_car_no': ref_car, 'ref_stint_no': ref_stint,
                'ref_driver': ref_driver,
                'ref_window_start': w_start, 'ref_window_end': w_end,
                'sector': sector,
                'comp_car_no': e['comp_car_no'], 'comp_driver': e['comp_driver'],
                'comp_car_drivers': e['comp_car_drivers'],
                'sector_time_sec': e['sector_time_sec'],
                'delta_to_best': round(e['sector_time_sec'] - best_time, 3),
                'rank': rank,
                'n_drivers': len(entries_sorted)
            })

print(json.dumps(output))
conn.close()
