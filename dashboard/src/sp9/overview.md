---
title: Overview — SP9 GT3
---

```js
const stints   = await FileAttachment("../data/sp9/stints.json").json();
const allLaps  = await FileAttachment("../data/sp9/all_laps.json").json();
const logoUrl  = await FileAttachment("../assets/logo-main.png").url();
```

```js
const CAR_COLORS = {
  1: "#f15959",
  3: "#f16f59",
  4: "#f18559",
  5: "#f19a59",
  7: "#f1b059",
  8: "#f1c659",
  11: "#f1db59",
  16: "#f1f159",
  17: "#dbf159",
  18: "#c6f159",
  19: "#b0f159",
  24: "#9af159",
  26: "#85f159",
  30: "#6ff159",
  32: "#59f159",
  33: "#59f16f",
  34: "#59f185",
  35: "#59f19a",
  37: "#59f1b0",
  39: "#59f1c6",
  44: "#59f1db",
  45: "#59f1f1",
  47: "#59dbf1",
  48: "#59c6f1",
  54: "#59b0f1",
  55: "#599af1",
  64: "#5985f1",
  65: "#596ff1",
  67: "#5959f1",
  69: "#6f59f1",
  71: "#8559f1",
  75: "#9a59f1",
  77: "#b059f1",
  80: "#c659f1",
  84: "#db59f1",
  86: "#f159f1",
  99: "#f159db",
  123: "#f159c6",
  130: "#f159b0",
  786: "#f1599a",
  911: "#f15985",
  992: "#f1596f",
};
const CARS = [...new Set(stints.map(d => d.car_no))].sort((a,b) => a-b);
const carDrivers = Object.fromEntries(stints.map(d => [d.car_no, d.car_drivers]));
const totalLaps = stints.reduce((s,d) => s + d.lap_count, 0);
```

```js
html`<div class="hero">
  <img src="${logoUrl}" style="height:64px;width:auto;margin-bottom:12px;display:block" alt="54th ADAC Ravenol 24h Nürburgring — SP9 GT3 2026">
  <h1>54th ADAC Ravenol 24h Nürburgring — SP9 GT3</h1>
  <h2>SP9 GT3 — May 14–17, 2026</h2>
  <div class="hero-stats">
    <div class="hero-stat"><span>${CARS.length}</span>cars</div>
    <div class="hero-stat"><span>${stints.length}</span>clean stints</div>
    <div class="hero-stat"><span>${totalLaps}</span>valid laps</div>
    <div class="hero-stat"><span style="font-size:.75em">outlaps &amp; laps&nbsp;&gt;11:30 excluded</span></div>
  </div>
</div>`
```

```js
html`<div class="landing-cards" style="margin:1.5rem 0;grid-template-columns:repeat(3,1fr)">

  <a href="./stint-rankings" style="text-decoration:none;color:inherit">
    <div class="card" style="
      border-top:4px solid var(--nbr-green,#43632d);
      cursor:pointer;padding:1.3rem;
      transition:transform .15s,box-shadow .15s;
    " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 24px rgba(67,99,45,.25)'"
       onmouseout="this.style.transform='';this.style.boxShadow=''">
      <div style="font-size:1.25em;font-weight:800;margin-bottom:.4rem">🏁 Stint Rankings</div>
      <p style="font-size:.88em;opacity:.65;margin:0 0 .7rem;line-height:1.5">
        How each driver ranks vs the field — best lap & average pace
        in the same time window.
      </p>
      <div style="font-size:.8em;color:var(--nbr-green-light,#5a8438);font-weight:700">Open analysis →</div>
    </div>
  </a>

  <a href="./sector-analysis" style="text-decoration:none;color:inherit">
    <div class="card" style="
      border-top:4px solid var(--nbr-gold,#f0c040);
      cursor:pointer;padding:1.3rem;
      transition:transform .15s,box-shadow .15s;
    " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 24px rgba(240,192,64,.22)'"
       onmouseout="this.style.transform='';this.style.boxShadow=''">
      <div style="font-size:1.25em;font-weight:800;margin-bottom:.4rem">📊 Sector Analysis</div>
      <p style="font-size:.88em;opacity:.65;margin:0 0 .7rem;line-height:1.5">
        Per-sector deltas — pick a stint, see exactly which sectors
        cost time vs the fastest peer.
      </p>
      <div style="font-size:.8em;color:var(--nbr-gold,#f0c040);font-weight:700">Open analysis →</div>
    </div>
  </a>

  <a href="./theoretical-lap" style="text-decoration:none;color:inherit">
    <div class="card" style="
      border-top:4px solid #9c27b0;
      cursor:pointer;padding:1.3rem;
      transition:transform .15s,box-shadow .15s;
    " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 24px rgba(156,39,176,.25)'"
       onmouseout="this.style.transform='';this.style.boxShadow=''">
      <div style="font-size:1.25em;font-weight:800;margin-bottom:.4rem">⚡ Theoretical Lap</div>
      <p style="font-size:.88em;opacity:.65;margin:0 0 .7rem;line-height:1.5">
        Sum of each driver's best sectors — the lap they could have
        driven if everything had lined up.
      </p>
      <div style="font-size:.8em;color:#c879d6;font-weight:700">Open analysis →</div>
    </div>
  </a>

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
