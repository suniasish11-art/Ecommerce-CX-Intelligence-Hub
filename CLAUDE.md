# Ecommerce CX Intelligence Hub — Claude Instructions

## Project Overview

A static single-page dashboard that reads from an Excel file and deploys to Netlify with no backend required. All data is baked into the HTML at build time.

**Live URL:** https://jade-frangollo-5f6edb.netlify.app
**GitHub Repo:** suniasish11-art/Ecommerce-CX-Intelligence-Hub

---

## How to Update Data

1. Replace `navedas_cx_1000 (1).xlsx` with the new Excel file (keep the same name)
2. Run the build script:
   ```bash
   cd "C:\Users\sunit\Ecommerce CX Intelligence Hub"
   python build_static.py
   ```
3. Build deploys automatically to Netlify at the end

---

## Architecture

```
Ecommerce CX Intelligence Hub/
├── build_static.py                  ← Master build script (run this to deploy)
├── ecommerce_cx_hub_v10 (3).html    ← Source HTML template (never edit directly)
├── navedas_cx_1000 (1).xlsx         ← Data source (4 sheets)
├── frontend/
│   └── index.html                   ← Generated output (do not edit by hand)
├── backend/                         ← Legacy Flask backend (not used for Netlify)
│   ├── server.py
│   └── requirements.txt
├── requirements.txt                 ← Python deps: streamlit, pandas, openpyxl, plotly
└── CLAUDE.md                        ← This file
```

---

## Key File: build_static.py

The build script does everything in one run:

1. Reads Excel (4 sheets via pandas)
2. Computes all KPIs, team stats, agent stats, signal data
3. Injects computed JS variables into the HTML template
4. Replaces Section-C (Signal Intelligence ROI cards) with real data
5. Replaces Section-E (Executive Briefing) with auto-generated text
6. Updates ROI_CFG with real LTV, churn, and win-back rates
7. Writes `frontend/index.html`
8. Runs `netlify deploy --dir=frontend --prod --site 3fe62b4a-4ca4-44d5-9077-c20ba9407873`

---

## Excel Sheet Structure

| Sheet Name | Content | Notes |
|---|---|---|
| Ticket Records | 1,000 support tickets | Has title row → use `skiprows=1` |
| Monthly Summary | 15 months of aggregated data | Direct read |
| Agent Performance | 12 agents with CSAT, scores | Direct read |
| Issue Intelligence | Category-level signals | 3 rows |

### Key Columns in Ticket Records
- `Ticket ID`, `Date`, `Month`, `Issue Category`, `Sub-Issue`
- `Status`, `Agent Name`, `Sentiment`, `Score`, `Revenue Impact`
- `Pattern Flag` (may be NaN → display as `—`)

---

## Real Data Values (from current Excel)

| Metric | Value |
|---|---|
| Total tickets | 1,000 |
| Avg Customer LTV | $122 |
| Churn tickets | 342 (peak 42.9% Dec 2025) |
| Revenue-at-risk tickets | 342 ($45K total) |
| Loyalty tickets | 316 (112 negative) |
| Billing tickets | 120 (avg $106/incident) |
| Win-back rate | 51% (174 resolved / 342 churn) |
| Best agent | P. Nair (93% CSAT) |
| Worst agent | M. Webb (71% CSAT, 14pt gap) |
| Total addressable revenue | $120K |

---

## Dashboard Sections

| Section | Data Source |
|---|---|
| KPI counters (top row) | Computed from all sheets |
| CX Trend Line Chart | Monthly Summary sheet |
| Revenue Impact Bar Chart | Monthly Summary sheet |
| Agent Performance Chart | Agent Performance sheet |
| CX Signal Intelligence (ROI cards) | Issue Intelligence + Ticket Records |
| Executive Briefing | Auto-generated from all computed metrics |
| ROI Calculator | ROI_CFG object with real uplift rates |
| Ticket Table | All 1,000 tickets from Ticket Records |
| Team Cards | Aggregated from Ticket Records by category |

---

## Tools Used

- **Python + pandas** — Excel reading and data processing
- **openpyxl** — Excel file engine for pandas
- **Netlify CLI** — Deployment (`netlify deploy`)
- **Vanilla JS** — All dashboard interactivity (no framework)
- **Plotly.js** — Charts (loaded via CDN)
- **html2canvas + jsPDF** — PDF export
- **GitHub** — Source control

---

## Common Tasks

### Rebuild and deploy after Excel update
```bash
python build_static.py
```

### Preview locally before deploying
Open `frontend/index.html` directly in a browser (note: fetch calls won't work, but layout is visible).

### Run local server for full testing
```bash
cd "C:\Users\sunit\Ecommerce CX Intelligence Hub\backend"
python server.py
# Then open http://localhost:8080
```

### Check Netlify site status
```bash
netlify status
netlify open --site
```

---

## Important Rules

- **Never edit `frontend/index.html` directly** — it is overwritten on every build
- **Never edit `ecommerce_cx_hub_v10 (3).html` directly** — it is the source template; all data injection happens in `build_static.py`
- Always run `build_static.py` after changing the Excel file or modifying `build_static.py`
- The Netlify site ID is `3fe62b4a-4ca4-44d5-9077-c20ba9407873` — do not change it

---

## Dependency Install

```bash
pip install pandas openpyxl streamlit plotly
npm install -g netlify-cli   # only needed once
netlify login                # only needed once
```
