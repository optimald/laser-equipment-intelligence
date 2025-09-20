#!/usr/bin/env python3
"""
Working LaserMatch.io data extractor based on debug findings
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_and_extract():
    """Fetch and extract LaserMatch data"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    print("🌐 Fetching LaserMatch.io homepage...")
    response = requests.get('https://lasermatch.io/', headers=headers, timeout=10)
    print(f"✅ Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    all_items = []
    
    # Extract Hot List items
    print("\n🔥 Extracting Hot List items...")
    hot_table = soup.find('table', id='dt-hotlist-items')
    if hot_table:
        tbody = hot_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"📋 Processing {len(rows)} Hot List rows")
            
            for i, row in enumerate(rows):
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        item_name = cells[0].get_text().strip()
                        description = cells[1].get_text().strip()
                        
                        # Parse brand and model
                        if ':' in item_name:
                            brand, model = item_name.split(':', 1)
                            brand = brand.strip()
                            model = model.strip()
                        else:
                            brand = item_name.split()[0] if item_name.split() else 'Unknown'
                            model = item_name
                        
                        item = {
                            'id': f"hot_list_{i+1:03d}",
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
                            'category': 'hot-list',
                            'availability': 'in-demand'
                        }
                        
                        all_items.append(item)
                        print(f"✅ Hot: {brand}: {model}")
                        
                except Exception as e:
                    print(f"⚠️ Error processing Hot List row {i}: {e}")
    
    # Extract In Demand items
    print("\n📈 Extracting In Demand items...")
    demand_table = soup.find('table', id='dt-demand-items')
    if demand_table:
        tbody = demand_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"📋 Processing {len(rows)} In Demand rows")
            
            for i, row in enumerate(rows):
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        item_name = cells[0].get_text().strip()
                        description = cells[1].get_text().strip()
                        
                        # Parse brand and model
                        if ':' in item_name:
                            brand, model = item_name.split(':', 1)
                            brand = brand.strip()
                            model = model.strip()
                        else:
                            brand = item_name.split()[0] if item_name.split() else 'Unknown'
                            model = item_name
                        
                        item = {
                            'id': f"in_demand_{i+1:03d}",
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
                            'category': 'in-demand',
                            'availability': 'in-demand'
                        }
                        
                        all_items.append(item)
                        print(f"✅ Demand: {brand}: {model}")
                        
                except Exception as e:
                    print(f"⚠️ Error processing In Demand row {i}: {e}")
    
    return all_items

def save_to_database_format(items):
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
            'score_overall': 85,
            'status': item['status']
        }
        db_items.append(db_item)
    
    with open('lasermatch_database_items.json', 'w') as f:
        json.dump(db_items, f, indent=2)
    
    print(f"💾 Saved {len(db_items)} items to lasermatch_database_items.json")
    return db_items

def main():
    """Main function"""
    print("🚀 Working LaserMatch.io Data Extractor")
    print("=" * 50)
    
    items = fetch_and_extract()
    
    print(f"\n🎯 Total items extracted: {len(items)}")
    
    if items:
        # Save to database format
        db_items = save_to_database_format(items)
        
        # Show sample items
        print("\n📋 Sample items:")
        for i, item in enumerate(items[:5]):
            print(f"   {i+1}. {item['title']}")
            print(f"      Brand: {item['brand']}")
            print(f"      Description: {item['description'][:80]}...")
        
        # Show brand breakdown
        brands = {}
        for item in items:
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
