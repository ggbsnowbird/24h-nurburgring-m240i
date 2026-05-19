---
name: stint-ranking
description: Query and interpret stint-level driver rankings for the 24h Nürburgring dashboard. Covers how stints are defined, how rankings are computed, the 8 methodology invariants, and how to produce per-driver or per-car analyses from the per-class stint_ranking views.
license: MIT
compatibility: opencode
metadata:
  domain: motorsport-data
  race: 54th ADAC Ravenol 24h Nürburgring 2026
  classes: M240i Racing Cup, SP9 GT3
---

## Context
- Database: `nbr_sector_times.db` (SQLite)
- Race: 54th ADAC Ravenol 24h Nürburgring, 14-17 May 2026
- Classes: **M240i Racing Cup** and **SP9 GT3** (all SP9 sub-categories merged)
- All tables have a `class` column (`'M240i'` or `'SP9'`)

---

## 8 Methodology Invariants — MUST be preserved for all classes

### Invariant 1 — Outlap exclusion
First lap of every stint excluded from all aggregations (cold tyres, pit exit).
```sql
WHERE l.lap_no > s.lap_start
```
Never use `BETWEEN s.lap_start AND s.lap_end` for aggregations.

### Invariant 2 — Hard lap ceiling 690s (11:30)
Laps ≥ 690s excluded everywhere (driver swaps, SC, Code 60, unscheduled stops).
```sql
WHERE lap_time_sec < 690
```
**Never 1200s — obsolete threshold.**

### Invariant 3 — 4-minute lookback on comparison windows
Window starts 4 min before `ref.day_time_start` to capture peers finishing a lap just before.
```sql
AND comp_l.lap_day_time >= DATETIME(ref.day_time_start, '-4 minutes')
AND comp_l.lap_day_time <= ref.day_time_end
```

### Invariant 4 — Dynamic per-sector thresholds
`median × 2.5` per sector (never hardcoded). Required because S7 (~217s) would be excluded by any fixed threshold ≤ 200s.
```python
sector_thresholds[i] = statistics.median(all_sector_vals[i]) * 2.5
```

### Invariant 5 — `day_time_start` = first valid lap timestamp
Stores the timestamp of the first valid lap (lap_start+1, < 690s), not the outlap itself.

### Invariant 6 — Driver name modulo lookup
```python
parts = car_drivers.split(' / ')
driver_name = parts[(driver_no - 1) % len(parts)]
```
Supports manual overrides dict `{(car_no, stint_no): "name"}` for known exceptions.

### Invariant 7 — CEST output, UTC storage
DB stores UTC. All JSON output is CEST (UTC+2) via `utc_to_cest()` in each loader.

### Invariant 8 — `stint_corrections` is per-class
Manual corrections (e.g. Boutonnet M240i stint 14 — puncture) logged with `class` column.

---

## Per-class structure

Views are split by class for clarity and performance:

| View | Class |
|---|---|
| `stint_ranking_m240i` | M240i only |
| `stint_ranking_sp9` | SP9 only |

Each view applies Invariants 1, 2, 3 internally. Never query across classes.

---

## Key tables

### `stints`
A stint = consecutive laps by the same driver on the same car.
`car_no, class, stint_no, driver_no, driver_name, lap_start, lap_end, lap_count, day_time_start, day_time_end, best_laptime, best_laptime_sec, avg_laptime_sec`

### `stint_ranking_m240i` / `stint_ranking_sp9`
For each reference stint, ranks ALL drivers from the same class on track in the same time window.

Key columns:
- `ref_car_no`, `ref_stint_no`, `ref_driver` — reference stint
- `ref_window_start`, `ref_window_end` — UTC time window (4-min lookback applied)
- `comp_car_no`, `comp_driver` — compared driver/car
- `laps_in_window` — laps completed in window (outlap excluded, ≥690s excluded)
- `best_laptime_sec`, `avg_laptime_sec`
- `rank_by_best`, `rank_by_avg`

### `laps`
Raw lap data from PDF: `car_no, class, lap_no, driver_no, laptime, sector1_time..sector9_time, v1..v8`

### `cars`
`car_no, class, drivers, model, theoretical_best`

### `stint_corrections`
Manual corrections: `car_no, class, stint_no, original_lap_start, corrected_lap_start, reason, corrected_at`

---

## Common queries

### All stints for a driver ranked (M240i example)
```sql
SELECT ref_stint_no, ref_window_start, ref_window_end,
       comp_car_no, comp_driver, laps_in_window,
       ROUND(best_laptime_sec,3), rank_by_best
FROM stint_ranking_m240i
WHERE ref_car_no=652 AND ref_driver='Boutonnet'
ORDER BY ref_stint_no, rank_by_best;
```

### Stint gap / pit duration
```sql
SELECT car_no, stint_no, driver_name, class,
       ROUND((JULIANDAY(day_time_start)-JULIANDAY(
         LAG(day_time_end) OVER (PARTITION BY car_no ORDER BY stint_no)
       ))*86400, 1) AS pit_duration_sec
FROM stints WHERE class='M240i';
```

## Notes
- M240i cars: 195, 650, 651, 652, 653, 658, 665, 667, 669, 670, 677
- SP9 car list: discovered during Phase 1 of expansion
- JSON outputs are in CEST; DB is UTC
- `day_time_start` in stints is already shifted to first valid lap (Invariant 5)
