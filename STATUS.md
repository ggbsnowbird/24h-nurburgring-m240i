# Project Status — 24h Nürburgring Dashboard

## Project goal
Public web dashboard analysing BMW M240i Racing Cup and SP9 GT3 performance at the **54th ADAC Ravenol 24h Nürburgring** (May 14–17, 2026).

## Live deployment
- **Public URL**: https://ggbsnowbird.github.io/24h-nurburgring-m240i/
- **Repo**: https://github.com/ggbsnowbird/24h-nurburgring-m240i
- **Stack**: Observable Framework + SQLite + Python data loaders + GitHub Pages (Actions)
- **Auto-deploys** on every push to `main`

## Current state — DONE (both classes live)

### Database (`nbr_sector_times.db`)
| Table / View | Rows M240i | Rows SP9 | Purpose |
|---|---:|---:|---|
| `cars` | 11 | 26 | Car metadata per class |
| `laps` | 1147 | 2473 | Raw laps from PDF, 9 sectors |
| `live_timing_laps` | 1147 | 2473 | Timestamps (M240i: LiveTiming WS; SP9: reconstructed from PDF) |
| `stints` | 132 | 224 | Consecutive same-driver groups |
| `stint_ranking_m240i` (view) | — | — | Cross-car ranking, M240i only |
| `stint_ranking_sp9` (view) | — | — | Cross-car ranking, SP9 only |
| `stint_corrections` | 1 | 0 | Manual corrections log |

### SP9 timestamp source
Race LiveTiming session expired after the event. Timestamps reconstructed from cumulative PDF lap times using `race_start_utc = 2026-05-16T12:59:55.626Z` — verified 0.0s variance against M240i LiveTiming ground truth across all 5 M240i cars.

### Dashboard pages (12 total)
- `/` — landing page with class picker cards
- `/m240i/overview`, `/m240i/stint-rankings`, `/m240i/sector-analysis`, `/m240i/about`
- `/sp9/overview`, `/sp9/stint-rankings`, `/sp9/sector-analysis`, `/sp9/about`
- Old `/index`, `/stint-rankings`, `/sector-analysis`, `/about` still present for backward compatibility

### SP9 cars
Cars: 1, 3, 7, 8, 11, 16, 19, 26, 32, 33, 34, 35, 37, 39, 45, 47, 69, 71, 75, 77, 80, 84, 99, 130, 786, 992
Models: BMW M4 GT3 EVO, Mercedes-AMG GT3, Audi R8 LMS GT3, Ferrari 296 GT3, Lamborghini Huracan GT3 EVO2, Aston Martin Vantage AMR GT3, McLaren 720S-GT3, Porsche 911 GT3 CUP MR

### Design system
- Dark theme + Roboto Condensed / JetBrains Mono
- Green NBR accent (#43632d) on header, control bars, info boxes, footer
- Inline `<style>` in `head:` config (NOT `style:` directive — that breaks the dark theme)
- Track map: `filter: invert(1) hue-rotate(180deg)` on the white-bg webp

### Statistical methodology (8 invariants — both classes)
1. Outlap exclusion: `lap_no > stint.lap_start`
2. Hard ceiling: `< 690s`
3. 4-min lookback on comparison windows
4. Dynamic per-sector thresholds: `median × 2.5`
5. `day_time_start` = first valid lap timestamp
6. Driver name modulo: `parts[(driver_no-1) % len(parts)]`
7. CEST output, UTC storage
8. `stint_corrections` per class

## Data files structure
```
dashboard/src/data/
├── m240i/   stints.json  ranking.json  sectors.json  corrections.json  all_laps.json  (+ .py loaders)
├── sp9/     stints.json  ranking.json  sectors.json  corrections.json  all_laps.json  (+ .py loaders)
└── [root]   original M240i files kept for backward compatibility
```

## Backup tags
| Reference | What |
|---|---|
| `stable-pre-sp9-20260519` | State before SP9 expansion began |
| `stable-pre-polish-swap-20260518` | Before polish promotion to main |
| `broken-polish-39c42bf` | Reference for the `style:` directive bug |

## Definition of done
1. PDF + LiveTiming merged in SQLite for M240i — ✅
2. SP9 data extracted and timestamps reconstructed — ✅
3. Per-class ranking and sector analysis — ✅
4. Landing page + grouped navigation — ✅
5. Public site deployed — ✅
6. Both classes verified with consistency check script — ✅

## Open items / next steps
- (optional) Driver Scoring page (composite z-score model, analysed in chat, not yet in UI)
- (optional) Cloudflare Access auth (plan in `PLAN-GT3-EXPANSION.md` Section 12)
- (optional) Mobile-responsive layout for sector map + pills
- (optional) Deduplicate old root pages (index.md, stint-rankings.md, etc.)

## Critical pitfalls to remember
- **NEVER set `style:` in observablehq.config.js** — it overrides dark theme. Use `head:` `<style>` block.
- **SP9 timestamps are reconstructed** (not from LiveTiming) — do not attempt to re-capture from LiveTiming WS
- **`class` column is TEXT** — values are exactly `'M240i'` and `'SP9'` (case-sensitive)
- Per-class views: `stint_ranking_m240i` and `stint_ranking_sp9` — never query `stint_ranking` (view deleted)
- Driver name modulo is critical for multi-pilot teams with `driver_no > len(parts)`

## SP9 expansion — Phase 1 findings (archived)
- 26 SP9/GT3 cars found in PDF, format identical to M240i
- LiveTiming session expired — DATA frames no longer streamed for archived races
- Workaround: timestamp reconstruction exact (verified 0.0s variance)
- Consistency check (SP9): PASS all 5 checks
