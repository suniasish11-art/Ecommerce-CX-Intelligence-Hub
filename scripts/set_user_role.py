"""
set_user_role.py — Assign roles to Supabase users
──────────────────────────────────────────────────
Usage:
  python scripts/set_user_role.py <email> <role>

  role must be one of: viewer | manager | admin

Examples:
  python scripts/set_user_role.py john@navedas.com admin
  python scripts/set_user_role.py sara@navedas.com manager
  python scripts/set_user_role.py guest@navedas.com viewer
"""

import os, sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file")
    sys.exit(1)

VALID_ROLES = ('viewer', 'manager', 'admin')

if len(sys.argv) != 3 or sys.argv[2] not in VALID_ROLES:
    print(__doc__)
    sys.exit(1)

email, role = sys.argv[1], sys.argv[2]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Find user by email
users = supabase.auth.admin.list_users()
user = next((u for u in users if u.email == email), None)

if not user:
    print(f"ERROR: No user found with email '{email}'")
    print("Create the user first via Supabase Dashboard > Authentication > Users > Add User")
    sys.exit(1)

# Set role in user_roles table
supabase.table('user_roles').upsert({
    'user_id': user.id,
    'role': role,
    'full_name': user.email,
}, on_conflict='user_id').execute()

print(f"Role set: {email} → {role}")
print(f"User ID: {user.id}")
