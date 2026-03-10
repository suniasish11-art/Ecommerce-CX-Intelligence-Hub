"""
Build a self-contained static HTML with data embedded.
No backend needed - works on Netlify directly.
"""
import pandas as pd
import json
import re

print("Reading Excel data...")
xl = 'navedas_cx_1000 (1).xlsx'

# --- Ticket Records ---
tickets_df = pd.read_excel(xl, sheet_name='Ticket Records', skiprows=1)
tickets_df.columns = tickets_df.columns.str.strip()
for col in ['Score (1\u20131\u2070\u2070)', 'Score (1-100)', 'Rev Impact ($)']:
    if col in tickets_df.columns:
        tickets_df[col] = pd.to_numeric(tickets_df[col], errors='coerce')

# Detect score column
score_col = next((c for c in tickets_df.columns if 'score' in c.lower()), None)
rev_col   = next((c for c in tickets_df.columns if 'rev' in c.lower() and 'impact' in c.lower()), None)
flag_col  = next((c for c in tickets_df.columns if 'pattern' in c.lower() or 'flag' in c.lower()), None)

ALL_TICKETS = []
for _, r in tickets_df.iterrows():
    row = [
        str(r.get('Ticket ID', '')),
        str(r.get('Date', '')).split(' ')[0].replace('NaT',''),
        str(r.get('Month', '')),
        str(r.get('Category', '')),
        str(r.get('Sub-Issue', '')),
        str(r.get('Status', '')),
        str(r.get('Agent', '')),
        str(r.get('Sentiment', '')),
        float(r[score_col]) if score_col and pd.notna(r[score_col]) else 0,
        float(r[rev_col])   if rev_col   and pd.notna(r[rev_col])   else 0,
        str(r[flag_col]) if flag_col and pd.notna(r[flag_col]) and str(r[flag_col]).strip() else '\u2014'
    ]
    ALL_TICKETS.append(row)

print(f"  Tickets loaded: {len(ALL_TICKETS)}")

# --- Monthly Summary ---
monthly_df = pd.read_excel(xl, sheet_name='Monthly Summary', skiprows=1)
monthly_df.columns = monthly_df.columns.str.strip()
for col in monthly_df.columns[1:]:
    monthly_df[col] = pd.to_numeric(monthly_df[col], errors='coerce')

MONTHLY_DATA = []
for _, r in monthly_df.iterrows():
    if pd.isna(r.get('Tickets', None)):
        continue
    MONTHLY_DATA.append({
        'label':    str(r.get('Month', '')),
        'total':    int(r.get('Tickets', 0) or 0),
        'loyalty':  int(r.get('Loyalty', 0) or 0),
        'revenue':  int(r.get('Revenue', 0) or 0),
        'churn':    int(r.get('Churn', 0) or 0),
        'resolved': int(r.get('Resolved', 0) or 0),
        'pending':  int(r.get('Pending', 0) or 0),
        'escalated':int(r.get('Escalated', 0) or 0),
        'neg_pct':  float(r.get('Neg Sent %', 0) or 0),
        'avg_score':float(r.get('Avg Score', 0) or 0),
        'avg_rev':  float(r.get('Avg Rev ($)', 0) or 0),
        'signals':  int(r.get('Signals Flagged', 0) or 0),
    })

print(f"  Monthly rows loaded: {len(MONTHLY_DATA)}")

# --- Agent Performance ---
agents_df = pd.read_excel(xl, sheet_name='Agent Performance', skiprows=1)
agents_df.columns = agents_df.columns.str.strip()

def safe_int(v):
    try:
        n = pd.to_numeric(v, errors='coerce')
        return int(n) if pd.notna(n) else 0
    except:
        return 0

def safe_float(v):
    try:
        n = pd.to_numeric(v, errors='coerce')
        return float(n) if pd.notna(n) else 0.0
    except:
        return 0.0

AGENT_DATA = []
for _, r in agents_df.iterrows():
    agent_name = str(r.get('Agent', '')).strip()
    if not agent_name or agent_name == 'Agent' or agent_name == 'nan':
        continue
    AGENT_DATA.append({
        'name':      agent_name,
        'team':      str(r.get('Team', '')),
        'tickets':   safe_int(r.get('Tickets', 0)),
        'resolved':  safe_int(r.get('Resolved', 0)),
        'escalated': safe_int(r.get('Escalated', 0)),
        'avg_score': safe_float(r.get('Avg Score', 0)),
        'csat':      safe_float(r.get('CSAT %', 0)),
        'vs_target': safe_float(r.get('Vs Target', 0)),
        'status':    str(r.get('Status', '')),
    })

print(f"  Agents loaded: {len(AGENT_DATA)}")

# --- Spark data from ticket records ---
SPARK_DATA = {'loyalty': [], 'revenue': [], 'churn': [], 'general': []}
if score_col:
    months = [m['label'] for m in MONTHLY_DATA]
    for cat in ['Loyalty', 'Revenue', 'Churn', 'General']:
        key = cat.lower()
        scores = []
        for m in months:
            sub = tickets_df[(tickets_df['Category'] == cat) & (tickets_df['Month'] == m)]
            scores.append(round(sub[score_col].mean(), 1) if len(sub) > 0 else 0)
        SPARK_DATA[key] = scores

# --- KPIs ---
all_scores = [r[8] for r in ALL_TICKETS if r[8] > 0]
avg_csat = sum(all_scores) / len(all_scores) if all_scores else 0

loyalty_scores = [r[8] for r in ALL_TICKETS if r[3] == 'Loyalty' and r[8] > 0]
loyalty_index = sum(loyalty_scores) / len(loyalty_scores) if loyalty_scores else 0

churn_tickets = [r for r in ALL_TICKETS if r[3] == 'Churn']
resolved_churn = [r for r in churn_tickets if r[5] == 'Resolved']
winback_rate = (len(resolved_churn) / len(churn_tickets) * 100) if churn_tickets else 0

agent_csats = [a['csat'] for a in AGENT_DATA if a['csat'] > 0]
csat_score = sum(agent_csats) / len(agent_csats) if agent_csats else avg_csat

rev_impacts = [abs(r[9]) for r in ALL_TICKETS if r[5] == 'Resolved' and r[9] != 0]
revenue_saved = sum(rev_impacts) / 1_000_000

all_rev = [abs(r[9]) for r in ALL_TICKETS if r[9] != 0]
revenue_at_risk = sum(all_rev) / 1_000_000

monthly_churn_pcts = [(m['churn'] / m['total'] * 100) if m['total'] > 0 else 0 for m in MONTHLY_DATA]
peak_churn_pct = max(monthly_churn_pcts) if monthly_churn_pcts else 0
latest_churn_pct = monthly_churn_pcts[-1] if monthly_churn_pcts else 0
churn_reduced = ((peak_churn_pct - latest_churn_pct) / peak_churn_pct * 100) if peak_churn_pct > 0 else 0

signals_df = pd.read_excel(xl, sheet_name='Issue Intelligence', skiprows=1)
signals_count = len(signals_df)

KPIS = {
    'loyalty_index':   round(loyalty_index, 1),
    'revenue_at_risk': round(revenue_at_risk, 2),
    'peak_churn_pct':  round(peak_churn_pct, 1),
    'customer_ltv':    2847,
    'revenue_saved':   round(revenue_saved, 2),
    'winback_rate':    round(winback_rate, 1),
    'csat_score':      round(csat_score, 1),
    'csat_ring':       round(csat_score / 100, 3),
    'signals_count':   signals_count,
    'churn_reduced_pct': round(churn_reduced, 1),
    'total_records':   len(ALL_TICKETS),
    'refresh_date':    'Live',
}

# --- Teams ---
def team_stats(cat):
    t = [r for r in ALL_TICKETS if r[3] == cat]
    sc = [r[8] for r in t if r[8] > 0]
    flags = [r for r in t if r[10] != '\u2014']
    agents = set(r[6] for r in t)
    return {
        'csat':        round(sum(sc)/len(sc), 1) if sc else 0,
        'tickets':     len(t),
        'flags':       len(flags),
        'agent_count': len(agents),
    }

TEAMS = {
    'loyalty': team_stats('Loyalty'),
    'revenue': team_stats('Revenue'),
    'churn':   team_stats('Churn'),
    'general': team_stats('General'),
}

print(f"  KPIs computed. CSAT: {KPIS['csat_score']}%")

# --- Executive Briefing (real values) ---
from datetime import date

# Churn reduction: peak month vs latest month
valid_monthly = [m for m in MONTHLY_DATA if m['total'] > 0]
churn_pcts = [(m['churn'] / m['total'] * 100, m['label']) for m in valid_monthly]
peak_churn_val, peak_churn_month = max(churn_pcts, key=lambda x: x[0])
latest_churn_val, latest_month_label = churn_pcts[-1]
churn_reduced_real = round((peak_churn_val - latest_churn_val) / peak_churn_val * 100)

# Revenue format
def fmt_money(v):
    if abs(v) >= 1:
        return f'${v:.2f}M'
    return f'${round(abs(v)*1000)}K'

rev_protected_fmt = fmt_money(revenue_saved)
rev_at_risk_fmt   = fmt_money(revenue_at_risk)

# CSAT
industry_avg = 71
csat_pts = round(csat_score - industry_avg)
csat_pct  = round(csat_score)

# Worst performing agent
worst_agent = min(AGENT_DATA, key=lambda a: a['csat'] if a['csat'] > 0 else 999)
worst_name  = worst_agent['name']
worst_csat  = round(worst_agent['csat'])
csat_gap    = round(85 - worst_csat)

# At-risk tickets this month
at_risk = [r for r in ALL_TICKETS if r[5] in ('Pending','Escalated')]
at_risk_count = len(at_risk)

# General queue low CSAT
general_low = [r for r in ALL_TICKETS if r[3] == 'General' and r[8] > 0 and r[8] < 75]
general_low_count = len(general_low)

# Today's date
today_str = date.today().strftime('%B %Y')  # e.g. "March 2026"

# Months span of data
months_span = len(valid_monthly)

EXEC_BRIEF = {
    'churn_reduced':      churn_reduced_real,
    'peak_churn_pct':     round(peak_churn_val, 1),
    'latest_churn_pct':   round(latest_churn_val, 1),
    'peak_churn_month':   peak_churn_month,
    'latest_month':       latest_month_label,
    'rev_protected':      rev_protected_fmt,
    'rev_at_risk':        rev_at_risk_fmt,
    'months_span':        months_span,
    'csat_pct':           csat_pct,
    'industry_avg':       industry_avg,
    'csat_pts':           csat_pts,
    'worst_agent':        worst_name,
    'worst_csat':         worst_csat,
    'csat_gap':           csat_gap,
    'at_risk_count':      at_risk_count,
    'general_low_count':  general_low_count,
    'today':              today_str,
}

print(f"  Exec Brief: Churn -{churn_reduced_real}% | Rev {rev_protected_fmt} protected | CSAT +{csat_pts}pts | Worst: {worst_name} {worst_csat}%")

# --- Signal Intelligence (real values) ---
def fmt_k(v):
    if abs(v) >= 1_000_000: return f'${abs(v)/1_000_000:.1f}M'
    if abs(v) >= 1_000:     return f'${round(abs(v)/1000)}K'
    return f'${round(abs(v))}'

# Reload tickets with sub-issue for signal calcs
tickets_df2 = pd.read_excel(xl, sheet_name='Ticket Records', skiprows=1)
tickets_df2.columns = tickets_df2.columns.str.strip()
tickets_df2[score_col] = pd.to_numeric(tickets_df2[score_col], errors='coerce')
tickets_df2[rev_col]   = pd.to_numeric(tickets_df2[rev_col],   errors='coerce')

churn_t   = tickets_df2[tickets_df2['Category']=='Churn']
revenue_t = tickets_df2[tickets_df2['Category']=='Revenue']
loyalty_t = tickets_df2[tickets_df2['Category']=='Loyalty']

# Signal 1 - Churn Driver
s1_count     = len(churn_t)
s1_avg_ltv   = round(churn_t[rev_col].abs().mean())
s1_total_rev = fmt_k(churn_t[rev_col].abs().sum())
s1_neg       = len(churn_t[churn_t['Sentiment']=='Negative'])
s1_peak_pct  = round(peak_churn_val, 1)
s1_latest    = round(latest_churn_val, 1)
s1_peak_mon  = peak_churn_month

# Signal 2 - Revenue Leak
s2_count     = len(revenue_t)
s2_total_rev = fmt_k(revenue_t[rev_col].abs().sum())
s2_neg       = len(revenue_t[revenue_t['Sentiment']=='Negative'])
promo_t      = tickets_df2[tickets_df2['Sub-Issue'].str.contains('promo|discount', case=False, na=False)]
refund_t     = tickets_df2[tickets_df2['Sub-Issue'].str.contains('refund|return', case=False, na=False)]
s2_promo     = len(promo_t)
s2_refund    = len(refund_t)

# Signal 3 - Loyalty
s3_count     = len(loyalty_t)
s3_neg       = len(loyalty_t[loyalty_t['Sentiment']=='Negative'])
s3_avg_score = round(loyalty_t[score_col].mean(), 1)
s3_rev       = fmt_k(loyalty_t[rev_col].abs().sum())

# Signal 4 - Billing/Ops
billing_t   = tickets_df2[tickets_df2['Sub-Issue'].str.contains('billing|overcharge|duplicate|charge', case=False, na=False)]
if len(billing_t) < 10:
    billing_t = tickets_df2[(tickets_df2[rev_col] < -50) & (tickets_df2['Category']=='Revenue')]
s4_count    = len(billing_t)
s4_avg      = round(billing_t[rev_col].abs().mean())
s4_total    = fmt_k(billing_t[rev_col].abs().sum())

# Signal 5 - Agent Gap
best_agent  = max(AGENT_DATA, key=lambda a: a['csat'])
s5_worst    = worst_name
s5_wcsat    = worst_csat
s5_gap      = csat_gap
s5_tickets  = worst_agent['tickets']
s5_esc_rate = round(worst_agent['escalated'] / worst_agent['tickets'] * 100, 1) if worst_agent['tickets'] > 0 else 0
s5_team_avg = round(sum(a['csat'] for a in AGENT_DATA if a['csat'] > 0) / len([a for a in AGENT_DATA if a['csat'] > 0]))
s5_team_esc = round(sum(a['escalated'] for a in AGENT_DATA) / sum(a['tickets'] for a in AGENT_DATA) * 100, 1)
s5_best     = best_agent['name']
s5_bcsat    = round(best_agent['csat'])
s5_rev_risk = fmt_k(s5_tickets * s1_avg_ltv * 0.15)  # 15% revenue at risk from low CSAT agent

# Signal 6 - Win-Back
resolved_churn_t = churn_t[churn_t['Status']=='Resolved']
pending_churn_t  = churn_t[churn_t['Status'].isin(['Pending','Escalated'])]
s6_resolved   = len(resolved_churn_t)
s6_pending    = len(pending_churn_t)
s6_rate       = round(s6_resolved / s1_count * 100)
s6_rev        = fmt_k(pending_churn_t[rev_col].abs().sum())

# Header badge
total_addressable = fmt_k(tickets_df2[rev_col].abs().sum())
total_flagged     = s1_count + s2_count  # churn + revenue as active signal tickets

print(f"  Signals: Churn={s1_count} | Rev={s2_count} | Loyalty={s3_count} | Billing={s4_count} | Agent={s5_worst} | WinBack={s6_resolved}")

# --- Embed into HTML ---
print("Building static HTML...")
with open('ecommerce_cx_hub_v10 (3).html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the API fetch block with embedded data
INJECT = f"""
  // Embedded data (no backend needed)
  var MONTHLY_DATA = {json.dumps(MONTHLY_DATA)};
  var AGENT_DATA   = {json.dumps(AGENT_DATA)};
  var ALL_TICKETS  = {json.dumps(ALL_TICKETS)};
  var SPARK_DATA   = {json.dumps(SPARK_DATA)};
  var _KPIS        = {json.dumps(KPIS)};
  var _TEAMS       = {json.dumps(TEAMS)};
  var _EXEC        = {json.dumps(EXEC_BRIEF)};
"""

# Replace the API_BASE_URL block and inject static data
api_pattern = r'var API_BASE_URL\s*=\s*\(function\(\)\{[\s\S]*?\}\)\(\);'
inject_str = INJECT.strip()
html = re.sub(api_pattern, lambda m: inject_str, html)

# Replace the window.addEventListener fetch call with static data loader
fetch_pattern = r"(window\.addEventListener\('load',\s*function\(\)\s*\{)([\s\S]*?)(fetch\(API_BASE_URL[\s\S]*?\.catch[\s\S]*?\}\);)"

def replace_fetch(m):
    return m.group(1) + """
    // Use embedded data directly
    MONTHLY_DATA = window.MONTHLY_DATA || MONTHLY_DATA;
    AGENT_DATA   = window.AGENT_DATA   || AGENT_DATA;
    ALL_TICKETS  = window.ALL_TICKETS  || ALL_TICKETS;
    SPARK_DATA   = window.SPARK_DATA   || SPARK_DATA;
    applyKPIs(_KPIS);
    applyTeams(_TEAMS);
    animateCounters();
    animateRing(_KPIS.csat_ring);
    applyExecBrief(_EXEC);
    _filtered = ALL_TICKETS.slice();
    renderTable();
    setTimeout(drawAllSparklines, 200);
    setTimeout(function(){ setCanvasDimensions(); if(_chartsOpen){ drawLineChart(); drawRevChart(); }}, 300);
  """

html = re.sub(fetch_pattern, replace_fetch, html)

# --- Replace hardcoded Executive Briefing section with real data ---
e = EXEC_BRIEF
new_section_e = f'''    <div class="section-card" id="section-e" style="animation-delay:.48s">
      <div class="section-head">
        <div class="section-title">
          Board-Ready Briefing — Auto-Generated
          <span class="slb slb-green">Executive Summary</span>
          <span class="slb slb-blue">GTM Asset</span>
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          <span class="freshness">Data as of: <strong id="exec-date">{e["today"]}</strong></span>
          <button class="btn-export-log" onclick="triggerExport('Executive Briefing PDF','exec')">📋 Export PDF <span style="font-size:9px;opacity:.7">· Logged</span></button>
        </div>
      </div>
      <div class="exec-grid">
        <div class="exec-kpi"><div class="exec-kpi-icon">📉</div><div class="metric-info"><div class="metric-label">Churn Reduced Since {e["peak_churn_month"]} Peak</div><div class="metric-sub">{e["peak_churn_pct"]}% → {e["latest_churn_pct"]}% {e["latest_month"]} · Navedas interventions</div></div><div class="exec-kpi-val" id="exec-churn-val">{e["churn_reduced"]}%</div></div>
        <div class="exec-kpi"><div class="exec-kpi-icon">💰</div><div class="metric-info"><div class="metric-label">Revenue Protected by CX Intelligence</div><div class="metric-sub">{e["months_span"]}-month · discount + retention + billing</div></div><div class="exec-kpi-val" id="exec-rev-val">{e["rev_protected"]}</div></div>
        <div class="exec-kpi"><div class="exec-kpi-icon">⭐</div><div class="metric-info"><div class="metric-label">CSAT vs Industry Average</div><div class="metric-sub">{e["csat_pct"]}% vs {e["industry_avg"]}% industry · Outperforming benchmark</div></div><div class="exec-kpi-val" id="exec-csat-val">+{e["csat_pts"]}pts</div></div>
      </div>
      <div class="exec-rec">
        <div class="exec-rec-lbl">🎯 Priority Recommendation — {e["today"]}</div>
        <div class="exec-rec-txt" id="exec-rec-txt">Deploy Navedas retention playbook on the <strong>{e["at_risk_count"]} at-risk accounts</strong> identified this month (Pending + Escalated tickets). Estimated impact: <strong>−{min(18, e["churn_reduced"])}% churn rate, revenue at risk {e["rev_at_risk"]} recoverable within 90 days</strong>. Secondary action: initiate {e["worst_agent"]} coaching plan to close the {e["csat_gap"]}pt CSAT gap on {e["general_low_count"]} General queue tickets.</div>
      </div>
      <div class="exec-actions">
        <button class="btn-copy" onclick="copyBriefing()">📋 Copy Briefing</button>
        <button class="btn-share" onclick="shareReport()">📤 Share Dashboard</button>
        <span class="watermark">Powered by Navedas Intelligence · Confidential · {e["today"]}</span>
      </div>
    </div><!-- /E -->'''

old_section_e_pattern = r'<div class="section-card" id="section-e"[\s\S]*?</div><!-- /E -->'
html = re.sub(old_section_e_pattern, lambda m: new_section_e, html)

# --- Replace hardcoded Signal Intelligence section with real data ---
new_section_c = f'''    <div class="section-card" id="section-c" style="animation-delay:.24s">
      <div class="section-head">
        <div class="section-title">
          CX Signal Intelligence → ROI Action Cards
          <span class="slb slb-red">6 Active Signals</span>
          <span class="slb slb-amber">{total_addressable} Addressable · {total_flagged} Detected</span>
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          <span class="freshness">Data as of: <strong>{e["today"]}</strong></span>
          <button class="btn-export-log" onclick="triggerExport('Signal Intelligence','signals')">📋 Export <span style="font-size:9px;opacity:.7">· Logged</span></button>
        </div>
      </div>
      <div class="filter-row">
        <div class="fc on" id="c-all">All Signals</div>
        <div class="fc" data-ccat="churn">📉 Churn</div>
        <div class="fc" data-ccat="revenue">💰 Revenue</div>
        <div class="fc" data-ccat="loyalty">🎁 Loyalty</div>
        <div class="fc" data-ccat="ops">⚙️ Operations</div>
        <button class="btn-reset" onclick="resetSignals()">Reset</button>
      </div>
      <div class="signal-grid" id="signal-grid">

        <div class="signal-card" data-category="churn">
          <div class="signal-header" onclick="toggleSignal(this)">
            <div class="signal-num sn-cr">1</div>
            <div class="signal-htxt">
              <div class="signal-title">Churn Driver — Price &amp; Loyalty Disconnect</div>
              <span class="sp-cr">🔴 Critical · Priority 98</span>
            </div>
            <span class="sc-badge cr">98</span><span class="signal-chevron">▼</span>
          </div>
          <div class="signal-body">
            <div class="s-sub">Customer Signals</div>
            <div class="s-box">
              <div class="s-item">{s1_count} churn tickets — subscription cost no longer justified after Q1 2025</div>
              <div class="s-item">Peak churn rate hit {s1_peak_pct}% in {s1_peak_mon} ({s1_neg} negative sentiment tickets)</div>
              <div class="s-item">Cancel intent expressed; avg revenue lost per customer ${s1_avg_ltv}</div>
            </div>
            <div class="s-sub">KPI Impact</div>
            <div style="font-size:11px;color:var(--text-dark);line-height:1.5;margin-bottom:8px">Churn peaked at {s1_peak_pct}% in {s1_peak_mon}, now at {s1_latest}%. {s1_count} tickets. Avg revenue lost ${s1_avg_ltv}/customer. Total at risk: {s1_total_rev}.</div>
            <div class="s-roi"><div class="s-roi-lbl">ROI Action</div><div class="s-roi-txt">Proactive retention playbook: price-sensitive cohort offer; loyalty upgrade trigger; extend pause to 60 days.</div></div>
            <div class="roi-calc"><div class="roi-calc-lbl">📐 Your ROI Calculator</div><div class="roi-calc-row"><input type="number" placeholder="Your monthly customers" id="ri-1" min="100"/><button onclick="calcROI(1)">Calculate</button></div><div class="roi-result" id="rr-1"></div></div>
            <div class="s-foot"><span class="s-uplift">↑ −15–20% Churn | {s1_total_rev} LTV recovered</span><button class="btn-share-sig" onclick="shareSignal(1)">📤 Share</button></div>
          </div>
        </div>

        <div class="signal-card" data-category="revenue">
          <div class="signal-header" onclick="toggleSignal(this)">
            <div class="signal-num sn-cr">2</div>
            <div class="signal-htxt">
              <div class="signal-title">Revenue Leak — Discount &amp; Refund Abuse</div>
              <span class="sp-cr">🔴 Critical · Priority 96</span>
            </div>
            <span class="sc-badge cr">96</span><span class="signal-chevron">▼</span>
          </div>
          <div class="signal-body">
            <div class="s-sub">Customer Signals</div>
            <div class="s-box">
              <div class="s-item">{s2_promo} promo/discount abuse tickets detected across {s2_count} revenue cases</div>
              <div class="s-item">{s2_refund} refund &amp; return disputes — policy enforcement gaps identified</div>
              <div class="s-item">{s2_neg} tickets with negative sentiment indicating unresolved financial friction</div>
            </div>
            <div class="s-sub">KPI Impact</div>
            <div style="font-size:11px;color:var(--text-dark);line-height:1.5;margin-bottom:8px">{s2_count} revenue tickets. Total financial exposure: {s2_total_rev}. Promo abuse and refund gaps driving majority of losses.</div>
            <div class="s-roi"><div class="s-roi-lbl">ROI Action</div><div class="s-roi-txt">Discount governance engine: single-code enforcement; expiry validation at checkout; automated finance anomaly alerts.</div></div>
            <div class="roi-calc"><div class="roi-calc-lbl">📐 Your ROI Calculator</div><div class="roi-calc-row"><input type="number" placeholder="Monthly revenue ($)" id="ri-2" min="1000"/><button onclick="calcROI(2)">Calculate</button></div><div class="roi-result" id="rr-2"></div></div>
            <div class="s-foot"><span class="s-uplift">↑ −2–4% Revenue Leak | {s2_total_rev} savings</span><button class="btn-share-sig" onclick="shareSignal(2)">📤 Share</button></div>
          </div>
        </div>

        <div class="signal-card" data-category="loyalty">
          <div class="signal-header" onclick="toggleSignal(this)">
            <div class="signal-num sn-hi">3</div>
            <div class="signal-htxt">
              <div class="signal-title">Loyalty Programme Gaps &amp; Member Confusion</div>
              <span class="sp-hi">🟡 High · Priority 92</span>
            </div>
            <span class="sc-badge hi">92</span><span class="signal-chevron">▼</span>
          </div>
          <div class="signal-body">
            <div class="s-sub">Customer Signals</div>
            <div class="s-box">
              <div class="s-item">{s3_count} loyalty tickets — points expiry, tier downgrades, referral credit failures</div>
              <div class="s-item">{s3_neg} negative sentiment tickets indicating programme trust erosion</div>
              <div class="s-item">Avg loyalty CSAT score: {s3_avg_score}/100 — below overall team target of 85</div>
            </div>
            <div class="s-sub">KPI Impact</div>
            <div style="font-size:11px;color:var(--text-dark);line-height:1.5;margin-bottom:8px">{s3_count} loyalty tickets. Revenue exposure: {s3_rev}. Avg score {s3_avg_score}/100 driving repurchase rate decline.</div>
            <div class="s-roi"><div class="s-roi-lbl">ROI Action</div><div class="s-roi-txt">Automated 7-day expiry alerts; transparent tier criteria; CRM referral tracking fix.</div></div>
            <div class="roi-calc"><div class="roi-calc-lbl">📐 Your ROI Calculator</div><div class="roi-calc-row"><input type="number" placeholder="Loyalty programme members" id="ri-3" min="100"/><button onclick="calcROI(3)">Calculate</button></div><div class="roi-result" id="rr-3"></div></div>
            <div class="s-foot"><span class="s-uplift">↑ +3–5% Retention | {s3_rev} LTV uplift</span><button class="btn-share-sig" onclick="shareSignal(3)">📤 Share</button></div>
          </div>
        </div>

        <div class="signal-card" data-category="revenue">
          <div class="signal-header" onclick="toggleSignal(this)">
            <div class="signal-num sn-hi">4</div>
            <div class="signal-htxt">
              <div class="signal-title">Revenue Ops — Overcharge &amp; Billing Errors</div>
              <span class="sp-hi">🟡 High · Priority 88</span>
            </div>
            <span class="sc-badge hi">88</span><span class="signal-chevron">▼</span>
          </div>
          <div class="signal-body">
            <div class="s-sub">Customer Signals</div>
            <div class="s-box">
              <div class="s-item">{s4_count} billing-related tickets — overcharges, duplicate charges, refund delays</div>
              <div class="s-item">Average incident value: ${s4_avg} per billing dispute</div>
              <div class="s-item">Total billing exposure: {s4_total} across all affected customers</div>
            </div>
            <div class="s-sub">KPI Impact</div>
            <div style="font-size:11px;color:var(--text-dark);line-height:1.5;margin-bottom:8px">{s4_count} billing incidents averaging ${s4_avg}/case. Each incident costs direct refund + CX handling time. Total: {s4_total}.</div>
            <div class="s-roi"><div class="s-roi-lbl">ROI Action</div><div class="s-roi-txt">Payment reconciliation engine; duplicate charge detection; SLA-enforced refund pipeline.</div></div>
            <div class="roi-calc"><div class="roi-calc-lbl">📐 Your ROI Calculator</div><div class="roi-calc-row"><input type="number" placeholder="Monthly transactions" id="ri-4" min="100"/><button onclick="calcROI(4)">Calculate</button></div><div class="roi-result" id="rr-4"></div></div>
            <div class="s-foot"><span class="s-uplift">↑ −3% Billing Errors | {s4_total} cost saving</span><button class="btn-share-sig" onclick="shareSignal(4)">📤 Share</button></div>
          </div>
        </div>

        <div class="signal-card" data-category="ops">
          <div class="signal-header" onclick="toggleSignal(this)">
            <div class="signal-num sn-me">5</div>
            <div class="signal-htxt">
              <div class="signal-title">Agent Gap — {s5_worst} Coaching Required</div>
              <span class="sp-me">🟢 Medium · Priority 85</span>
            </div>
            <span class="sc-badge me">85</span><span class="signal-chevron">▼</span>
          </div>
          <div class="signal-body">
            <div class="s-sub">Performance Signals</div>
            <div class="s-box">
              <div class="s-item">{s5_worst} CSAT {s5_wcsat}% vs team avg {s5_team_avg}% — {s5_gap}pt gap across {s5_tickets} tickets</div>
              <div class="s-item">Escalation rate {s5_esc_rate}% vs team avg {s5_team_esc}%</div>
              <div class="s-item">Top performer: {s5_best} at {s5_bcsat}% CSAT — paired coaching opportunity</div>
            </div>
            <div class="s-sub">KPI Impact</div>
            <div style="font-size:11px;color:var(--text-dark);line-height:1.5;margin-bottom:8px">{s5_tickets} tickets at {s5_wcsat}% CSAT vs {s5_team_avg}% team avg = {s5_rev_risk} preventable revenue at risk.</div>
            <div class="s-roi"><div class="s-roi-lbl">ROI Action</div><div class="s-roi-txt">Structured coaching: weekly QA review; call recording analysis; paired sessions with {s5_best}.</div></div>
            <div class="s-foot"><span class="s-uplift">↑ +{s5_gap}pt CSAT | {s5_rev_risk} revenue de-risked</span><button class="btn-share-sig" onclick="shareSignal(5)">📤 Share</button></div>
          </div>
        </div>

        <div class="signal-card" data-category="churn">
          <div class="signal-header" onclick="toggleSignal(this)">
            <div class="signal-num sn-pu">6</div>
            <div class="signal-htxt">
              <div class="signal-title">Win-Back Programme — Reactivation Opportunity</div>
              <span class="sp-pu">🔵 Strategic · Priority 82</span>
            </div>
            <span class="sc-badge pu">82</span><span class="signal-chevron">▼</span>
          </div>
          <div class="signal-body">
            <div class="s-sub">Customer Signals</div>
            <div class="s-box">
              <div class="s-item">{s6_pending} churned customers still unresolved — active win-back opportunity</div>
              <div class="s-item">{s6_resolved} of {s1_count} churn tickets already resolved ({s6_rate}% recovery rate)</div>
              <div class="s-item">Revenue at stake from unresolved churn: {s6_rev}</div>
            </div>
            <div class="s-sub">KPI Impact</div>
            <div style="font-size:11px;color:var(--text-dark);line-height:1.5;margin-bottom:8px">{s6_pending} customers pending reactivation. Current win-back rate: {s6_rate}%. Revenue recoverable: {s6_rev}.</div>
            <div class="s-roi"><div class="s-roi-lbl">ROI Action</div><div class="s-roi-txt">Personalised win-back sequences; 30/60/90-day offer cadence; loyalty upgrade as retention lever.</div></div>
            <div class="roi-calc"><div class="roi-calc-lbl">📐 Your ROI Calculator</div><div class="roi-calc-row"><input type="number" placeholder="Churned customers/month" id="ri-6" min="10"/><button onclick="calcROI(6)">Calculate</button></div><div class="roi-result" id="rr-6"></div></div>
            <div class="s-foot"><span class="s-uplift">↑ +{s6_rate}% Win-Back Rate | {s6_rev} reactivation revenue</span><button class="btn-share-sig" onclick="shareSignal(6)">📤 Share</button></div>
          </div>
        </div>

      </div>
    </div><!-- /C -->'''

old_section_c_pattern = r'<div class="section-card" id="section-c"[\s\S]*?</div><!-- /C -->'
result = re.sub(old_section_c_pattern, lambda m: new_section_c, html)
if result != html:
    html = result
    print("  Section-C replaced with real signal data")
else:
    # Fallback: replace the signal-grid content only
    html = html.replace(
        '<span class="slb slb-amber">$3.87M Addressable · 493 Detected</span>',
        f'<span class="slb slb-amber">{total_addressable} Addressable · {total_flagged} Detected</span>'
    )
    print("  Section-C header updated (full replacement skipped)")

# --- Add applyExecBrief JS function near applyTeams ---
apply_exec_fn = """
function applyExecBrief(e){
  var d = document.getElementById('exec-date');
  var cv = document.getElementById('exec-churn-val');
  var rv = document.getElementById('exec-rev-val');
  var sv = document.getElementById('exec-csat-val');
  var rt = document.getElementById('exec-rec-txt');
  if(d)  d.textContent = e.today;
  if(cv) cv.textContent = e.churn_reduced + '%';
  if(rv) rv.textContent = e.rev_protected;
  if(sv) sv.textContent = '+' + e.csat_pts + 'pts';
  if(rt) rt.innerHTML = 'Deploy Navedas retention playbook on the <strong>' + e.at_risk_count + ' at-risk accounts</strong> identified this month (Pending + Escalated tickets). Estimated impact: <strong>−' + Math.min(18, e.churn_reduced) + '% churn rate, revenue at risk ' + e.rev_at_risk + ' recoverable within 90 days</strong>. Secondary action: initiate ' + e.worst_agent + ' coaching plan to close the ' + e.csat_gap + 'pt CSAT gap on ' + e.general_low_count + ' General queue tickets.';
}
"""
html = html.replace('function applyTeams(', apply_exec_fn + '\nfunction applyTeams(')

# --- Update ROI_CFG with real values from data ---
# Real values: avg_ltv=$122, churn_reduction=20%, winback_rate=51%, billing_avg=$106
real_churn_uplift   = round(churn_reduced_real / 100, 3)          # e.g. 0.20
real_ltv            = s1_avg_ltv                                   # e.g. 122
real_rev_leak_pct   = round(revenue_t[rev_col].abs().sum() / max(revenue_t[rev_col].abs().sum() * 33, 1) * 0.03, 4)  # ~3% of revenue
real_loyalty_ltv    = round(loyalty_t[rev_col].abs().mean())       # avg loyalty rev impact
real_loyalty_uplift = 0.04                                         # keep 4% retention uplift
real_billing_avg    = s4_avg                                       # real avg billing cost
real_billing_uplift = 0.032                                        # keep 3.2% error rate
real_winback_rate   = round(s6_rate / 100, 3)                      # e.g. 0.51

old_roi_cfg = "var ROI_CFG={1:{ltv:312,uplift:.175,lbl:'LTV recovered'},2:{ltv:null,uplift:.03,lbl:'revenue saved'},3:{ltv:94,uplift:.04,lbl:'LTV uplift'},4:{ltv:178,uplift:.032,lbl:'cost saving'},6:{ltv:312,uplift:.07,lbl:'reactivation revenue'}};"
new_roi_cfg = f"var ROI_CFG={{1:{{ltv:{real_ltv},uplift:{real_churn_uplift},lbl:'LTV recovered'}},2:{{ltv:null,uplift:.03,lbl:'revenue saved'}},3:{{ltv:{real_loyalty_ltv},uplift:{real_loyalty_uplift},lbl:'LTV uplift'}},4:{{ltv:{real_billing_avg},uplift:{real_billing_uplift},lbl:'cost saving'}},6:{{ltv:{real_ltv},uplift:{real_winback_rate},lbl:'reactivation revenue'}}}};"
html = html.replace(old_roi_cfg, new_roi_cfg)
print(f"  ROI_CFG updated: LTV=${real_ltv} | Churn uplift={real_churn_uplift} | WinBack={real_winback_rate}")

# Write static output
import os
os.makedirs('frontend', exist_ok=True)
with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"  Static HTML written: frontend/index.html ({len(html)//1024} KB)")
print("\nDone! Ready to deploy to Netlify.")
