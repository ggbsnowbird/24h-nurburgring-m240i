---
title: Overview
---

```js
const stints = await FileAttachment("data/stints.json").json();
const logoUrl = await FileAttachment("assets/logo-main.png").url();
```

```js
const CAR_COLORS = {
  195: "#e63946", 650: "#2196f3", 651: "#4caf50", 652: "#ff9800",
  653: "#9c27b0", 658: "#00bcd4", 665: "#f44336", 667: "#8bc34a",
  669: "#ff5722", 670: "#3f51b5", 677: "#ffc107"
};
const CARS = [...new Set(stints.map(d => d.car_no))].sort((a,b) => a-b);
const carDrivers = Object.fromEntries(stints.map(d => [d.car_no, d.car_drivers]));
const totalLaps = stints.reduce((s,d) => s + d.lap_count, 0);
```

```js
html`<div class="hero">
  <img src="${logoUrl}" style="height:64px;width:auto;margin-bottom:12px;display:block" alt="54th ADAC Ravenol 24h Nürburgring 2026">
  <h1>54th ADAC Ravenol 24h Nürburgring</h1>
  <h2>BMW M240i Racing Cup · May 14–17, 2026</h2>
  <div class="hero-stats">
    <div class="hero-stat"><span>${CARS.length}</span>cars</div>
    <div class="hero-stat"><span>${stints.length}</span>clean stints</div>
    <div class="hero-stat"><span>${totalLaps}</span>valid laps</div>
    <div class="hero-stat"><span style="font-size:.75em">outlaps &amp; laps&nbsp;&gt;11:30 excluded</span></div>
  </div>
</div>`
```

---

## Pace map — best lap per stint over race time

```js
const stintData = stints.map(d => ({
  ...d,
  day_start: new Date(d.day_time_start.replace(' ','T') + 'Z')
})).filter(d => d.best_laptime_sec > 400 && d.best_laptime_sec < 690);

const yMin = Math.floor(d3.min(stintData, d => d.best_laptime_sec) / 10) * 10;
const yMax = Math.ceil(d3.max(stintData, d => d.best_laptime_sec) / 10) * 10;
```

```js
Plot.plot({
  width,
  height: 400,
  marginLeft: 68,
  marginRight: 12,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: {
    label: "Race time (CEST) →",
    type: "time",
    tickFormat: d => {
      const h = d.getUTCHours() + 2;
      return `${(h%24).toString().padStart(2,'0')}:${d.getUTCMinutes().toString().padStart(2,'0')}`;
    }
  },
  y: {
    label: "↑ Best lap",
    domain: [yMin, yMax],
    tickFormat: s => `${Math.floor(s/60)}:${String(Math.round(s%60)).padStart(2,'0')}`
  },
  marks: [
    Plot.gridY({ stroke: "#2a2a2a" }),
    Plot.dot(stintData, {
      x: "day_start",
      y: "best_laptime_sec",
      fill: d => CAR_COLORS[d.car_no] ?? "#888",
      r: d => Math.max(3, Math.sqrt(d.lap_count) * 2.2),
      opacity: 0.85,
      tip: true,
      title: d => `#${d.car_no} ${d.driver_name}\nBest: ${d.best_laptime}\nAvg: ${Math.floor(d.avg_laptime_sec/60)}:${String(Math.round(d.avg_laptime_sec%60)).padStart(2,'0')}\nLaps: ${d.lap_count}\n${d.day_time_start.slice(11,16)} UTC`
    })
  ]
})
```

---

## Cars & crews

```js
const summary = CARS.map(car => {
  const cs = stints.filter(s => s.car_no === car);
  const best = cs.reduce((b, s) => (!b || s.best_laptime_sec < b.best_laptime_sec) ? s : b, null);
  return {
    car_no: car,
    drivers: carDrivers[car],
    stints: cs.length,
    total_laps: cs.reduce((s, d) => s + d.lap_count, 0),
    best_lap: best?.best_laptime ?? "—",
    best_lap_sec: best?.best_laptime_sec,
    best_driver: best?.driver_name ?? "—"
  };
}).sort((a,b) => (a.best_lap_sec??9999) - (b.best_lap_sec??9999));
```

```js
html`<div class="grid grid-cols-3">${summary.map((c,i) =>
  html`<div class="card" style="border-left:4px solid ${CAR_COLORS[c.car_no]}">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h3 style="margin:0">#${c.car_no}</h3>
      <span style="font-size:1.1em;font-weight:700;color:${CAR_COLORS[c.car_no]}">${i===0?'🥇':i===1?'🥈':i===2?'🥉':''} ${c.best_lap}</span>
    </div>
    <p style="font-size:0.82em;opacity:0.6;margin:4px 0">${c.drivers}</p>
    <p style="margin:4px 0">Best by: <strong>${c.best_driver}</strong></p>
    <p style="opacity:0.5;font-size:0.82em;margin:0">${c.total_laps} valid laps · ${c.stints} stints</p>
  </div>`
)}</div>`
```

<style>
.hero { padding: 1.5rem 0 1rem; }
.hero h1 { font-size: 1.9em; font-weight: 800; margin: 0 0 4px; }
.hero h2 { font-size: 1.05em; opacity: 0.55; margin: 0 0 1rem; font-weight: 400; }
.hero-stats { display: flex; gap: 2rem; flex-wrap: wrap; }
.hero-stat span { display: block; font-size: 2em; font-weight: 800; line-height: 1; }
.hero-stat { font-size: 0.8em; opacity: 0.6; text-transform: uppercase; letter-spacing: 1px; }
</style>
