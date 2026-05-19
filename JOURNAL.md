# Session Journal — M240i Dashboard

## Context
Building a public web dashboard analysing BMW M240i Racing Cup performance at the 54th ADAC Ravenol 24h Nürburgring (May 2026). Data extracted from the official ADAC PDF + LiveTiming WebSocket. Deployed as a public site on GitHub Pages from `dashboard/` via Observable Framework.

## Session 1 — Data pipeline
- Verified local PDF source (`Data Source/42_24h_Race_Sector_Times.pdf`)
- Built SQLite extraction with `pdfplumber`, filtered to M240i class only
- 11 cars × 1147 laps loaded into `m240i_sector_times.db`
- Schema: `cars`, `laps`, plus a `live_timing_laps` table prepared for daytime enrichment

## Session 2 — LiveTiming enrichment
- Page `livetiming.azurewebsites.net/event/50/laps-data` was JS-rendered, not raw JSON
- Raw WebSocket only gave `LTS_TIMESYNC` frames in CLI environment
- Solved with Playwright + Chromium headless intercepting WS frames → got the `DATA` payload
- 1147 lap day-times merged; built `lap_driver_times` view joining PDF lap data + LiveTiming heure
- Created `stints` table from consecutive same-driver lap groups (auto-detected from `driver_no` changes)

## Session 3 — Dashboard scaffolding
- Set up Observable Framework with `dashboard/` folder
- 4 pages: Overview, Stint Rankings, Sector Analysis, About
- Python data loaders generating JSON: `stints.json`, `ranking.json`, `sectors.json`, `corrections.json`, `all_laps.json`
- GitHub Actions workflow deploying `dashboard/dist/` to GitHub Pages
- Initial publish at https://ggbsnowbird.github.io/24h-nurburgring-m240i/

## Session 4 — Statistical refinements
- Excluded outlaps (first lap of each stint) — cold tyres / pit exit bias
- 11:30 (690s) hard threshold for driver swap / SC / Code 60 laps
- 4-min lookback on comparison windows (captures peers finishing a lap just before)
- Dynamic sector thresholds: `median × 2.5` per sector (fixes S7 ~217s being excluded)
- Per-sector ranking heatmap added
- Driver name fix: modulo for cases like Sari/Sari (`driver_no=3` on 2-pilot team → D'Hauw confirmed manually)
- Manual correction for Boutonnet stint 14 (puncture, laps 93-96 excluded) logged in `stint_corrections` table

## Session 5 — UX iteration
- Trailing rolling window + P5 percentile (instead of centered + Math.min) — no future data leakage
- Window size slider (15/30/60 min)
- Driver multi-select filter on Overview scatter
- Gap-to-P1 column corrected in stint table (was computing vs `xDomainMin`)
- All timestamps converted from UTC to CEST at the data loader layer
- Track map (Nürburgring sector layout) integrated into Sector Analysis

## Session 6 — Driver scoring analysis
- Computed composite z-score model:
  - AvgZ (gap to mean of peers / std)
  - RobustZ (gap to P1 / IQR)
  - Percentile rank
  - Weights: -0.4×AvgZ - 0.4×RobustZ + 0.2×PctRank
- Tested with last stint included vs excluded
- Result: Boutonnet ranks higher excluding stint 18 (his last stint, +15s vs P1)
- Analysis exists in chat history only — not yet a dashboard page

## Session 7 — Design polish (failed attempt, then recovered)
- First polish attempt broke: used `style: "style/custom.css"` in config which **overrides** the dark theme entirely → white-on-white site
- Reverted via `git revert` (commit `9e7bda2`)
- Tagged the broken state as `broken-polish-39c42bf` for reference

## Session 8 — Dual-track deployment
- Built a second dashboard `dashboard-polish/` with all design improvements
- Deployed to `/polish/` sub-path via `base:` config + combined-artifact CI
- Main URL stayed untouched, polish preview at `/polish/`
- Validated the polish in isolation

## Session 9 — Promotion of polish to main
- Tagged previous stable as `stable-pre-polish-swap-20260518`
- Swapped `dashboard-polish/` contents into `dashboard/`
- Removed `base:` from config (now root deployment)
- Cleaned title/footer of "polish" suffix
- Removed `dashboard-polish/` folder and reverted workflow to single build
- Polish design is now the canonical stable version

## Key technical pitfalls discovered
1. **`style:` directive in Observable config replaces theme** — never use it, inline the CSS inside `head:` `<style>` block instead
2. **`mix-blend-mode:multiply` is black-on-black on dark themes** — for white-bg images use `filter: invert(1) hue-rotate(180deg)`
3. **`localeCompare(null)` throws** — defensive `(value ?? "")` is required when sorting driver names
4. **JSON data files committed to git** must be regenerated whenever the DB schema or driver name corrections change
5. **`base:` in Observable config rewrites all asset URLs** — only use for sub-path deployments, remove when promoting to root

## How to resume in the next session
1. Read `STATUS.md` for current state
2. Source of truth is `m240i_sector_times.db` (gitignored, local only)
3. Data loaders: `dashboard/src/data/*.json.py` — run them whenever DB changes, JSON files are committed
4. Build locally: `cd dashboard && npm install && npm run build`
5. Push to `main` triggers automatic GitHub Pages deploy via Actions
6. Backup rollback points listed in `STATUS.md`

## Files structure
```
Simple 24hrs app/
├── m240i_sector_times.db          # SQLite source of truth (gitignored)
├── Data Source/                    # Raw PDF + race photos (gitignored)
├── dashboard/                      # Observable Framework site (deployed)
│   ├── observablehq.config.js     # ⚠ inline CSS in head, NO style: directive
│   ├── src/
│   │   ├── index.md               # Overview
│   │   ├── stint-rankings.md      # Stint Rankings
│   │   ├── sector-analysis.md     # Sector Analysis
│   │   ├── about.md               # About + car photo
│   │   ├── assets/                # logos, car photo, track map
│   │   └── data/*.json.py         # Python data loaders → CEST JSON
├── .github/workflows/deploy.yml    # GitHub Pages CI
├── .opencode/skills/               # Project skills: design, stats, sqlite
├── STATUS.md                       # Current state snapshot
└── JOURNAL.md                      # This file
```
