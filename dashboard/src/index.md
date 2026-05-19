---
title: 54th ADAC Ravenol 24h Nürburgring 2026
---

```js
const logoUrl = await FileAttachment("assets/logo-main.png").url();
const m240i_stints = await FileAttachment("data/m240i/stints.json").json();
const sp9_stints   = await FileAttachment("data/sp9/stints.json").json();
```

```js
const m240i_cars = [...new Set(m240i_stints.map(s => s.car_no))].length;
const sp9_cars   = [...new Set(sp9_stints.map(s => s.car_no))].length;
const m240i_laps = m240i_stints.reduce((s, d) => s + d.lap_count, 0);
const sp9_laps   = sp9_stints.reduce((s, d) => s + d.lap_count, 0);
```

```js
html`<div style="text-align:center;padding:2rem 0 1.5rem">
  <img src="${logoUrl}" style="height:72px;width:auto;margin-bottom:1rem;display:block;margin-inline:auto" alt="54th ADAC Ravenol 24h Nürburgring">
  <h1 style="font-size:1.8em;font-weight:800;margin:0 0 .3rem">54th ADAC Ravenol 24h Nürburgring</h1>
  <p style="opacity:.5;margin:0;font-size:.95em">May 14–17, 2026 · Nürburgring Nordschleife · 25,378 m · Driver Stint Analysis</p>
</div>`
```

---

```js
html`<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin:1.5rem 0">

  <!-- M240i card -->
  <a href="./m240i/overview" style="text-decoration:none;color:inherit">
    <div class="card" style="
      border-top:4px solid #ff9800;
      cursor:pointer;
      transition:transform .15s,box-shadow .15s;
      padding:1.5rem;
    " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 24px rgba(255,152,0,.2)'"
       onmouseout="this.style.transform='';this.style.boxShadow=''">
      <div style="font-size:.72em;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#ff9800;margin-bottom:.5rem">BMW M240i Racing Cup</div>
      <div style="font-size:1.6em;font-weight:800;margin-bottom:.75rem">M240i Class</div>
      <div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-bottom:1rem">
        <div style="font-size:.8em;opacity:.6"><span style="display:block;font-size:1.8em;font-weight:800;opacity:1;color:#ccc">${m240i_cars}</span>Cars</div>
        <div style="font-size:.8em;opacity:.6"><span style="display:block;font-size:1.8em;font-weight:800;opacity:1;color:#ccc">${m240i_stints.length}</span>Stints</div>
        <div style="font-size:.8em;opacity:.6"><span style="display:block;font-size:1.8em;font-weight:800;opacity:1;color:#ccc">${m240i_laps}</span>Valid laps</div>
      </div>
      <p style="font-size:.85em;opacity:.55;margin:0">Cup class · Single-model BMW M240i · Spec racing</p>
      <div style="margin-top:1rem;font-size:.82em;color:#ff9800;font-weight:700">Open analysis →</div>
    </div>
  </a>

  <!-- SP9 card -->
  <a href="./sp9/overview" style="text-decoration:none;color:inherit">
    <div class="card" style="
      border-top:4px solid #3b82f6;
      cursor:pointer;
      transition:transform .15s,box-shadow .15s;
      padding:1.5rem;
    " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 24px rgba(59,130,246,.2)'"
       onmouseout="this.style.transform='';this.style.boxShadow=''">
      <div style="font-size:.72em;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#3b82f6;margin-bottom:.5rem">ADAC GT Masters / SP9</div>
      <div style="font-size:1.6em;font-weight:800;margin-bottom:.75rem">SP9 GT3</div>
      <div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-bottom:1rem">
        <div style="font-size:.8em;opacity:.6"><span style="display:block;font-size:1.8em;font-weight:800;opacity:1;color:#ccc">${sp9_cars}</span>Cars</div>
        <div style="font-size:.8em;opacity:.6"><span style="display:block;font-size:1.8em;font-weight:800;opacity:1;color:#ccc">${sp9_stints.length}</span>Stints</div>
        <div style="font-size:.8em;opacity:.6"><span style="display:block;font-size:1.8em;font-weight:800;opacity:1;color:#ccc">${sp9_laps}</span>Valid laps</div>
      </div>
      <p style="font-size:.85em;opacity:.55;margin:0">GT3 class · BMW · Mercedes-AMG · Audi · Ferrari · Lamborghini · Aston Martin · McLaren · Porsche</p>
      <div style="margin-top:1rem;font-size:.82em;color:#3b82f6;font-weight:700">Open analysis →</div>
    </div>
  </a>

</div>

<p style="text-align:center;font-size:.8em;opacity:.4;margin-top:1rem">
  Outlaps &amp; laps &gt;11:30 excluded · Data: ADAC PDF + LiveTiming · Built with Observable Framework
</p>`
```
