---
title: Stint Rankings
---

```js
const ranking     = await FileAttachment("../data/m240i/ranking.json").json();
const stints      = await FileAttachment("../data/m240i/stints.json").json();
const corrections = await FileAttachment("../data/m240i/corrections.json").json();
```

```js
const CAR_COLORS = {
  195: "#e63946", 650: "#2196f3", 651: "#4caf50", 652: "#ff9800",
  653: "#9c27b0", 658: "#00bcd4", 665: "#f44336", 667: "#8bc34a",
  669: "#ff5722", 670: "#3f51b5", 677: "#ffc107"
};
const CARS = [...new Set(stints.map(d => d.car_no))].sort((a,b) => a-b);
function driversOf(car) {
  return [...new Set(stints.filter(s=>s.car_no===car).map(s=>s.driver_name).filter(Boolean))].sort();
}
function fmtSec(s) {
  if (!s) return "—";
  return `${Math.floor(s/60)}:${String(Math.round(s%60)).padStart(2,'0')}`;
}
```

# Stint Rankings

<div class="info-box">
  Outlap (first lap of each stint) excluded — cold tyres / pit exit.<br>
  Laps &gt; 11:30 (690s) excluded — driver swap / Safety Car / Code 60.<br>
  Each driver is ranked against all M240i cars on track in the <strong>same time window</strong>.<br>
  Window extended 4 min before stint start to include drivers finishing a lap just before.
</div>

```js
corrections.length > 0 ? html`<div class="correction-log">
  <strong>⚠ Manual corrections</strong>
  ${corrections.map(c => html`<div class="correction-item">
    <span class="badge">#${c.car_no} · Stint ${c.stint_no}</span>
    <span>${c.reason}</span>
    <span class="meta">Laps ${c.original_lap_start}–${c.original_lap_end} → <strong>${c.corrected_lap_start}–${c.corrected_lap_end}</strong> · ${c.corrected_at.slice(0,10)}</span>
  </div>`)}
</div>` : ""
```

<div class="control-bar">

```js
const refCar = view(Inputs.select(CARS, {
  label: "Reference car",
  format: c => `#${c} — ${stints.find(s=>s.car_no===c)?.car_drivers ?? ""}`,
  value: 652
}));
```

```js
const refDrivers = driversOf(refCar);
const refDriver = view(Inputs.select(["All drivers", ...refDrivers], {
  label: "Driver",
  value: refDrivers.includes("Boutonnet") ? "Boutonnet" : "All drivers"
}));
```

</div>

```js
const filteredStints = stints.filter(s =>
  s.car_no === refCar &&
  (refDriver === "All drivers" || s.driver_name === refDriver) &&
  s.best_laptime_sec < 690
);

const filteredRanking = ranking.filter(r =>
  r.ref_car_no === refCar &&
  (refDriver === "All drivers" || r.ref_driver === refDriver) &&
  r.best_laptime_sec < 690
);

const selfRows = filteredRanking.filter(r =>
  r.comp_car_no === refCar &&
  (refDriver === "All drivers" ? r.comp_driver === r.ref_driver : r.comp_driver === refDriver)
);

const maxRank = d3.max(filteredRanking, r => r.rank_by_best) ?? 15;
```

---

## Rank evolution — real race time axis

```js
// Join selfRows with stint start time for proper temporal x axis
const rankLineWithTime = selfRows.map(r => ({
  ...r,
  stint_start: new Date(filteredStints.find(s => s.stint_no === r.ref_stint_no)?.day_time_start ?? ""),
  stint_label: `S${r.ref_stint_no}`
})).filter(r => r.stint_start && !isNaN(r.stint_start));
```

### Rank evolution — real race time

```js
html`<div class="chart-subtitle">${refDriver === "All drivers" ? "All stints" : refDriver} — rank by best lap, plotted at each stint start time</div>`
```

```js
Plot.plot({
  width,
  height: 320,
  marginLeft: 48,
  marginRight: 40,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: {
    label: "Race time (CEST) →",
    type: "time",
    tickFormat: d => {
      return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
    }
  },
  y: {
    label: "↓ Rank (1 = fastest)",
    domain: [1, maxRank + 1],
    reverse: false,
    tickFormat: d => Number.isInteger(d) ? `P${d}` : ""
  },
  marks: [
    Plot.gridY({ stroke: "#2a2a2a" }),
    Plot.ruleY([1], { stroke: "#f0c040", strokeDasharray: "4,3", strokeWidth: 1.5 }),
    Plot.ruleY([3], { stroke: "#4caf50", strokeDasharray: "2,4", strokeWidth: 1, opacity: 0.5 }),
    Plot.line(rankLineWithTime, {
      x: "stint_start",
      y: "rank_by_best",
      stroke: d => CAR_COLORS[d.ref_car_no] ?? "#ff9800",
      strokeWidth: 2.5,
      curve: "linear"
    }),
    Plot.dot(rankLineWithTime, {
      x: "stint_start",
      y: "rank_by_best",
      fill: d => CAR_COLORS[d.ref_car_no] ?? "#ff9800",
      r: 5,
      tip: true,
      title: d => `${d.stint_label} · ${d.ref_driver}\nP${d.rank_by_best} / ${maxRank}\nBest: ${fmtSec(d.best_laptime_sec)}\nLaps in window: ${d.laps_in_window}\n${d.ref_window_start.slice(11,16)}→${d.ref_window_end.slice(11,16)} CEST`
    }),
    Plot.text(rankLineWithTime, {
      x: "stint_start",
      y: "rank_by_best",
      text: d => `P${d.rank_by_best}`,
      dy: -13,
      fontSize: 10,
      fill: "#aaa"
    })
  ]
})
```

---

## Stint detail

<div class="control-bar">

```js
const selectedStint = view(Inputs.select(
  filteredStints.map(s => s.stint_no),
  {
    label: "Stint",
    format: n => {
      const s = filteredStints.find(x => x.stint_no === n);
      return `Stint ${n} · ${s?.driver_name} · L${s?.lap_start}–${s?.lap_end} · ${s?.day_time_start?.slice(11,16)}→${s?.day_time_end?.slice(11,16)} CEST`;
    }
  }
));
```

</div>

```js
const stintRows = filteredRanking
  .filter(r => r.ref_stint_no === selectedStint)
  .sort((a,b) => a.rank_by_best - b.rank_by_best);

const refStint = filteredStints.find(s => s.stint_no === selectedStint);
const p1Sec = stintRows[0]?.best_laptime_sec ?? 560;
const xDomainMax = d3.quantile(stintRows.map(r=>r.best_laptime_sec).sort(d3.ascending), 0.9) * 1.02;
const xDomainMin = p1Sec * 0.99;
```

```js
html`<div class="stint-meta">
  <span>🏎 #${refStint?.car_no} ${refStint?.car_drivers}</span>
  <span>Driver: <strong>${refStint?.driver_name}</strong></span>
  <span>Laps ${refStint?.lap_start}–${refStint?.lap_end} (${refStint?.lap_count} valid)</span>
  <span>${refStint?.day_time_start?.slice(11,16)}→${refStint?.day_time_end?.slice(11,16)} CEST</span>
</div>`
```

```js
html`<h3 style="margin:1.5rem 0 .25rem">Stint ${selectedStint} ranking</h3>
<div class="chart-subtitle">${stintRows.length} drivers on track in this window — ranked by best lap (outlap excluded)</div>${stintRows.length === 0 ? html`<div class="empty-state">No data for this selection — try a different stint or driver.</div>` : ''}`
```

```js
Plot.plot({
  width,
  height: Math.max(180, stintRows.length * 26 + 70),
  marginLeft: 16,
  marginRight: 16,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: {
    label: "Best lap →",
    domain: [xDomainMin, xDomainMax],
    tickFormat: s => fmtSec(s)
  },
  y: {
    label: null,
    axis: null,
    domain: stintRows.map(r => `${r.comp_driver} #${r.comp_car_no}`)
  },
  color: {
    domain: [1, stintRows.length],
    range: ["#1b5e20","#4caf50","#ff9800","#e63946","#7f0000"],
    legend: false
  },
  marks: [
    Plot.barX(stintRows, {
      x: "best_laptime_sec",
      y: d => `${d.comp_driver} #${d.comp_car_no}`,
      fill: d => d.rank_by_best,
      inset: 2, rx: 3,
      tip: true,
      title: d => `P${d.rank_by_best} · #${d.comp_car_no} ${d.comp_driver}\nBest: ${fmtSec(d.best_laptime_sec)}\nAvg: ${fmtSec(d.avg_laptime_sec)}\nLaps: ${d.laps_in_window}`
    }),
    Plot.text(stintRows, {
      x: d => xDomainMin + (xDomainMax - xDomainMin) * 0.01,
      y: d => `${d.comp_driver} #${d.comp_car_no}`,
      text: d => `P${d.rank_by_best}`,
      textAnchor: "start", fontSize: 10, fontWeight: "bold",
      fill: d => d.rank_by_best <= 3 ? "#fff" : "#eee"
    }),
    Plot.text(stintRows, {
      x: d => d.best_laptime_sec + (xDomainMax - xDomainMin) * 0.012,
      y: d => `${d.comp_driver} #${d.comp_car_no}`,
      text: d => {
        const gap = d.best_laptime_sec - p1Sec;
        const gapStr = gap < 0.05 ? "P1" : `+${gap.toFixed(1)}s`;
        return `#${d.comp_car_no} ${d.comp_driver}  ${fmtSec(d.best_laptime_sec)}  ${gapStr}`;
      },
      textAnchor: "start", fontSize: 10, fill: "#bbb"
    }),
    Plot.ruleX(stintRows.filter(r => r.comp_car_no === refCar), {
      x: d => d.best_laptime_sec,
      stroke: "#ff9800", strokeWidth: 2, strokeDasharray: "3,2"
    })
  ]
})
```

```js
html`<div class="table-scroll">${Inputs.table(stintRows.map(r => ({
  "P": r.rank_by_best,
  "Car": `#${r.comp_car_no}`,
  "Driver": r.comp_driver,
  "Best": fmtSec(r.best_laptime_sec),
  "Avg": fmtSec(r.avg_laptime_sec),
  "Gap vs P1": r.rank_by_best === 1 ? "—" : `+${((r.best_laptime_sec ?? 0) - p1Sec).toFixed(1)}s`,
  "Laps": r.laps_in_window,
  "Window": `${r.ref_window_start.slice(11,16)}→${r.ref_window_end.slice(11,16)}`
})), {
  sort: "P",
  width: { P: 42, Car: 52, Driver: 130, Best: 80, Avg: 80, "Gap vs P1": 90, Laps: 52, Window: 120 }
})}</div>`
```

<style>
.info-box {
  background: #161e1e; border-left: 3px solid #00bcd4;
  border-radius: 6px; padding: .6rem 1rem; margin: 1rem 0;
  font-size: .85em; line-height: 1.6; opacity: .85;
}
.stint-meta {
  display: flex; gap: 1.2rem; flex-wrap: wrap;
  background: #1a1a2e; border-radius: 8px;
  padding: .65rem 1rem; margin: .8rem 0;
  font-size: .88em;
}
.stint-meta strong { color: #ff9800; }
.correction-log {
  border-left: 4px solid #f0a500; background: #1e1a0e;
  border-radius: 6px; padding: .7rem 1rem; margin: 1rem 0; font-size: .87em;
}
.correction-log strong { color: #f0a500; display: block; margin-bottom: .4rem; }
.correction-item { display: flex; flex-direction: column; gap: 2px; padding: .35rem 0; border-top: 1px solid #333; }
.correction-item .badge { font-weight: 700; color: #ff9800; font-size: .88em; }
.correction-item .meta { opacity: .5; font-size: .82em; }
</style>
