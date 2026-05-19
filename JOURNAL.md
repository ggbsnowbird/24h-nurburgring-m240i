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

## Session N+1 — SP9 (GT3) expansion — Phases 0 to 6

### What was built
Full expansion of the dashboard to cover the SP9 GT3 class alongside M240i.

### Key technical decisions and discoveries

**Phase 0**: Updated `stint-ranking` and `sqlite-queries` skills to fix the obsolete 1200s threshold and add all 8 methodology invariants.

**Phase 1**: 26 SP9 cars found in PDF, same row format as M240i. LiveTiming WS session expired post-race — DATA frames no longer served. **Workaround**: cumulative lap time reconstruction exact to 0.0s variance against M240i LiveTiming ground truth. Race start: `2026-05-16 12:59:55.626 UTC`.

**Phase 2**: Renamed DB to `nbr_sector_times.db`, added `class TEXT DEFAULT 'M240i'` column to all tables, recreated views as `stint_ranking_m240i` and `stint_ranking_sp9`.

**Phase 3**: Extracted 26 SP9 cars, 2473 laps, 224 stints from PDF. Timestamps reconstructed. Sector times re-parsed from raw lines (98% S1-S8, 84% S9 — same truncation as M240i). Consistency check: PASS all 5.

**Phase 4**: Per-class JSON loaders in `data/m240i/` and `data/sp9/`. CLASS variable was `M240I` (wrong case) due to `tr '[:lower:]' '[:upper:]'` — fixed to `M240i`.

**Phase 5**: Landing page + 8 sub-pages. SP9 car palette: 26 colours via HSL interpolation. Built 12 pages, zero errors.

**Phase 6**: Deploy + doc update.

### Pitfalls discovered
- `tr '[:lower:]' '[:upper:]'` converts `m240i` to `M240I` but DB has `M240i` — always hardcode class strings
- LiveTiming sessions are ephemeral — only stream DATA during active race. No archival endpoint.
- Cumulative lap time reconstruction works perfectly for closed-event data (no SC gaps matter here because the timestamps include all laps, SC or not)

## Session N+2 — SP9 driver fixes + AGENTS.md + incomplete SP9 extraction

### What was done
- **AGENTS.md** created at repo root: skill invocation table (25 skills), 8 critical rules, working conventions, key file map
- **20 external skills** copied from `Skills/skills/` into `.opencode/skills/` (deploy-to-vercel, publish-to-pages, github-actions-*, python-*, sql-*, kpi-dashboard-design, frontend-design, data-storytelling, etc.)
- **SP9 driver strings fixed**: all 26 existing SP9 cars had truncated driver names (trailing `/` due to regex stopping before last pilot). 119 stints corrected. Full driver lists now include e.g. `van der Linde` (#1), `Juncadella` (#3), etc.
- **Bocolacci investigation**: car #17 is `Andlauer / Boccolacci / Menzel / Picariello` (two c's). DNF'd around 1am. Car #992 drivers were `Griesemann / Griesemann / Adorf` — "Holzer" is the team name, not a pilot.
- **Full SP9 audit**: PDF contains **42 GT3 cars**, not 26. 16 were missed due to incomplete MODELS list in `scripts/extract_sp9.py` (missing `Porsche 911 GT3 R` and `Ford Mustang GT3`).

### What is NOT done — handoff to next agent

**🔴 Critical**: Add the 16 missing SP9 cars to the DB.

**Exact steps**:

1. **Fix `scripts/extract_sp9.py`** — add to the `MODELS` list:
   ```python
   'Porsche 911 GT3 R EVO',
   'Porsche 911 GT3 R',
   'Ford Mustang GT3',
   ```
   The list is around line 20. Also update the header regex to be more robust — the broader pattern that worked:
   ```python
   MODELS.sort(key=len, reverse=True)  # must always sort desc
   ```

2. **Run extraction for missing cars only**:
   ```bash
   python3 scripts/extract_sp9.py --missing-only
   ```
   OR modify the script to skip cars already in DB using `INSERT OR IGNORE` + checking `existing` set. The script already uses `INSERT OR IGNORE` on laps, but the main loop needs to track `existing` cars and skip re-inserting them.

   **Important**: The single-pass approach (scan all 633 pages once) is the only approach that won't time out. Two previous attempts timed out because they scanned the PDF multiple times. The script must do ONE pass through all pages, tracking current_car and only writing when current_car is in the missing set.

   **The working script logic** (from the session — use this as template):
   ```python
   RACE_START_UTC = datetime(2026, 5, 16, 12, 59, 55, 626000, tzinfo=timezone.utc)
   # Load existing cars from DB first
   existing = set(r[0] for r in cur.execute("SELECT car_no FROM cars WHERE class='SP9'").fetchall())
   current_car = None
   car_cumulative = {}
   # Single pass through all pages:
   for pg_no, page in enumerate(pdf.pages, 1):
       for line in page.extract_text().splitlines():
           if any_header.match(line):
               m = header_re.match(line)
               if m:
                   car_no = int(m.group(1))
                   if car_no not in existing:
                       # try to match model
                       # set current_car if GT3
                   else:
                       current_car = None  # skip already-extracted cars
           elif current_car and lap_re.match(line):
               # extract lap, compute timestamp, insert
   ```

3. **Run consistency check**:
   ```bash
   python3 scripts/check_class_consistency.py SP9
   ```
   Expected: 42 cars, ~6000 laps, ~450 stints. PASS on all 5 checks.

4. **Regenerate SP9 JSON** (all 5 files):
   ```bash
   python3 dashboard/src/data/sp9/stints.json.py      > dashboard/src/data/sp9/stints.json
   python3 dashboard/src/data/sp9/ranking.json.py     > dashboard/src/data/sp9/ranking.json
   python3 dashboard/src/data/sp9/corrections.json.py > dashboard/src/data/sp9/corrections.json
   python3 dashboard/src/data/sp9/all_laps.json.py    > dashboard/src/data/sp9/all_laps.json
   python3 dashboard/src/data/sp9/sectors.json.py     > dashboard/src/data/sp9/sectors.json
   ```

5. **Fix SP9 colour palette** in `dashboard/src/sp9/overview.md`, `stint-rankings.md`, `sector-analysis.md`:
   The current `CAR_COLORS` only has 26 entries. With 42 cars, need to regenerate:
   ```python
   # 42 distinct colours via HSL interpolation
   import colorsys
   cars = [list of 42 car numbers from DB]
   for i, car in enumerate(cars):
       hue = i / len(cars)
       r, g, b = colorsys.hls_to_rgb(hue, 0.65, 0.85)
       print(f"  {car}: \"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}\",")
   ```

6. **Build and push**:
   ```bash
   cd dashboard && npm run build
   # check 12 pages build clean
   git add -A && git commit -m "feat(sp9): add 16 missing SP9 cars (Porsche GT3 R + Ford Mustang GT3)"
   git push
   ```

### Pitfall discovered
- The PDF full-scan (633 pages) takes ~8-10 min in Python with pdfplumber — only do ONE pass
- The script must NOT scan for one car at a time (13 separate scans = timeout)
- `INSERT OR IGNORE` is safe — idempotent, won't duplicate existing cars/laps

### DB state at handoff
- **Clean** — no partial writes, safe to start fresh
- 26 SP9 cars, 2473 laps, 224 stints (pre-fix state)
- M240i fully intact (11 cars, 1147 laps, 132 stints)

## Session N+3 — 16 missing SP9 cars added (real root cause was the regex, not a MODELS list)

### Diagnosis (the previous handoff was wrong about the cause)
The previous session attributed the miss to an incomplete hardcoded `MODELS` list, but `scripts/extract_sp9.py` was already using a generic regex. The actual root cause was a **character-class gap**:

```python
# Before
r'^(\d+)\s+(.+?)\s+([\w\s\-\.]+GT3[\w\s\-\.]*)\s+theoretical besttime:\s+(.+)$'
```

The model character class `[\w\s\-\.]` excluded `(` and `)`. The 16 missing cars all carry parenthesised generation tags in their model string:
- `Porsche 911 GT3 R (992) Evo26` (13 cars)
- `Ford Mustang GT3 EVO (2026)` (3 cars)

So the regex silently failed on every line where the model contained `(`.

### Fix
1. **Anchor model on a known make** so the non-greedy `(.+?)` driver group can't truncate prematurely:
```python
MAKES = r'(?:BMW|Porsche|Mercedes-AMG|Audi|Ferrari|Lamborghini|Aston Martin|McLaren|Ford)'
SP9_HEADER_RE = re.compile(
    r'^(\d+)\s+(.+?)\s+(' + MAKES + r'[\w\s\-\.()]*GT3[\w\s\-\.()]*)\s+theoretical besttime:\s+(.+)$'
)
```
Adding `()` to the char class is necessary to catch the parens. Anchoring on a make is necessary to capture the full drivers list — the previous non-anchored regex truncated drivers because the engine picked the shortest non-greedy match.

2. **Exclude Carrera Cup, keep #992 Manthey**. The broader regex now also matches `Porsche 911 GT3 Cup (992)` (14 separate Cup cars across the PDF — they run in class CUP, not SP9). Filter them out with a case-sensitive check; `'GT3 CUP MR'` (all-caps, #992) is the legitimate Manthey SP9 entry, so distinguish on case:
```python
is_sp9 = bool(m) and 'GT4' not in m.group(3).upper() and 'GT3 Cup' not in m.group(3)
```

3. **Reset `current_car` on every non-SP9 header**. The previous branch only reset when `SP9_HEADER_RE` didn't match. Since Cup headers now match `SP9_HEADER_RE` (and then get rejected by the Cup filter), the old reset branch left `current_car` pointing at the previous SP9 car, and Cup-car lap rows got attributed to it. The new flow:
```python
if ANY_HEADER_RE.match(line):
    if is_sp9:
        # set current_car, insert if new
    else:
        current_car = None
    continue
```

### What was caught when I forgot the reset
First re-run (after only fixing the char class) inserted 30 cars and 3694 laps. Car #911 alone got 426 laps with driver_no values cycling through 1,1,1,2 four times per lap — the laps of every Cup car after page 537 were being written under #911. Spotted via `SELECT car_no, COUNT(*) FROM stints WHERE class='SP9' GROUP BY car_no ORDER BY 2 DESC`. After wiping SP9 cleanly and applying the reset fix, the second run produced the expected 42 cars / 4369 laps / 379 stints.

### Result
| Class | cars | laps | stints |
|---|---:|---:|---:|
| M240i | 11 | 1147 | 132 |
| SP9   | **42** | **4369** | **379** |

`scripts/check_class_consistency.py SP9` → PASS all 5.
`npm run build` → clean 12 pages.

### Side effects
- `dashboard/src/data/sp9/sectors.json` grew from 17.8 MB to 53 MB (cubic-ish growth with car count via cross-stint comparison windows). Still under GitHub Pages' 100 MB file limit; left as-is.
- `dashboard/src/data/sp9/ranking.json` grew from a few MB to 6.3 MB. Acceptable.
- 42-colour palette regenerated via `colorsys.hls_to_rgb(i/42, 0.65, 0.85)` and propagated to all three SP9 pages.

### Pre-existing issue noted (not fixed)
`check_class_consistency.py M240i` reports `Check 1: 5 stints have best_laptime_sec >= 690s`. This was already true before this session — the SP9 extractor never touches M240i stints. Most likely Code-60 / Safety-Car periods where every lap of a stint was slow. Out of scope here.

### Pitfalls discovered (carry these into future PDF parsing work)
- **Parens in models break naive char classes.** Always include `()` when the right side of a non-greedy match contains real product names — Porsche, Ford, etc. love bracketed homologation tags.
- **Anchor model regex on a known make** rather than letting a generic char class consume drivers. A non-greedy `.+?` is happy to land the model boundary one word inside the drivers list if the make is unconstrained.
- **`ANY_HEADER_RE` must reset `current_car`** regardless of whether the new header matches the target class. Otherwise rejected-class laps silently get attributed to the previous accepted car.
- **GLOB vs LIKE on SQLite.** `LIKE '%Cup%'` is case-insensitive and would clobber the legit `#992` "CUP MR" entry; `GLOB '*Cup*'` is case-sensitive — use it when distinguishing on letter case.
