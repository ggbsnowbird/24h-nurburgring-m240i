---
title: Theoretical Lap
---

```js
const sectors = await FileAttachment("../data/m240i/sectors.json").json();
const stints  = await FileAttachment("../data/m240i/stints.json").json();
```

```js
const CAR_COLORS = {
  195: "#e63946", 650: "#2196f3", 651: "#4caf50", 652: "#ff9800",
  653: "#9c27b0", 658: "#00bcd4", 665: "#f44336", 667: "#8bc34a",
  669: "#ff5722", 670: "#3f51b5", 677: "#ffc107"
};

function fmtSec(s) {
  if (s == null || isNaN(s)) return "—";
  return `${Math.floor(s/60)}:${(s%60).toFixed(3).padStart(6,'0')}`;
}

// Hard floor — M240i theoretical sums below 9:20 (560s) are PDF-truncated
// sector entries leaking into the wrong slots, not real performance.
const THEORETICAL_FLOOR_SEC = 560;
```

<div class="page-hero">
  <h1><span class="icon">⚡</span> Theoretical best lap</h1>
  <p class="page-pitch">Sum of each driver's fastest sector times — the lap they could have driven if all their best sectors had landed on the same flying lap.</p>
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
  For each driver, we take their <strong>fastest time in each of the 9 Nordschleife sectors</strong> across the selected track-condition data (outlaps & laps &gt; 11:30 excluded). Summed, that gives the lap they <em>could</em> have driven if every best sector had landed on the same lap.<br>
  <strong>Gap = Actual best lap − Theoretical best lap.</strong> Small gap → consistent execution. Large gap → time left on the table.<br>
  <strong>Piste green</strong> and <strong>Piste optimum</strong> classify each stint by track condition (early vs rubbered-in).<br>
  Drivers with a theoretical sum under 9:20 are dropped — that's a known artefact of S9 truncation in the PDF source.
</div>
</details>

<div class="control-bar">

```js
const trackCondition = view(Inputs.radio(["Piste optimum", "Piste green"], {
  label: "Track conditions",
  value: "Piste optimum"
}));
```

</div>

```js
// Green windows = Boutonnet's stint time ranges
const greenWindows = stints
  .filter(s => s.driver_name === "Boutonnet")
  .map(s => ({
    start: new Date(s.day_time_start).getTime(),
    end:   new Date(s.day_time_end).getTime()
  }));

function isGreenTime(ts) {
  const t = new Date(ts).getTime();
  return greenWindows.some(w => t >= w.start && t <= w.end);
}

// Filter sectors by track condition:
//  · green   → ref stint was driven by Boutonnet (whole window is green)
//  · optimum → ref stint was NOT driven by Boutonnet
const filteredSectors = trackCondition === "Piste green"
  ? sectors.filter(r => r.ref_driver === "Boutonnet")
  : sectors.filter(r => r.ref_driver !== "Boutonnet");

// Filter stints by track condition:
//  · green   → stint overlaps a Boutonnet window (or is one of his stints)
//  · optimum → stint does not overlap
const filteredStints = stints.filter(s => {
  const inGreen = isGreenTime(s.day_time_start) || isGreenTime(s.day_time_end);
  return trackCondition === "Piste green" ? inGreen : !inGreen;
});
```

```js
const SECT = [1, 2, 3, 4, 5, 6, 7, 8, 9];

const bestBy = d3.rollup(
  filteredSectors,
  rows => d3.min(rows, r => r.sector_time_sec),
  r => `${r.comp_car_no}|${r.comp_driver}`,
  r => r.sector
);

const driverRows = [...bestBy.entries()].map(([key, sectorMap]) => {
  const [carStr, driver] = key.split("|");
  const car = +carStr;
  const sectorBests = SECT.map(s => sectorMap.get(s) ?? null);
  const missing = sectorBests.filter(v => v == null).length;
  const theoretical = missing === 0 ? d3.sum(sectorBests) : null;
  const driverStints = filteredStints.filter(s =>
    s.car_no === car && s.driver_name === driver && s.best_laptime_sec < 690
  );
  const actual = d3.min(driverStints, s => s.best_laptime_sec) ?? null;
  const gap   = (theoretical != null && actual != null) ? actual - theoretical : null;
  return { car, driver, label: `#${car} ${driver}`, sectorBests, theoretical, actual, gap };
})
// Data-quality filter — drop bogus sums (truncated PDF sectors → unrealistic totals)
.filter(d =>
  d.theoretical != null &&
  d.actual != null &&
  d.theoretical >= THEORETICAL_FLOOR_SEC &&
  d.theoretical <= d.actual   // theoretical can never be slower than actual
)
.sort((a, b) => a.theoretical - b.theoretical);
```

```js
display(html`<div style="font-size:.85em;opacity:.55;margin:.4rem 0 1rem">
  ${driverRows.length} valid driver${driverRows.length>1?"s":""} · ${trackCondition.toLowerCase()}
</div>`);
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
  height: 380,
  marginLeft: 60,
  marginRight: 16,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: {
    label: "Theoretical best lap (s) →",
    domain: [xMin - pad, xMax + pad],
    tickFormat: s => fmtSec(s)
  },
  y: {
    label: "↑ Actual best lap (s)",
    domain: [xMin - pad, xMax + pad],
    tickFormat: s => fmtSec(s)
  },
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
      fill: d => CAR_COLORS[d.car] ?? "#ff9800",
      r: 6,
      stroke: "#111", strokeWidth: 1,
      tip: true,
      title: d => `${d.label}\nTheoretical: ${fmtSec(d.theoretical)}\nActual:      ${fmtSec(d.actual)}\nGap:         +${d.gap.toFixed(3)}s`
    }),
    Plot.text(driverRows, {
      x: "theoretical",
      y: "actual",
      text: d => `#${d.car} ${d.driver}`,
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
    Driver: 150, Theoretical: 96, "Actual best": 96, Gap: 78,
    ...Object.fromEntries(SECT.map(s => [`S${s}`, 60]))
  }
})}</div>`
```
