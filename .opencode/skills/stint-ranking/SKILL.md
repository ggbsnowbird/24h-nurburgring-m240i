---
name: stint-ranking
description: Query and interpret stint-level driver rankings for the 24h Nürburgring M240i class. Covers how stints are defined, how rankings are computed, and how to produce per-driver or per-car analyses from the stint_ranking view.
license: MIT
compatibility: opencode
metadata:
  domain: motorsport-data
  race: 54th ADAC Ravenol 24h Nürburgring 2026
  class: BMW M240i Racing Cup
---

## Context
- Database: `m240i_sector_times.db` (SQLite)
- Race: 54th ADAC Ravenol 24h Nürburgring, 14-17 May 2026
- Class: BMW M240i Racing Cup only (cars: 195, 650, 651, 652, 653, 658, 665, 667, 669, 670, 677)

## Key tables and views

### `stints`
A stint = consecutive laps by the same driver on the same car.
Columns: `car_no, stint_no, driver_no, driver_name, lap_start, lap_end, lap_count, day_time_start, day_time_end, best_laptime, best_laptime_sec, avg_laptime_sec`

### `stint_ranking`
For each reference stint (ref_car_no, ref_stint_no), ranks ALL drivers from ALL M240i cars
who were on track during the same time window, by best lap time and average lap time.

Key columns:
- `ref_car_no`, `ref_stint_no`, `ref_driver` — the reference stint
- `ref_window_start`, `ref_window_end` — UTC time window
- `comp_car_no`, `comp_driver` — the compared driver/car
- `laps_in_window` — how many laps they completed in the window
- `best_laptime_sec`, `avg_laptime_sec` — performance metrics
- `rank_by_best`, `rank_by_avg` — rank among all drivers in that window

### `lap_driver_times` (view)
Maps every lap to: `car_no, lap_no, driver_no, driver_name, lap_time_pdf, lap_day_time`

### `laps`
Raw lap data from PDF: `car_no, lap_no, driver_no, laptime, sector1_time..sector9_time, v1..v8, page_no`

### `cars`
`car_no, drivers, model, theoretical_best`

## Common queries

### All Boutonnet stints ranked
```sql
SELECT ref_stint_no, ref_window_start, ref_window_end,
       comp_car_no, comp_driver, laps_in_window,
       ROUND(best_laptime_sec,3), rank_by_best
FROM stint_ranking
WHERE ref_car_no=652 AND ref_driver='Boutonnet'
ORDER BY ref_stint_no, rank_by_best;
```

### Summary: Boutonnet average rank across all stints
```sql
SELECT ref_stint_no,
       r.rank_by_best AS boutonnet_rank,
       COUNT(*) AS drivers_in_window
FROM stint_ranking r
WHERE ref_car_no=652 AND ref_driver='Boutonnet' AND comp_driver='Boutonnet'
ORDER BY ref_stint_no;
```

### Best individual lap in a stint
```sql
SELECT s.car_no, s.stint_no, s.driver_name, l.lap_no, l.laptime, lt.lap_day_time
FROM stints s
JOIN laps l ON l.car_no=s.car_no AND l.lap_no BETWEEN s.lap_start AND s.lap_end
JOIN live_timing_laps lt ON lt.car_no=l.car_no AND lt.lap_no=l.lap_no
WHERE s.car_no=652 AND s.driver_name='Boutonnet'
ORDER BY lt.lap_day_time;
```

## Notes
- Outlier laps (>1200s = 20 min) excluded from rankings (pit stops, Safety Car)
- `day_time_start/end` are UTC timestamps (race ran 14-17 May 2026)
- `driver_no` in `laps` is 1-indexed, matching order in `cars.drivers` (split by ' / ')
