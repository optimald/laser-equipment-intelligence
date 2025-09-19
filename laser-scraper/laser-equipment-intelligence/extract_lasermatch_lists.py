#!/usr/bin/env python3
"""
Extract LaserMatch.io Hot List and In Demand lists from homepage
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

def extract_hot_list_items(html):
    """Extract items from Hot List section"""
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    print("🔍 Looking for Hot List section...")
    
    # Look for Hot List section
    hot_list_section = None
    
    # Try to find the Hot List section by looking for the title
    hot_list_headers = soup.find_all(text=re.compile(r'HOT LIST', re.IGNORECASE))
    for header in hot_list_headers:
        parent = header.parent
        # Look for the table or list structure after the header
        section = parent.find_next_sibling()
        if section:
            hot_list_section = section
            break
    
    if not hot_list_section:
        # Try alternative selectors
        hot_list_section = soup.find('div', class_=re.compile(r'hot', re.IGNORECASE))
    
    if hot_list_section:
        print(f"📦 Found Hot List section")
        items.extend(extract_items_from_section(hot_list_section, 'HOT LIST'))
    else:
        print("❌ Could not find Hot List section")
    
    return items

def extract_in_demand_items(html):
    """Extract items from In Demand section"""
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    print("🔍 Looking for In Demand section...")
    
    # Look for In Demand section
    in_demand_section = None
    
    # Try to find the In Demand section by looking for the title
    in_demand_headers = soup.find_all(text=re.compile(r'IN DEMAND', re.IGNORECASE))
    for header in in_demand_headers:
        parent = header.parent
        # Look for the table or list structure after the header
        section = parent.find_next_sibling()
        if section:
            in_demand_section = section
            break
    
    if not in_demand_section:
        # Try alternative selectors
        in_demand_section = soup.find('div', class_=re.compile(r'demand', re.IGNORECASE))
    
    if in_demand_section:
        print(f"📦 Found In Demand section")
        items.extend(extract_items_from_section(in_demand_section, 'IN DEMAND'))
    else:
        print("❌ Could not find In Demand section")
    
    return items

def extract_items_from_section(section, list_type):
    """Extract items from a section (Hot List or In Demand)"""
    items = []
    
    # Look for table rows or list items
    rows = section.find_all(['tr', 'div'], class_=re.compile(r'row|item|entry', re.IGNORECASE))
    
    if not rows:
        # Try to find any structured data
        rows = section.find_all(['div', 'li', 'p'])
    
    print(f"📋 Found {len(rows)} potential rows in {list_type} section")
    
    for i, row in enumerate(rows[:50]):  # Limit to first 50 items
        try:
            # Extract text content
            text_content = row.get_text().strip()
            
            if len(text_content) < 10:  # Skip very short content
                continue
            
            # Look for colon pattern (Brand: Model)
            if ':' in text_content:
                parts = text_content.split(':', 1)
                if len(parts) == 2:
                    brand = parts[0].strip()
                    rest = parts[1].strip()
                    
                    # Split model from description (look for dash or newline)
                    if '-' in rest:
                        model_part, description_part = rest.split('-', 1)
                        model = model_part.strip()
                        description = description_part.strip()
                    else:
                        model = rest.split('\n')[0].strip() if '\n' in rest else rest
                        description = rest
                    
                    item = {
                        'id': f"{list_type.lower().replace(' ', '_')}_{i+1:03d}",
                        'title': f"{brand}: {model}",
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
                    print(f"✅ Extracted: {brand}: {model}")
            
        except Exception as e:
            print(f"⚠️ Error processing row {i}: {e}")
            continue
    
    return items

def save_items_to_database_format(items, filename='lasermatch_database_items.json'):
    """Save items in database format"""
    # Convert to database format
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

def main():
    """Main function"""
    print("🚀 LaserMatch.io List Extractor")
    print("=" * 50)
    
    # Fetch homepage
    html = fetch_lasermatch_homepage()
    if not html:
        print("❌ Failed to fetch homepage")
        return
    
    all_items = []
    
    # Extract Hot List items
    print("\n🔥 Extracting Hot List items...")
    hot_items = extract_hot_list_items(html)
    all_items.extend(hot_items)
    
    # Extract In Demand items
    print("\n📈 Extracting In Demand items...")
    demand_items = extract_in_demand_items(html)
    all_items.extend(demand_items)
    
    print(f"\n🎯 Total items extracted: {len(all_items)}")
    print(f"   Hot List: {len(hot_items)} items")
    print(f"   In Demand: {len(demand_items)} items")
    
    if all_items:
        # Save to database format
        save_items_to_database_format(all_items)
        
        # Also save raw format
        with open('lasermatch_raw_items.json', 'w') as f:
            json.dump(all_items, f, indent=2)
        
        print("✅ Extraction complete!")
        
        # Show sample items
        print("\n📋 Sample items:")
        for i, item in enumerate(all_items[:3]):
            print(f"   {i+1}. {item['title']}")
            print(f"      Description: {item['description'][:100]}...")
    else:
        print("❌ No items extracted")

if __name__ == "__main__":
    main()
