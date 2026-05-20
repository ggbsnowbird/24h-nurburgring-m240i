# Auth Setup — NBR Dashboard

Team-based login for the 24h Nürburgring dashboard. One credential pair per car entry (login = `car-NNN`).

## Overview

| File | Role |
|------|------|
| `tools/generate_team_credentials.py` | Generates logins/passwords, writes CSV + JS table |
| `dashboard/src/auth/auth-table.js` | SHA-256 lookup dict (committed, safe — no plain-text passwords) |
| `teams_credentials.csv` | Plain-text credentials (gitignored — distribute by hand) |
| `dashboard/src/auth/guard.js` | Client-side utilities (getTeam, logout, renderAuthBadge) |
| `dashboard/src/login.md` | Login page |

## First-time setup

### 1. Generate credentials

```bash
python3 tools/generate_team_credentials.py --db /path/to/nbr_sector_times.db
```

This writes:
- `teams_credentials.csv` — keep private, send each row to the relevant team
- `dashboard/src/auth/auth-table.js` — commit this file

The script is **idempotent**: re-running preserves existing passwords and only generates new ones for cars not yet in the CSV.

### 2. (Optional) Wire up the login webhook

To log team logins to a Google Sheet:

1. Open [Google Apps Script](https://script.google.com) and create a new project.
2. Paste the following `doPost` handler:

```js
function doPost(e) {
  const data  = JSON.parse(e.postData.contents);
  const sheet = SpreadsheetApp.openById("YOUR_SHEET_ID").getSheetByName("Logins");
  sheet.appendRow([
    new Date(data.ts),
    data.team,
    data.ua,
    new Date().toISOString(),
  ]);
  return ContentService.createTextOutput("ok");
}
```

3. Deploy → **New deployment** → Type: **Web App** → Execute as: *Me* → Who has access: *Anyone*.
4. Copy the deployment URL.
5. In `dashboard/src/auth/auth-table.js`, replace the empty string on the `WEBHOOK_URL` line:

```js
export const WEBHOOK_URL = "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec";
```

6. Commit and redeploy the dashboard.

### 3. Distribute credentials

Send each team their row from `teams_credentials.csv` through a private channel (email, WhatsApp, etc.). Never commit the CSV.

## Revoking a team

1. Remove the team's entry from `teams_credentials.csv`.
2. Re-run `generate_team_credentials.py` — this regenerates `auth-table.js` without the revoked team.
3. Commit `auth-table.js` and redeploy the dashboard.

The old SHA-256 key will no longer be in the table, so the old password stops working immediately after deploy.

## How it works

1. **Pre-render check** — an inline script in `<head>` (injected via `observablehq.config.js`) redirects any non-`/login` page to `/login` if `localStorage.nbr_team` is not set. This runs synchronously, before Observable hydrates the page, so there is no content flash.
2. **Login flow** — `login.md` hashes `login:password` with Web Crypto SHA-256 and looks up the result in `AUTH_TABLE`. On match: sets `localStorage.nbr_team`, a 30-day cookie, fires the optional webhook, then redirects to `/`.
3. **Badge** — on DOMContentLoaded, the same inline script injects the team name + Logout button into the header bar.
4. **Logout** — clears `localStorage.nbr_team`, expires the cookie, redirects to `/login`.
