"""
import_data.py — One-time Excel → Supabase import
─────────────────────────────────────────────────
Usage:
  1. pip install supabase pandas openpyxl python-dotenv
  2. Create .env file in project root with:
       SUPABASE_URL=https://xxxx.supabase.co
       SUPABASE_SERVICE_KEY=eyJ...
  3. Run: python scripts/import_data.py
"""

import os, sys, math
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Excel file path
EXCEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'navedas_cx_1000 (1).xlsx')


def clean(val):
    """Convert NaN / numpy types to plain Python."""
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    if hasattr(val, 'item'):          # numpy scalar → Python
        return val.item()
    return val


def upsert_batch(table, records, conflict_col):
    """Upsert records in batches of 200."""
    for i in range(0, len(records), 200):
        batch = records[i:i + 200]
        supabase.table(table).upsert(batch, on_conflict=conflict_col).execute()
        print(f"  {table}: {min(i + 200, len(records))}/{len(records)}", end='\r')
    print()


# ── 1. Tickets ────────────────────────────────────────────────────
def import_tickets():
    print("Importing tickets...")
    df = pd.read_excel(EXCEL_PATH, sheet_name='Ticket Records', skiprows=1)
    df.columns = df.columns.str.strip()

    records = []
    for _, row in df.iterrows():
        flag = clean(row.get('Pattern Flag'))
        records.append({
            'ticket_id':      str(clean(row['Ticket ID'])),
            'date':           str(row['Date'].date()) if pd.notna(row.get('Date')) else None,
            'month':          clean(row.get('Month')),
            'category':       clean(row.get('Issue Category')),
            'sub_issue':      clean(row.get('Sub-Issue')),
            'status':         clean(row.get('Status')),
            'agent':          clean(row.get('Agent Name')),
            'sentiment':      clean(row.get('Sentiment')),
            'score':          clean(row.get('Score')),
            'revenue_impact': clean(row.get('Revenue Impact')),
            'pattern_flag':   '\u2014' if (flag is None or str(flag).strip() == '') else str(flag),
        })

    upsert_batch('tickets', records, 'ticket_id')
    print(f"  Done: {len(records)} tickets imported.")


# ── 2. Agent Performance ──────────────────────────────────────────
def import_agents():
    print("Importing agent performance...")
    df = pd.read_excel(EXCEL_PATH, sheet_name='Agent Performance')
    df.columns = df.columns.str.strip()

    records = []
    for _, row in df.iterrows():
        name = clean(row.get('Agent Name') or row.get('Name') or row.iloc[0])
        if not name:
            continue
        records.append({
            'agent_name': str(name),
            'team':       clean(row.get('Team')),
            'tickets':    int(clean(row.get('Tickets', 0)) or 0),
            'resolved':   int(clean(row.get('Resolved', 0)) or 0),
            'escalated':  int(clean(row.get('Escalated', 0)) or 0),
            'avg_score':  float(clean(row.get('Avg Score', 0)) or 0),
            'csat':       float(clean(row.get('CSAT', 0)) or 0),
            'vs_target':  float(clean(row.get('Vs Target', 0)) or 0),
            'status':     clean(row.get('Status')),
        })

    upsert_batch('agent_performance', records, 'agent_name')
    print(f"  Done: {len(records)} agents imported.")


# ── 3. Monthly Summary ────────────────────────────────────────────
def import_monthly():
    print("Importing monthly summary...")
    df = pd.read_excel(EXCEL_PATH, sheet_name='Monthly Summary')
    df.columns = df.columns.str.strip()

    records = []
    for _, row in df.iterrows():
        label = clean(row.get('Month') or row.get('Label') or row.iloc[0])
        if not label:
            continue
        records.append({
            'label':     str(label),
            'total':     int(clean(row.get('Total', 0)) or 0),
            'loyalty':   int(clean(row.get('Loyalty', 0)) or 0),
            'revenue':   int(clean(row.get('Revenue', 0)) or 0),
            'churn':     int(clean(row.get('Churn', 0)) or 0),
            'resolved':  int(clean(row.get('Resolved', 0)) or 0),
            'pending':   int(clean(row.get('Pending', 0)) or 0),
            'escalated': int(clean(row.get('Escalated', 0)) or 0),
            'neg_pct':   float(clean(row.get('Neg Pct', 0) or row.get('Negative %', 0)) or 0),
            'avg_score': float(clean(row.get('Avg Score', 0)) or 0),
            'avg_rev':   float(clean(row.get('Avg Rev', 0) or row.get('Avg Revenue', 0)) or 0),
            'signals':   int(clean(row.get('Signals', 0)) or 0),
        })

    upsert_batch('monthly_summary', records, 'label')
    print(f"  Done: {len(records)} months imported.")


if __name__ == '__main__':
    print(f"\nConnecting to Supabase: {SUPABASE_URL}\n")
    import_tickets()
    import_agents()
    import_monthly()
    print("\nAll data imported successfully!")
    print("Next: Create user accounts in Supabase Auth dashboard,")
    print("      then run: python scripts/set_user_role.py")
