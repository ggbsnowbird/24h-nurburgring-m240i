#!/usr/bin/env python3
"""
Extract SP9 GT3 class data from the 42_24h_Race_Sector_Times.pdf into nbr_sector_times.db.
Reconstructs lap timestamps from cumulative lap times using the known race start UTC.
Applies all 8 methodology invariants from PLAN-GT3-EXPANSION.md.
"""
import sqlite3, re, statistics
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pdfplumber

PDF  = Path(__file__).parent.parent / 'Data Source' / '42_24h_Race_Sector_Times.pdf'
DB   = Path(__file__).parent.parent / 'nbr_sector_times.db'

# Invariant 7: Race start UTC (verified from M240i LiveTiming data, 0.0s variance)
RACE_START_UTC = datetime(2026, 5, 16, 12, 59, 55, 626000, tzinfo=timezone.utc)
CEST = timedelta(hours=2)

# Regex patterns
SP9_HEADER_RE = re.compile(
    r'^(\d+)\s+(.+?)\s+([\w\s\-\.]+GT3[\w\s\-\.]*)\s+theoretical besttime:\s+(.+)$',
    re.IGNORECASE
)
ANY_HEADER_RE = re.compile(r'^(\d+)\s+.+\s+theoretical besttime:\s+.+$')
LAP_RE = re.compile(r'^(\d+)\s+(\d+)\s+([0-9:]+\.\d+)\s*(.*)$')
TIME_RE = re.compile(r'^(?:\d+:)?\d+\.\d+$')
INT_RE  = re.compile(r'^\d{2,3}$')

def to_sec(t):
    if not t: return None
    p = t.split(':')
    try:
        if len(p) == 1: return float(p[0])
        if len(p) == 2: return float(p[0]) * 60 + float(p[1])
        if len(p) == 3: return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2])
    except: return None

def utc_to_cest(dt):
    return (dt + CEST).strftime('%Y-%m-%d %H:%M:%S.%f')

def parse_sectors(tokens):
    """Parse [sector speed]×8 [sector9] from remaining tokens after laptime."""
    sectors = [None] * 9
    speeds  = [None] * 8
    t = tokens[:]
    if t and t[0] == '#':
        t.pop(0)
    for i in range(8):
        if not t: break
        if TIME_RE.match(t[0]):
            sectors[i] = t.pop(0)
            if t and INT_RE.match(t[0]):
                speeds[i] = int(t.pop(0))
        else:
            break
    if t and TIME_RE.match(t[0]):
        sectors[8] = t.pop(0)
    return sectors, speeds

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Track cumulative lap time per car for timestamp reconstruction
# Structure: car_no -> cumulative_seconds
car_cumulative = {}  # car_no -> float (seconds from race start)

cars_inserted = 0
laps_inserted = 0

print(f"Parsing {PDF.name}...")

with pdfplumber.open(str(PDF)) as pdf:
    current_car = None
    current_drivers = None
    current_model = None
    current_best = None
    current_page = None

    for page_no, page in enumerate(pdf.pages, 1):
        txt = page.extract_text() or ''
        for line in txt.splitlines():
            line = line.strip()
            if not line: continue

            # Detect SP9 car header
            m = SP9_HEADER_RE.match(line)
            if m and 'GT4' not in m.group(3).upper():
                car_no = int(m.group(1))
                drivers = m.group(2).strip()
                model = m.group(3).strip()
                best = m.group(4).strip()
                current_car = car_no
                current_drivers = drivers
                current_model = model
                current_best = best
                current_page = page_no

                # Insert car if not exists
                existing = cur.execute("SELECT car_no FROM cars WHERE car_no=? AND class='SP9'", (car_no,)).fetchone()
                if not existing:
                    cur.execute('''
                        INSERT INTO cars (car_no, drivers, model, theoretical_best, source_page, class)
                        VALUES (?,?,?,?,?,?)
                    ''', (car_no, drivers, model, best, page_no, 'SP9'))
                    cars_inserted += 1
                continue

            # Detect non-SP9 car header (reset current car)
            if ANY_HEADER_RE.match(line) and not (SP9_HEADER_RE.match(line) and 'GT4' not in line.upper()):
                if not (SP9_HEADER_RE.match(line) and 'GT4' not in line.upper()):
                    current_car = None
                continue

            if current_car is None: continue
            if line.startswith('Lap Driver') or line.startswith('Sector Times'): continue

            lm = LAP_RE.match(line)
            if not lm: continue

            lap_no = int(lm.group(1))
            driver_no = int(lm.group(2))
            laptime = lm.group(3)
            rest = lm.group(4).strip()
            tokens = rest.split() if rest else []
            sectors, speeds = parse_sectors(tokens)

            lap_sec = to_sec(laptime)
            if lap_sec is None: continue

            # Accumulate cumulative time per car (Invariant 7: reconstruct timestamp)
            if current_car not in car_cumulative:
                car_cumulative[current_car] = 0.0
            car_cumulative[current_car] += lap_sec
            lap_end_utc = RACE_START_UTC + timedelta(seconds=car_cumulative[current_car])
            lap_day_time = lap_end_utc.strftime('%Y-%m-%d %H:%M:%S.%f')

            # Insert lap
            cur.execute('''
                INSERT OR IGNORE INTO laps (
                    car_no, class, page_no, lap_no, driver_no, laptime,
                    sector1_time, sector2_time, sector3_time, sector4_time,
                    sector5_time, sector6_time, sector7_time, sector8_time, sector9_time,
                    v1, v2, v3, v4, v5, v6, v7, v8,
                    raw_line
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                current_car, 'SP9', page_no, lap_no, driver_no, laptime,
                sectors[0], sectors[1], sectors[2], sectors[3],
                sectors[4], sectors[5], sectors[6], sectors[7], sectors[8],
                speeds[0], speeds[1], speeds[2], speeds[3],
                speeds[4], speeds[5], speeds[6], speeds[7],
                line
            ))
            laps_inserted += cur.rowcount

            # Insert into live_timing_laps (reconstructed timestamp)
            cur.execute('''
                INSERT OR IGNORE INTO live_timing_laps
                (car_no, lap_no, class, driver_id, driver_name, lap_time, lap_day_time, source, payload_json)
                VALUES (?,?,?,?,?,?,?,?,?)
            ''', (
                current_car, lap_no, 'SP9', None, None,
                laptime, lap_day_time, 'pdf_reconstructed', None
            ))

conn.commit()
print(f"✓ Inserted {cars_inserted} SP9 cars, {laps_inserted} laps")

# ── Compute SP9 stints ─────────────────────────────────────────────────────────
print("\nComputing SP9 stints...")

drivers_map = {}
for car_no, drivers in cur.execute("SELECT car_no, drivers FROM cars WHERE class='SP9'").fetchall():
    drivers_map[car_no] = [d.strip() for d in drivers.split(' / ')]

sp9_cars = [r[0] for r in cur.execute("SELECT DISTINCT car_no FROM laps WHERE class='SP9' ORDER BY car_no").fetchall()]

stints_inserted = 0
for car_no in sp9_cars:
    rows = cur.execute('''
        SELECT l.lap_no, l.driver_no, l.laptime, lt.lap_day_time
        FROM laps l
        LEFT JOIN live_timing_laps lt ON lt.car_no=l.car_no AND lt.lap_no=l.lap_no AND lt.class='SP9'
        WHERE l.car_no=? AND l.class='SP9'
        ORDER BY l.lap_no
    ''', (car_no,)).fetchall()

    # Group into stints (consecutive same driver_no)
    stints = []
    current_stint = None
    for lap_no, driver_no, laptime, dt in rows:
        if current_stint is None or driver_no != current_stint['driver_no']:
            if current_stint: stints.append(current_stint)
            current_stint = {'driver_no': driver_no, 'lap_start': lap_no, 'lap_end': lap_no,
                             'laptimes': [laptime], 'day_times': [dt]}
        else:
            current_stint['lap_end'] = lap_no
            current_stint['laptimes'].append(laptime)
            current_stint['day_times'].append(dt)
    if current_stint: stints.append(current_stint)

    parts = drivers_map.get(car_no, [])
    for stint_no, s in enumerate(stints, 1):
        drv_no = s['driver_no']
        # Invariant 6: modulo driver name lookup
        drv_name = parts[(drv_no - 1) % len(parts)] if parts and drv_no else None

        # Invariant 1+2: exclude outlap and laps >= 690s for stats
        valid_secs = [to_sec(t) for t in s['laptimes'][1:] if to_sec(t) is not None and to_sec(t) < 690]
        if not valid_secs:
            valid_secs = [to_sec(t) for t in s['laptimes'] if to_sec(t) is not None and to_sec(t) < 690]

        if not valid_secs: continue

        best_sec = min(valid_secs)
        avg_sec  = statistics.mean(valid_secs)

        # Invariant 5: day_time_start = first valid (non-outlap) lap timestamp
        valid_dts = [s['day_times'][i+1] for i, t in enumerate(s['laptimes'][1:])
                     if to_sec(t) is not None and to_sec(t) < 690 and i+1 < len(s['day_times'])]
        if not valid_dts:
            valid_dts = [dt for dt, t in zip(s['day_times'], s['laptimes'])
                         if dt and to_sec(t) is not None and to_sec(t) < 690]

        dt_start = min(valid_dts) if valid_dts else None
        dt_end   = max(d for d in s['day_times'] if d) if any(s['day_times']) else None

        # Best laptime string
        best_str = s['laptimes'][[to_sec(t) for t in s['laptimes']].index(best_sec)] if best_sec in [to_sec(t) for t in s['laptimes']] else None

        cur.execute('''
            INSERT OR REPLACE INTO stints
            (car_no, class, stint_no, driver_no, driver_name, lap_start, lap_end, lap_count,
             day_time_start, day_time_end, best_laptime, best_laptime_sec, avg_laptime_sec)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            car_no, 'SP9', stint_no, drv_no, drv_name,
            s['lap_start'], s['lap_end'], s['lap_end'] - s['lap_start'] + 1,
            dt_start, dt_end, best_str, round(best_sec, 3), round(avg_sec, 3)
        ))
        stints_inserted += 1

conn.commit()
print(f"✓ Inserted {stints_inserted} SP9 stints")

# Summary
n_cars  = cur.execute("SELECT COUNT(*) FROM cars  WHERE class='SP9'").fetchone()[0]
n_laps  = cur.execute("SELECT COUNT(*) FROM laps  WHERE class='SP9'").fetchone()[0]
n_stints = cur.execute("SELECT COUNT(*) FROM stints WHERE class='SP9'").fetchone()[0]
print(f"\nSP9 summary: {n_cars} cars, {n_laps} laps, {n_stints} stints")

conn.close()
print("\nDone. Run scripts/check_class_consistency.py SP9 to verify.")
