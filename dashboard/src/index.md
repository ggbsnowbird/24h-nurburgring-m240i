---
title: Overview
---

```js
const stints   = await FileAttachment("data/stints.json").json();
const allLaps  = await FileAttachment("data/all_laps.json").json();
const logoUrl  = await FileAttachment("assets/logo-main.png").url();
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

## Pace evolution

<div class="chart-subtitle">Each valid lap (outlap & laps &gt;11:30 excluded) plotted on real race time · P5 rolling min, rolling avg and ±1σ band computed over a trailing window</div>

```js
// Timestamps are already CEST — parse as-is (ISO local, no Z suffix)
const lapsWithDate = allLaps
  .map(d => ({ ...d, t: new Date(d.day_time) }))
  .sort((a,b) => a.t - b.t);

// All unique drivers sorted by car number then name
const allDrivers = [...new Map(
  allLaps
    .filter(d => d.driver != null)
    .map(d => [`${d.car_no}||${d.driver}`, { driver: d.driver, car_no: d.car_no, label: `#${d.car_no} ${d.driver}` }])
).values()].sort((a,b) => a.car_no - b.car_no || (a.driver ?? "").localeCompare(b.driver ?? ""));
```

<div class="control-bar">

```js
const selectedDrivers = view(Inputs.select(allDrivers, {
  multiple: true,
  value: allDrivers,
  format: d => d.label,
  label: "Filter drivers",
  size: 8
}));
```

```js
const windowMin = view(Inputs.range([15, 60], {
  step: 15,
  value: 30,
  label: "Rolling window (min)"
}));
```

</div>

```js
// Select all / Clear buttons
html`<div style="display:flex;gap:8px;margin:-.5rem 0 .5rem">
  <button onclick=${() => {
    const sel = document.querySelector('select[name="selectedDrivers"], select');
    if (sel) { [...sel.options].forEach(o => o.selected = true); sel.dispatchEvent(new Event('input')); }
  }} style="font-size:11px;padding:2px 10px;cursor:pointer;background:#1e1e1e;color:#ccc;border:1px solid #444;border-radius:4px">Select all</button>
  <button onclick=${() => {
    const sel = document.querySelector('select[name="selectedDrivers"], select');
    if (sel) { [...sel.options].forEach(o => o.selected = false); sel.dispatchEvent(new Event('input')); }
  }} style="font-size:11px;padding:2px 10px;cursor:pointer;background:#1e1e1e;color:#ccc;border:1px solid #444;border-radius:4px">Clear</button>
  <span style="font-size:11px;opacity:.45;align-self:center">${selectedDrivers.length} / ${allDrivers.length} drivers shown · Cmd/Ctrl+click to multi-select</span>
</div>`
```

```js
// Filtered laps for scatter only — rolling stats always use whole field
const filteredLaps = lapsWithDate.filter(d =>
  selectedDrivers.some(s => s.driver === d.driver && s.car_no === d.car_no)
);

// Trailing window: only laps completed in the last N minutes (no future data)
const windowMs = windowMin * 60 * 1000;

// P5 helper: 5th percentile of a sorted array
function p5(sorted) {
  return sorted[Math.max(0, Math.floor(sorted.length * 0.05))];
}

// Downsample step: finer at smaller windows
const step = Math.min(windowMin, 15) * 60 * 1000;
const tMin = lapsWithDate[0].t.getTime();
const tMax = lapsWithDate[lapsWithDate.length-1].t.getTime();

const rollingLine = [];
for (let t = tMin; t <= tMax; t += step) {
  // TRAILING: only laps with end time in [t - windowMs, t]
  const inWindow = lapsWithDate.filter(l =>
    l.t.getTime() >= t - windowMs && l.t.getTime() <= t
  );
  if (inWindow.length === 0) continue;
  const times = inWindow.map(l => l.lap_sec);
  const sorted = [...times].sort((a,b) => a - b);
  const min5 = p5(sorted);
  const avg = times.reduce((s,x) => s+x, 0) / times.length;
  const sigma = Math.sqrt(times.reduce((s,x) => s + (x-avg)**2, 0) / times.length);
  rollingLine.push({
    t: new Date(t),
    min: min5,
    avg,
    sigma,
    lo: avg - sigma,
    hi: avg + sigma,
    n: times.length
  });
}

const yMin = Math.floor(d3.min(lapsWithDate, d => d.lap_sec) / 10) * 10;
const yMax = 700; // 11:40 cap

function fmtSec(s) {
  return `${Math.floor(s/60)}:${String(Math.round(s%60)).padStart(2,'0')}`;
}
function fmtTime(d) {
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}
```

```js
Plot.plot({
  width,
  height: 460,
  marginLeft: 68,
  marginRight: 16,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: {
    label: "Race time (CEST) →",
    type: "time",
    tickFormat: fmtTime
  },
  y: {
    label: "↑ Lap time",
    domain: [yMin, yMax],
    tickFormat: fmtSec
  },
  marks: [
    // Night band 22:00 → 06:00 CEST (timestamps now local CEST)
    Plot.rectX([1], {
      x1: new Date("2026-05-16T22:00:00"),
      x2: new Date("2026-05-17T06:00:00"),
      fill: "#ffffff", fillOpacity: 0.03
    }),

    Plot.gridY({ stroke: "#1e1e1e" }),

    // ±1σ band (field spread)
    Plot.areaY(rollingLine, {
      x: "t",
      y1: "lo",
      y2: "hi",
      fill: "#ffffff",
      fillOpacity: 0.06,
      curve: "monotone-x"
    }),

    // Individual laps — filtered by driver selection
    Plot.dot(filteredLaps, {
      x: "t",
      y: "lap_sec",
      fill: d => CAR_COLORS[d.car_no] ?? "#666",
      r: 2.5,
      opacity: 0.55,
      tip: true,
      title: d => `#${d.car_no} ${d.driver}\nLap ${d.lap_no}: ${d.lap_time}\n${fmtTime(d.t)} CEST`
    }),

    // Rolling average line
    Plot.line(rollingLine, {
      x: "t",
      y: "avg",
      stroke: "#90caf9",
      strokeWidth: 2,
      curve: "monotone-x",
      opacity: 0.9
    }),

    // Rolling minimum line
    Plot.line(rollingLine, {
      x: "t",
      y: "min",
      stroke: "#4caf50",
      strokeWidth: 2.5,
      curve: "monotone-x",
      opacity: 0.95
    }),

    // Legend annotations (right side of chart)
    Plot.text([
      { t: new Date(tMax), y: rollingLine[rollingLine.length-1]?.min, label: `P5 min (${windowMin}m)` },
      { t: new Date(tMax), y: rollingLine[rollingLine.length-1]?.avg, label: `Avg (${windowMin}m)` },
    ], {
      x: "t", y: "y",
      text: "label",
      textAnchor: "end",
      dx: -6,
      fontSize: 10,
      fill: d => d.label.includes("P5") ? "#4caf50" : "#90caf9"
    })
  ]
})
```

```js
html`<div style="display:flex;gap:1.5rem;font-size:.82em;opacity:.7;margin-top:.5rem;flex-wrap:wrap">
  <span><span style="display:inline-block;width:20px;height:3px;background:#4caf50;vertical-align:middle;margin-right:4px;border-radius:2px"></span>P5 rolling min — trailing ${windowMin}min (no future data)</span>
  <span><span style="display:inline-block;width:20px;height:3px;background:#90caf9;vertical-align:middle;margin-right:4px;border-radius:2px"></span>Rolling avg — trailing ${windowMin}min</span>
  <span><span style="display:inline-block;width:20px;height:8px;background:rgba(255,255,255,.1);vertical-align:middle;margin-right:4px;border-radius:2px"></span>±1σ spread</span>
  <span><span style="display:inline-block;width:8px;height:8px;background:#888;border-radius:50%;vertical-align:middle;margin-right:4px"></span>Individual lap (colour = car)</span>
  <span style="opacity:.5">Night zone shaded · Outlaps excluded</span>
</div>`
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
