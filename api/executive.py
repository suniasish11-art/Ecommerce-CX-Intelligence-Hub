"""
GET /api/executive
Roles allowed: admin only
Returns high-level KPI summary for Executive Briefing tab.
"""
from http.server import BaseHTTPRequestHandler
from _middleware import require_role, json_response, options_response


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._send(options_response())

    def do_GET(self):
        try:
            client, role = require_role(self, ['admin'])
        except (ValueError, PermissionError) as e:
            self._send(json_response(403, {'error': str(e)}))
            return

        try:
            # Aggregate KPIs from tickets table for exec briefing
            tickets = client.table('tickets').select(
                'status, category, sentiment, score, revenue_impact'
            ).execute().data

            total = len(tickets)
            resolved = sum(1 for t in tickets if t['status'] == 'Resolved')
            churn = [t for t in tickets if t['category'] == 'Churn']
            churn_resolved = sum(1 for t in churn if t['status'] == 'Resolved')
            neg = sum(1 for t in tickets if t['sentiment'] in ('Negative', 'Very Negative'))
            scores = [t['score'] for t in tickets if t['score'] and t['score'] > 0]
            rev_saved = sum(abs(t['revenue_impact']) for t in tickets
                           if t['status'] == 'Resolved' and t['revenue_impact'])

            kpis = {
                'total_tickets':    total,
                'resolution_rate':  round(resolved / total * 100, 1) if total else 0,
                'winback_rate':     round(churn_resolved / len(churn) * 100, 1) if churn else 0,
                'neg_sentiment_pct':round(neg / total * 100, 1) if total else 0,
                'avg_csat':         round(sum(scores) / len(scores), 1) if scores else 0,
                'revenue_saved_k':  round(rev_saved / 1000, 1),
                'churn_count':      len(churn),
            }
            self._send(json_response(200, {'kpis': kpis}))

        except Exception as e:
            self._send(json_response(500, {'error': str(e)}))

    def _send(self, res):
        self.send_response(res['statusCode'])
        for k, v in res.get('headers', {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(res['body'].encode())
