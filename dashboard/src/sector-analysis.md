---
title: Sector Analysis
---

```js
const sectors = await FileAttachment("data/sectors.json").json();
const stints  = await FileAttachment("data/stints.json").json();
```

```js
const CAR_COLORS = {
  195: "#e63946", 650: "#2196f3", 651: "#4caf50", 652: "#ff9800",
  653: "#9c27b0", 658: "#00bcd4", 665: "#f44336", 667: "#8bc34a",
  669: "#ff5722", 670: "#3f51b5", 677: "#ffc107"
};
const CARS = [...new Set(sectors.map(d => d.ref_car_no))].sort((a,b)=>a-b);
function driversOf(car) {
  return [...new Set(stints.filter(s=>s.car_no===car).map(s=>s.driver_name).filter(Boolean))].sort();
}
```

# Sector Analysis

<div class="info-box">
  Best sector time per driver per stint window — outlap excluded, laps &gt;11:30 filtered.<br>
  Heatmap: <span style="color:#4caf50">■</span> fastest · <span style="color:#e63946">■</span> slowest. Reference driver outlined in orange.
</div>

---

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
  (refDriver === "All drivers" || s.driver_name === refDriver) &&
  s.best_laptime_sec < 690
);
```

```js
const selectedStint = view(Inputs.select(
  filteredStints.map(s => s.stint_no),
  {
    label: "Stint",
    format: n => {
      const s = filteredStints.find(x => x.stint_no === n);
      return `Stint ${n} · ${s?.driver_name} · ${s?.day_time_start?.slice(11,16)}→${s?.day_time_end?.slice(11,16)} UTC`;
    }
  }
));
```

```js
const stintSectors = sectors.filter(r =>
  r.ref_car_no === refCar && r.ref_stint_no === selectedStint
);
const sectorNums = [1,2,3,4,5,6,7,8,9];

const driverKeys = [...new Set(stintSectors.map(d => `${d.comp_driver}|${d.comp_car_no}`))];

// Pivot + sort by total rank sum
const pivotData = driverKeys.map(key => {
  const [driver, carStr] = key.split('|');
  const car = +carStr;
  const row = { driver, car, label: `${driver} #${car}`, is_ref: car === refCar };
  let rankSum = 0, rankCount = 0;
  for (const s of sectorNums) {
    const e = stintSectors.find(r => r.comp_driver === driver && r.comp_car_no === car && r.sector === s);
    row[`s${s}_rank`] = e?.rank ?? null;
    row[`s${s}_time`] = e?.sector_time_sec ?? null;
    if (e) { rankSum += e.rank; rankCount++; }
  }
  row.avg_rank = rankCount ? rankSum / rankCount : 99;
  return row;
}).sort((a,b) => a.avg_rank - b.avg_rank);

const driverOrder = pivotData.map(r => r.label);
const maxRank = d3.max(stintSectors, d => d.rank) ?? 10;
```

---

## Sector rank heatmap — Stint ${selectedStint}

```js
const heatData = [];
for (const row of pivotData) {
  for (const s of sectorNums) {
    if (row[`s${s}_rank`] !== null) {
      heatData.push({
        label: row.label,
        car: row.car,
        sector: `S${s}`,
        rank: row[`s${s}_rank`],
        time: row[`s${s}_time`],
        is_ref: row.is_ref
      });
    }
  }
}
```

```js
Plot.plot({
  title: "Sector rank per driver (rows sorted by average rank)",
  width,
  height: Math.max(180, driverOrder.length * 36 + 80),
  marginLeft: 168,
  marginBottom: 36,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: { label: "Sector →", domain: sectorNums.map(s=>`S${s}`) },
  y: { label: null, domain: driverOrder },
  color: {
    domain: [1, maxRank],
    range: ["#1b5e20","#4caf50","#cddc39","#ff9800","#e63946"],
    legend: true, label: "Rank"
  },
  marks: [
    Plot.cell(heatData, {
      x: "sector", y: "label", fill: "rank",
      inset: 2, rx: 4,
      tip: true,
      title: d => `${d.label}\n${d.sector}: P${d.rank}\nTime: ${d.time?.toFixed(3)}s`
    }),
    Plot.text(heatData, {
      x: "sector", y: "label",
      text: d => `${d.rank}`,
      fontSize: 11,
      fontWeight: d => d.is_ref ? "bold" : "normal",
      fill: d => d.rank <= Math.ceil(maxRank/3) ? "#fff" : "#111"
    }),
    Plot.cell(heatData.filter(d => d.is_ref), {
      x: "sector", y: "label",
      stroke: "#ff9800", strokeWidth: 2.5,
      fill: "none", inset: 2, rx: 4
    })
  ]
})
```

---

## Sector times — select a sector

```js
const sectorSel = view(Inputs.select(
  sectorNums.map(s => `S${s}`),
  { label: "Sector", value: "S1" }
));
```

```js
const sNum = +sectorSel.slice(1);
const sectorBarData = stintSectors
  .filter(r => r.sector === sNum)
  .map(r => ({ ...r, label: `${r.comp_driver} #${r.comp_car_no}`, is_ref: r.comp_car_no === refCar }))
  .sort((a,b) => a.sector_time_sec - b.sector_time_sec);

const sBest  = sectorBarData[0]?.sector_time_sec ?? 1;
const sWorst = d3.quantile(sectorBarData.map(d=>d.sector_time_sec).sort(d3.ascending), 0.9) ?? sBest * 1.1;
```

```js
Plot.plot({
  title: `${sectorSel} times — Stint ${selectedStint}`,
  width,
  height: Math.max(160, sectorBarData.length * 30 + 70),
  marginLeft: 168,
  marginRight: 120,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: {
    label: "Sector time (s) →",
    domain: [sBest * 0.99, sWorst * 1.01],
    tickFormat: s => `${s.toFixed(1)}s`
  },
  y: { label: null, domain: sectorBarData.map(r => r.label) },
  marks: [
    Plot.barX(sectorBarData, {
      x: "sector_time_sec", y: "label",
      fill: d => d.is_ref ? "#ff9800" : (CAR_COLORS[d.comp_car_no] ?? "#555"),
      opacity: 0.85, inset: 2, rx: 3,
      tip: true,
      title: d => `P${d.rank} · #${d.comp_car_no} ${d.comp_driver}\n${d.sector_time_sec}s (+${(d.sector_time_sec-sBest).toFixed(3)}s vs best)`
    }),
    Plot.ruleX([sBest], { stroke: "#4caf50", strokeWidth: 1.5, strokeDasharray: "4,3" }),
    Plot.text(sectorBarData, {
      x: d => d.sector_time_sec + (sWorst - sBest) * 0.01,
      y: "label",
      text: d => `P${d.rank}  ${d.sector_time_sec}s  +${(d.sector_time_sec-sBest).toFixed(3)}s`,
      textAnchor: "start", fontSize: 10, fill: "#bbb"
    })
  ]
})
```

---

## Delta to best per sector

```js
const deltaData = [];
for (const s of sectorNums) {
  const rows = stintSectors.filter(r => r.sector === s).sort((a,b)=>a.sector_time_sec-b.sector_time_sec);
  if (!rows.length) continue;
  const best = rows[0].sector_time_sec;
  for (const r of rows) {
    deltaData.push({
      label: `${r.comp_driver} #${r.comp_car_no}`,
      sector: `S${s}`,
      delta: +(r.sector_time_sec - best).toFixed(3),
      is_ref: r.comp_car_no === refCar,
      car: r.comp_car_no
    });
  }
}
const maxDelta = d3.quantile(deltaData.map(d=>d.delta).sort(d3.ascending), 0.85) ?? 20;
const refDeltaData = deltaData.filter(d => d.is_ref);
```

```js
Plot.plot({
  title: `Delta to best per sector — Stint ${selectedStint} (ref: ${refDriver === "All drivers" ? `#${refCar}` : refDriver} in orange)`,
  width,
  height: 300,
  marginLeft: 48,
  marginRight: 16,
  style: { background: "transparent", color: "#ccc", fontSize: "12px" },
  x: { label: "Sector →", domain: sectorNums.map(s=>`S${s}`) },
  y: {
    label: "← Delta to best (s)",
    domain: [0, maxDelta * 1.1],
    tickFormat: s => `+${s.toFixed(1)}s`
  },
  marks: [
    Plot.gridY({ stroke: "#2a2a2a" }),
    Plot.ruleY([0], { stroke: "#4caf50", strokeWidth: 1.5 }),
    Plot.line(deltaData.filter(d => !d.is_ref), {
      x: "sector", y: "delta", z: "label",
      stroke: d => CAR_COLORS[d.car] ?? "#555",
      strokeWidth: 1, opacity: 0.35, curve: "linear"
    }),
    Plot.line(refDeltaData, {
      x: "sector", y: "delta",
      stroke: "#ff9800", strokeWidth: 3, curve: "linear"
    }),
    Plot.dot(refDeltaData, {
      x: "sector", y: "delta",
      fill: "#ff9800", r: 5, tip: true,
      title: d => `${d.label}\n${d.sector}: +${d.delta}s vs best`
    })
  ]
})
```

<style>
.info-box {
  background: #161e1e; border-left: 3px solid #00bcd4;
  border-radius: 6px; padding: .6rem 1rem; margin: 1rem 0;
  font-size: .85em; line-height: 1.6; opacity: .85;
}
</style>
