# Project Status — 24h Nürburgring Dashboard

## Project goal
Public web dashboard analysing BMW M240i Racing Cup and SP9 GT3 performance at the **54th ADAC Ravenol 24h Nürburgring** (May 14–17, 2026).

## Live deployment
- **Public URL**: https://ggbsnowbird.github.io/24h-nurburgring-m240i/
- **Repo**: https://github.com/ggbsnowbird/24h-nurburgring-m240i
- **Stack**: Observable Framework + SQLite + Python data loaders + GitHub Pages (Actions)
- **Auto-deploys** on every push to `main`

## Current state

### ✅ DONE — both classes complete with full grid

### Database (`nbr_sector_times.db`)
| Table / View | Rows M240i | Rows SP9 |
|---|---:|---:|
| `cars` | 11 | **42** |
| `laps` | 1147 | **4369** |
| `live_timing_laps` | 1147 | **4369** |
| `stints` | 132 | **379** |

### SP9 grid (42 GT3 cars)
13 × Porsche 911 GT3 R (#4, #5, #17, #18, #24, #30, #44, #48, #54, #55, #86, #123, #911 — Manthey "Grello") and 3 × Ford Mustang GT3 (#64, #65, #67) were added in the latest session, on top of the original 26 (BMW M4 GT3 EVO, Mercedes-AMG GT3, Audi R8 LMS GT3, Ferrari 296 GT3, Lamborghini Huracan GT3 EVO2, Aston Martin Vantage AMR GT3, McLaren 720S-GT3, Porsche 911 GT3 CUP MR).

### SP9 timestamp source
Race LiveTiming session expired. Timestamps reconstructed from cumulative PDF lap times using `race_start_utc = 2026-05-16T12:59:55.626Z` — verified 0.0s variance against M240i ground truth.

### Known minor issue (pre-existing, not blocking)
`check_class_consistency.py M240i` reports 5 stints with `best_laptime_sec >= 690s`. This predates the current session — extraction touches SP9 only. Likely Code-60 / Safety-Car stints where every lap was slow. Out of scope for the SP9 work.

---

## Dashboard pages (12 total)
- `/` — landing page with class picker
- `/m240i/overview`, `/m240i/stint-rankings`, `/m240i/sector-analysis`, `/m240i/about`
- `/sp9/overview`, `/sp9/stint-rankings`, `/sp9/sector-analysis`, `/sp9/about`
- Old root pages still present for backward compatibility

---

## Critical rules — never deviate
1. **Never `style:` in observablehq.config.js** → white page
2. **690s threshold** (not 1200s)
3. **Outlap excluded**: `lap_no > stint.lap_start`
4. **4-min lookback**: `DATETIME(ref.day_time_start, '-4 minutes')`
5. **CEST in JSON, UTC in DB**
6. **`class` is case-sensitive**: `'M240i'` and `'SP9'` exactly
7. **Per-class views only**: `stint_ranking_m240i` / `stint_ranking_sp9`
8. **SP9 timestamps reconstructed** — do not re-fetch from LiveTiming

## Backup tags
| Tag | State |
|---|---|
| `stable-pre-sp9-20260519` | Before SP9 expansion |
| `stable-pre-polish-swap-20260518` | Before polish |
| `broken-polish-39c42bf` | Reference only |

## Key files
```
nbr_sector_times.db                  SQLite DB (gitignored)
dashboard/src/data/m240i/            M240i JSON + loaders (complete)
dashboard/src/data/sp9/              SP9 JSON + loaders (42-car grid)
dashboard/src/sp9/                   SP9 dashboard pages (42-colour palette)
scripts/extract_sp9.py               SP9 extraction (make-anchored regex, Cup excluded)
scripts/check_class_consistency.py   DB validation script
PLAN-GT3-EXPANSION.md                Original SP9 plan
```
