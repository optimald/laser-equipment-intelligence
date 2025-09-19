#!/usr/bin/env python3
"""
Simple LaserMatch.io scraper using curl/requests
No Scrapy, no Playwright - just simple HTTP requests
"""

import requests
import json
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_lasermatch_page(url):
    """Fetch a page from LaserMatch.io using simple HTTP request"""
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
        print(f"🌐 Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Success: {response.status_code} - {len(response.content)} bytes")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def parse_lasermatch_page(html, url):
    """Parse LaserMatch.io page HTML"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    print(f"🔍 Parsing HTML from {url}")
    
    # Look for common item patterns
    item_selectors = [
        '.item', '.equipment-item', '.listing-item', '.product-item',
        '.inventory-item', '.equipment-card', '.listing-card',
        'article', '.hot-list-item', '.in-demand-item', '.demand-item'
    ]
    
    found_elements = []
    for selector in item_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"📦 Found {len(elements)} elements with selector: {selector}")
            found_elements.extend(elements)
    
    # If no specific items found, look for any text that might be equipment
    if not found_elements:
        print("🔍 No specific item elements found, looking for equipment-related text")
        # Look for text that contains laser equipment keywords
        laser_keywords = ['laser', 'sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma', 'inmode']
        all_text = soup.get_text()
        
        for keyword in laser_keywords:
            if keyword.lower() in all_text.lower():
                print(f"🎯 Found keyword '{keyword}' in page content")
                # Create a basic item from the page content
                item = {
                    'id': f"lasermatch_{int(time.time())}_{keyword}",
                    'title': f"Equipment found containing '{keyword}'",
                    'brand': keyword.title(),
                    'model': 'Unknown',
                    'condition': 'unknown',
                    'price': None,
                    'location': 'Unknown',
                    'description': f"Equipment related to {keyword} found on LaserMatch.io",
                    'url': url,
                    'images': [],
                    'discovered_at': datetime.now().isoformat(),
                    'source': 'LaserMatch.io',
                    'status': 'active'
                }
                items.append(item)
    
    # Parse found elements
    for element in found_elements[:10]:  # Limit to first 10 to avoid too many items
        item = parse_item_element(element, url)
        if item:
            items.append(item)
    
    print(f"📊 Extracted {len(items)} items from {url}")
    return items

def parse_item_element(element, base_url):
    """Parse individual item element"""
    try:
        # Extract title
        title = None
        title_selectors = ['.title', '.item-title', '.equipment-title', 'h1', 'h2', 'h3', 'h4', '.name']
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                break
        
        # Extract description
        description = None
        desc_selectors = ['.description', '.item-description', '.equipment-description', '.summary']
        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                description = desc_elem.get_text().strip()
                break
        
        # Extract price
        price = None
        price_selectors = ['.price', '.cost', '.value', '.asking-price']
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text().strip()
                price = parse_price(price_text)
                break
        
        # Extract brand/model
        brand = None
        model = None
        text_content = element.get_text().lower()
        
        # Look for known brands
        known_brands = ['sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma', 'inmode', 'btl', 'lutronic']
        for known_brand in known_brands:
            if known_brand in text_content:
                brand = known_brand.title()
                break
        
        # Create item
        if title or description or brand:
            item = {
                'id': f"lasermatch_{int(time.time())}_{len(element.get_text())}",
                'title': title or 'LaserMatch Equipment',
                'brand': brand or 'Unknown',
                'model': model or 'Unknown',
                'condition': 'unknown',
                'price': price,
                'location': 'Unknown',
                'description': description or 'Equipment from LaserMatch.io',
                'url': base_url,
                'images': [],
                'discovered_at': datetime.now().isoformat(),
                'source': 'LaserMatch.io',
                'status': 'active'
            }
            return item
        
    except Exception as e:
        print(f"⚠️ Error parsing element: {e}")
    
    return None

def parse_price(price_text):
    """Parse price text to number"""
    if not price_text:
        return None
    
    try:
        # Remove non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.,]', '', price_text)
        cleaned = cleaned.replace(',', '')
        if cleaned:
            return float(cleaned)
    except (ValueError, TypeError):
        pass
    
    return None

def main():
    """Main function"""
    print("🚀 Simple LaserMatch.io Scraper")
    print("=" * 50)
    
    # URLs to scrape
    urls = [
        'https://lasermatch.io/',
        'https://lasermatch.io/hot-list',
        'https://lasermatch.io/in-demand',
        'https://lasermatch.io/inventory',
        'https://lasermatch.io/equipment'
    ]
    
    all_items = []
    
    for url in urls:
        print(f"\n📄 Processing: {url}")
        html = fetch_lasermatch_page(url)
        if html:
            items = parse_lasermatch_page(html, url)
            all_items.extend(items)
        time.sleep(1)  # Be nice to the server
    
    print(f"\n🎯 Total items found: {len(all_items)}")
    
    # Save to JSON
    if all_items:
        with open('lasermatch_items.json', 'w') as f:
            json.dump(all_items, f, indent=2)
        print(f"💾 Saved {len(all_items)} items to lasermatch_items.json")
    else:
        print("❌ No items found")
    
    print("✅ Scraping complete!")

if __name__ == "__main__":
    main()
