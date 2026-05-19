---
name: sqlite-queries
description: Write efficient SQLite queries for the 24h NBR multi-class racing database. Covers schema reference, time conversion helpers, common patterns for lap/stint/ranking analysis, per-class filtering, and window functions available in SQLite 3.25+.
license: MIT
compatibility: opencode
metadata:
  domain: data-engineering
  db: SQLite 3.25+
---

## Database
`nbr_sector_times.db` — covers M240i and SP9 GT3 classes.
All tables have a `class TEXT` column (`'M240i'` or `'SP9'`).

## Schema summary

```
cars(car_no PK, class, drivers, model, theoretical_best, source_page)
laps(id PK, car_no FK, class, page_no, lap_no, driver_no, laptime TEXT,
     sector1_time..sector9_time, v1..v8, raw_line)
live_timing_laps(id PK, car_no, class, lap_no, lap_time TEXT,
                 lap_day_time TEXT UTC, payload_json, source)
stints(id PK, car_no, class, stint_no, driver_no, driver_name,
       lap_start, lap_end, lap_count,
       day_time_start TEXT UTC, day_time_end TEXT UTC,
       best_laptime TEXT, best_laptime_sec REAL, avg_laptime_sec REAL)
stint_corrections(id PK, car_no, class, stint_no,
                  original_lap_start, corrected_lap_start,
                  reason, corrected_at)
stint_ranking_m240i VIEW  -- M240i only, Invariants 1-3 applied
stint_ranking_sp9 VIEW    -- SP9 only, Invariants 1-3 applied
lap_driver_times VIEW     -- per-class driver+lap+daytime mapping
```

## Critical query rules (from methodology contract)

- **Always filter by class**: `WHERE class='M240i'` or `WHERE class='SP9'`
- **Outlap excluded**: `WHERE l.lap_no > s.lap_start` (never BETWEEN for aggregations)
- **690s ceiling**: `WHERE lap_time_sec < 690` (not 1200s — obsolete)
- **4-min lookback**: `DATETIME(ref.day_time_start, '-4 minutes')` on window queries
- **Avoid SELECT * on stint_ranking views** — expensive cross-join — always filter by `ref_car_no`

## Time conversion in SQLite

Lap times stored as TEXT in `MM:SS.mmm` or `H:MM:SS.mmm` format.
```sql
CASE
  WHEN LENGTH(laptime)-LENGTH(REPLACE(laptime,':',''))=1
    THEN CAST(SUBSTR(laptime,1,INSTR(laptime,':')-1) AS REAL)*60
         + CAST(SUBSTR(laptime,INSTR(laptime,':')+1) AS REAL)
  WHEN LENGTH(laptime)-LENGTH(REPLACE(laptime,':',''))=2
    THEN CAST(SUBSTR(laptime,1,INSTR(laptime,':')-1) AS REAL)*3600
         + CAST(SUBSTR(SUBSTR(laptime,INSTR(laptime,':')+1),1,
                INSTR(SUBSTR(laptime,INSTR(laptime,':')+1),':')-1) AS REAL)*60
         + CAST(SUBSTR(SUBSTR(laptime,INSTR(laptime,':')+1),
                INSTR(SUBSTR(laptime,INSTR(laptime,':')+1),':')+1) AS REAL)
  ELSE NULL
END AS laptime_sec
```

## Common patterns

### Per-class best laps per driver
```sql
SELECT car_no, driver_no, lap_no, laptime
FROM (
  SELECT *, <time_conversion> AS laptime_sec,
         ROW_NUMBER() OVER (PARTITION BY car_no, driver_no ORDER BY laptime_sec) rn
  FROM laps WHERE class='SP9'
) WHERE rn=1 AND laptime_sec < 690;
```

### Stint gap / pit duration per class
```sql
SELECT car_no, stint_no, driver_name,
       ROUND((JULIANDAY(day_time_start)-JULIANDAY(
         LAG(day_time_end) OVER (PARTITION BY car_no ORDER BY stint_no)
       ))*86400, 1) AS pit_sec
FROM stints WHERE class='SP9';
```

### All drivers on track during a reference stint window (with 4-min lookback)
```sql
SELECT comp_car_no, comp_driver, laps_in_window,
       ROUND(best_laptime_sec,3), rank_by_best
FROM stint_ranking_sp9  -- or stint_ranking_m240i
WHERE ref_car_no=? AND ref_stint_no=?
ORDER BY rank_by_best;
```

### Driver name from driver_no (Python, Invariant 6)
```python
parts = drivers_string.split(' / ')
driver_name = parts[(driver_no - 1) % len(parts)]
```

## Performance tips
- Always filter `WHERE class=?` first — keeps result sets small
- Indexes on: `laps(car_no,lap_no)`, `live_timing_laps(car_no,lap_no)`
- `EXPLAIN QUERY PLAN` to debug slow queries
- SP9 field is ~30 cars — `stint_ranking_sp9` cross-join is large; always add `ref_car_no` filter
