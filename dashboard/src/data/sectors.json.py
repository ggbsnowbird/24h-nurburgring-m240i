#!/usr/bin/env python3
"""
For each stint, compute per-sector best times and rank drivers in the same window.
Output: array of {ref_car_no, ref_stint_no, ref_driver, sector (1-9),
                  comp_car_no, comp_driver, sector_time_sec, rank}
"""
import sqlite3, json
from pathlib import Path

db = Path(__file__).parent.parent.parent.parent / "m240i_sector_times.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def to_sec(t):
    if not t:
        return None
    try:
        parts = t.split(':')
        if len(parts) == 2:
            return round(float(parts[0]) * 60 + float(parts[1]), 3)
        elif len(parts) == 3:
            return round(float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2]), 3)
    except:
        return None

# Load all stints
stints = cur.execute("""
    SELECT s.car_no, s.stint_no, s.driver_name,
           s.day_time_start, s.day_time_end, s.lap_start, s.lap_end
    FROM stints s
    WHERE s.best_laptime_sec IS NOT NULL AND s.best_laptime_sec < 1200
""").fetchall()

# For each reference stint, find all laps in window across all cars
# and compute best sector time per driver per sector
output = []

for ref in stints:
    ref_car = ref['car_no']
    ref_stint = ref['stint_no']
    ref_driver = ref['driver_name']
    w_start = ref['day_time_start']
    w_end = ref['day_time_end']

    # Get all laps in window with their sector times
    laps = cur.execute("""
        SELECT l.car_no, l.lap_no, l.driver_no,
               l.sector1_time, l.sector2_time, l.sector3_time,
               l.sector4_time, l.sector5_time, l.sector6_time,
               l.sector7_time, l.sector8_time, l.sector9_time,
               lt.lap_day_time,
               s.driver_name,
               c.drivers AS car_drivers
        FROM laps l
        JOIN live_timing_laps lt ON lt.car_no=l.car_no AND lt.lap_no=l.lap_no
        JOIN stints s ON s.car_no=l.car_no
                     AND l.lap_no BETWEEN s.lap_start AND s.lap_end
        JOIN cars c ON c.car_no=l.car_no
        WHERE lt.lap_day_time >= ? AND lt.lap_day_time <= ?
          AND l.laptime IS NOT NULL
    """, (w_start, w_end)).fetchall()

    # Filter: exclude outlier laps (>1200s)
    sector_cols = [f'sector{i}_time' for i in range(1, 10)]

    # Per driver, per sector: collect best
    best = {}  # (car_no, driver_name, sector_idx) -> best_sec
    for lap in laps:
        lap_sec = to_sec(lap['sector1_time'])  # rough check
        driver = lap['driver_name']
        car = lap['car_no']
        for i, col in enumerate(sector_cols, 1):
            s_time = to_sec(lap[col])
            if s_time is None or s_time <= 0 or s_time > 300:
                continue
            key = (car, driver, i)
            if key not in best or s_time < best[key][0]:
                best[key] = (s_time, lap['car_drivers'])

    if not best:
        continue

    # Rank per sector
    sectors_drivers = {}
    for (car, driver, sector), (sec, car_drivers) in best.items():
        sectors_drivers.setdefault(sector, []).append({
            'comp_car_no': car,
            'comp_driver': driver,
            'comp_car_drivers': car_drivers,
            'sector_time_sec': sec
        })

    for sector, entries in sectors_drivers.items():
        entries_sorted = sorted(entries, key=lambda x: x['sector_time_sec'])
        for rank, e in enumerate(entries_sorted, 1):
            output.append({
                'ref_car_no': ref_car,
                'ref_stint_no': ref_stint,
                'ref_driver': ref_driver,
                'ref_window_start': w_start,
                'ref_window_end': w_end,
                'sector': sector,
                'comp_car_no': e['comp_car_no'],
                'comp_driver': e['comp_driver'],
                'comp_car_drivers': e['comp_car_drivers'],
                'sector_time_sec': e['sector_time_sec'],
                'rank': rank
            })

print(json.dumps(output))
conn.close()
