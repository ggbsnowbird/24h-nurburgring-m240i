#!/usr/bin/env python3
"""Consistency check for a class in nbr_sector_times.db. Exit 0 = pass, 1 = fail."""
import sqlite3, sys
from pathlib import Path

CLASS = sys.argv[1] if len(sys.argv) > 1 else 'M240i'
DB = Path(__file__).parent.parent / 'nbr_sector_times.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

failures = []

# Check 1: no stint with best_laptime_sec >= 690 for this class
n_bad_laptime = cur.execute(
    "SELECT COUNT(*) FROM stints WHERE class=? AND best_laptime_sec >= 690",
    (CLASS,)
).fetchone()[0]
if n_bad_laptime > 0:
    failures.append(f"Check 1: {n_bad_laptime} stints have best_laptime_sec >= 690s")

# Check 2: day_time_start matches first valid (non-outlap, <690s) lap timestamp
rows = cur.execute("""
    SELECT s.car_no, s.stint_no, s.day_time_start, s.lap_start,
           (SELECT MIN(lt.lap_day_time)
              FROM live_timing_laps lt
              JOIN laps l ON l.car_no=lt.car_no AND l.lap_no=lt.lap_no AND l.class=s.class
              WHERE l.car_no=s.car_no
                AND l.lap_no > s.lap_start
                AND l.lap_no <= s.lap_end
                AND lt.lap_day_time IS NOT NULL
                AND lt.class=s.class
                AND (CASE WHEN LENGTH(l.laptime)-LENGTH(REPLACE(l.laptime,':',''))=1
                          THEN CAST(SUBSTR(l.laptime,1,INSTR(l.laptime,':')-1) AS REAL)*60
                               +CAST(SUBSTR(l.laptime,INSTR(l.laptime,':')+1) AS REAL)
                          ELSE 99999 END) < 690
           ) AS first_valid
    FROM stints s WHERE s.class=?
""", (CLASS,)).fetchall()
mismatches = [r for r in rows if r[2] and r[4] and r[2] != r[4]]
if mismatches:
    failures.append(f"Check 2: {len(mismatches)} stints have day_time_start != first valid lap")

# Check 3: no NULL driver_name in stints for this class
n_null_driver = cur.execute(
    "SELECT COUNT(*) FROM stints WHERE class=? AND (driver_name IS NULL OR driver_name='')",
    (CLASS,)
).fetchone()[0]
if n_null_driver > 0:
    failures.append(f"Check 3: {n_null_driver} stints have NULL driver_name")

# Check 4: plausible stint count for the class
n_stints = cur.execute("SELECT COUNT(*) FROM stints WHERE class=?", (CLASS,)).fetchone()[0]
min_expected = 50 if CLASS == 'M240i' else 100
max_expected = 200 if CLASS == 'M240i' else 600
if not (min_expected <= n_stints <= max_expected):
    failures.append(f"Check 4: stint count {n_stints} outside plausible range [{min_expected},{max_expected}]")

# Check 5: sector1 data populated for >= 80% of laps in this class
n_laps_class = cur.execute("SELECT COUNT(*) FROM laps WHERE class=?", (CLASS,)).fetchone()[0]
n_with_s1 = cur.execute(
    "SELECT COUNT(*) FROM laps WHERE class=? AND sector1_time IS NOT NULL AND sector1_time != ''",
    (CLASS,)
).fetchone()[0]
if n_laps_class > 0 and (n_with_s1 / n_laps_class) < 0.80:
    failures.append(f"Check 5: only {n_with_s1}/{n_laps_class} laps have sector1 data (<80%)")

# Report
print(f"=== Consistency check for class={CLASS} ===")
print(f"Stints: {n_stints}, Laps: {n_laps_class}, Sector1 coverage: {100*n_with_s1//max(n_laps_class,1)}%")
if failures:
    print("FAILED:")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
print("PASS — all 5 checks succeeded")
conn.close()
sys.exit(0)
