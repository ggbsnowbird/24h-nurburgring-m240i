# Project Status — M240i Dashboard

## Project goal
Public web dashboard analysing BMW M240i Racing Cup performance at the **54th ADAC Ravenol 24h Nürburgring** (14-17 May 2026). Data combines the official ADAC sector times PDF with LiveTiming WebSocket timestamps.

## Live deployment
- **Public URL**: https://ggbsnowbird.github.io/24h-nurburgring-m240i/
- **Repo**: https://github.com/ggbsnowbird/24h-nurburgring-m240i
- **Stack**: Observable Framework + SQLite + Python data loaders + GitHub Pages (Actions)
- **Auto-deploys** on every push to `main`

## Current state — DONE

### Database (`m240i_sector_times.db`)
| Table / View | Rows | Purpose |
|---|---:|---|
| `cars` | 11 | M240i car metadata |
| `laps` | 1147 | Raw laps from PDF, 9 sectors per lap |
| `live_timing_laps` | 1147 | UTC timestamps per lap |
| `stints` | 127 | Consecutive same-driver lap groups |
| `stint_ranking` (view) | — | Cross-car ranking in same time window |
| `lap_driver_times` (view) | — | Final mapping driver+lap → daytime |
| `stint_corrections` | 1 | Manual corrections log (Boutonnet stint 14) |

### Dashboard pages
1. **Overview** — pace scatter with P5 trailing rolling min, rolling avg, ±1σ band, driver multi-filter, window size slider (15/30/60 min)
2. **Stint Rankings** — z-score normalised driver ranking per stint window, rank evolution chart on real race time axis
3. **Sector Analysis** — heatmap of sector ranks, per-sector bar chart, delta to best, track map of Nürburgring 24h layout with sector colours
4. **About** — English narrative + car #652 hero photo, methodology explained

### Design system (current — polish promoted to stable)
- Dark theme + Roboto Condensed / JetBrains Mono
- Green NBR accent (#43632d) on header, control bars, info boxes, footer
- Standardised components: `.info-box`, `.stint-meta`, `.control-bar`, `.chart-subtitle`, `.empty-state`
- Track map: `filter: invert(1) hue-rotate(180deg)` to integrate the white-bg webp on dark theme
- Inline `<style>` in `head:` config (NOT `style:` directive — that breaks the dark theme)

### Statistical methodology
- **Outlap excluded** from every stint (cold tyres, pit exit)
- **Laps > 11:30 (690s) excluded** (driver swap, SC, Code 60)
- **4-min lookback** on comparison window start (captures drivers finishing a lap just before)
- **Dynamic sector thresholds**: `median × 2.5` per sector (handles S7 ~217s correctly)
- **Driver scoring**: composite z-score model (-0.4×AvgZ - 0.4×RobustZ + 0.2×PctRank)
  - RobustZ = gap to P1 / IQR (fair comparison across denser vs sparser windows)
  - NOT yet implemented as a dashboard page — analysis exists in chat history only

### M240i cars analysed
`195, 650, 651, 652, 653, 658, 665, 667, 669, 670, 677`

### Manual data corrections logged
- **Car 652 Boutonnet stint 14**: laps 93–96 excluded (puncture + pit). Valid window now laps 97–101.
- **Car 658 stint 2**: `driver_no=3` resolved to `D'Hauw` (only 2 names in PDF "Sari / Sari"). General fix applied: modulo when `driver_no > len(parts)`.

## Backups & rollback points
| Reference | What it points to |
|---|---|
| Tag `stable-pre-polish-swap-20260518` | Last state before promoting polish to main |
| Tag `broken-polish-39c42bf` | Original broken polish attempt (style: directive override) |
| Tag `dashboard.before-polish-swap/` | Local-only mirror (gitignored) |

## Definition of done
1. PDF data + LiveTiming merged in SQLite — ✅
2. Driver/lap/daytime mapping — ✅
3. Per-stint ranking against same-window peers — ✅
4. Sector-level analysis — ✅
5. Public site deployed with polished design — ✅
6. Driver scoring page (composite z-score model) — ⏳ analysed, not yet a UI page

## Open items / next steps
- (optional) Implement Driver Scoring as a 5th dashboard page (composite z-score model, exists in chat analysis)
- (optional) Mobile-responsive grid for the track map + sector pills layout
- (optional) KPI strip at the top of each page
- (optional) Podium row redesign on Cars & crews section

## Critical things to remember for the next session
- **NEVER set `style:` in `observablehq.config.js`** — it overrides the dark theme, breaks the whole site. Keep design CSS inline inside `head:` `<style>` block.
- The webp track map has a white background — use `filter: invert(1) hue-rotate(180deg)`, not `mix-blend-mode:multiply` (black on black).
- `lap_day_time` in DB is **UTC**, but all JSON output is converted to **CEST** (UTC+2) inside the data loader Python scripts.
- Driver names from `cars.drivers` can mismatch `driver_no` (PDF chronograph quirk) — modulo `parts[(driver_no-1) % len(parts)]` is the safe lookup.
- The Nordschleife S7 is ~3:30–4:00 long — sector thresholds use **median × 2.5** per sector dynamically, NOT a fixed value.

## Relevant files
- `dashboard/observablehq.config.js` — site config + inline design CSS
- `dashboard/src/index.md` — Overview page
- `dashboard/src/stint-rankings.md` — Stint Rankings page
- `dashboard/src/sector-analysis.md` — Sector Analysis page
- `dashboard/src/about.md` — About page
- `dashboard/src/data/*.json.py` — Python data loaders (CEST timestamps, dynamic thresholds)
- `dashboard/src/assets/track-sectors.webp` — sector map (white bg, use filter:invert)
- `m240i_sector_times.db` — SQLite source of truth (gitignored)
- `.github/workflows/deploy.yml` — single dashboard build + Pages deploy
- `.opencode/skills/` — local design/data/stats skills
