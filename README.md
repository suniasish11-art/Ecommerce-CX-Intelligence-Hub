# Navedas CX Intelligence Hub - Live Dashboard

Your Ecommerce CX Intelligence Hub is now fully connected to live Excel data!

## Quick Start (3 Simple Steps)

### Option 1: Using Batch File (EASIEST)
1. **Double-click** `START.bat`
2. Wait for the message: `Server starting... Open browser: http://localhost:8080`
3. Your browser will open automatically to the dashboard

### Option 2: Using PowerShell
1. **Right-click** `START.ps1`
2. Select **"Run with PowerShell"**
3. Your browser will open automatically to the dashboard

### Option 3: Manual Command Prompt
```
cd "C:\Users\sunit\Ecommerce CX Intelligence Hub"
python server.py
```
Then open your browser to: **http://localhost:8080**

---

## What You'll See

The dashboard displays:
- ✓ **1,000 ticket records** from your Excel file
- ✓ **16 months** of CX trends (Jan 2025 - Mar 2026)
- ✓ **19 agent** performance metrics
- ✓ **Real-time KPIs**: CSAT, Revenue Impact, Churn Rate, etc.
- ✓ **Interactive charts, filters, and searches**
- ✓ **Export functionality** (CSV, PDF, Excel)

---

## File Structure

```
Ecommerce CX Intelligence Hub/
├── START.bat                           ← Run this! (Windows)
├── START.ps1                           ← Or this! (PowerShell)
├── server.py                           ← Python backend (do not edit)
├── ecommerce_cx_hub_v10 (3).html      ← Dashboard (do not edit)
├── navedas_cx_1000 (1).xlsx           ← Your data source
└── README.md                           ← This file
```

---

## Updating Your Data

When you update `navedas_cx_1000 (1).xlsx`:
1. **Stop** the server (close the command window)
2. **Restart** the server using `START.bat`
3. The dashboard will load your **updated data**

---

## Troubleshooting

### "Python not found"
- Install Python 3.8+: https://python.org
- Make sure to check "Add Python to PATH" during installation

### Port 8080 already in use
- Close any other applications using port 8080
- Or change `PORT = 8080` in `server.py` to `PORT = 8081`

### Data not showing
- Press `Ctrl+F5` in your browser (hard refresh)
- Check that the server shows: "Loaded 1000 tickets"

### Browser doesn't open automatically
- Manually open: **http://localhost:8080**

---

## API Endpoints

If you want to integrate with other tools:

- **HTML Dashboard**: `http://localhost:8080`
- **Data API**: `http://localhost:8080/api/data`

The API returns JSON with all tickets, agents, monthly data, and KPIs.

---

## Features

### Dashboard Sections
1. **CX Score Summary** - Key metrics at a glance
2. **Agent Performance** - Team CSAT and productivity
3. **CX Signal Intelligence** - Priority issues with ROI
4. **Ticket Intelligence** - 1,000 individual records with search/filter
5. **Board-Ready Briefing** - Executive summary

### Interactive Features
- ✓ Filter by category, status, sentiment
- ✓ Search tickets by ID, agent, issue
- ✓ View trends over time
- ✓ Drill into agent and team performance
- ✓ Export data to CSV/PDF/Excel

---

## Support

If you encounter any issues:
1. Run `diagnose.bat` to check system setup
2. Check the command window for error messages
3. Verify all files are present in this directory

---

**Last Updated**: March 2026
**Status**: Live & Ready to Use ✓
