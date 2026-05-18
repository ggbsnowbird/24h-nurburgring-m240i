---
name: racing-stats
description: Statistical models and methods for endurance racing lap time analysis. Covers track evolution correction, driver comparison under comparable conditions, tyre degradation modelling, outlier detection, and pace normalisation for the 24h Nürburgring M240i dataset.
license: MIT
compatibility: opencode
metadata:
  domain: motorsport-statistics
  references: FastF1, f1metrics, Boschetti & Massaron "Python Data Science Essentials"
---

## Core challenge: track evolution & comparable conditions

In endurance racing (24h), the track evolves continuously (rubber, rain, temperature, safety cars).
**A lap time at 14:00 is NOT comparable to one at 03:00.**
The only fair comparison is: drivers who were on track **at the same time** (±1 lap).

### Key principles (from F1 analysis literature)

1. **Peer group normalisation** — compare driver X's lap time to the median of all drivers
   completing laps in the same time window (our `stint_ranking` view does this)
2. **Outlap exclusion** — first lap after pit exit: cold tyres, full fuel, no track position.
   Always exclude from pace analysis. (Implemented: `lap_no > stint.lap_start`)
3. **Inlap exclusion** — last lap before pit entry: driver managing tyres/fuel.
   Optional but relevant for very long stints.
4. **Safety car / Code 60 filter** — laps > threshold (11:30 = 690s) excluded.
   Remaining spikes detected by IQR or Z-score per stint.

---

## Statistical models for this project

### 1. Relative pace index (RPI)
For driver D in stint S with window W:
```
RPI(D, S) = median(peers in W) / best_lap(D in W)
```
- RPI > 1.0 → faster than median
- RPI < 1.0 → slower than median
- Use for cross-stint comparison (eliminates track evolution)

### 2. Tyre/fuel degradation model (linear regression)
Within a clean stint (no SC, no rain):
```python
import numpy as np
# laps = [(lap_no_in_stint, laptime_sec), ...]
x = np.array([i for i, _ in laps])
y = np.array([t for _, t in laps])
slope, intercept = np.polyfit(x, y, 1)
# slope > 0 → degradation (seconds lost per lap)
# slope < 0 → track improvement (fuel burn / tyre warm-up)
```
Typical values at Nürburgring: +0.5 to +3s per lap degradation.

### 3. IQR outlier detection (per stint)
```python
import numpy as np
q1, q3 = np.percentile(lap_times, [25, 75])
iqr = q3 - q1
clean = [t for t in lap_times if t <= q3 + 1.5 * iqr]
```
More robust than fixed threshold for variable stints.

### 4. Z-score peer comparison
For a driver's best lap vs. their peer group in window W:
```python
from scipy import stats
peer_times = [best_sec for (car, driver), (best_sec, _) in peers]
z = (driver_best - np.mean(peer_times)) / np.std(peer_times)
# z < -1 → notably faster; z > +1 → notably slower
percentile = stats.norm.cdf(z) * 100
```

### 5. Track evolution delta
Compare a driver's lap time to the **class best lap in the same 30-min window**:
```python
window_best = min(peer_times)
delta_pct = (driver_time - window_best) / window_best * 100
# e.g. +2.3% → 2.3% slower than the fastest in class at that moment
```

---

## Outlier detection rules (this project)

| Rule | Threshold | Reason |
|---|---|---|
| Hard ceiling | 690s (11:30) | Driver swap / pit / SC |
| Outlap | `lap_no = stint.lap_start` | Cold tyres, pit exit |
| IQR filter | `Q3 + 1.5*IQR` per stint | Detect remaining spikes |
| Minimum laps | ≥ 2 valid laps per stint | Avoid single-lap artefacts |

---

## Python recipe — full stint pace analysis

```python
import sqlite3, numpy as np
from scipy import stats
from pathlib import Path

db = Path('m240i_sector_times.db')
conn = sqlite3.connect(db)

# Get clean laps for a stint (outlap excluded, < 690s)
def get_clean_laps(car_no, stint_no):
    s = conn.execute(
        'SELECT lap_start, lap_end FROM stints WHERE car_no=? AND stint_no=?',
        (car_no, stint_no)
    ).fetchone()
    rows = conn.execute('''
        SELECT l.lap_no, lt.lap_day_time,
            CASE WHEN instr(l.laptime,':')>0
                 THEN CAST(substr(l.laptime,1,instr(l.laptime,':')-1) AS REAL)*60
                      + CAST(substr(l.laptime,instr(l.laptime,':')+1) AS REAL)
                 ELSE NULL END AS sec
        FROM laps l
        JOIN live_timing_laps lt ON lt.car_no=l.car_no AND lt.lap_no=l.lap_no
        WHERE l.car_no=? AND l.lap_no > ? AND l.lap_no <= ?
    ''', (car_no, s[0], s[1])).fetchall()
    return [(r[0], r[1], r[2]) for r in rows if r[2] and r[2] < 690]

# Relative Pace Index vs peer group
def rpi(driver_best, peer_bests):
    return np.median(peer_bests) / driver_best

# Degradation slope
def degradation(laps):
    if len(laps) < 3: return None
    x = np.arange(len(laps))
    y = np.array([t for _, _, t in laps])
    return np.polyfit(x, y, 1)[0]  # seconds per lap
```

---

## Key references

- **FastF1** (theOehrly) — https://docs.fastf1.dev — battle-tested F1 data pipeline patterns
- **f1metrics** blog — statistical driver ranking via mixed models, peer normalisation
- **Boschetti & Massaron** — "Python Data Science Essentials" — IQR, Z-score, regression recipes
- **Motorsport analytics pattern** — always normalise by peer group in same time window,
  never compare absolute lap times across different sessions or time-of-race positions

---

## Notes specific to 24h Nürburgring M240i

- Track length: 25,378m — sector times S1-S9 are meaningful partial splits
- Race starts Saturday ~15:30 CEST, ends Sunday ~15:30 CEST
- Night laps (22:00→06:00 CEST) typically +15 to +40s vs day laps even for same driver
- Code 60 zones reduce lap times to ~12-15min → hard filter at 690s catches these
- Weather changes (rain) create step changes in pace — detect via sudden increase in
  `window_best` across consecutive 30-min windows
