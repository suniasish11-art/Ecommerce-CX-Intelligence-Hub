"""
GET /api/monthly
Roles allowed: viewer, manager, admin
Returns monthly summary data for charts.
"""
from http.server import BaseHTTPRequestHandler
from _middleware import require_role, json_response, options_response


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._send(options_response())

    def do_GET(self):
        try:
            client, role = require_role(self, ['viewer', 'manager', 'admin'])
        except (ValueError, PermissionError) as e:
            self._send(json_response(403, {'error': str(e)}))
            return

        try:
            result = client.table('monthly_summary').select('*').order('label').execute()
            self._send(json_response(200, {'monthly': result.data}))
        except Exception as e:
            self._send(json_response(500, {'error': str(e)}))

    def _send(self, res):
        self.send_response(res['statusCode'])
        for k, v in res.get('headers', {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(res['body'].encode())
