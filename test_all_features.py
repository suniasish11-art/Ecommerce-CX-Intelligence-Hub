#!/usr/bin/env python3
"""Test all dashboard features"""
import json
import subprocess
import time
import urllib.request
import sys

def test_api():
    """Test API endpoint"""
    try:
        response = urllib.request.urlopen('http://localhost:8080/api/data', timeout=5)
        data = json.loads(response.read())

        print("\n=== API TEST ===")
        print(f"OK - Tickets: {len(data['all_tickets'])}")
        print(f"OK - Months: {len(data['monthly_data'])}")
        print(f"OK - Agents: {len(data['agent_data'])}")
        print(f"OK - KPIs: {len(data['kpis'])} keys")
        print(f"OK - Teams: {len(data['teams'])} teams")

        # Check first ticket structure
        if data['all_tickets']:
            t = data['all_tickets'][0]
            print(f"\nFirst Ticket: {t[0]} ({t[3]}) - {t[5]}")
            print(f"  Score: {t[8]}, Revenue: {t[9]}, Agent: {t[6]}")

        # Check monthly data
        if data['monthly_data']:
            m = data['monthly_data'][0]
            print(f"\nFirst Month: {m['label']} - {m['total']} tickets")

        # Check agent data
        if data['agent_data']:
            a = data['agent_data'][0]
            print(f"\nFirst Agent: {a['name']} - CSAT {a['csat']}%")

        # Check KPIs
        if data['kpis']:
            print(f"\nKPIs: CSAT {data['kpis']['csat_score']}%, Revenue at risk ${data['kpis']['revenue_at_risk']}M")

        return True
    except Exception as e:
        print(f"\nERROR - API Test Failed: {e}")
        return False

def test_html():
    """Test HTML file integrity"""
    try:
        with open('ecommerce_cx_hub_v10 (3).html', 'r') as f:
            content = f.read()

        print("\n=== HTML FILE TEST ===")

        # Check for key elements
        checks = [
            ('DOCTYPE', '<!DOCTYPE html>'),
            ('Body tag', '<body'),
            ('Script tag', '<script'),
            ('animateCounters', 'function animateCounters'),
            ('renderTable', 'function renderTable'),
            ('applyFilters', 'function applyFilters'),
            ('toggleCharts', 'function toggleCharts'),
            ('doCSVExport', 'function doCSVExport'),
            ('drawLineChart', 'function drawLineChart'),
            ('toggleTop25', 'function toggleTop25'),
        ]

        for name, pattern in checks:
            if pattern in content:
                print(f"OK - {name}: Found")
            else:
                print(f"MISSING - {name}: Not found")

        return True
    except Exception as e:
        print(f"\nERROR - HTML Test Failed: {e}")
        return False

def main():
    print("=" * 50)
    print("DASHBOARD FEATURE TEST")
    print("=" * 50)

    # Start server
    print("\nStarting server...")
    proc = subprocess.Popen(['python', 'server.py'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    time.sleep(3)

    try:
        # Run tests
        api_ok = test_api()
        html_ok = test_html()

        print("\n" + "=" * 50)
        if api_ok and html_ok:
            print("SUCCESS - ALL TESTS PASSED - Dashboard should work!")
        else:
            print("FAILED - Some tests failed - check above")
        print("=" * 50)

    finally:
        print("\nStopping server...")
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except:
            proc.kill()

if __name__ == '__main__':
    main()
