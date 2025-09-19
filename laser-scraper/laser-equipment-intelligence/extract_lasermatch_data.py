#!/usr/bin/env python3
"""
Extract LaserMatch.io Hot List and In Demand data from homepage tables
"""

import requests
import json
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_lasermatch_homepage():
    """Fetch LaserMatch.io homepage"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print("🌐 Fetching LaserMatch.io homepage...")
        response = requests.get('https://lasermatch.io/', headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Success: {response.status_code} - {len(response.content)} bytes")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching homepage: {e}")
        return None

def extract_table_data(html, table_id, list_type):
    """Extract data from specific table"""
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    print(f"🔍 Looking for {list_type} table (ID: {table_id})...")
    
    # Find the table by ID
    table = soup.find('table', id=table_id)
    
    if not table:
        print(f"❌ Could not find table with ID: {table_id}")
        return items
    
    print(f"📦 Found {list_type} table")
    
    # Find all rows in the table body
    tbody = table.find('tbody')
    if not tbody:
        print(f"❌ No tbody found in {list_type} table")
        return items
    
    rows = tbody.find_all('tr')
    print(f"📋 Processing {len(rows)} rows from {list_type} table")
    
    for i, row in enumerate(rows):
        try:
            cells = row.find_all('td')
            
            if len(cells) >= 2:
                item_name = cells[0].get_text().strip()
                description = cells[1].get_text().strip()
                
                # Skip empty rows
                if not item_name or not description:
                    continue
                
                # Parse brand and model from item name
                if ':' in item_name:
                    brand, model = item_name.split(':', 1)
                    brand = brand.strip()
                    model = model.strip()
                else:
                    brand = item_name.split()[0] if item_name.split() else 'Unknown'
                    model = item_name
                
                item = {
                    'id': f"{list_type.lower().replace(' ', '_')}_{i+1:03d}",
                    'title': item_name,
                    'brand': brand,
                    'model': model,
                    'condition': 'any',
                    'price': None,
                    'location': 'Various',
                    'description': description,
                    'url': 'https://lasermatch.io/',
                    'images': [],
                    'discovered_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'source': 'LaserMatch.io',
                    'status': 'active',
                    'category': list_type.lower().replace(' ', '-'),
                    'availability': 'in-demand'
                }
                
                items.append(item)
                print(f"✅ {list_type}: {brand}: {model}")
            
        except Exception as e:
            print(f"⚠️ Error processing row {i} in {list_type}: {e}")
            continue
    
    return items

def save_to_database_format(items, filename='lasermatch_database_items.json'):
    """Save items in database format"""
    db_items = []
    for item in items:
        db_item = {
            'id': item['id'],
            'title': item['title'],
            'brand': item['brand'],
            'model': item['model'],
            'condition': item['condition'],
            'price': item['price'],
            'source': item['source'],
            'url': item['url'],
            'location': item['location'],
            'description': item['description'],
            'images': item['images'],
            'discovered_at': item['discovered_at'],
            'last_updated': item['last_updated'],
            'margin_estimate': None,
            'score_overall': 85,  # High score for demand items
            'status': item['status']
        }
        db_items.append(db_item)
    
    with open(filename, 'w') as f:
        json.dump(db_items, f, indent=2)
    
    print(f"💾 Saved {len(db_items)} items to {filename}")
    return db_items

def main():
    """Main function"""
    print("🚀 LaserMatch.io Data Extractor")
    print("=" * 50)
    
    # Fetch homepage
    html = fetch_lasermatch_homepage()
    if not html:
        print("❌ Failed to fetch homepage")
        return
    
    all_items = []
    
    # Extract Hot List items
    print("\n🔥 Extracting Hot List items...")
    hot_items = extract_table_data(html, 'dt-hotlist-items', 'HOT LIST')
    all_items.extend(hot_items)
    
    # Extract In Demand items
    print("\n📈 Extracting In Demand items...")
    demand_items = extract_table_data(html, 'dt-demand-items', 'IN DEMAND')
    all_items.extend(demand_items)
    
    print(f"\n🎯 Total items extracted: {len(all_items)}")
    print(f"   Hot List: {len(hot_items)} items")
    print(f"   In Demand: {len(demand_items)} items")
    
    if all_items:
        # Save to database format
        db_items = save_to_database_format(all_items)
        
        # Also save raw format
        with open('lasermatch_raw_items.json', 'w') as f:
            json.dump(all_items, f, indent=2)
        
        print("✅ Extraction complete!")
        
        # Show sample items
        print("\n📋 Sample items:")
        for i, item in enumerate(all_items[:3]):
            print(f"   {i+1}. {item['title']}")
            print(f"      Brand: {item['brand']}")
            print(f"      Model: {item['model']}")
            print(f"      Description: {item['description'][:100]}...")
        
        # Show brand breakdown
        brands = {}
        for item in all_items:
            brand = item['brand']
            brands[brand] = brands.get(brand, 0) + 1
        
        print(f"\n📊 Top brands:")
        top_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]
        for brand, count in top_brands:
            print(f"   {brand}: {count} items")
        
        print(f"\n🎯 Ready to import {len(db_items)} items to database!")
        
    else:
        print("❌ No items extracted")

if __name__ == "__main__":
    main()
