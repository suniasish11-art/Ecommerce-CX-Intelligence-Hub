"""
Shared JWT verification middleware for all API endpoints.
Reads the role from the user_roles table in Supabase.
"""
import os, json
from supabase import create_client

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')


def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def verify_token(request):
    """
    Verify the Bearer JWT and return (supabase_client_with_user_auth, role).
    Raises ValueError on auth failure.
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise ValueError('Missing or invalid Authorization header')

    token = auth_header.split(' ', 1)[1]

    # Use user's token to query — RLS will enforce access automatically
    from supabase import create_client as _cc
    user_client = _cc(SUPABASE_URL, os.environ.get('SUPABASE_ANON_KEY', ''))
    user_client.auth.set_session(token, '')

    # Get role from user_roles table (RLS: user can only read own row)
    try:
        result = user_client.table('user_roles').select('role').execute()
        rows = result.data
        if not rows:
            raise ValueError('No role assigned. Contact admin.')
        role = rows[0]['role']
        return user_client, role
    except Exception as e:
        raise ValueError(f'Auth failed: {str(e)}')


def require_role(request, allowed_roles: list):
    """Returns (user_client, role) or raises ValueError / PermissionError."""
    client, role = verify_token(request)
    if role not in allowed_roles:
        raise PermissionError(f'Role "{role}" cannot access this resource')
    return client, role


def json_response(status: int, body: dict):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        },
        'body': json.dumps(body),
    }


def options_response():
    """Handle CORS preflight."""
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        },
        'body': '',
    }
