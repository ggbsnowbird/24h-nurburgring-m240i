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
html`<div class="nbr-header">
  <img src="${logoUrl}" class="nbr-logo" alt="54th ADAC Ravenol 24h Nürburgring 2026">
  <div class="nbr-header-text">
    <span class="nbr-badge">54th edition · May 14–17, 2026</span>
    <span class="nbr-title">M240i Racing Cup — Stint Analysis</span>
    <span class="nbr-subtitle">Nürburgring Nordschleife · 25,378 m</span>
  </div>
</div>`
```

```js
html`<div class="hero-stats">
  <div class="hero-stat"><span>${CARS.length}</span>Cars</div>
  <div class="hero-stat"><span>${stints.length}</span>Clean stints</div>
  <div class="hero-stat"><span>${totalLaps}</span>Valid laps</div>
  <div class="hero-stat"><span style="font-size:.55em;color:var(--theme-foreground-muted)">Outlaps &amp; laps&nbsp;&gt;11:30 excluded</span></div>
</div>`
```

---

## Pace map — best lap per stint

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
  marginRight: 16,
  style: { background: "transparent", color: "var(--theme-foreground)", fontSize: "12px", fontFamily: '"Roboto Condensed", sans-serif' },
  x: {
    label: "Race time (CEST) →",
    type: "time",
    tickFormat: d => {
      const h = (d.getUTCHours() + 2) % 24;
      return `${String(h).padStart(2,'0')}:${String(d.getUTCMinutes()).padStart(2,'0')}`;
    }
  },
  y: {
    label: "↑ Best lap",
    domain: [yMin, yMax],
    tickFormat: s => `${Math.floor(s/60)}:${String(Math.round(s%60)).padStart(2,'0')}`
  },
  marks: [
    Plot.gridY({ stroke: "var(--theme-foreground-faintest)" }),
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
    car_no: car, drivers: carDrivers[car], stints: cs.length,
    total_laps: cs.reduce((s, d) => s + d.lap_count, 0),
    best_lap: best?.best_laptime ?? "—",
    best_lap_sec: best?.best_laptime_sec,
    best_driver: best?.driver_name ?? "—"
  };
}).sort((a,b) => (a.best_lap_sec??9999) - (b.best_lap_sec??9999));

const medals = ["🥇","🥈","🥉"];
```

```js
html`<div class="grid grid-cols-3">${summary.map((c,i) =>
  html`<div class="card" style="border-top:3px solid ${CAR_COLORS[c.car_no]};border-left:none">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
      <span style="font-size:1.3em;font-weight:800;font-family:'Roboto Condensed',sans-serif;color:${CAR_COLORS[c.car_no]}">#${c.car_no}</span>
      <span style="font-size:1em;font-weight:700;font-family:'JetBrains Mono',monospace">${medals[i] ?? ""} ${c.best_lap}</span>
    </div>
    <p style="font-size:0.8em;opacity:0.55;margin:0 0 6px;line-height:1.4">${c.drivers}</p>
    <p style="margin:0 0 2px;font-size:.88em">Best: <strong style="color:${CAR_COLORS[c.car_no]}">${c.best_driver}</strong></p>
    <p style="opacity:0.4;font-size:0.78em;margin:0">${c.total_laps} valid laps · ${c.stints} stints</p>
  </div>`
)}</div>`
```
