---
name: data-viz-racing
description: Build racing data visualizations for the 24h Nürburgring M240i project. Covers lap time charts, stint comparison plots, sector heatmaps, and driver ranking charts using Python (matplotlib/plotly) or web (Chart.js/D3). Style guidelines for motorsport dashboards.
license: MIT
compatibility: opencode
metadata:
  domain: motorsport-viz
  stack: python matplotlib plotly chartjs
---

## Preferred stack
- **Python**: `matplotlib` + `seaborn` for static exports, `plotly` for interactive HTML
- **Web**: `Chart.js` for simple embeds, `D3.js` for custom racing-specific charts
- **Data source**: SQLite `m240i_sector_times.db` via `sqlite3` or `pandas`

## Style guidelines (motorsport theme)
- Dark background: `#1a1a2e` or `#0d0d0d`
- Accent colors per car: use a consistent palette (e.g. BMW blue `#0066cc`, accent `#e63946`)
- Fonts: monospace for lap times, sans-serif for labels
- Time axis: format as `MM:SS.mmm`, not raw seconds
- Always show: car number + driver name in legends
- Rank badges: gold/silver/bronze for top 3

## Key chart types for this project

### 1. Stint lap time progression
Line chart: x=lap_no, y=laptime_sec, one line per stint/driver
Useful to see pace evolution within a stint (tyre deg, fuel load)

### 2. Driver ranking heatmap (per stint)
Matrix: rows=stints, cols=drivers, value=rank_by_best
Color: green=good rank, red=bad rank

### 3. Sector comparison bar chart
Grouped bars: sector1..sector9 times for top N drivers in a window
Highlights where time is lost/gained vs best in class

### 4. Stint-to-stint pace evolution
Scatter: x=stint_no (or day_time_start), y=avg_laptime_sec, grouped by driver
Reveals improvement/degradation across race

## Python boilerplate (plotly)
```python
import sqlite3, pandas as pd, plotly.express as px
from pathlib import Path

db = Path('m240i_sector_times.db')
conn = sqlite3.connect(db)

df = pd.read_sql('''
    SELECT ref_driver, ref_stint_no, rank_by_best, avg_laptime_sec
    FROM stint_ranking WHERE ref_car_no=652 AND ref_driver="Boutonnet"
    ORDER BY ref_stint_no
''', conn)

fig = px.line(df, x='ref_stint_no', y='rank_by_best',
              title='Boutonnet rank across stints (lower=better)',
              template='plotly_dark')
fig.write_html('boutonnet_ranking.html')
```

## Car images / liveries
- Use the RACB / ADAC official entry list for livery references
- For web display: fetch car images from `livetiming.azurewebsites.net` assets or ADAC media
- Fallback: generate colored car silhouettes (BMW M240i shape SVG) with car number overlay
- Picto source to investigate: check network requests on the live timing page for `/assets/cars/` or `/assets/logos/` paths

## Notes
- Install: `python3 -m pip install --user plotly pandas matplotlib seaborn`
- All times in seconds for computation, format back to MM:SS.mmm for display
- Exclude laps > 1200s (SC/pit) before plotting
