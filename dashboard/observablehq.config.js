export default {
  title: "24h Nürburgring 2026",
  root: "src",
  pages: [
    { name: "Home", path: "/" },
    {
      name: "M240i Racing Cup",
      pages: [
        { name: "Overview",        path: "/m240i/overview" },
        { name: "Stint Rankings",  path: "/m240i/stint-rankings" },
        { name: "Sector Analysis", path: "/m240i/sector-analysis" },
        { name: "About",           path: "/m240i/about" },
      ]
    },
    {
      name: "SP9 GT3",
      pages: [
        { name: "Overview",        path: "/sp9/overview" },
        { name: "Stint Rankings",  path: "/sp9/stint-rankings" },
        { name: "Sector Analysis", path: "/sp9/sector-analysis" },
        { name: "About",           path: "/sp9/about" },
      ]
    },
  ],
  theme: "dark",
  head: `<script>
(function(){
  var p=location.pathname;
  var base=p.match(/^(\/[^/]+\/)/)?.[1]||'/';
  var loginPath=base+'login';
  if(!p.startsWith(loginPath)&&!localStorage.getItem('nbr_team')){
    location.replace(loginPath);return;
  }
  document.addEventListener('DOMContentLoaded',function(){
    if(p.startsWith(loginPath))return;
    var t=localStorage.getItem('nbr_team');
    if(!t)return;
    var h=document.querySelector('#observablehq-header > div');
    if(!h)return;
    var b=document.createElement('div');
    b.style.cssText='margin-left:auto;display:flex;align-items:center;gap:.5rem;font-size:.78em;opacity:.65';
    b.innerHTML='<span style="max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+t+'</span>';
    var btn=document.createElement('button');
    btn.textContent='Logout';
    btn.style.cssText='padding:2px 7px;cursor:pointer;border:1px solid currentColor;border-radius:3px;background:transparent;font-size:.85em;font-family:inherit';
    btn.onclick=function(){localStorage.removeItem('nbr_team');document.cookie='nbr_team=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Lax';location.replace(loginPath);};
    b.appendChild(btn);h.appendChild(b);
  });
})();
</script>
<link rel="icon" type="image/png" sizes="32x32" href="data:image/png;base64,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">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@300;400;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  /* ─── Brand tokens ─────────────────────────────────── */
  :root {
    --nbr-green:        #43632d;
    --nbr-green-light:  #5a8438;
    --nbr-gold:         #f0c040;
    --nbr-amber:        #ff9800;
    --nbr-mono:         "JetBrains Mono", "Fira Mono", monospace;
  }

  /* ─── Typography ───────────────────────────────────── */
  body, .observablehq, h1, h2, h3, h4,
  select, input, button, table {
    font-family: "Roboto Condensed", sans-serif !important;
  }
  .observablehq svg text { font-family: "Roboto Condensed", sans-serif !important; }

  .observablehq h1 { font-weight: 800; letter-spacing: .5px; margin: 1.5rem 0 .25rem; }
  .observablehq h2 {
    font-weight: 700; letter-spacing: .3px;
    margin: 2rem 0 .5rem; padding-bottom: .35rem;
    border-bottom: 1px solid var(--theme-foreground-faintest);
  }
  .observablehq h3 {
    font-weight: 700; font-size: 1.1em; margin: 1.5rem 0 .25rem;
  }

  /* ─── Header strip ─────────────────────────────────── */
  #observablehq-header { border-bottom: 2px solid var(--nbr-green) !important; }

  /* ─── Reusable components ──────────────────────────── */
  .info-box {
    background: var(--theme-background-alt);
    border-left: 3px solid var(--nbr-green);
    border-radius: 6px;
    padding: .7rem 1rem; margin: 1rem 0;
    font-size: .87em; line-height: 1.7;
  }
  .info-box strong { color: var(--nbr-green-light); }

  .stint-meta {
    display: flex; gap: 1.2rem; flex-wrap: wrap;
    background: var(--theme-background-alt);
    border-left: 3px solid var(--nbr-green);
    border-radius: 6px;
    padding: .65rem 1rem; margin: .8rem 0 1.2rem;
    font-size: .88em;
  }
  .stint-meta strong { color: var(--nbr-amber); }

  .muted-note, .missing-note {
    font-size: .8em; opacity: .5; margin: .5rem 0 1rem;
    padding: .3rem .8rem; border-left: 2px solid var(--theme-foreground-faint);
  }

  .empty-state {
    background: var(--theme-background-alt);
    border-radius: 6px; padding: 2rem 1rem; margin: 1rem 0;
    text-align: center; font-size: .9em; opacity: .6;
  }

  .chart-subtitle { font-size: .82em; opacity: .55; margin: -.1rem 0 .8rem; }

  /* ─── Control bar ──────────────────────────────────── */
  .control-bar {
    display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
    background: var(--theme-background-alt);
    border-radius: 8px; padding: .8rem 1rem;
    margin: 1rem 0 1.2rem;
    border-top: 2px solid var(--nbr-green);
  }
  .control-bar > * { min-width: 0; }
  .control-bar form { margin: 0; }
  .control-bar label { font-size: .75em !important; opacity: .65; }
  .control-bar select { font-size: .88em !important; }

  /* ─── Correction log ───────────────────────────────── */
  .correction-log {
    border-left: 4px solid #f0a500;
    background: var(--theme-background-alt);
    border-radius: 6px;
    padding: .7rem 1rem; margin: 1rem 0; font-size: .87em;
  }
  .correction-log strong { color: #f0a500; display: block; margin-bottom: .4rem; }
  .correction-item { display: flex; flex-direction: column; gap: 2px; padding: .35rem 0; border-top: 1px solid var(--theme-foreground-faintest); }
  .correction-item .badge { font-weight: 700; color: var(--nbr-amber); font-size: .88em; }
  .correction-item .meta { opacity: .5; font-size: .82em; }

  /* ─── Tables ───────────────────────────────────────── */
  .observablehq table { font-size: .88em !important; }
  .observablehq table th {
    text-transform: uppercase; letter-spacing: .7px;
    font-size: .76em !important; opacity: .6; font-weight: 700;
  }
  .observablehq table td { font-feature-settings: "tnum"; }

  /* ─── Hero ─────────────────────────────────────────── */
  .hero h1 { font-size: 1.9em; font-weight: 800; margin: 0 0 4px; }
  .hero h2 { font-size: 1.05em; opacity: .55; margin: 0 0 1rem; font-weight: 400; }
  .hero-stats { display: flex; gap: 2rem; flex-wrap: wrap; }
  .hero-stat span { display: block; font-size: 2em; font-weight: 800; line-height: 1; color: var(--nbr-gold); }
  .hero-stat { font-size: .8em; opacity: .6; text-transform: uppercase; letter-spacing: 1px; }

  /* ─── Sector map + pills (responsive) ──────────────── */
  .sector-map-row {
    display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-start;
  }
  .sector-map-img {
    width: 280px; height: 280px; object-fit: contain; display: block;
  }
  .sector-pills-col {
    display: flex; flex-direction: column; gap: 4px; padding-top: 4px;
  }

  /* ─── Landing-page picker cards ────────────────────── */
  .landing-cards {
    display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.5rem;
  }

  /* ─── Table horizontal scroll wrapper ──────────────── */
  .table-scroll {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  /* ─── Mobile (≤640px) ──────────────────────────────── */
  @media (max-width: 640px) {
    .sector-map-row { flex-direction: column; align-items: stretch; }
    .sector-map-img { width: min(280px, 100%); height: auto; max-width: 100%; }
    .sector-pills-col { flex-direction: row; flex-wrap: wrap; padding-top: 0; }
    .landing-cards { grid-template-columns: 1fr; }
    .hero h1 { font-size: 1.5em; }
    .hero-stats { gap: 1.2rem; }
    .hero-stat span { font-size: 1.6em; }
    .control-bar { gap: .6rem; padding: .6rem .7rem; }
    .observablehq h1 { font-size: 1.4em; }
    .observablehq h2 { font-size: 1.15em; margin: 1.4rem 0 .4rem; }
  }
</style>`,
  header: `<div style="display:flex;align-items:center;gap:10px;padding:6px 0">
    <img src="data:image/png;base64,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" style="height:26px;width:auto" alt="">
    <span style="font-size:1em;font-weight:700;letter-spacing:.5px;font-family:'Roboto Condensed',sans-serif;text-transform:uppercase">54th ADAC Ravenol 24h Nürburgring</span>
    <span style="opacity:0.4;font-size:0.82em;font-family:'Roboto Condensed',sans-serif">M240i Racing Cup · 2026</span>
  </div>`,
  footer: "Data: ADAC Sector Times PDF + LiveTiming WebSocket · Outlaps excluded · Laps >11:30 filtered · Built with Observable Framework",
};
