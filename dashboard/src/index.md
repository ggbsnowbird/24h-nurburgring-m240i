---
title: Overview
---

```js
const stints = await FileAttachment("data/stints.json").json();
const ranking = await FileAttachment("data/ranking.json").json();
```

```js
// Car color palette
const CAR_COLORS = {
  195: "#e63946", 650: "#2196f3", 651: "#4caf50", 652: "#ff9800",
  653: "#9c27b0", 658: "#00bcd4", 665: "#f44336", 667: "#8bc34a",
  669: "#ff5722", 670: "#3f51b5", 677: "#ffc107"
};

const CARS = [...new Set(stints.map(d => d.car_no))].sort((a,b) => a-b);
const carDrivers = Object.fromEntries(stints.map(d => [d.car_no, d.car_drivers]));
```

<div class="hero">
  <h1>54th ADAC Ravenol 24h Nürburgring</h1>
  <h2>BMW M240i Racing Cup — Driver Stint Analysis</h2>
  <p>May 14–17, 2026 · Nürburgring Nordschleife (25,378 m) · ${CARS.length} cars · ${stints.length} stints analysed</p>
</div>

---

## Pace Overview — Best lap per stint

```js
// Build dataset: one row per stint
const stintData = stints.map(d => ({
  ...d,
  label: `#${d.car_no} ${d.driver_name}`,
  color: CAR_COLORS[d.car_no] ?? "#888",
  time_str: d.best_laptime,
  day_time_start_ms: new Date(d.day_time_start + "Z").getTime()
})).filter(d => d.best_laptime_sec > 400);
```

```js
Plot.plot({
  title: "Best lap time per stint (all M240i cars)",
  width: 960,
  height: 420,
  marginLeft: 60,
  marginRight: 20,
  style: { background: "transparent", color: "#ccc" },
  x: {
    label: "Race time (UTC) →",
    type: "time",
    tickFormat: d => `${d.getUTCHours().toString().padStart(2,'0')}:${d.getUTCMinutes().toString().padStart(2,'0')}`
  },
  y: {
    label: "↑ Best lap (s)",
    domain: [540, 900],
    tickFormat: s => `${Math.floor(s/60)}:${String(Math.round(s%60)).padStart(2,'0')}`
  },
  marks: [
    Plot.ruleY([570, 600, 630, 660], { stroke: "#333", strokeDasharray: "4,4" }),
    Plot.dot(stintData, {
      x: d => new Date(d.day_time_start + "Z"),
      y: "best_laptime_sec",
      fill: d => CAR_COLORS[d.car_no] ?? "#888",
      r: d => Math.sqrt(d.lap_count) * 2.5,
      opacity: 0.85,
      tip: true,
      title: d => `#${d.car_no} ${d.driver_name}\nBest: ${d.best_laptime}\nAvg: ${Math.floor(d.avg_laptime_sec/60)}:${String(Math.round(d.avg_laptime_sec%60)).padStart(2,'0')}\nLaps: ${d.lap_count}\n${d.day_time_start.slice(11,16)} UTC`
    }),
  ]
})
```

---

## Cars & Crews

```js
const summary = CARS.map(car => {
  const carStints = stints.filter(s => s.car_no === car);
  const drivers = [...new Set(carStints.map(s => s.driver_name).filter(Boolean))];
  const bestLap = carStints.reduce((best, s) =>
    (!best || s.best_laptime_sec < best.best_laptime_sec) ? s : best, null);
  return {
    car_no: car,
    drivers: carDrivers[car],
    stints: carStints.length,
    total_laps: carStints.reduce((s, d) => s + d.lap_count, 0),
    best_lap: bestLap?.best_laptime ?? "—",
    best_lap_sec: bestLap?.best_laptime_sec,
    best_driver: bestLap?.driver_name ?? "—"
  };
}).sort((a,b) => (a.best_lap_sec??9999) - (b.best_lap_sec??9999));
```

<div class="grid grid-cols-3">
${summary.map(c => `
  <div class="card" style="border-left: 4px solid ${CAR_COLORS[c.car_no]}">
    <h3>#${c.car_no}</h3>
    <p style="font-size:0.85em;opacity:0.7">${c.drivers}</p>
    <p>Best: <strong>${c.best_lap}</strong> (${c.best_driver})</p>
    <p style="opacity:0.6">${c.total_laps} laps · ${c.stints} stints</p>
  </div>
`).join('')}
</div>

<style>
.hero { padding: 2rem 0 1rem; }
.hero h1 { font-size: 2em; font-weight: 800; margin: 0; }
.hero h2 { font-size: 1.2em; opacity: 0.7; margin: 0.3em 0 0.5em; font-weight: 400; }
.hero p  { opacity: 0.5; font-size: 0.9em; }
</style>
