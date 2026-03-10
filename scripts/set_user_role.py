"""
set_user_role.py — Assign roles to Supabase users (requests only, no SDK)

Usage:
  python scripts/set_user_role.py <email> <role>
  role: viewer | manager | admin

Examples:
  python scripts/set_user_role.py admin@navedas.com admin
  python scripts/set_user_role.py sara@navedas.com manager
  python scripts/set_user_role.py guest@navedas.com viewer
"""
import os, sys, json
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")
    sys.exit(1)

VALID_ROLES = ('viewer', 'manager', 'admin')

if len(sys.argv) != 3 or sys.argv[2] not in VALID_ROLES:
    print(__doc__)
    sys.exit(1)

email, role = sys.argv[1], sys.argv[2]

HEADERS = {
    'apikey':        SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type':  'application/json',
}

# Step 1: Find user by email via Admin API
r = requests.get(
    f"{SUPABASE_URL}/auth/v1/admin/users?page=1&per_page=1000",
    headers=HEADERS
)
if r.status_code != 200:
    print(f"ERROR fetching users: {r.status_code} {r.text[:200]}")
    sys.exit(1)

users = r.json().get('users', [])
user = next((u for u in users if u.get('email') == email), None)

if not user:
    print(f"ERROR: No user found with email '{email}'")
    print("Create the user first:")
    print("  Supabase Dashboard -> Authentication -> Users -> Add User")
    sys.exit(1)

user_id = user['id']

# Step 2: Upsert role into user_roles table
r2 = requests.post(
    f"{SUPABASE_URL}/rest/v1/user_roles",
    headers={**HEADERS, 'Prefer': 'resolution=merge-duplicates'},
    data=json.dumps({'user_id': user_id, 'role': role, 'full_name': email})
)

if r2.status_code in (200, 201):
    print(f"Role set: {email} -> {role}")
    print(f"User ID:  {user_id}")
else:
    print(f"ERROR setting role: {r2.status_code} {r2.text[:200]}")
