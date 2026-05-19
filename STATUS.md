# Project Status — 24h Nürburgring Dashboard

## Project goal
Public web dashboard analysing BMW M240i Racing Cup and SP9 GT3 performance at the **54th ADAC Ravenol 24h Nürburgring** (May 14–17, 2026).

## Live deployment
- **Public URL**: https://ggbsnowbird.github.io/24h-nurburgring-m240i/
- **Repo**: https://github.com/ggbsnowbird/24h-nurburgring-m240i
- **Stack**: Observable Framework + SQLite + Python data loaders + GitHub Pages (Actions)
- **Auto-deploys** on every push to `main`

## Current state

### ✅ DONE — M240i fully complete
### 🔴 IN PROGRESS — SP9 has 16 missing cars (see open issue below)

### Database (`nbr_sector_times.db`)
| Table / View | Rows M240i | Rows SP9 (current) | Rows SP9 (target) |
|---|---:|---:|---:|
| `cars` | 11 | **26** | **42** |
| `laps` | 1147 | **2473** | **~6000+** |
| `live_timing_laps` | 1147 | **2473** | **~6000+** |
| `stints` | 132 | **224** | **~450+** |

### 🔴 OPEN ISSUE — 16 SP9 cars missing from DB

**Root cause**: `scripts/extract_sp9.py` had an incomplete `MODELS` list. It was missing `Porsche 911 GT3 R` (13 cars) and `Ford Mustang GT3` (3 cars). The full scan confirmed **42 GT3 cars in PDF**, but only 26 were extracted.

**Missing cars** (confirmed by full PDF scan):
```
#4   Goroyan/Kvitka/Berthon/Fontana         Porsche 911 GT3 R
#5   Kaya/Kiefer/Piana/Stursberg             Porsche 911 GT3 R
#17  Andlauer/Boccolacci/Menzel/Picariello   Porsche 911 GT3 R  ← DNS early, ~1am
#18  Tilley/Hill/Kolb/Hofer                 Porsche 911 GT3 R
#24  Heinrich/Vanthoor/Feller               Porsche 911 GT3 R
#30  Kim/Bruins/Cho/Seefried                Porsche 911 GT3 R
#44  Bachler/Heinemann/Müller/Schuring       Porsche 911 GT3 R
#48  Arrow/Assenheimer/Müller/Pereira        Porsche 911 GT3 R
#54  Buus/Christensen/Sturm/Hartog           Porsche 911 GT3 R
#55  Beretta/Ghiretti/Sturm/Hartog           Porsche 911 GT3 R
#64  Maini/Scherer/Schumacher/Stippler       Ford Mustang GT3
#65  Haupt/Kolb/Schumacher/Caresani          Ford Mustang GT3
#67  Olsen/Mies/Vervisch/Stippler            Ford Mustang GT3
#86  Li/Fjordbach/Ye/King                   Porsche 911 GT3 R
#123 Rump/Bünnagel/Brundle                  Porsche 911 GT3 R
#911 Estre/Güven/Preining/Campbell           Porsche 911 GT3 R  ← "Grello" Manthey
```

**DB state is clean** — both extraction attempts were aborted before any commit, so no partial writes exist. DB is safe to re-run.

**What next agent needs to do** (see JOURNAL.md for exact script):
1. Add `'Porsche 911 GT3 R'` and `'Ford Mustang GT3'` to the MODELS list in `scripts/extract_sp9.py`
2. Re-run the extraction **only for missing cars** (skip existing 26 — use `INSERT OR IGNORE`)
3. Run `python3 scripts/check_class_consistency.py SP9`
4. Regenerate all 5 SP9 JSON files
5. Fix the colour palette in `dashboard/src/sp9/` pages (currently 26 colours, need 42)
6. Build + push

### SP9 timestamp source
Race LiveTiming session expired. Timestamps reconstructed from cumulative PDF lap times using `race_start_utc = 2026-05-16T12:59:55.626Z` — verified 0.0s variance against M240i ground truth.

### Driver name correction (this session)
All 26 existing SP9 cars had truncated driver strings (trailing `/`). Fixed by re-parsing with model-aware splitting. 119 stints corrected. Note: **car #17 Boccolacci** (two c's — not "Bocolacci") — he DNF'd around 1am with his Porsche 911 GT3 R.

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
dashboard/src/data/sp9/              SP9 JSON + loaders (need regen after fix)
dashboard/src/sp9/                   SP9 dashboard pages (need colour palette fix)
scripts/extract_sp9.py               SP9 extraction — NEEDS MODELS LIST FIX
scripts/check_class_consistency.py   DB validation script
PLAN-GT3-EXPANSION.md                Original SP9 plan
```
