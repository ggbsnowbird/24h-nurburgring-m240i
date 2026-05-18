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

> Partial (sector) times ranked for each driver in their stint window.  
> Pinpoints where time is **gained or lost** relative to the M240i field.

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
const refDriver = view(Inputs.select(["All drivers", ...driversOf(refCar)], {
  label: "Driver",
  value: "Boutonnet"
}));
```

```js
const filteredStints = stints.filter(s =>
  s.car_no === refCar &&
  (refDriver === "All drivers" || s.driver_name === refDriver) &&
  s.best_laptime_sec < 1200
);
```

```js
const selectedStint = view(Inputs.select(
  filteredStints.map(s => s.stint_no),
  {
    label: "Stint",
    format: n => {
      const s = filteredStints.find(x => x.stint_no === n);
      return `Stint ${n} — ${s?.driver_name} · ${s?.day_time_start?.slice(11,16)}→${s?.day_time_end?.slice(11,16)} UTC`;
    }
  }
));
```

```js
// All sector rows for this ref stint
const stintSectors = sectors.filter(r =>
  r.ref_car_no === refCar && r.ref_stint_no === selectedStint
);

// Drivers in this stint window (sorted by total rank)
const driversInWindow = [...new Set(stintSectors.map(d => `${d.comp_driver}|${d.comp_car_no}`))];

// Pivot: rows = drivers, cols = sectors, value = rank
const sectorNums = [1,2,3,4,5,6,7,8,9];

const pivotData = driversInWindow.map(key => {
  const [driver, carStr] = key.split('|');
  const carNo = +carStr;
  const row = { driver, car_no: carNo, label: `${driver} #${carNo}` };
  for (const s of sectorNums) {
    const entry = stintSectors.find(r => r.comp_driver === driver && r.comp_car_no === carNo && r.sector === s);
    row[`s${s}_rank`] = entry?.rank ?? null;
    row[`s${s}_time`] = entry?.sector_time_sec ?? null;
  }
  // Sort key: sum of sector ranks
  row.sort_key = sectorNums.reduce((acc, s) => acc + (row[`s${s}_rank`] ?? 20), 0);
  return row;
}).sort((a,b) => a.sort_key - b.sort_key);
```

---

## Sector rank heatmap

```js
// Flatten for Plot
const heatData = [];
for (const row of pivotData) {
  for (const s of sectorNums) {
    if (row[`s${s}_rank`] !== null) {
      heatData.push({
        driver_label: row.label,
        car_no: row.car_no,
        sector: `S${s}`,
        rank: row[`s${s}_rank`],
        time_sec: row[`s${s}_time`],
        is_ref: row.car_no === refCar
      });
    }
  }
}

const driverOrder = pivotData.map(r => r.label);
```

```js
Plot.plot({
  title: `Stint ${selectedStint} — Sector rank heatmap (green=fast, red=slow)`,
  width: 820,
  height: Math.max(240, driverOrder.length * 30 + 80),
  marginLeft: 160,
  marginBottom: 40,
  style: { background: "transparent", color: "#ccc" },
  x: { label: "Sector →", domain: sectorNums.map(s=>`S${s}`) },
  y: { label: null, domain: driverOrder },
  color: {
    domain: [1, Math.max(...heatData.map(d=>d.rank))],
    range: ["#1b5e20","#4caf50","#ff9800","#e63946","#7f0000"],
    legend: true,
    label: "Rank"
  },
  marks: [
    Plot.cell(heatData, {
      x: "sector",
      y: "driver_label",
      fill: "rank",
      inset: 1,
      rx: 3,
      tip: true,
      title: d => `${d.driver_label}\n${d.sector}: rank ${d.rank}\nTime: ${d.time_sec?.toFixed(3)}s`
    }),
    Plot.text(heatData, {
      x: "sector",
      y: "driver_label",
      text: d => `${d.rank}`,
      fontSize: 11,
      fill: d => d.rank <= 2 ? "#fff" : d.rank >= 8 ? "#fff" : "#eee",
      fontWeight: d => d.is_ref ? "bold" : "normal"
    }),
    // Outline ref car rows
    Plot.cell(heatData.filter(d => d.is_ref), {
      x: "sector",
      y: "driver_label",
      stroke: "#ff9800",
      strokeWidth: 2,
      fill: "none",
      inset: 1,
      rx: 3
    })
  ]
})
```

---

## Sector time comparison (bar chart)

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
  .map(r => ({
    ...r,
    label: `${r.comp_driver} #${r.comp_car_no}`,
    is_ref: r.comp_car_no === refCar
  }))
  .sort((a,b) => a.sector_time_sec - b.sector_time_sec);

const bestSec = sectorBarData[0]?.sector_time_sec ?? 1;
```

```js
Plot.plot({
  title: `${sectorSel} — Sector times ranked (stint ${selectedStint})`,
  width: 820,
  height: Math.max(200, sectorBarData.length * 30 + 80),
  marginLeft: 160,
  style: { background: "transparent", color: "#ccc" },
  x: {
    label: "Sector time (s) →",
    domain: [bestSec * 0.98, bestSec * 1.15]
  },
  y: { label: null, domain: sectorBarData.map(r => r.label) },
  marks: [
    Plot.barX(sectorBarData, {
      x: "sector_time_sec",
      y: "label",
      fill: d => d.is_ref ? "#ff9800" : (CAR_COLORS[d.comp_car_no] ?? "#555"),
      opacity: 0.85,
      tip: true,
      title: d => `#${d.comp_car_no} ${d.comp_driver}\nSector ${d.sector}: ${d.sector_time_sec}s\nRank: ${d.rank}`
    }),
    Plot.ruleX([bestSec], { stroke: "#4caf50", strokeWidth: 1.5, strokeDasharray: "4,3" }),
    Plot.text(sectorBarData, {
      x: d => d.sector_time_sec + 0.05,
      y: "label",
      text: d => `#${d.rank}  ${d.sector_time_sec}s`,
      textAnchor: "start",
      fontSize: 10,
      fill: "#ccc"
    })
  ]
})
```

---

## Delta to best (seconds lost per sector)

```js
// For each sector in the stint, compute delta vs best time in that sector
const deltaData = [];
for (const s of sectorNums) {
  const rows = stintSectors.filter(r => r.sector === s).sort((a,b) => a.sector_time_sec - b.sector_time_sec);
  if (!rows.length) continue;
  const best = rows[0].sector_time_sec;
  for (const r of rows) {
    deltaData.push({
      label: `${r.comp_driver} #${r.comp_car_no}`,
      sector: `S${s}`,
      delta: +(r.sector_time_sec - best).toFixed(3),
      is_ref: r.comp_car_no === refCar,
      car_no: r.comp_car_no
    });
  }
}
```

```js
Plot.plot({
  title: `Delta to best per sector — Stint ${selectedStint}`,
  width: 900,
  height: 360,
  marginLeft: 160,
  style: { background: "transparent", color: "#ccc" },
  x: { label: "Sector →", domain: sectorNums.map(s=>`S${s}`) },
  y: { label: "← Delta to best (s)", domain: [0, 60] },
  color: { domain: CARS, range: CARS.map(c => CAR_COLORS[c] ?? "#888"), legend: false },
  marks: [
    Plot.ruleY([0], { stroke: "#4caf50", strokeWidth: 1.5 }),
    Plot.line(
      deltaData.filter(d => d.is_ref),
      {
        x: "sector",
        y: "delta",
        stroke: "#ff9800",
        strokeWidth: 3,
        curve: "linear"
      }
    ),
    Plot.line(
      deltaData.filter(d => !d.is_ref),
      {
        x: "sector",
        y: "delta",
        z: "label",
        stroke: d => CAR_COLORS[d.car_no] ?? "#555",
        strokeWidth: 1,
        opacity: 0.4,
        curve: "linear"
      }
    ),
    Plot.dot(
      deltaData.filter(d => d.is_ref),
      {
        x: "sector",
        y: "delta",
        fill: "#ff9800",
        r: 5,
        tip: true,
        title: d => `${d.label}\n${d.sector}: +${d.delta}s vs best`
      }
    )
  ]
})
```
