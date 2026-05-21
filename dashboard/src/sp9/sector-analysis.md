---
title: Sector Analysis — SP9
---

```js
const sectors    = await FileAttachment("../data/sp9/sectors.json").json();
const stints     = await FileAttachment("../data/sp9/stints.json").json();
const trackMapUrl = await FileAttachment("../assets/track-sectors.webp").url();
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

const CARS = [...new Set(stints.map(d => d.car_no))].sort((a,b)=>a-b);

function driversOf(car) {
  return [...new Set(stints.filter(s=>s.car_no===car).map(s=>s.driver_name).filter(Boolean))].sort();
}

function fmtSec(s) {
  if (s == null) return "—";
  return s < 60 ? `${s.toFixed(3)}s` : `${Math.floor(s/60)}:${String((s%60).toFixed(3)).padStart(6,'0')}`;
}
```

<div class="page-hero">
  <h1><span class="icon">📊</span> Where I gain or lose time</h1>
  <p class="page-pitch">Per-sector deltas across the Nordschleife — pick a stint, see exactly which sectors cost time vs the fastest peer.</p>
</div>

<details class="methodology">
<summary>How is this computed?</summary>
<div class="info-box">
  For each stint, all drivers on track in the same time window are ranked by best sector time.<br>
  <strong>Window:</strong> 4 min before ref stint start → ref stint end. Outlap excluded. Laps &gt;11:30 filtered.<br>
  Reference driver/car highlighted in orange.
</div>
</details>

---

<div class="control-bar">

```js
const refCar = view(Inputs.select(CARS, {
  label: "Reference car",
  format: c => `#${c} — ${stints.find(s=>s.car_no===c)?.car_drivers ?? ""}`,
  value: 652
}));
```

```js
const refDriver = view(Inputs.select(["All drivers", ...driversOf(refCar)], {
  label: "Driver",
  value: driversOf(652).includes("Boutonnet") ? "Boutonnet" : "All drivers"
}));
```

```js
const filteredStints = stints.filter(s =>
  s.car_no === refCar &&
  (refDriver === "All drivers" || s.driver_name === refDriver)
);
```

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
const refStint = filteredStints.find(s => s.stint_no === selectedStint);

// All sector data for this stint
const stintSectors = sectors.filter(r =>
  r.ref_car_no === refCar && r.ref_stint_no === selectedStint
);

const sectorNums = [...new Set(stintSectors.map(d => d.sector))].sort((a,b)=>a-b);
const nSectors = sectorNums.length;

// All unique drivers in this window, sorted by average rank across sectors
const driverKeys = [...new Set(stintSectors.map(d => `${d.comp_driver}||${d.comp_car_no}`))];

const driverSummary = driverKeys.map(key => {
  const [driver, carStr] = key.split('||');
  const car = +carStr;
  const rows = stintSectors.filter(r => r.comp_driver === driver && r.comp_car_no === car);
  const avgRank = rows.length ? d3.mean(rows, r => r.rank) : 99;
  const sumDelta = d3.sum(rows, r => r.delta_to_best);
  return { driver, car, label: `#${car} ${driver}`, avgRank, sumDelta, is_ref: car === refCar && (refDriver === "All drivers" || driver === refDriver) };
}).sort((a,b) => a.sumDelta - b.sumDelta);

const driverOrder = driverSummary.map(d => d.label);
const maxRank = d3.max(stintSectors, d => d.rank) ?? 10;
```

```js
html`<div class="stint-meta">
  <span>🏎 #${refStint?.car_no} ${refStint?.car_drivers}</span>
  <span>Driver on ref: <strong>${refStint?.driver_name}</strong></span>
  <span>Laps ${refStint?.lap_start}–${refStint?.lap_end}</span>
  <span>${refStint?.day_time_start?.slice(11,16)}→${refStint?.day_time_end?.slice(11,16)} CEST</span>
  <span style="opacity:.5">${driverOrder.length} drivers · ${nSectors} sectors</span>
</div>`
```

```js
// Hero stats for the ref driver across all sectors of the selected stint
const refSectorRows = stintSectors.filter(r =>
  r.comp_car_no === refCar && (refDriver === "All drivers" || r.comp_driver === refDriver)
);
const refByDelta = [...refSectorRows].sort((a,b) => a.delta_to_best - b.delta_to_best);
const bestSec  = refByDelta[0];
const worstSec = refByDelta[refByDelta.length - 1];
const avgSecRank = d3.mean(refSectorRows, r => r.rank);
display(html`<div class="stat-row">
  <div class="stat-card">
    <div class="label">Best sector</div>
    <div class="value">${bestSec ? `S${bestSec.sector}` : "—"}</div>
    <div class="sub">${bestSec ? `P${bestSec.rank}/${bestSec.n_drivers} · +${bestSec.delta_to_best.toFixed(2)}s` : ""}</div>
  </div>
  <div class="stat-card">
    <div class="label">Worst sector</div>
    <div class="value">${worstSec ? `S${worstSec.sector}` : "—"}</div>
    <div class="sub">${worstSec ? `P${worstSec.rank}/${worstSec.n_drivers} · +${worstSec.delta_to_best.toFixed(2)}s` : ""}</div>
  </div>
  <div class="stat-card">
    <div class="label">Avg sector rank</div>
    <div class="value">${avgSecRank != null ? `P${avgSecRank.toFixed(1)}` : "—"}</div>
    <div class="sub">across ${refSectorRows.length} sector${refSectorRows.length>1?"s":""}</div>
  </div>
</div>`);
```

---

## Sector heatmap

<div class="chart-subtitle">Rows = drivers, sorted by total delta to best · Columns = sectors S1–S9 · Cell = rank in that sector · Orange outline = reference</div>

```js
const heatData = stintSectors.map(r => ({
  label: `#${r.comp_car_no} ${r.comp_driver}`,
  sector: `S${r.sector}`,
  rank: r.rank,
  time: r.sector_time_sec,
  delta: r.delta_to_best,
  n: r.n_drivers,
  is_ref: r.comp_car_no === refCar && (refDriver === "All drivers" || r.comp_driver === refDriver)
}));
```

```js
Plot.plot({
  width,
  height: Math.max(160, driverOrder.length * 38 + 70),
  marginLeft: width < 640 ? 60 : 148,
  marginBottom: 36,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: {
    label: "Sector →",
    domain: sectorNums.map(s => `S${s}`)
  },
  y: {
    label: null,
    domain: driverOrder
  },
  color: {
    domain: [1, maxRank],
    range: ["#1b5e20", "#4caf50", "#cddc39", "#ff9800", "#e63946"],
    legend: true,
    label: "Rank"
  },
  marks: [
    // Grey "no data" cells for missing sectors
    Plot.cell(
      d3.cross(driverOrder, sectorNums.map(s=>`S${s}`)).map(([label, sector]) => ({label, sector}))
        .filter(({label, sector}) => !heatData.find(d => d.label===label && d.sector===sector)),
      {
        x: "sector", y: "label",
        fill: "#1a1a1a", inset: 2, rx: 4
      }
    ),
    Plot.text(
      d3.cross(driverOrder, sectorNums.map(s=>`S${s}`)).map(([label, sector]) => ({label, sector}))
        .filter(({label, sector}) => !heatData.find(d => d.label===label && d.sector===sector)),
      {
        x: "sector", y: "label",
        text: () => "n/a",
        fontSize: 9, fill: "#444"
      }
    ),
    Plot.cell(heatData, {
      x: "sector",
      y: "label",
      fill: "rank",
      inset: 2,
      rx: 4,
      tip: true,
      title: d => `${d.label}\n${d.sector}: P${d.rank}/${d.n}\nTime: ${fmtSec(d.time)}\n+${d.delta.toFixed(3)}s vs best`
    }),
    Plot.text(heatData, {
      x: "sector",
      y: "label",
      text: d => `${d.rank}`,
      fontSize: 11,
      fontWeight: d => d.is_ref ? "bold" : "normal",
      fill: d => (d.rank / maxRank) < 0.4 ? "#fff" : "#111"
    }),
    // Orange border for reference driver
    Plot.cell(heatData.filter(d => d.is_ref), {
      x: "sector",
      y: "label",
      stroke: "#ff9800",
      strokeWidth: 2.5,
      fill: "none",
      inset: 2,
      rx: 4
    })
  ]
})
```

<div class="missing-note">
  <strong>n/a</strong> = sector time not available in PDF source (some laps printed without sector breakdown, or S9 truncated at end of line). Data gap is in the original timing document, not a processing error.
</div>

---

## Ranking by sector

<div class="control-bar">

```js
const sectorSel = view(Inputs.select(
  sectorNums.map(s => `S${s}`),
  { label: "Sector", value: "S1" }
));
```

</div>

```js
const SECTOR_COLORS = {
  1: "#22c55e", 2: "#16a34a", 3: "#0d9488",
  4: "#06b6d4", 5: "#3b82f6", 6: "#8b5cf6",
  7: "#d946ef", 8: "#e11d48", 9: "#ef4444"
};
const selectedSectorNum = +sectorSel.slice(1);
const selectedColor = SECTOR_COLORS[selectedSectorNum] ?? "#888";
function fmtSectorTime(sec) {
  if (sec == null) return "—";
  return sec < 60 ? `${sec.toFixed(3)}s` : `${Math.floor(sec/60)}:${(sec%60).toFixed(3).padStart(6,'0')}`;
}
```

```js
// Track map — right next to the sector selector, dark bg to kill the checkerboard
html`<div class="sector-map-row" style="margin:10px 0 16px">

  <!-- Map card: filter:invert + hue-rotate kills the white bg and preserves colours -->
  <div style="
    background:var(--theme-background-alt);
    border-radius:10px;
    border:1.5px solid ${selectedColor}77;
    box-shadow:0 0 18px ${selectedColor}30;
    transition:border-color .25s,box-shadow .25s;
    padding:8px;
    overflow:hidden;
  ">
    <img class="sector-map-img" src="${trackMapUrl}"
      alt="Nürburgring 24h — sector map"
      style="filter:invert(1) hue-rotate(180deg)">
  </div>

  <!-- Sector pills: vertical stack on desktop, horizontal wrap on mobile -->
  <div class="sector-pills-col">
    <div style="font-size:.72em;opacity:.4;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;width:100%">Sectors</div>
    ${sectorNums.map(s => {
      const c = SECTOR_COLORS[s] ?? "#888";
      const active = s === selectedSectorNum;
      const rows = stintSectors.filter(r => r.sector === s);
      const best = rows.length ? Math.min(...rows.map(r => r.sector_time_sec)) : null;
      const p1 = rows.find(r => r.rank === 1);
      return html`<div style="
        display:flex;align-items:center;gap:7px;
        padding:3px 10px 3px 8px;
        border-radius:20px;
        border:1.5px solid ${active ? c : c+'44'};
        background:${active ? c+'1a' : 'transparent'};
        box-shadow:${active ? `0 0 7px ${c}66` : 'none'};
        transition:all .2s;
        font-family:'Roboto Condensed',sans-serif;
      ">
        <span style="font-weight:800;font-size:.82em;color:${c};min-width:18px">S${s}</span>
        <span style="font-size:.78em;opacity:.7;font-family:'JetBrains Mono',monospace">${fmtSectorTime(best)}</span>
        ${active && p1 ? html`<span style="font-size:.7em;opacity:.5;margin-left:2px">· P1 ${p1.comp_driver} #${p1.comp_car_no}</span>` : ''}
      </div>`;
    })}
  </div>

</div>`
```

```js
const sNum = +sectorSel.slice(1);
const sectorBarData = stintSectors
  .filter(r => r.sector === sNum)
  .map(r => ({
    ...r,
    label: `#${r.comp_car_no} ${r.comp_driver}`,
    is_ref: r.comp_car_no === refCar && (refDriver === "All drivers" || r.comp_driver === refDriver)
  }))
  .sort((a,b) => a.sector_time_sec - b.sector_time_sec);

const sBest  = sectorBarData[0]?.sector_time_sec ?? 1;
const sMax   = d3.max(sectorBarData, d => d.sector_time_sec) ?? sBest * 1.1;
const xPad   = (sMax - sBest) * 0.04;
```

```js
html`<h3 style="margin:1.5rem 0 .25rem">${sectorSel} ranking — Stint ${selectedStint}</h3>
<div class="chart-subtitle">${refStint?.driver_name} on track — best ${sectorSel} time per driver in window</div>${sectorBarData.length === 0 ? html`<div class="empty-state">No sector data for this selection.</div>` : ''}`
```

```js
Plot.plot({
  width,
  height: Math.max(140, sectorBarData.length * 26 + 60),
  marginLeft: 12,
  marginRight: width < 640 ? 80 : 180,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: {
    label: "Sector time →",
    domain: [sBest - xPad, sMax + xPad * 2],
    tickFormat: s => `${s.toFixed(2)}s`
  },
  y: {
    label: null,
    axis: null,
    domain: sectorBarData.map(r => r.label)
  },
  marks: [
    Plot.barX(sectorBarData, {
      x: "sector_time_sec",
      y: "label",
      fill: d => d.is_ref ? "#ff9800" : (CAR_COLORS[d.comp_car_no] ?? "#555"),
      opacity: d => d.is_ref ? 1 : 0.75,
      inset: 2,
      rx: 3,
      tip: true,
      title: d => `P${d.rank}/${d.n_drivers} · #${d.comp_car_no} ${d.comp_driver}\n${fmtSec(d.sector_time_sec)}\n+${d.delta_to_best.toFixed(3)}s vs best`
    }),
    // Best time marker
    Plot.ruleX([sBest], {
      stroke: "#4caf50",
      strokeWidth: 1.5,
      strokeDasharray: "4,3"
    }),
    // Driver name inside bar (white on dark bars, dark on orange ref bar)
    Plot.text(sectorBarData, {
      x: d => (sBest - xPad) + xPad * 0.3,
      y: "label",
      text: d => d.label,
      textAnchor: "start",
      fontSize: 10,
      fontWeight: d => d.is_ref ? "bold" : "normal",
      fill: d => d.is_ref ? "#000" : "#ddd"
    }),
    // Labels outside bar: rank + time + delta
    Plot.text(sectorBarData, {
      x: d => d.sector_time_sec + xPad * 0.5,
      y: "label",
      text: d => `P${d.rank}  ${fmtSec(d.sector_time_sec)}  +${d.delta_to_best.toFixed(3)}s`,
      textAnchor: "start",
      fontSize: 10,
      fill: "#bbb"
    })
  ]
})
```

---

## Delta to best — all sectors at once

> Each line = one driver. Orange = reference. Shows where time is lost/gained across all sectors.

```js
const deltaData = stintSectors.map(r => ({
  label: `#${r.comp_car_no} ${r.comp_driver}`,
  sector: `S${r.sector}`,
  delta: r.delta_to_best,
  is_ref: r.comp_car_no === refCar && (refDriver === "All drivers" || r.comp_driver === refDriver),
  car: r.comp_car_no
}));

const refDeltaData = deltaData.filter(d => d.is_ref);
const maxDelta = d3.quantile(
  deltaData.map(d => d.delta).sort(d3.ascending), 0.85
) ?? 10;
```

```js
html`<h3 style="margin:1.5rem 0 .25rem">Delta to best per sector</h3>
<div class="chart-subtitle">Reference driver (orange) vs other drivers in the window — gap to fastest sector time</div>`
```

```js
Plot.plot({
  width,
  height: 280,
  marginLeft: 48,
  marginRight: 16,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: {
    label: "Sector →",
    domain: sectorNums.map(s => `S${s}`)
  },
  y: {
    label: "← Delta to best (s)",
    domain: [0, maxDelta * 1.1],
    tickFormat: s => `+${s.toFixed(1)}s`
  },
  marks: [
    Plot.gridY({ stroke: "#2a2a2a" }),
    Plot.ruleY([0], { stroke: "#4caf50", strokeWidth: 1.5 }),
    // All other drivers (thin, muted)
    Plot.line(deltaData.filter(d => !d.is_ref), {
      x: "sector",
      y: "delta",
      z: "label",
      stroke: d => CAR_COLORS[d.car] ?? "#555",
      strokeWidth: 1,
      opacity: 0.3,
      curve: "linear"
    }),
    // Reference driver (bold orange)
    Plot.line(refDeltaData, {
      x: "sector",
      y: "delta",
      stroke: "#ff9800",
      strokeWidth: 3,
      curve: "linear"
    }),
    Plot.dot(refDeltaData, {
      x: "sector",
      y: "delta",
      fill: "#ff9800",
      r: 5,
      tip: true,
      title: d => `${d.label}\n${d.sector}: +${d.delta.toFixed(3)}s vs best`
    }),
    // Labels on ref dots
    Plot.text(refDeltaData, {
      x: "sector",
      y: "delta",
      text: d => `+${d.delta.toFixed(2)}`,
      dy: -12,
      fontSize: 9,
      fill: "#ff9800"
    })
  ]
})
```

---

## Full sector table

```js
// Pivot: one row per driver, one col per sector
const tableRows = driverSummary.map(d => {
  const row = {
    "Driver": d.label,
    "Avg rank": d.avgRank.toFixed(1),
    "Σ delta": `+${d.sumDelta.toFixed(2)}s`
  };
  for (const s of sectorNums) {
    const e = stintSectors.find(r =>
      r.comp_driver === d.driver && r.comp_car_no === d.car && r.sector === s
    );
    row[`S${s}`] = e ? `P${e.rank} (${e.sector_time_sec.toFixed(2)}s)` : "n/a";
  }
  return row;
});
```

```js
Inputs.table(tableRows, {
  sort: "Avg rank",
  width: Object.fromEntries([
    ["Driver", 140], ["Avg rank", 72], ["Σ delta", 72],
    ...sectorNums.map(s => [`S${s}`, 110])
  ])
})
```

<style>
.missing-note {
  font-size: .8em; opacity: .55; margin: .5rem 0 1rem;
  padding: .3rem .8rem;
  border-left: 2px solid #444;
}
.info-box {
  background: #161e1e; border-left: 3px solid #00bcd4;
  border-radius: 6px; padding: .6rem 1rem; margin: 1rem 0;
  font-size: .85em; line-height: 1.7; opacity: .9;
}
.stint-meta {
  display: flex; gap: 1.2rem; flex-wrap: wrap;
  background: #1a1a2e; border-radius: 8px;
  padding: .65rem 1rem; margin: .8rem 0;
  font-size: .88em;
}
.stint-meta strong { color: #ff9800; }
</style>
