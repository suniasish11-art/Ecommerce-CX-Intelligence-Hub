"""
import_data.py — One-time Excel -> Supabase import
Uses requests only (no supabase SDK) - works on Python 3.14
"""
import os, sys, math, json
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file")
    sys.exit(1)

HEADERS = {
    'apikey':        SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type':  'application/json',
    'Prefer':        'resolution=merge-duplicates',
}

EXCEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'navedas_cx_1000 (1).xlsx')

def clean(val):
    if val is None: return None
    if isinstance(val, float) and math.isnan(val): return None
    if hasattr(val, 'item'): return val.item()
    return val

def upsert(table, records):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    for i in range(0, len(records), 200):
        batch = records[i:i+200]
        r = requests.post(url, headers=HEADERS, data=json.dumps(batch))
        if r.status_code not in (200, 201):
            print(f"\n  ERROR {table}: {r.status_code} {r.text[:300]}")
            return False
        print(f"  {table}: {min(i+200, len(records))}/{len(records)}", end='\r')
    print()
    return True

def import_tickets():
    print("Importing tickets...")
    df = pd.read_excel(EXCEL_PATH, sheet_name='Ticket Records', skiprows=1)
    df.columns = df.columns.str.strip()
    records = []
    for _, row in df.iterrows():
        flag = clean(row.get('Pattern Flag'))
        records.append({
            'ticket_id':      str(clean(row['Ticket ID'])),
            'date':           str(clean(row.get('Date'))) if pd.notna(row.get('Date')) else None,
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
    if upsert('tickets', records):
        print(f"  Done: {len(records)} tickets.")

def import_agents():
    print("Importing agents...")
    df = pd.read_excel(EXCEL_PATH, sheet_name='Agent Performance')
    df.columns = df.columns.str.strip()
    records = []
    for _, row in df.iterrows():
        name = clean(row.get('Agent Name') or row.get('Name') or row.iloc[0])
        if not name: continue
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
    if upsert('agent_performance', records):
        print(f"  Done: {len(records)} agents.")

def import_monthly():
    print("Importing monthly summary...")
    df = pd.read_excel(EXCEL_PATH, sheet_name='Monthly Summary')
    df.columns = df.columns.str.strip()
    records = []
    for _, row in df.iterrows():
        label = clean(row.get('Month') or row.get('Label') or row.iloc[0])
        if not label: continue
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
    if upsert('monthly_summary', records):
        print(f"  Done: {len(records)} months.")

if __name__ == '__main__':
    print(f"\nConnecting to: {SUPABASE_URL}\n")
    import_tickets()
    import_agents()
    import_monthly()
    print("\nAll data imported successfully!")
    print("Next: python scripts/set_user_role.py <email> <role>")
