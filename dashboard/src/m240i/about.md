---
title: About
---

```js
const carUrl = await FileAttachment("../assets/car-652.webp").url();
```

```js
html`<div style="
  position:relative;
  width:100%;
  height:320px;
  border-radius:12px;
  overflow:hidden;
  margin-bottom:2rem;
">
  <img src="${carUrl}" alt="Car #652 Adrenalin Motorsport — 54th ADAC Ravenol 24h Nürburgring"
    style="width:100%;height:100%;object-fit:cover;object-position:center 55%">
  <div style="
    position:absolute;inset:0;
    background:linear-gradient(to top, rgba(0,0,0,.75) 0%, rgba(0,0,0,.1) 50%, transparent 100%);
  "></div>
  <div style="
    position:absolute;bottom:0;left:0;right:0;
    padding:1.5rem 1.8rem;
  ">
    <div style="font-family:'Roboto Condensed',sans-serif;font-weight:800;font-size:1.5em;letter-spacing:.5px;color:#fff">
      #652 — Adrenalin Motorsport Team
    </div>
    <div style="font-size:.88em;opacity:.7;color:#fff;margin-top:2px">
      Opran · Boutonnet · Laparra · Kravets &nbsp;·&nbsp; BMW M240i Racing Cup
    </div>
  </div>
</div>`
```

# About this application

This tool was built to analyse the performance data of **BMW M240i Racing Cup** drivers at the **54th ADAC Ravenol 24h Nürburgring** (May 14–17, 2026).

---

## Data sources

Two sources were combined:
- **Official ADAC sector times PDF** (wige Solutions) — lap times and all 9 sector splits for every car in the M240i class
- **LiveTiming WebSocket feed** — timestamps each lap with its exact real-world clock time (CEST, Nürburgring local time)

Together they produce a clean dataset: **11 cars · 127 stints · 791 valid laps**.

> Outlaps (first lap of each stint — cold tyres, pit exit) and laps over 11:30 (driver changes, Safety Car, Code 60) are systematically excluded from all analyses.

---

## The three pages

### 1. Overview
Full race pace picture. Every valid lap is plotted on a real-time axis. Three rolling statistics are computed over a trailing window (adjustable: 15 / 30 / 60 min):
- **P5 rolling min** (green) — 5th-percentile lap time in the trailing window, reflecting the true pace potential of the class at each moment — no future data used
- **Rolling avg** (blue) — mean pace of the field in the same window
- **±1σ band** (grey) — spread of the field, which visibly widens during rain or Safety Car periods

A driver filter lets you isolate one or several drivers on the scatter while keeping the rolling stats over the whole field.

### 2. Stint Rankings
Comparative ranking by stint. For a given driver, each stint is benchmarked against **all other M240i drivers on track at the same time** — the only fair comparison, as track conditions (weather, grip, temperature) are identical for everyone. The comparison window is extended 4 minutes before the stint start to capture drivers finishing a lap just before.

The ranking uses a **z-score normalised model** (not a simple lap time comparison) so that a driver who is P2/16 in a dense, competitive window is ranked fairly against one who is P1/6 in a quieter one.

### 3. Sector Analysis — the most insightful page

In my view, this is the richest page. It shows **exactly where time is gained or lost**, sector by sector, within a stint.

The Nordschleife is split into 9 sectors (S1–S9). For each reference stint, all drivers present on track in the same time window are ranked on each sector independently. The result is a heatmap that immediately shows:
- Which sectors a driver is strong or weak in relative to the field
- The **delta to best** per sector — how many seconds are lost vs the class leader on that portion of the track
- Which sectors show high variance (changing conditions) vs stable ones

This is the tool to use to pinpoint specific areas for improvement.

---

## Technical notes

- All timestamps in **CEST (UTC+2)** — Nürburgring local time
- Sector 7 (Nordschleife, ~3:30–4:00 min) handled correctly with a dynamic per-sector threshold
- Manual corrections logged for specific stints (e.g. Boutonnet stint 14 — puncture, laps 93–96 excluded)

---

*Built with Observable Framework · Data: ADAC / wige Solutions · LiveTiming WebSocket*
