#!/usr/bin/env python3
import json
import sys
import time
import subprocess
import urllib.request

# Start server in background
proc = subprocess.Popen([sys.executable, 'server.py'],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
time.sleep(4)

try:
    # Test API
    response = urllib.request.urlopen('http://localhost:8080/api/data', timeout=5)
    data = json.loads(response.read().decode())

    print('SUCCESS! API Response:')
    print(f'  Tickets: {len(data["all_tickets"])}')
    print(f'  Months: {len(data["monthly_data"])}')
    print(f'  Agents: {len(data["agent_data"])}')
    print(f'  CSAT Score: {data["kpis"]["csat_score"]}%')
    print(f'  Revenue at Risk: ${data["kpis"]["revenue_at_risk"]}M')
    print()
    print('Dashboard is ready to run!')

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
finally:
    proc.terminate()
    proc.wait(timeout=2)
