#!/usr/bin/env python3
"""
Navedas CX Intelligence Hub - Live Data Server
Reads Excel data and serves dashboard via HTTP
"""

import json
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

EXCEL_FILE = Path(__file__).parent / "navedas_cx_1000 (1).xlsx"
HTML_FILE  = Path(__file__).parent / "ecommerce_cx_hub_v10 (3).html"
PORT = 8080

def load_data():
    """Load all Excel sheets and process into dashboard format"""
    print("Loading Excel data...")

    # Read all 4 sheets - skip title rows where they exist
    tickets_df  = pd.read_excel(EXCEL_FILE, sheet_name="Ticket Records", skiprows=1)
    monthly_df  = pd.read_excel(EXCEL_FILE, sheet_name="Monthly Summary", skiprows=1)
    signals_df  = pd.read_excel(EXCEL_FILE, sheet_name="Issue Intelligence", skiprows=1)
    agents_df   = pd.read_excel(EXCEL_FILE, sheet_name="Agent Performance", skiprows=1)

    # Normalize column names and convert numeric columns to numeric types
    for df in [tickets_df, monthly_df, signals_df, agents_df]:
        df.columns = df.columns.str.strip()

        # Convert common numeric columns to float where they exist
        numeric_cols = ["Tickets", "Loyalty", "Revenue", "Churn", "Resolved", "Pending",
                       "Escalated", "Neg Sent %", "Avg Score", "Avg Rev ($)", "Avg Res Hrs",
                       "Signals Flagged", "Priority", "Score", "Revenue Impact ($)", "CSAT %",
                       "vs 85%", "Net Rev Impact ($)"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

    # Build data structures
    all_tickets   = build_tickets(tickets_df)
    monthly_data  = build_monthly(monthly_df)
    agent_data    = build_agents(agents_df)
    spark_data    = build_sparks(tickets_df, monthly_df)
    kpis          = compute_kpis(tickets_df, monthly_df, agents_df, signals_df)
    teams         = compute_teams(agents_df, agent_data)

    print(f"  Loaded {len(all_tickets)} tickets")
    print(f"  Loaded {len(monthly_data)} months")
    print(f"  Loaded {len(agent_data)} agents")
    print("  Data processing complete")

    return {
        "all_tickets": all_tickets,
        "monthly_data": monthly_data,
        "agent_data": agent_data,
        "spark_data": spark_data,
        "kpis": kpis,
        "teams": teams
    }

def build_tickets(df):
    """Convert Ticket Records sheet to flat array format"""
    tickets = []
    for _, row in df.iterrows():
        pattern_flag = row.get("Pattern Flag", "—")
        if pd.isna(pattern_flag) or pattern_flag == "nan":
            pattern_flag = "—"

        # Revenue impact - handle both numeric and string formats
        rev_impact = row.get("Revenue Impact ($)", 0)
        if pd.isna(rev_impact):
            rev_impact = 0
        else:
            rev_impact = float(rev_impact)

        # Score as integer
        score = int(row.get("Score (1–100)", 50)) if not pd.isna(row.get("Score (1–100)")) else 50

        ticket = [
            str(row.get("Ticket ID", "")),                # [0]
            str(row.get("Date", "")),                     # [1]
            str(row.get("Month", "")),                    # [2]
            str(row.get("Category", "")),                 # [3]
            str(row.get("Sub-Issue", "")),                # [4]
            str(row.get("Status", "")),                   # [5]
            str(row.get("Agent", "")),                    # [6]
            str(row.get("Sentiment", "")),                # [7]
            score,                                        # [8]
            rev_impact,                                   # [9]
            str(pattern_flag)                             # [10]
        ]
        tickets.append(ticket)

    return tickets

def build_monthly(df):
    """Convert Monthly Summary sheet to object array"""
    monthly = []
    for _, row in df.iterrows():
        # Skip rows with non-numeric tickets (summary rows, empty rows)
        tickets_val = row.get("Tickets", None)
        try:
            tickets_int = int(float(tickets_val)) if not pd.isna(tickets_val) else 0
        except (ValueError, TypeError):
            continue  # Skip non-numeric rows

        if tickets_int == 0:
            continue  # Skip empty rows

        neg_pct = float(row.get("Neg Sent %", 0)) if not pd.isna(row.get("Neg Sent %")) else 0
        avg_rev = float(row.get("Avg Rev ($)", 0)) if not pd.isna(row.get("Avg Rev ($)")) else 0

        # Convert string columns to int safely
        def safe_int(val):
            try:
                return int(float(val)) if not pd.isna(val) else 0
            except (ValueError, TypeError):
                return 0

        month_obj = {
            "label": str(row.get("Month", "")),
            "total": safe_int(row.get("Tickets", 0)),
            "loyalty": safe_int(row.get("Loyalty", 0)),
            "revenue": safe_int(row.get("Revenue", 0)),
            "churn": safe_int(row.get("Churn", 0)),
            "resolved": int(row.get("Resolved", 0)) if not pd.isna(row.get("Resolved")) else 0,
            "pending": int(row.get("Pending", 0)) if not pd.isna(row.get("Pending")) else 0,
            "escalated": int(row.get("Escalated", 0)) if not pd.isna(row.get("Escalated")) else 0,
            "neg_pct": neg_pct,
            "avg_score": float(row.get("Avg Score", 50)) if not pd.isna(row.get("Avg Score")) else 50,
            "avg_rev": avg_rev,
            "signals": int(row.get("Signals Flagged", 0)) if not pd.isna(row.get("Signals Flagged")) else 0
        }
        monthly.append(month_obj)

    return monthly

def build_agents(df):
    """Convert Agent Performance sheet to object array"""
    agents = []

    def safe_int(val, default=0):
        try:
            return int(float(val)) if not pd.isna(val) else default
        except (ValueError, TypeError):
            return default

    def safe_float(val, default=50.0):
        try:
            return float(val) if not pd.isna(val) else default
        except (ValueError, TypeError):
            return default

    for _, row in df.iterrows():
        agent_name = str(row.get("Agent", "")).strip()
        # Skip header rows or empty rows
        if not agent_name or agent_name == "Agent" or agent_name.lower() == "agent":
            continue

        agent_obj = {
            "name": agent_name,
            "team": str(row.get("Team", "")),
            "tickets": safe_int(row.get("Tickets", 0)),
            "resolved": safe_int(row.get("Resolved", 0)),
            "escalated": safe_int(row.get("Escalated", 0)),
            "avg_score": safe_float(row.get("Avg Score", 50)),
            "csat": safe_int(row.get("CSAT %", 85), 85),
            "vs_target": safe_int(row.get("vs 85%", 0)),
            "status": str(row.get("Status", "On Target"))
        }
        agents.append(agent_obj)

    return agents

def build_sparks(tickets_df, monthly_df):
    """Build monthly CSAT sparklines per team"""
    months_ordered = monthly_df["Month"].tolist()
    spark = {"loyalty": [], "revenue": [], "churn": [], "general": []}

    # Map category to team
    category_to_team = {"Loyalty": "loyalty", "Revenue": "revenue", "Churn": "churn"}

    for month in months_ordered:
        month_tickets = tickets_df[tickets_df["Month"] == month]

        for category, team_key in category_to_team.items():
            team_tickets = month_tickets[month_tickets["Category"] == category]
            avg_score = team_tickets["Score (1–100)"].mean() if len(team_tickets) > 0 else 80
            spark[team_key].append(round(float(avg_score)))

        # General team = all tickets
        avg_gen = month_tickets["Score (1–100)"].mean() if len(month_tickets) > 0 else 80
        spark["general"].append(round(float(avg_gen)))

    return spark

def compute_kpis(tickets_df, monthly_df, agents_df, signals_df):
    """Compute all KPI values for dashboard headers"""

    # Filter agents_df to remove non-numeric rows and convert numeric columns
    agents_clean = agents_df.copy()
    agents_clean = agents_clean[pd.to_numeric(agents_clean["CSAT %"], errors='coerce').notna()]
    agents_clean["CSAT %"] = pd.to_numeric(agents_clean["CSAT %"], errors='coerce')

    # CSAT Score - average of all agents
    csat_score = agents_clean["CSAT %"].mean() if len(agents_clean) > 0 else 85
    csat_score = round(float(csat_score))

    # Revenue Saved - sum of abs(rev_impact) for resolved tickets
    resolved_tickets = tickets_df[tickets_df["Status"] == "Resolved"]
    revenue_saved = abs(resolved_tickets["Revenue Impact ($)"].sum()) / 1_000_000 if len(resolved_tickets) > 0 else 0
    revenue_saved = round(revenue_saved, 2)

    # Revenue at Risk - sum of abs(avg_rev) across months
    revenue_at_risk = abs(monthly_df["Avg Rev ($)"].sum()) / 1_000_000 if len(monthly_df) > 0 else 0
    revenue_at_risk = round(revenue_at_risk, 2)

    # Peak Churn % - max(churn/total * 100)
    monthly_df_copy = monthly_df.copy()
    # Convert to numeric, removing any non-numeric rows
    monthly_df_copy["Churn"] = pd.to_numeric(monthly_df_copy["Churn"], errors='coerce')
    monthly_df_copy["Tickets"] = pd.to_numeric(monthly_df_copy["Tickets"], errors='coerce')
    monthly_df_copy = monthly_df_copy.dropna(subset=["Churn", "Tickets"])

    if len(monthly_df_copy) > 0:
        monthly_df_copy["churn_pct"] = (monthly_df_copy["Churn"] / monthly_df_copy["Tickets"] * 100)
    else:
        monthly_df_copy["churn_pct"] = []
    peak_churn = monthly_df_copy["churn_pct"].max() if len(monthly_df_copy) > 0 else 6.1
    peak_churn = round(float(peak_churn), 1)

    # Latest churn for churn_reduced calculation
    latest_churn = monthly_df_copy.iloc[-1]["churn_pct"] if len(monthly_df_copy) > 0 else peak_churn
    churn_reduced = ((peak_churn - latest_churn) / peak_churn * 100) if peak_churn > 0 else 0
    churn_reduced = round(float(churn_reduced))

    # Loyalty Index - avg CSAT of Loyalty team
    loyalty_agents = agents_df[agents_df["Team"] == "Loyalty"]
    loyalty_index = loyalty_agents["CSAT %"].mean() if len(loyalty_agents) > 0 else 77
    loyalty_index = round(float(loyalty_index))

    # Customer LTV - total rev impact / resolved tickets
    if len(resolved_tickets) > 0:
        customer_ltv = abs(resolved_tickets["Revenue Impact ($)"].sum()) / len(resolved_tickets)
    else:
        customer_ltv = 334
    customer_ltv = round(float(customer_ltv))

    # Win-back Rate - resolved churn / total churn
    churn_tickets = tickets_df[tickets_df["Category"] == "Churn"]
    resolved_churn = len(churn_tickets[churn_tickets["Status"] == "Resolved"])
    total_churn = len(churn_tickets)
    winback_rate = (resolved_churn / total_churn * 100) if total_churn > 0 else 21
    winback_rate = round(float(winback_rate))

    # Signals Count and Addressable Revenue from Issue Intelligence
    signals_count = len(signals_df) if not signals_df.empty else 6
    addressable_rev = abs(signals_df["Net Rev Impact ($)"].sum()) / 1_000_000 if len(signals_df) > 0 else 3.87
    addressable_rev = round(float(addressable_rev), 2)

    # Total records and refresh date
    total_records = len(tickets_df)
    latest_month = monthly_df.iloc[-1]["Month"] if len(monthly_df) > 0 else "Mar 2026"

    return {
        "loyalty_index": loyalty_index,
        "revenue_at_risk": revenue_at_risk,
        "peak_churn_pct": peak_churn,
        "customer_ltv": customer_ltv,
        "revenue_saved": revenue_saved,
        "winback_rate": winback_rate,
        "csat_score": csat_score,
        "csat_ring": float(csat_score) / 100.0,
        "signals_count": signals_count,
        "addressable_rev": addressable_rev,
        "churn_reduced_pct": churn_reduced,
        "total_records": total_records,
        "latest_month": str(latest_month),
        "refresh_date": "Mar 1, 2026"
    }

def compute_teams(agents_df, agent_data):
    """Compute team aggregations for team cards"""
    teams = {}
    team_map = {"Loyalty": "loyalty", "Revenue": "revenue", "Churn": "churn", "General": "general"}

    for team_name, team_key in team_map.items():
        team_agents = agents_df[agents_df["Team"] == team_name] if team_name != "General" else agents_df[~agents_df["Team"].isin(["Loyalty", "Revenue", "Churn"])]

        csat = team_agents["CSAT %"].mean() if len(team_agents) > 0 else 85
        tickets = team_agents["Tickets"].sum() if len(team_agents) > 0 else 0
        flags = len(team_agents[team_agents["vs 85%"] < 0]) if len(team_agents) > 0 else 0
        agent_count = len(team_agents)

        teams[team_key] = {
            "csat": round(float(csat)),
            "tickets": int(tickets),
            "flags": int(flags),
            "agent_count": int(agent_count)
        }

    return teams

class Handler(BaseHTTPRequestHandler):
    _data = None  # cached data loaded at startup

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_html()
        elif self.path == "/api/data":
            self.send_json(Handler._data)
        else:
            self.send_error(404)

    def send_html(self):
        content = HTML_FILE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # suppress access logs

def main():
    if not EXCEL_FILE.exists():
        print(f"ERROR: Excel file not found: {EXCEL_FILE}")
        return

    if not HTML_FILE.exists():
        print(f"ERROR: HTML file not found: {HTML_FILE}")
        return

    print(f"Navedas CX Intelligence Hub - Live Data Server")
    print(f"=" * 50)

    # Load and cache data
    Handler._data = load_data()

    print(f"\nServer starting...")
    print(f"  Open browser: http://localhost:{PORT}")
    print(f"  API endpoint: http://localhost:{PORT}/api/data")
    print(f"  Press Ctrl+C to stop\n")

    try:
        server = HTTPServer(("localhost", PORT), Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
