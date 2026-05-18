---
name: dashboard-design
description: Design system for the 24h Nürburgring M240i dashboard. Covers color palette, typography, Observable Framework theme config, logo usage, CSS patterns, and component styles inspired by the official 24h-rennen.de identity.
license: MIT
compatibility: opencode
metadata:
  domain: design
  source: 24h-rennen.de
---

## Brand identity (24h-rennen.de)

### Colors
- **Primary green** (nav/brand): `#43632d` — signature 24h NBR forest green
- **White**: `#ffffff`
- **Dark text**: `#212529`
- **Blue accent**: `#007bff`
- **Black**: `#000000`

### Car palette (M240i field)
```js
const CAR_COLORS = {
  195: "#e63946", 650: "#2196f3", 651: "#4caf50", 652: "#ff9800",
  653: "#9c27b0", 658: "#00bcd4", 665: "#f44336", 667: "#8bc34a",
  669: "#ff5722", 670: "#3f51b5", 677: "#ffc107"
};
```

### Typography
- **Primary font**: `"Roboto Condensed", sans-serif` (Google Fonts)
- **Monospace** (lap times): `"JetBrains Mono", "Fira Mono", monospace`
- Header H1: font-weight 700, letter-spacing 0.5px
- Stats/numbers: font-weight 800

### Logo assets
- Main logo: `src/assets/logo-main.png` (794×592px, transparent bg)
- Favicon: `src/assets/favicon-32.png` (32×32px)
- Usage: max-height 48px in header, white filter on dark bg

---

## Observable Framework config

```js
// observablehq.config.js
export default {
  title: "24h Nürburgring 2026 — M240i",
  root: "src",
  theme: ["deep-space", "alt"],  // dark + card foreground
  // Do NOT add "wide" — standard column width is fine for this dashboard
}
```

### Custom CSS imports
Add to `observablehq.config.js`:
```js
style: "style/custom.css"
```

---

## CSS patterns

### Header with logo
```html
<div class="nbr-header">
  <img src="./assets/logo-main.png" class="nbr-logo" alt="54th ADAC Ravenol 24h Nürburgring">
  <div class="nbr-header-text">
    <span class="nbr-title">M240i Racing Cup</span>
    <span class="nbr-subtitle">Driver Stint Analysis · May 2026</span>
  </div>
</div>
```

```css
.nbr-header {
  display: flex; align-items: center; gap: 16px;
  padding: 12px 0 8px;
  border-bottom: 2px solid #43632d;
  margin-bottom: 1.5rem;
}
.nbr-logo { height: 48px; width: auto; }
.nbr-title { font-family: "Roboto Condensed", sans-serif; font-weight: 700; font-size: 1.1em; letter-spacing: 1px; text-transform: uppercase; }
.nbr-subtitle { font-size: 0.8em; opacity: 0.5; display: block; }
```

### Stat cards
```css
.stat-card {
  background: var(--theme-background-alt);
  border-radius: 8px;
  border-top: 3px solid #43632d;
  padding: 1rem;
}
.stat-value { font-size: 2.2em; font-weight: 800; font-family: "Roboto Condensed", sans-serif; line-height: 1; }
.stat-label { font-size: 0.72em; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.5; margin-top: 2px; }
```

### Info boxes
```css
.info-box {
  background: var(--theme-background-alt);
  border-left: 3px solid #43632d;
  border-radius: 6px;
  padding: .6rem 1rem;
  font-size: .85em;
  line-height: 1.7;
}
```

### Lap time formatting
Always format as `MM:SS.s` (1 decimal) for display, never raw seconds:
```js
function fmtLap(sec) {
  if (!sec) return "—";
  const m = Math.floor(sec/60);
  const s = (sec % 60).toFixed(1);
  return `${m}:${s.padStart(4,'0')}`;
}
```

---

## Plot styling

```js
// Standard plot style for this project
const plotStyle = {
  background: "transparent",
  color: "var(--theme-foreground)",
  fontSize: "12px",
  fontFamily: '"Roboto Condensed", sans-serif'
};

// Grid lines
Plot.gridY({ stroke: "var(--theme-foreground-faintest)" })

// Axis tick format for race time
tickFormat: d => {
  const h = (d.getUTCHours() + 2) % 24; // UTC → CEST
  return `${String(h).padStart(2,'0')}:${String(d.getUTCMinutes()).padStart(2,'0')}`;
}
```

---

## Notes
- Theme `deep-space` = very dark background (#0d1117 range), great contrast
- `alt` modifier = cards use --theme-background-alt as foreground surface
- Roboto Condensed loaded via Google Fonts in custom.css
- Logo has transparent background — works on both dark and light
- **Images with white background on dark theme**: use a white card bg (`background:#ffffff`)
  with a coloured border. Do NOT use `mix-blend-mode:multiply` (black on black).
  Do NOT use `filter:invert()` (inverts track colours too).
  White card with coloured border is the clean, legible solution.
