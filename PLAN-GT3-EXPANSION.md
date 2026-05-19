# PLAN — GT3 (SP9) expansion of the 24h Nürburgring dashboard

This plan is self-contained. Sonnet must read it start to finish before starting Phase 0, then reread Section 2 (methodology contract) and Section 5 (consistency check script) before each phase.

---

## 1. Context & decisions

### Project
Expand the public M240i dashboard (https://ggbsnowbird.github.io/24h-nurburgring-m240i/) to also cover the **SP9 GT3** class from the 54th ADAC Ravenol 24h Nürburgring 2026.

### User decisions (locked, do not revisit)

| Item | Decision |
|---|---|
| Routing | Separate pages per class with a landing picker (option 1A) |
| Class scope | **SP9 only** (all SP9 sub-categories merged into one `/sp9/` view), not GT4/V4/SP-PRO/etc |
| URL slug | `/sp9/` (matches official ADAC class name) |
| Auth | Cloudflare Access — postponed, ship publicly first |
| Commit cadence | **One commit per phase** |
| Target branch | Straight to `main` (no parallel/preview deployment) |
| Execution model | Sonnet |

### Key existing references

| File | Purpose |
|---|---|
| `STATUS.md` | Current project state, schema, methodology summary |
| `JOURNAL.md` | Session-by-session history and pitfalls discovered |
| `m240i_sector_times.db` | SQLite source of truth (will be renamed in Phase 2) |
| `dashboard/observablehq.config.js` | Observable Framework site config |
| `dashboard/src/*.md` | Current 4 M240i pages |
| `dashboard/src/data/*.json.py` | Python data loaders, output JSON to `dashboard/src/data/` |
| `.opencode/skills/stint-ranking/SKILL.md` | Stint methodology skill (will be updated in Phase 0) |
| `.opencode/skills/racing-stats/SKILL.md` | Statistical methodology skill |
| `.github/workflows/deploy.yml` | GitHub Pages deploy workflow |

### Backup tags to know

- `stable-pre-polish-swap-20260518` — state just before the polish promotion
- `broken-polish-39c42bf` — broken `style:` directive attempt
- A new tag `stable-pre-sp9-20260518` should be created at the start of Phase 0

---

## 2. Methodology contract — 8 invariants that MUST be preserved for SP9

These rules apply to every aggregation, view, loader, and chart, for both M240i and SP9. Do not deviate. If a rule appears to conflict with what you find in the codebase, the rule wins.

### Invariant 1 — Outlap exclusion
The first lap of every stint (when a driver enters the track from the pit lane) is excluded from all aggregations.

```sql
WHERE l.lap_no > s.lap_start
```

Never use `BETWEEN s.lap_start AND s.lap_end` for aggregations.

### Invariant 2 — Hard lap ceiling at 690 seconds (11:30)
Laps of 690s or more are excluded from all rankings, stint stats, and lap-time charts. These correspond to driver swaps, Safety Car laps, Code 60, and unscheduled stops.

```sql
WHERE lap_time_sec < 690
```

**Never use 1200s — that was an obsolete threshold and the previous skill documentation still mentions it incorrectly.**

### Invariant 3 — 4-minute lookback on comparison windows
When comparing a reference stint against peers on track at the same time, the window starts **4 minutes before** the reference stint's `day_time_start`. This captures peer drivers who were finishing a lap right before the reference stint began.

```sql
JOIN live_timing_laps comp_l ON ...
  AND comp_l.lap_day_time >= DATETIME(ref.day_time_start, '-4 minutes')
  AND comp_l.lap_day_time <= ref.day_time_end
```

This is applied in the `stint_ranking` view and in `sectors.json.py`.

### Invariant 4 — Dynamic per-sector thresholds
Sector aberrant-value filtering uses `median × 2.5` **per sector**, not a fixed value. Sector 7 (Nordschleife backbone, ~3:30–4:00) requires this approach — a hardcoded 200s threshold incorrectly excludes valid S7 times.

```python
sector_thresholds = {}
for i in range(1, 10):
    if all_sector_vals[i]:
        med = statistics.median(all_sector_vals[i])
        sector_thresholds[i] = med * 2.5
```

### Invariant 5 — `day_time_start` shifted to first valid lap
The `stints.day_time_start` column stores the timestamp of the first **valid** lap (after the outlap), not the outlap itself. This is critical because the `stint_ranking` view uses `day_time_start` as the window boundary.

In practice: when populating the `stints` table, query the laps with `lap_no > stint.lap_start AND lap_time_sec < 690`, take the minimum `lap_day_time` of that subset.

### Invariant 6 — Driver name modulo lookup
PDF chronograph data sometimes uses `driver_no` values higher than the count of pilots in `cars.drivers` (e.g. 4-driver team where driver_no=5 appears due to a chrono quirk, or 2-driver team "Sari / Sari" where driver_no=3 appears).

```python
parts = car_drivers.split(' / ')
driver_name = parts[(driver_no - 1) % len(parts)]
```

After computing modulo, also support manual overrides: a dictionary like `{(car_no, stint_no): "D'Hauw"}` can override the computed name when known.

### Invariant 7 — CEST output, UTC storage
The database stores `lap_day_time` and `day_time_start` in **UTC** (as received from LiveTiming). All JSON output files must convert to **CEST (UTC+2)** in the Python loader. The dashboard reads CEST and uses local hours.

```python
from datetime import datetime, timezone, timedelta
CEST = timedelta(hours=2)
def utc_to_cest(s):
    if not s: return None
    dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)
    return (dt + CEST).strftime('%Y-%m-%dT%H:%M:%S')
```

### Invariant 8 — `stint_corrections` is per-class
The `stint_corrections` table logs manual fixes (e.g. Boutonnet M240i stint 14 — puncture). Any SP9 manual correction must go in the same table. The corrections.json loader filters by class when producing per-class JSON.

If a `class` column does not exist in `stint_corrections`, add it during Phase 2 schema migration with default `M240i`.

---

## 3. Phase 0 — Sync `stint-ranking` skill + create backup tag

### Goal
Make the existing skill accurate before SP9 work starts, and tag the current stable state.

### Steps
1. Create backup tag: `git tag stable-pre-sp9-$(date +%Y%m%d) && git push origin stable-pre-sp9-$(date +%Y%m%d)`
2. Read `.opencode/skills/stint-ranking/SKILL.md`
3. Replace the file contents to:
   - Fix the database name to `nbr_sector_times.db` (will be renamed in Phase 2)
   - Replace `outlier laps > 1200s` with `laps ≥ 690s (11:30)`
   - Add the 8 invariants from Section 2 of this plan
   - Remove M240i-only language; make the skill class-agnostic
   - Add a "Per-class structure" subsection explaining that views are split per class (`stint_ranking_m240i`, `stint_ranking_sp9`)
4. Also update `.opencode/skills/sqlite-queries/SKILL.md` similarly if it mentions the old 1200s threshold or single-class assumption.

### Files to modify
- `.opencode/skills/stint-ranking/SKILL.md`
- `.opencode/skills/sqlite-queries/SKILL.md` (only if it has outdated content)

### Definition of done
- Skill files reflect the 8 invariants
- No mention of 1200s anywhere
- No M240i-only assumptions
- Tag `stable-pre-sp9-YYYYMMDD` pushed to origin

### Commit message
`docs(skill): sync stint-ranking with current methodology before SP9 expansion`

---

## 4. Phase 1 — Investigate PDF + LiveTiming for SP9

### Goal
Confirm SP9 data is extractable using the existing parser and LiveTiming flow, with no code change.

### Steps
1. **PDF inspection** (read-only):
   - Open `Data Source/42_24h_Race_Sector_Times.pdf` with `pdfplumber`
   - Search for car header lines matching the SP9 pattern. The M240i pattern is:
     `^(\d+) (.+) BMW M240i Racing Cup\* theoretical besttime: (.+)$`
   - SP9 cars likely have headers like:
     `^(\d+) (.+) BMW M4 GT3 EVO theoretical besttime: (.+)$`
     or `Mercedes-AMG GT3`, `Porsche 992 GT3 R`, `Audi R8 LMS GT3`, `Ferrari 296 GT3`, `Lamborghini Huracán GT3`, etc.
   - Build a regex that captures all SP9 GT3 cars (any "GT3" in the model string, excluding "GT4")
   - Count cars and report
2. **Sample 2-3 SP9 car blocks**: dump the raw lines and confirm they match the existing parser (same column structure: `lap_no driver_no laptime [sector_time speed]x8 [sector9_time]`)
3. **LiveTiming test**: pick one SP9 car number from step 1, run the existing Playwright capture pattern (see `Session 2` in `JOURNAL.md`) against `livetiming.azurewebsites.net/event/50/laps-data?session=4600205102&startingNo=<CAR_NO>`. Confirm the DATA frame is returned with the expected fields (`L`, `N`, `D`, `T`, `S1..S9`).
4. **Write findings** to `STATUS.md` under a new section `## SP9 expansion — Phase 1 findings`:
   - Number of SP9 cars detected
   - Sample of detected car models
   - Confirmation that parser format matches
   - Confirmation that LiveTiming returns data
5. Commit the `STATUS.md` update.

### Escalation triggers (stop, ask user)
- Zero SP9 cars detected (regex wrong, or PDF doesn't contain GT3 cars)
- SP9 car block uses a different column layout (different sector count, different speed columns)
- LiveTiming returns no DATA frame for the tested SP9 car after 30s wait
- More than 35 SP9 cars detected (colour palette assumption breaks)

### Definition of done
- `STATUS.md` updated with Phase 1 findings
- No code changes in this phase
- A clear go/no-go signal recorded

### Commit message
`docs: SP9 expansion Phase 1 — PDF and LiveTiming feasibility findings`

---

## 5. Phase 2 — Database schema migration + view recreation

### Goal
Make the database multi-class without disturbing existing M240i data.

### Steps

1. **Rename the database file**:
   ```
   mv m240i_sector_times.db nbr_sector_times.db
   ```
   Update `.gitignore` if needed (it likely already ignores `*.db`).

2. **Add `class` column** to all relevant tables with default `'M240i'`:
   ```sql
   ALTER TABLE cars              ADD COLUMN class TEXT DEFAULT 'M240i';
   ALTER TABLE laps              ADD COLUMN class TEXT DEFAULT 'M240i';
   ALTER TABLE stints            ADD COLUMN class TEXT DEFAULT 'M240i';
   ALTER TABLE live_timing_laps  ADD COLUMN class TEXT DEFAULT 'M240i';
   ALTER TABLE stint_corrections ADD COLUMN class TEXT DEFAULT 'M240i';
   ```

3. **Recreate the `stint_ranking` view as per-class**:
   - Drop the existing `stint_ranking` view
   - Create `stint_ranking_m240i` filtering `ref.class='M240i' AND comp.class='M240i'`
   - Create `stint_ranking_sp9` filtering `ref.class='SP9' AND comp.class='SP9'`
   - Each view must apply Invariants 1, 2, 3 (outlap, 690s, 4-min lookback)
   - SP9 view is empty for now (no SP9 data yet)

4. **Recreate `lap_driver_times` view** similarly per-class if it exists.

5. **Update all `.json.py` loaders** to point to `nbr_sector_times.db` instead of `m240i_sector_times.db`. Loaders still output the same JSON files unchanged in this phase — restructuring comes in Phase 4.

6. **Verify M240i regression-free**:
   - Run all 5 loaders (`stints`, `ranking`, `sectors`, `corrections`, `all_laps`)
   - Compare output JSON files to the pre-migration version (byte-compare or row-count compare)
   - Counts must match exactly

### Files to modify
- `m240i_sector_times.db` → `nbr_sector_times.db` (rename + schema migration)
- `dashboard/src/data/stints.json.py`
- `dashboard/src/data/ranking.json.py`
- `dashboard/src/data/sectors.json.py`
- `dashboard/src/data/corrections.json.py`
- `dashboard/src/data/all_laps.json.py`

### Escalation triggers
- Pre/post migration JSON files differ in row count or content
- A loader fails to find the DB

### Definition of done
- DB renamed and migrated
- Per-class views created (M240i populated, SP9 empty)
- All 5 loaders run successfully and produce identical JSON to pre-migration
- M240i pages still build cleanly: `cd dashboard && npm run build`

### Commit message
`feat(db): multi-class schema migration — add class column and per-class views`

---

## 6. Phase 3 — Extract SP9 data (PDF + LiveTiming)

### Goal
Populate the database with SP9 data using the existing extraction infrastructure.

### Steps

1. **Extend the PDF parser** (a script in the project root, similar to the original M240i extraction):
   - Walk the PDF page by page
   - Detect class via car header regex (use the SP9 pattern confirmed in Phase 1)
   - For each detected SP9 car: insert into `cars` with `class='SP9'`
   - For each lap row: insert into `laps` with `class='SP9'`, parsing the existing format
   - Apply Invariant 6 (driver name modulo) when computing driver names for stints

2. **Capture LiveTiming for SP9** using the existing Playwright pattern (Session 2 in `JOURNAL.md`):
   - Loop over SP9 car numbers found in step 1
   - For each car: navigate to `livetiming.azurewebsites.net/event/50/laps-data?session=4600205102&startingNo=<CAR_NO>`, capture the DATA frame, insert into `live_timing_laps` with `class='SP9'`
   - **Add 2s sleep between cars** to avoid rate limiting

3. **Compute SP9 stints**:
   - Group SP9 laps by car, detect driver changes via `driver_no` changes
   - Apply Invariant 5: `day_time_start` = timestamp of `lap_start + 1`, filtered for `lap_time < 690s`
   - Insert into `stints` with `class='SP9'`
   - Compute `best_laptime_sec` and `avg_laptime_sec` after Invariants 1 and 2

4. **Run the consistency check script** (Section 7 of this plan). If any check fails for SP9 → stop and escalate.

### Files to create
- A new extraction script, e.g. `extract_sp9.py` in the project root (gitignored or kept)

### Escalation triggers
- PDF parser regex misses some SP9 cars (count diverges from Phase 1)
- LiveTiming Playwright capture fails for any car (timeout, no DATA frame)
- Consistency check script reports any failure

### Definition of done
- SP9 cars present in `cars` table
- SP9 laps and stints populated
- LiveTiming timestamps merged
- Consistency check script passes all 5 conditions
- Counts reported in commit message

### Commit message
`feat(data): SP9 cars/laps/stints extracted from PDF + LiveTiming (N cars, M laps)`

---

## 7. Consistency check script

Sonnet must save this as `scripts/check_class_consistency.py` and run it after Phase 3 (for SP9) and before Phase 4 (re-run for both M240i and SP9 as regression check).

```python
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

# Check 2: day_time_start matches first valid lap (lap_start + 1 if it exists)
rows = cur.execute("""
    SELECT s.car_no, s.stint_no, s.day_time_start, s.lap_start,
           (SELECT MIN(lt.lap_day_time)
              FROM live_timing_laps lt
              JOIN laps l ON l.car_no=lt.car_no AND l.lap_no=lt.lap_no
              WHERE l.car_no=s.car_no
                AND l.lap_no > s.lap_start
                AND l.lap_no <= s.lap_end
                AND lt.lap_day_time IS NOT NULL) AS first_valid
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
print(f"Stints: {n_stints}, Laps: {n_laps_class}, Sector1 coverage: {100*n_with_s1/max(n_laps_class,1):.1f}%")
if failures:
    print("FAILED:")
    for f in failures: print(f"  - {f}")
    sys.exit(1)
print("PASS — all 5 checks succeeded")
conn.close()
sys.exit(0)
```

Run with: `python3 scripts/check_class_consistency.py M240i` and `python3 scripts/check_class_consistency.py SP9`.

---

## 8. Phase 4 — Restructure data loaders to per-class JSON

### Goal
Output JSON files into per-class subdirectories so dashboard pages load only their class's data.

### Steps

1. **Restructure data directory**:
   ```
   dashboard/src/data/m240i/stints.json
   dashboard/src/data/m240i/ranking.json
   dashboard/src/data/m240i/sectors.json
   dashboard/src/data/m240i/corrections.json
   dashboard/src/data/m240i/all_laps.json
   dashboard/src/data/sp9/stints.json
   ...
   ```

2. **Update each `.json.py` loader** to:
   - Accept a class name via environment variable: `CLASS_FILTER` (default: `M240i`)
   - Filter all queries with `WHERE class = ?`
   - The view used must match: `stint_ranking_m240i` or `stint_ranking_sp9`
   - Output path must be `dashboard/src/data/<class_lower>/<file>.json`

3. **Update Observable Framework data loader paths**:
   - Each `.json.py` file must be moved into `dashboard/src/data/m240i/` and `dashboard/src/data/sp9/` (or use a single loader that runs twice with different env vars — Observable supports the latter pattern with file naming).
   - Simpler approach: duplicate each loader, hardcode the class. Less elegant, more reliable.

4. **Verify M240i regression-free**:
   - All M240i pages must still build correctly (FileAttachment paths will change in Phase 5)
   - Counts in each JSON must match pre-restructure counts

### Files to modify
- `dashboard/src/data/*.json.py` (refactor or duplicate per class)
- `dashboard/src/data/` directory structure

### Escalation triggers
- M240i JSON output row counts differ from pre-restructure
- A loader fails to write its target path

### Definition of done
- `dashboard/src/data/m240i/*.json` populated, identical row counts to pre-restructure
- `dashboard/src/data/sp9/*.json` populated with SP9 data
- Consistency check script still passes for both classes

### Commit message
`feat(data): per-class JSON loaders — outputs split into m240i/ and sp9/ subdirectories`

---

## 9. Phase 5 — Multi-page routing

### Goal
Add the landing page + SP9 pages, keep M240i pages working.

### Steps

1. **Restructure `dashboard/src/` directory**:
   ```
   src/
   ├── index.md                 ← NEW landing page with class picker
   ├── m240i/
   │   ├── overview.md          ← renamed from src/index.md
   │   ├── stint-rankings.md
   │   ├── sector-analysis.md
   │   └── about.md
   ├── sp9/
   │   ├── overview.md
   │   ├── stint-rankings.md
   │   ├── sector-analysis.md
   │   └── about.md
   ├── assets/                  ← shared
   └── data/m240i/, data/sp9/   ← from Phase 4
   ```

2. **Create the landing page** `src/index.md`:
   - Header: race name, dates, brief intro
   - Two side-by-side cards:
     - M240i Racing Cup → `/m240i/overview` (with car count, stint count, lap count)
     - SP9 GT3 → `/sp9/overview` (with car count, stint count, lap count)
   - Style consistent with the polished design (uses the same NBR green accent, Roboto Condensed)
   - Counts loaded from each class's `stints.json` and `all_laps.json`

3. **Move M240i pages**: copy `src/index.md`, `src/stint-rankings.md`, `src/sector-analysis.md`, `src/about.md` into `src/m240i/` (rename `index.md` to `overview.md`). Update all `FileAttachment` paths from `data/foo.json` to `data/m240i/foo.json`.

4. **Duplicate to SP9**: copy the 4 M240i pages into `src/sp9/`. Inside each:
   - Update `FileAttachment` paths to `data/sp9/foo.json`
   - Update page title (e.g. "Overview — SP9 GT3")
   - Replace `CAR_COLORS` palette: SP9 has more cars, generate ~30 distinct colours using `d3.interpolateRainbow(i / N)` or a curated palette
   - In About: replace the M240i car photo with a generic SP9 photo if available, otherwise omit the photo for SP9 about page
   - Track map (`track-sectors.webp`) is the same image, reused

5. **Update `observablehq.config.js` pages**:
   ```js
   pages: [
     { name: "Home", path: "/" },
     {
       name: "M240i Racing Cup",
       pages: [
         { name: "Overview",        path: "/m240i/overview" },
         { name: "Stint Rankings",  path: "/m240i/stint-rankings" },
         { name: "Sector Analysis", path: "/m240i/sector-analysis" },
         { name: "About",           path: "/m240i/about" },
       ]
     },
     {
       name: "SP9 GT3",
       pages: [
         { name: "Overview",        path: "/sp9/overview" },
         { name: "Stint Rankings",  path: "/sp9/stint-rankings" },
         { name: "Sector Analysis", path: "/sp9/sector-analysis" },
         { name: "About",           path: "/sp9/about" },
       ]
     },
   ],
   ```

6. **Build and check pages**:
   - `cd dashboard && npm install && npm run build`
   - Open `dist/index.html`, both `m240i/overview.html`, both `sp9/overview.html`
   - No console errors, all charts render

### Files to create / modify
- `dashboard/src/index.md` (new landing page)
- `dashboard/src/m240i/*.md` (4 files, copies of current)
- `dashboard/src/sp9/*.md` (4 files, copies adapted for SP9)
- `dashboard/observablehq.config.js` (pages array updated)

### Escalation triggers
- M240i pages break after restructure
- SP9 charts have rendering errors due to data shape differences
- Build time exceeds 3 minutes
- Page count breaks Observable sidebar layout

### Definition of done
- Landing page renders with both class cards
- All 8 content pages (4 M240i + 4 SP9) build and render
- Sidebar navigation shows the grouped layout
- Console clean on all pages

### Commit message
`feat(routing): per-class pages with landing picker — /m240i/ and /sp9/`

---

## 10. Phase 6 — Deploy, verify, document

### Goal
Ship to production, update documentation.

### Steps

1. **Final local build**: `cd dashboard && npm run build`
2. **Push to main**: existing GitHub Actions workflow auto-deploys
3. **Wait for deploy** (~1 min), verify https://ggbsnowbird.github.io/24h-nurburgring-m240i/ shows the new landing page
4. **Click through both classes**: confirm no regressions on M240i, SP9 pages all work
5. **Update `STATUS.md`**:
   - Bump "Live deployment" section with the new class support
   - Update "Database" section with new class column
   - Update "Dashboard pages" section: 1 landing + 4 M240i + 4 SP9
   - Add "SP9 expansion completed" note in "Definition of done"
6. **Update `JOURNAL.md`**:
   - Add Session N+1 entry: "GT3 (SP9) expansion — Phases 0 to 6"
   - List the key technical decisions and any pitfalls encountered

### Files to modify
- `STATUS.md`
- `JOURNAL.md`

### Definition of done
- Both classes accessible from /
- Deployment successful
- Documentation updated

### Commit message
`docs: SP9 expansion shipped — update STATUS and JOURNAL`

---

## 11. Risk register & escalation rules (consolidated)

Sonnet must **stop and escalate to the user** if any of these triggers fire:

| # | Trigger | Action |
|---|---|---|
| 1 | PDF format for SP9 differs from M240i (different sector count, column layout) | Stop after Phase 1, ask user |
| 2 | LiveTiming returns no DATA for any SP9 car after 30s | Stop after Phase 1, ask user |
| 3 | More than 35 SP9 cars detected | Stop after Phase 1, ask user (colour palette concern) |
| 4 | Pre/post DB migration JSON row counts differ for M240i | Stop after Phase 2, ask user |
| 5 | Consistency check fails on any of 5 conditions | Stop after Phase 3, ask user |
| 6 | M240i pages fail to build after Phase 4 or Phase 5 refactor | Stop, ask user |
| 7 | Build time exceeds 3 minutes | Stop, ask user (performance issue) |
| 8 | Any unexpected error during Playwright capture | Stop, ask user (don't retry silently) |

Do not improvise solutions to any of these. Always escalate.

---

## 12. Cloudflare Access setup (deferred — Phase 7, when user is ready)

This section is informational only for Sonnet during this expansion. Sonnet does not execute any of this. It's here so the user can refer back to it later.

### Prerequisites
- A domain the user controls (~$10/year, or use one already owned)
- Free Cloudflare account

### Steps for the user (~30 min total)

1. **Add domain to Cloudflare** (free plan)
2. **Configure GitHub Pages custom domain**:
   - In repo settings → Pages → Custom domain: enter `nbr.yourdomain.com`
   - Wait for SSL cert provisioning (a few minutes)
3. **Add CNAME in Cloudflare DNS**:
   - Type: CNAME
   - Name: `nbr`
   - Target: `ggbsnowbird.github.io`
   - Proxy status: **orange cloud** (proxied)
4. **Configure Cloudflare Zero Trust**:
   - Dashboard → Zero Trust → Access → Applications → Add an application → Self-hosted
   - Application name: `24h NBR Dashboard`
   - Application domain: `nbr.yourdomain.com` with path `/*`
   - Identity provider: One-Time PIN (default — emails get a PIN sent)
   - Policy: Include → Emails → paste comma-separated list of allowed emails (drivers, team members)
   - Session duration: 24h or longer
5. **Test in incognito**: visit `https://nbr.yourdomain.com` → email prompt → receive PIN by mail → enter PIN → access granted
6. **Manage access**: add or remove emails any time from the policy

### Removing auth later
- In Cloudflare Zero Trust → Applications → delete the application
- Site immediately becomes public again

---

## 13. Definition of done for the whole expansion

Sonnet must verify all of these before declaring the expansion complete:

- [ ] Backup tag `stable-pre-sp9-YYYYMMDD` created and pushed
- [ ] `stint-ranking` skill updated to match the 8 invariants
- [ ] `sqlite-queries` skill checked and updated if outdated
- [ ] Database migrated, renamed to `nbr_sector_times.db`, per-class views in place
- [ ] SP9 data extracted: cars, laps, stints, live timing — all tagged with `class='SP9'`
- [ ] Consistency check script passes for both `M240i` and `SP9`
- [ ] Per-class JSON files at `dashboard/src/data/m240i/` and `dashboard/src/data/sp9/`
- [ ] Landing page at `/` with two class cards
- [ ] M240i pages still work, no regressions
- [ ] SP9 pages work, all charts render
- [ ] Sidebar shows grouped navigation
- [ ] Site deployed and live
- [ ] `STATUS.md` and `JOURNAL.md` updated
- [ ] 6 commits visible in `git log` matching the templated messages above (one per phase, plus the docs update)

---

End of plan. Sonnet: start with Phase 0.
