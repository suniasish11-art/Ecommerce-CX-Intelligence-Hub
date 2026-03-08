#!/usr/bin/env python3
import json
import time
import subprocess
import sys
import urllib.request

# Start server
proc = subprocess.Popen([sys.executable, 'server.py'],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
time.sleep(4)

try:
    response = urllib.request.urlopen('http://localhost:8080/api/data', timeout=5)
    data = json.loads(response.read().decode())

    print("API Response Structure:")
    print("=" * 60)

    print("\n1. MONTHLY_DATA (first item):")
    if data.get('monthly_data'):
        print(json.dumps(data['monthly_data'][0], indent=2))

    print("\n2. AGENT_DATA (first item):")
    if data.get('agent_data'):
        print(json.dumps(data['agent_data'][0], indent=2))

    print("\n3. ALL_TICKETS (first item):")
    if data.get('all_tickets'):
        print(f"  {data['all_tickets'][0]}")

    print("\n4. SPARK_DATA (structure):")
    if data.get('spark_data'):
        for team in data['spark_data']:
            print(f"  {team}: {len(data['spark_data'][team])} months")

    print("\n5. KPIs (full list):")
    if data.get('kpis'):
        for key, value in data['kpis'].items():
            print(f"  {key}: {value}")

    print("\n6. TEAMS (structure):")
    if data.get('teams'):
        for team, info in data['teams'].items():
            print(f"  {team}: {info}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    proc.terminate()
    proc.wait(timeout=2)
