"""
GET /api/role
Roles allowed: all authenticated users
Returns the current user's role — called right after login to get role info.
"""
from http.server import BaseHTTPRequestHandler
from _middleware import verify_token, json_response, options_response


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._send(options_response())

    def do_GET(self):
        try:
            client, role = verify_token(self)
            self._send(json_response(200, {'role': role}))
        except ValueError as e:
            self._send(json_response(403, {'error': str(e)}))

    def _send(self, res):
        self.send_response(res['statusCode'])
        for k, v in res.get('headers', {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(res['body'].encode())
