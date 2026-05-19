# AGENTS.md — 24h Nürburgring M240i / SP9 Dashboard

## Project orientation

**Live site**: https://ggbsnowbird.github.io/24h-nurburgring-m240i/
**Repo**: https://github.com/ggbsnowbird/24h-nurburgring-m240i
**Stack**: Observable Framework · SQLite (`nbr_sector_times.db`) · Python data loaders · GitHub Pages

Read these files before starting any session:
- `STATUS.md` — current state, schema, open items, backup tags
- `JOURNAL.md` — session history, pitfalls discovered
- `PLAN-GT3-EXPANSION.md` — SP9 expansion plan (if working on GT3)

---

## Skills — when to invoke them

### Project skills (`.opencode/skills/`)

| Skill | Invoke when |
|---|---|
| `stint-ranking` | Any work on stints, rankings, methodology — contains the 8 invariants |
| `sqlite-queries` | Writing SQL, schema questions, per-class query patterns |
| `racing-stats` | Statistical models, driver scoring, pace analysis |
| `dashboard-design` | CSS, theme, layout, images — especially the `style:` pitfall |
| `data-viz-racing` | Observable Plot charts, heatmaps, scatter plots |

### External skills (also in `.opencode/skills/`)

| Skill | Invoke when |
|---|---|
| `github-actions-templates` | Modifying `.github/workflows/deploy.yml` |
| `github-actions-docs` | Debugging CI/CD failures |
| `publish-to-pages` | GitHub Pages deploy issues |
| `deploy-to-vercel` | If migrating away from GitHub Pages |
| `kpi-dashboard-design` | Adding KPI strips or metrics cards to pages |
| `data-storytelling` | Improving chart narrative and annotation |
| `frontend-design` | UI layout and component design |
| `responsive-design` | Mobile layout (deferred but planned) |
| `visual-design-foundations` | Colour, typography, spacing decisions |
| `modern-javascript-patterns` | Observable Framework JS patterns |
| `python-code-style` | Data loader Python scripts |
| `python-performance-optimization` | Slow loader scripts (sectors.json.py is ~30s) |
| `python-testing-patterns` | Adding tests to scripts |
| `sql-optimization` | Slow SQLite views (stint_ranking_sp9 is large) |
| `sql-code-review` | Reviewing new views/queries |
| `data-quality-frameworks` | Consistency checks, validation scripts |
| `conventional-commit` | Commit message formatting |
| `debugging-strategies` | General debugging approach |
| `systematic-debugging` | Complex multi-step bugs |
| `code-review-excellence` | Pre-push code review |

---

## Critical rules — never deviate

1. **Never set `style:` in `observablehq.config.js`** — it overrides the dark theme → white page. Use `head:` `<style>` block instead.
2. **690s threshold** everywhere (not 1200s — that's obsolete).
3. **Outlap always excluded**: `lap_no > stint.lap_start` (never `BETWEEN`).
4. **4-minute lookback** on comparison windows: `DATETIME(ref.day_time_start, '-4 minutes')`.
5. **CEST in JSON output, UTC in DB** — conversion done in Python loaders via `utc_to_cest()`.
6. **`class` column is case-sensitive**: `'M240i'` and `'SP9'` exactly (not `'M240I'`, not `'sp9'`).
7. **Per-class views only**: `stint_ranking_m240i` and `stint_ranking_sp9` (the old `stint_ranking` view no longer exists).
8. **SP9 timestamps are reconstructed** from cumulative PDF lap times — do not attempt to re-fetch from LiveTiming WS (session expired).

---

## Working conventions

- Read `STATUS.md` before starting any session
- One commit per logical phase; use conventional commit format
- Run `cd dashboard && npm run build` locally before pushing
- Update `STATUS.md` + `JOURNAL.md` at the end of each session
- Run `python3 scripts/check_class_consistency.py M240i` and `SP9` after any DB change

## Key file map

```
nbr_sector_times.db                  SQLite DB (gitignored, local only)
dashboard/observablehq.config.js     Site config — inline CSS in head:
dashboard/src/index.md               Landing page (class picker)
dashboard/src/m240i/                 M240i pages (4 files)
dashboard/src/sp9/                   SP9 pages (4 files)
dashboard/src/data/m240i/            M240i JSON + Python loaders
dashboard/src/data/sp9/              SP9 JSON + Python loaders
dashboard/src/assets/                logos, car photo, track map
.github/workflows/deploy.yml         Single-dashboard GitHub Pages deploy
.opencode/skills/                    25 skills (5 project + 20 external)
scripts/check_class_consistency.py   DB validation script
scripts/extract_sp9.py               SP9 extraction from PDF
STATUS.md                            Current project state
JOURNAL.md                           Session history
PLAN-GT3-EXPANSION.md                SP9 expansion plan (complete)
```
