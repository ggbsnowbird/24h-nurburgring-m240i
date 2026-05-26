---
title: Theoretical Lap — SP9
---

```js
const sectors = await FileAttachment("../data/sp9/sectors.json").json();
const stints  = await FileAttachment("../data/sp9/stints.json").json();
```

```js
const CAR_COLORS = {
  1: "#f15959", 3: "#f16f59", 4: "#f18559", 5: "#f19a59", 7: "#f1b059",
  8: "#f1c659", 11: "#f1db59", 16: "#f1f159", 17: "#dbf159", 18: "#c6f159",
  19: "#b0f159", 24: "#9af159", 26: "#85f159", 30: "#6ff159", 32: "#59f159",
  33: "#59f16f", 34: "#59f185", 35: "#59f19a", 37: "#59f1b0", 39: "#59f1c6",
  44: "#59f1db", 45: "#59f1f1", 47: "#59dbf1", 48: "#59c6f1", 54: "#59b0f1",
  55: "#599af1", 64: "#5985f1", 65: "#596ff1", 67: "#5959f1", 69: "#6f59f1",
  71: "#8559f1", 75: "#9a59f1", 77: "#b059f1", 80: "#c659f1", 84: "#db59f1",
  86: "#f159f1", 99: "#f159db", 123: "#f159c6", 130: "#f159b0", 786: "#f1599a",
  911: "#f15985", 992: "#f1596f"
};

function fmtSec(s) {
  if (s == null || isNaN(s)) return "—";
  return `${Math.floor(s/60)}:${(s%60).toFixed(3).padStart(6,'0')}`;
}

// Hard floor — GT3 theoretical sums under 7:40 (460s) are PDF-truncated
// sector entries leaking into wrong slots, not real performance.
const THEORETICAL_FLOOR_SEC = 460;
```

<div class="page-hero">
  <h1><span class="icon">⚡</span> Theoretical best lap</h1>
  <p class="page-pitch">Sum of each SP9 / GT3 driver's fastest sector times — the lap they could have driven if all their best sectors had lined up.</p>
</div>

```js
html`<div class="landing-cards" style="margin:1rem 0 1.4rem;grid-template-columns:repeat(3,1fr)">
  <a href="./overview" style="text-decoration:none;color:inherit">
    <div class="card" style="border-top:4px solid #00bcd4;cursor:pointer;padding:1.1rem 1.4rem;transition:transform .15s,box-shadow .15s"
      onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 22px rgba(0,188,212,.22)'"
      onmouseout="this.style.transform='';this.style.boxShadow=''">
      <div style="font-size:1.1em;font-weight:800;margin-bottom:.3rem">🏎 Overview</div>
      <p style="font-size:.85em;opacity:.6;margin:0 0 .7rem;line-height:1.5">Class summary — cars, drivers, pace evolution.</p>
      <div style="font-size:.78em;color:#00bcd4;font-weight:700">Open analysis →</div>
    </div>
  </a>
  <a href="./stint-rankings" style="text-decoration:none;color:inherit">
    <div class="card" style="border-top:4px solid var(--nbr-green,#43632d);cursor:pointer;padding:1.1rem 1.4rem;transition:transform .15s,box-shadow .15s"
      onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 22px rgba(67,99,45,.25)'"
      onmouseout="this.style.transform='';this.style.boxShadow=''">
      <div style="font-size:1.1em;font-weight:800;margin-bottom:.3rem">🏁 Stint Rankings</div>
      <p style="font-size:.85em;opacity:.6;margin:0 0 .7rem;line-height:1.5">Best lap & average pace ranked against drivers in the same time window.</p>
      <div style="font-size:.78em;color:var(--nbr-green-light,#5a8438);font-weight:700">Open analysis →</div>
    </div>
  </a>
  <a href="./sector-analysis" style="text-decoration:none;color:inherit">
    <div class="card" style="border-top:4px solid var(--nbr-gold,#f0c040);cursor:pointer;padding:1.1rem 1.4rem;transition:transform .15s,box-shadow .15s"
      onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 22px rgba(240,192,64,.22)'"
      onmouseout="this.style.transform='';this.style.boxShadow=''">
      <div style="font-size:1.1em;font-weight:800;margin-bottom:.3rem">📊 Sector Analysis</div>
      <p style="font-size:.85em;opacity:.6;margin:0 0 .7rem;line-height:1.5">Per-sector deltas — where time is gained or lost on the Nordschleife.</p>
      <div style="font-size:.78em;color:var(--nbr-gold,#f0c040);font-weight:700">Open analysis →</div>
    </div>
  </a>
</div>`
```

<details class="methodology">
<summary>How is this computed?</summary>
<div class="info-box">
  For each driver, we take their <strong>fastest time in each of the 9 Nordschleife sectors</strong> across the whole race (all stints they drove, outlaps & laps &gt; 11:30 excluded). Summed, that gives the lap they <em>could</em> have driven if every best sector had landed on the same lap.<br>
  <strong>Gap = Actual best lap − Theoretical best lap.</strong> A small gap means the driver consistently stitched their sectors together; a large gap means time was left on the table.<br>
  Drivers with a theoretical sum under 7:40 are dropped — that's a known artefact of S9 truncation in the PDF source.
</div>
</details>

```js
const bestBy = d3.rollup(
  sectors,
  rows => d3.min(rows, r => r.sector_time_sec),
  r => `${r.comp_car_no}|${r.comp_driver}`,
  r => r.sector
);

const SECT = [1, 2, 3, 4, 5, 6, 7, 8, 9];

const driverRows = [...bestBy.entries()].map(([key, sectorMap]) => {
  const [carStr, driver] = key.split("|");
  const car = +carStr;
  const sectorBests = SECT.map(s => sectorMap.get(s) ?? null);
  const missing = sectorBests.filter(v => v == null).length;
  const theoretical = missing === 0 ? d3.sum(sectorBests) : null;
  const driverStints = stints.filter(s =>
    s.car_no === car && s.driver_name === driver && s.best_laptime_sec < 690
  );
  const actual = d3.min(driverStints, s => s.best_laptime_sec) ?? null;
  const gap   = (theoretical != null && actual != null) ? actual - theoretical : null;
  return { car, driver, label: `#${car} ${driver}`, sectorBests, theoretical, actual, gap };
})
.filter(d =>
  d.theoretical != null &&
  d.actual != null &&
  d.theoretical >= THEORETICAL_FLOOR_SEC &&
  d.theoretical <= d.actual   // theoretical can never be slower than actual
)
.sort((a, b) => a.theoretical - b.theoretical);
```

```js
const podium     = driverRows[0];
const mostUnreal = [...driverRows].sort((a, b) => b.gap - a.gap)[0];
const mostMaxed  = [...driverRows].sort((a, b) => a.gap - b.gap)[0];
display(html`<div class="stat-row">
  <div class="stat-card">
    <div class="label">Best theoretical</div>
    <div class="value">${fmtSec(podium?.theoretical)}</div>
    <div class="sub">${podium?.label ?? "—"}</div>
  </div>
  <div class="stat-card">
    <div class="label">Biggest hidden gap</div>
    <div class="value">+${mostUnreal?.gap?.toFixed(2) ?? "—"}s</div>
    <div class="sub">${mostUnreal?.label ?? "—"}</div>
  </div>
  <div class="stat-card">
    <div class="label">Closest to potential</div>
    <div class="value">+${mostMaxed?.gap?.toFixed(2) ?? "—"}s</div>
    <div class="sub">${mostMaxed?.label ?? "—"}</div>
  </div>
</div>`);
```

---

## Actual vs Theoretical — distance from perfection

<div class="chart-subtitle">Each dot = one driver · X-axis: theoretical best · Y-axis: actual best · Diagonal = perfect execution · Distance above the diagonal = unrealized potential</div>

```js
const xMin = d3.min(driverRows, d => d.theoretical);
const xMax = d3.max(driverRows, d => d.actual);
const pad  = (xMax - xMin) * 0.04;

Plot.plot({
  width,
  height: 420,
  marginLeft: 60,
  marginRight: 16,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: { label: "Theoretical best lap (s) →", domain: [xMin - pad, xMax + pad], tickFormat: s => fmtSec(s) },
  y: { label: "↑ Actual best lap (s)",      domain: [xMin - pad, xMax + pad], tickFormat: s => fmtSec(s) },
  marks: [
    Plot.gridY({ stroke: "#2a2a2a" }),
    Plot.gridX({ stroke: "#2a2a2a" }),
    Plot.line(
      [[xMin - pad, xMin - pad], [xMax + pad, xMax + pad]],
      { stroke: "#4caf50", strokeWidth: 1.5, strokeDasharray: "4,3" }
    ),
    Plot.dot(driverRows, {
      x: "theoretical",
      y: "actual",
      fill: d => CAR_COLORS[d.car] ?? "#888",
      r: 6,
      stroke: "#111", strokeWidth: 1,
      tip: true,
      title: d => `${d.label}\nTheoretical: ${fmtSec(d.theoretical)}\nActual:      ${fmtSec(d.actual)}\nGap:         +${d.gap.toFixed(3)}s`
    }),
    Plot.text(driverRows, {
      x: "theoretical",
      y: "actual",
      text: d => `#${d.car}`,
      dx: 8, dy: -4,
      fontSize: 9, fill: "#aaa",
      textAnchor: "start"
    })
  ]
})
```

---

## Full ranking

```js
html`<div class="table-scroll">${Inputs.table(driverRows.map(d => ({
  "Driver":      d.label,
  "Theoretical": fmtSec(d.theoretical),
  "Actual best": fmtSec(d.actual),
  "Gap":         `+${d.gap.toFixed(2)}s`,
  ...Object.fromEntries(d.sectorBests.map((v, i) => [`S${i+1}`, v != null ? v.toFixed(2) : "—"]))
})), {
  sort: "Theoretical",
  width: {
    Driver: 170, Theoretical: 96, "Actual best": 96, Gap: 78,
    ...Object.fromEntries(SECT.map(s => [`S${s}`, 60]))
  }
})}</div>`
```
