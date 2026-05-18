export default {
  title: "24h Nürburgring 2026 — M240i",
  root: "src",
  pages: [
    { name: "Overview", path: "/" },
    { name: "Stint Rankings", path: "/stint-rankings" },
    { name: "Sector Analysis", path: "/sector-analysis" },
  ],
  theme: "dark",
  header: `<div style="display:flex;align-items:center;gap:16px;padding:8px 0">
    <span style="font-size:1.25em;font-weight:800;letter-spacing:.5px">🏁 54th ADAC Ravenol 24h Nürburgring 2026</span>
    <span style="opacity:0.45;font-size:0.85em;font-weight:400">BMW M240i Racing Cup</span>
  </div>`,
  footer: "Data: ADAC Sector Times PDF + LiveTiming WebSocket · Outlaps excluded · Laps >11:30 filtered · Built with Observable Framework",
};
