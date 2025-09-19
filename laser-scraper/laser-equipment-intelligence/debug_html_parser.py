#!/usr/bin/env python3
"""
Debug HTML parser for LaserMatch.io
"""

import requests
from bs4 import BeautifulSoup

def debug_lasermatch():
    """Debug the HTML parsing"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    print("🌐 Fetching LaserMatch.io homepage...")
    response = requests.get('https://lasermatch.io/', headers=headers, timeout=10)
    print(f"✅ Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check if tables exist
    print("\n🔍 Looking for tables...")
    
    # Find all tables
    tables = soup.find_all('table')
    print(f"📊 Found {len(tables)} tables total")
    
    for i, table in enumerate(tables):
        table_id = table.get('id', 'no-id')
        print(f"   Table {i+1}: ID='{table_id}'")
    
    # Specifically look for our tables
    hot_table = soup.find('table', id='dt-hotlist-items')
    demand_table = soup.find('table', id='dt-demand-items')
    
    print(f"\n🎯 Hot List table found: {hot_table is not None}")
    print(f"🎯 In Demand table found: {demand_table is not None}")
    
    if hot_table:
        print("\n🔥 Hot List table structure:")
        tbody = hot_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"   Rows in tbody: {len(rows)}")
            for i, row in enumerate(rows[:3]):  # Show first 3 rows
                cells = row.find_all('td')
                if len(cells) >= 2:
                    item = cells[0].get_text().strip()
                    desc = cells[1].get_text().strip()
                    print(f"   Row {i+1}: {item}")
                    print(f"           {desc[:50]}...")
        else:
            print("   No tbody found")
    
    if demand_table:
        print("\n📈 In Demand table structure:")
        tbody = demand_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"   Rows in tbody: {len(rows)}")
            for i, row in enumerate(rows[:3]):  # Show first 3 rows
                cells = row.find_all('td')
                if len(cells) >= 2:
                    item = cells[0].get_text().strip()
                    desc = cells[1].get_text().strip()
                    print(f"   Row {i+1}: {item}")
                    print(f"           {desc[:50]}...")
        else:
            print("   No tbody found")

if __name__ == "__main__":
    debug_lasermatch()
