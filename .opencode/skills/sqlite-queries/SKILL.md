---
name: sqlite-queries
description: Write efficient SQLite queries for the M240i racing database. Covers schema reference, time conversion helpers, common patterns for lap/stint/ranking analysis, and window functions available in SQLite 3.25+.
license: MIT
compatibility: opencode
metadata:
  domain: data-engineering
  db: SQLite 3.25+
---

## Schema summary

```
cars(car_no PK, drivers, model, theoretical_best, source_page)
laps(id PK, car_no FK, page_no, lap_no, driver_no, laptime TEXT, sector1_time..sector9_time, v1..v8, raw_line)
live_timing_laps(id PK, car_no, lap_no, lap_time TEXT, lap_day_time TEXT UTC, payload_json, source)
stints(id PK, car_no, stint_no, driver_no, driver_name, lap_start, lap_end, lap_count, day_time_start, day_time_end, best_laptime, best_laptime_sec REAL, avg_laptime_sec REAL)
lap_driver_times VIEW: car_no, lap_no, driver_no, driver_name, lap_time_pdf, lap_day_time, lap_time_live
stint_ranking VIEW: ref_car_no, ref_stint_no, ref_driver, ref_window_start, ref_window_end, comp_car_no, comp_car_drivers, comp_driver, laps_in_window, best_laptime_raw, best_laptime_sec, avg_laptime_sec, rank_by_best, rank_by_avg
```

## Time conversion in SQLite

Lap times are stored as TEXT in `MM:SS.mmm` or `H:MM:SS.mmm` format.
Convert to seconds:
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
END AS laptime_sec
```

## Useful patterns

### Top N laps per driver (window function)
```sql
SELECT * FROM (
  SELECT car_no, driver_no, lap_no, laptime,
         ROW_NUMBER() OVER (PARTITION BY car_no, driver_no ORDER BY laptime_sec) rn
  FROM (SELECT *, <time_conversion> AS laptime_sec FROM laps)
) WHERE rn <= 5;
```

### Drivers on track at same time as a given lap
```sql
SELECT lt2.car_no, lt2.lap_no, lt2.lap_day_time, lt2.lap_time
FROM live_timing_laps lt1
JOIN live_timing_laps lt2
  ON lt2.lap_day_time BETWEEN lt1.lap_day_time
     AND datetime(lt1.lap_day_time, '+' || CAST(lt1_sec AS TEXT) || ' seconds')
WHERE lt1.car_no=652 AND lt1.lap_no=6;
```

### Stint gap analysis (time between stints = pit stop duration)
```sql
SELECT car_no, stint_no, driver_name,
       day_time_start,
       LAG(day_time_end) OVER (PARTITION BY car_no ORDER BY stint_no) AS prev_end,
       ROUND((JULIANDAY(day_time_start)-JULIANDAY(
         LAG(day_time_end) OVER (PARTITION BY car_no ORDER BY stint_no)
       ))*86400, 1) AS pit_duration_sec
FROM stints;
```

## Performance tips
- Add `WHERE car_no IN (195,650,651,652,653,658,665,667,669,670,677)` always — small table but good habit
- Avoid SELECT * on `stint_ranking` view (expensive cross-join) — always filter by ref_car_no
- Use `EXPLAIN QUERY PLAN` to debug slow queries
- Indexes exist on: `laps(car_no,lap_no)`, `live_timing_laps(car_no,lap_no)`
