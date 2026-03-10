"""
GET /api/tickets
Roles allowed: viewer, manager, admin
Returns all ticket records for the dashboard table + compute engine.
"""
import json
from http.server import BaseHTTPRequestHandler
from _middleware import require_role, json_response, options_response


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        res = options_response()
        self._send(res)

    def do_GET(self):
        try:
            client, role = require_role(self, ['viewer', 'manager', 'admin'])
        except (ValueError, PermissionError) as e:
            self._send(json_response(403, {'error': str(e)}))
            return

        try:
            result = client.table('tickets').select(
                'ticket_id, date, month, category, sub_issue, '
                'status, agent, sentiment, score, revenue_impact, pattern_flag'
            ).order('date').execute()

            # Return as array-of-arrays matching existing ALL_TICKETS format:
            # [ticket_id, date, month, category, sub_issue,
            #  status, agent, sentiment, score, revenue_impact, pattern_flag]
            rows = [
                [
                    r['ticket_id'], r['date'], r['month'], r['category'],
                    r['sub_issue'], r['status'], r['agent'], r['sentiment'],
                    r['score'], r['revenue_impact'], r['pattern_flag']
                ]
                for r in result.data
            ]
            self._send(json_response(200, {'tickets': rows, 'count': len(rows)}))

        except Exception as e:
            self._send(json_response(500, {'error': str(e)}))

    def _send(self, res):
        self.send_response(res['statusCode'])
        for k, v in res.get('headers', {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(res['body'].encode())
