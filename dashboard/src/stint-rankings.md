---
title: Stint Rankings
---

```js
const ranking = await FileAttachment("data/ranking.json").json();
const stints  = await FileAttachment("data/stints.json").json();
```

```js
const CAR_COLORS = {
  195: "#e63946", 650: "#2196f3", 651: "#4caf50", 652: "#ff9800",
  653: "#9c27b0", 658: "#00bcd4", 665: "#f44336", 667: "#8bc34a",
  669: "#ff5722", 670: "#3f51b5", 677: "#ffc107"
};

const CARS = [...new Set(ranking.map(d => d.ref_car_no))].sort((a,b)=>a-b);

// Driver list for reference car
function driversOf(car) {
  return [...new Set(stints.filter(s=>s.car_no===car).map(s=>s.driver_name).filter(Boolean))].sort();
}
```

# Stint Rankings

> For each stint, all M240i drivers on track **at the same time** are ranked by best lap.  
> This enables fair, condition-comparable performance comparison.

---

```js
const refCar = view(Inputs.select(CARS, {
  label: "Reference car",
  format: c => {
    const d = stints.find(s=>s.car_no===c)?.car_drivers ?? "";
    return `#${c} — ${d}`;
  },
  value: 652
}));
```

```js
const refDrivers = driversOf(refCar);
const refDriver = view(Inputs.select(["All drivers", ...refDrivers], {
  label: "Driver",
  value: "All drivers"
}));
```

```js
// Filter stints for ref car/driver
const filteredStints = stints.filter(s =>
  s.car_no === refCar &&
  (refDriver === "All drivers" || s.driver_name === refDriver) &&
  s.best_laptime_sec < 1200
);

// Filter ranking rows for those stints
const filteredRanking = ranking.filter(r =>
  r.ref_car_no === refCar &&
  (refDriver === "All drivers" || r.ref_driver === refDriver) &&
  r.best_laptime_sec < 1200
);

// Self-rows (ref driver in their own stints)
const selfRows = filteredRanking.filter(r =>
  r.comp_car_no === refCar && r.comp_driver === (refDriver === "All drivers" ? r.ref_driver : refDriver)
);
```

---

## Rank evolution across stints

```js
Plot.plot({
  title: `${refDriver === "All drivers" ? "All drivers" : refDriver} — rank by best lap per stint`,
  width: 900,
  height: 340,
  marginLeft: 50,
  style: { background: "transparent", color: "#ccc" },
  x: { label: "Stint →", tickFormat: d => `S${d}` },
  y: { label: "↓ Rank (1 = fastest)", reverse: false, domain: [1, 22] },
  marks: [
    Plot.ruleY([1], { stroke: "#f0c040", strokeDasharray: "4,4", strokeWidth: 1.5 }),
    Plot.ruleY([5], { stroke: "#4caf50", strokeDasharray: "2,4", strokeWidth: 1 }),
    Plot.line(
      refDriver === "All drivers"
        ? selfRows
        : filteredRanking.filter(r => r.comp_driver === refDriver && r.comp_car_no === refCar),
      {
        x: "ref_stint_no",
        y: "rank_by_best",
        stroke: d => CAR_COLORS[d.ref_car_no] ?? "#ff9800",
        strokeWidth: 2.5,
        curve: "monotone-x"
      }
    ),
    Plot.dot(
      refDriver === "All drivers"
        ? selfRows
        : filteredRanking.filter(r => r.comp_driver === refDriver && r.comp_car_no === refCar),
      {
        x: "ref_stint_no",
        y: "rank_by_best",
        fill: d => CAR_COLORS[d.ref_car_no] ?? "#ff9800",
        r: 5,
        tip: true,
        title: d => `Stint ${d.ref_stint_no} · ${d.ref_driver}\nRank: ${d.rank_by_best}\nBest: ${Math.floor(d.best_laptime_sec/60)}:${String(Math.round(d.best_laptime_sec%60)).padStart(2,'0')}\nLaps in window: ${d.laps_in_window}\n${d.ref_window_start.slice(11,16)} → ${d.ref_window_end.slice(11,16)} UTC`
      }
    ),
    Plot.text(
      refDriver === "All drivers"
        ? selfRows
        : filteredRanking.filter(r => r.comp_driver === refDriver && r.comp_car_no === refCar),
      {
        x: "ref_stint_no",
        y: "rank_by_best",
        text: d => `${d.rank_by_best}`,
        dy: -12,
        fontSize: 10,
        fill: "#ccc"
      }
    )
  ]
})
```

---

## Stint detail table

```js
const selectedStint = view(Inputs.select(
  filteredStints.map(s => s.stint_no),
  {
    label: "Select stint",
    format: n => {
      const s = filteredStints.find(x => x.stint_no === n);
      return `Stint ${n} — ${s?.driver_name} · Laps ${s?.lap_start}–${s?.lap_end} · ${s?.day_time_start?.slice(11,16)}→${s?.day_time_end?.slice(11,16)} UTC`;
    }
  }
));
```

```js
const stintRows = filteredRanking
  .filter(r => r.ref_stint_no === selectedStint)
  .sort((a,b) => a.rank_by_best - b.rank_by_best);

const refStint = filteredStints.find(s => s.stint_no === selectedStint);
```

<div class="stint-meta">
  ${refStint ? `
    <span>🏎 #${refStint.car_no} ${refStint.car_drivers}</span>
    <span>Driver: <strong>${refStint.driver_name}</strong></span>
    <span>Laps ${refStint.lap_start}–${refStint.lap_end} (${refStint.lap_count} laps)</span>
    <span>${refStint.day_time_start?.slice(11,16)} → ${refStint.day_time_end?.slice(11,16)} UTC</span>
  ` : ''}
</div>

```js
// Heatmap-style table
Plot.plot({
  title: `Stint ${selectedStint} — All drivers ranked by best lap`,
  width: 820,
  height: Math.max(200, stintRows.length * 32 + 60),
  marginLeft: 160,
  marginRight: 100,
  style: { background: "transparent", color: "#ccc" },
  x: { label: "Best lap (s) →", domain: [540, 1000] },
  y: { label: null, domain: stintRows.map(r => `${r.comp_driver} #${r.comp_car_no}`) },
  color: {
    domain: [1, Math.max(...stintRows.map(r=>r.rank_by_best))],
    range: ["#4caf50","#ff9800","#e63946"],
    legend: false
  },
  marks: [
    Plot.barX(stintRows, {
      x: "best_laptime_sec",
      y: d => `${d.comp_driver} #${d.comp_car_no}`,
      fill: d => d.rank_by_best,
      opacity: 0.8,
      tip: true,
      title: d => `#${d.comp_car_no} ${d.comp_driver}\nRank: ${d.rank_by_best}\nBest: ${Math.floor(d.best_laptime_sec/60)}:${String(Math.round(d.best_laptime_sec%60)).padStart(2,'0')}\nAvg: ${Math.floor(d.avg_laptime_sec/60)}:${String(Math.round(d.avg_laptime_sec%60)).padStart(2,'0')}\nLaps: ${d.laps_in_window}`
    }),
    Plot.text(stintRows, {
      x: d => d.best_laptime_sec + 4,
      y: d => `${d.comp_driver} #${d.comp_car_no}`,
      text: d => `#${d.rank_by_best}  ${Math.floor(d.best_laptime_sec/60)}:${String(Math.round(d.best_laptime_sec%60)).padStart(2,'0')}`,
      textAnchor: "start",
      fontSize: 11,
      fill: "#ddd"
    }),
    // Highlight ref car
    Plot.ruleX(
      stintRows.filter(r => r.comp_car_no === refCar),
      { x: d => d.best_laptime_sec, stroke: "#ff9800", strokeWidth: 2 }
    )
  ]
})
```

```js
// Full detail table
Inputs.table(stintRows.map(r => ({
  "Rank": r.rank_by_best,
  "Car #": r.comp_car_no,
  "Driver": r.comp_driver,
  "Best lap": `${Math.floor(r.best_laptime_sec/60)}:${String(Math.round(r.best_laptime_sec%60)).padStart(2,'0')}`,
  "Avg lap": `${Math.floor(r.avg_laptime_sec/60)}:${String(Math.round(r.avg_laptime_sec%60)).padStart(2,'0')}`,
  "Laps in window": r.laps_in_window,
  "Window": `${r.ref_window_start.slice(11,16)}→${r.ref_window_end.slice(11,16)}`
})), {
  sort: "Rank",
  width: { "Rank": 60, "Car #": 60, "Driver": 140, "Best lap": 90, "Avg lap": 90, "Laps in window": 120, "Window": 130 }
})
```

<style>
.stint-meta {
  display: flex; gap: 1.5rem; flex-wrap: wrap;
  background: #1a1a2e; border-radius: 8px;
  padding: 0.75rem 1rem; margin: 1rem 0;
  font-size: 0.9em; opacity: 0.85;
}
.stint-meta strong { color: #ff9800; }
</style>
