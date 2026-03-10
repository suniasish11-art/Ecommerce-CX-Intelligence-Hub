"""
GET /api/agents
Roles allowed: manager, admin
Returns agent performance data.
"""
from http.server import BaseHTTPRequestHandler
from _middleware import require_role, json_response, options_response


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._send(options_response())

    def do_GET(self):
        try:
            client, role = require_role(self, ['manager', 'admin'])
        except (ValueError, PermissionError) as e:
            self._send(json_response(403, {'error': str(e)}))
            return

        try:
            result = client.table('agent_performance').select('*').order('csat', desc=True).execute()
            self._send(json_response(200, {'agents': result.data}))
        except Exception as e:
            self._send(json_response(500, {'error': str(e)}))

    def _send(self, res):
        self.send_response(res['statusCode'])
        for k, v in res.get('headers', {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(res['body'].encode())
