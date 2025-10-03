#!/usr/bin/env python3
"""
LaserMatch.io Scraper
Scrapes laser equipment listings from lasermatch.io website
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import time
import random

class LaserMatchScraper:
    def __init__(self):
        self.base_url = "https://lasermatch.io"
        self.session = None
        self.items = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def __aenter__(self):
        # Create SSL context that doesn't verify certificates
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30),
            connector=connector
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_page(self, url: str) -> str:
        """Get page content with retry logic"""
        for attempt in range(3):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:
                        print(f"Rate limited, waiting 5 seconds...")
                        await asyncio.sleep(5)
                    else:
                        print(f"HTTP {response.status} for {url}")
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
        
        return ""

    def extract_listings_from_html(self, html: str) -> List[Dict[str, Any]]:
        """Extract equipment listings from HTML content"""
        items = []
        
        # Extract modal content IDs and titles
        modal_pattern = r"updateModalContent\('([^']+)',\s*'([^']+)'\)"
        modal_matches = re.findall(modal_pattern, html)
        
        for modal_id, title in modal_matches:
            modal_id = modal_id.strip()
            if modal_id and title:
                item = {
                    "title": title,
                    "brand": "",
                    "model": "",
                    "condition": "Used - Good",
                    "price": 0.0,
                    "location": "Unknown",
                    "description": f"Equipment listing from LaserMatch.io - {title}",
                    "url": f"https://lasermatch.io/modal/{modal_id}",
                    "images": [],
                    "source": "LaserMatch.io",
                    "status": "active",
                    "category": "Laser System",
                    "availability": "Available",
                    "assigned_rep": None,
                    "target_price": None,
                    "notes": None,
                    "spider_urls": None,
                    "modal_id": modal_id
                }
                
                # Extract brand and model from title
                brand, model = self.extract_brand_model(title)
                item["brand"] = brand
                item["model"] = model
                
                items.append(item)
        
        # Also look for direct equipment listings in HTML
        equipment_patterns = [
            r'<div[^>]*class="[^"]*equipment[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*listing[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*item[^"]*"[^>]*>(.*?)</div>',
            r'<article[^>]*>(.*?)</article>',
        ]
        
        for pattern in equipment_patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            for match in matches:
                item = self.parse_equipment_item(match)
                if item:
                    items.append(item)
        
        # Look for JSON data in script tags
        json_pattern = r'<script[^>]*type="application/json"[^>]*>(.*?)</script>'
        json_matches = re.findall(json_pattern, html, re.DOTALL)
        
        for json_data in json_matches:
            try:
                data = json.loads(json_data)
                if isinstance(data, list):
                    for item_data in data:
                        if self.is_equipment_item(item_data):
                            items.append(self.parse_json_item(item_data))
                elif isinstance(data, dict) and 'items' in data:
                    for item_data in data['items']:
                        if self.is_equipment_item(item_data):
                            items.append(self.parse_json_item(item_data))
            except json.JSONDecodeError:
                continue
        
        return items

    def parse_equipment_item(self, html: str) -> Dict[str, Any]:
        """Parse equipment item from HTML snippet"""
        try:
            # Extract title
            title_match = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ""
            
            # Extract price
            price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', html)
            price = price_match.group(0) if price_match else ""
            
            # Extract description
            desc_match = re.search(r'<p[^>]*>(.*?)</p>', html, re.DOTALL | re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Extract brand and model from title
            brand, model = self.extract_brand_model(title)
            
            # Extract condition
            condition = self.extract_condition(html)
            
            # Extract location
            location = self.extract_location(html)
            
            # Extract images
            images = self.extract_images(html)
            
            if title and price:
                return {
                    "title": title,
                    "brand": brand,
                    "model": model,
                    "condition": condition,
                    "price": self.parse_price(price),
                    "location": location,
                    "description": description,
                    "url": "",  # Will be filled by caller
                    "images": images,
                    "source": "LaserMatch.io",
                    "status": "active",
                    "category": "Laser System",
                    "availability": "Available",
                    "assigned_rep": None,
                    "target_price": None,
                    "notes": None,
                    "spider_urls": None
                }
        except Exception as e:
            print(f"Error parsing equipment item: {e}")
        
        return None

    def parse_json_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse equipment item from JSON data"""
        try:
            title = data.get('title', data.get('name', ''))
            price = data.get('price', data.get('cost', 0))
            description = data.get('description', '')
            brand = data.get('brand', '')
            model = data.get('model', '')
            condition = data.get('condition', 'Used - Good')
            location = data.get('location', 'Unknown')
            images = data.get('images', [])
            
            if not brand and not model and title:
                brand, model = self.extract_brand_model(title)
            
            return {
                "title": title,
                "brand": brand,
                "model": model,
                "condition": condition,
                "price": float(price) if price else 0,
                "location": location,
                "description": description,
                "url": data.get('url', ''),
                "images": images if isinstance(images, list) else [images] if images else [],
                "source": "LaserMatch.io",
                "status": "active",
                "category": "Laser System",
                "availability": "Available",
                "assigned_rep": None,
                "target_price": None,
                "notes": None,
                "spider_urls": None
            }
        except Exception as e:
            print(f"Error parsing JSON item: {e}")
            return None

    def is_equipment_item(self, data: Dict[str, Any]) -> bool:
        """Check if data represents an equipment item"""
        if not isinstance(data, dict):
            return False
        
        title = data.get('title', data.get('name', '')).lower()
        price = data.get('price', data.get('cost', 0))
        
        # Check for laser-related keywords
        laser_keywords = ['laser', 'aesthetic', 'medical', 'equipment', 'system', 'device']
        has_laser_keyword = any(keyword in title for keyword in laser_keywords)
        
        # Check for reasonable price range
        has_reasonable_price = False
        if price:
            try:
                price_val = float(price)
                has_reasonable_price = 1000 <= price_val <= 500000
            except (ValueError, TypeError):
                pass
        
        return has_laser_keyword or has_reasonable_price

    def extract_brand_model(self, title: str) -> tuple:
        """Extract brand and model from title"""
        if not title:
            return "", ""
        
        # Common laser brands
        brands = [
            'Aerolase', 'Candela', 'Cynosure', 'Lumenis', 'Syneron', 'Alma', 
            'Cutera', 'Sciton', 'Agnes', 'Allergan', 'Solta', 'Palomar',
            'Fotona', 'Quanta', 'Asclepion', 'BTL', 'Venus', 'Pollogen'
        ]
        
        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                # Extract model (usually after brand)
                model_start = title_upper.find(brand.upper()) + len(brand)
                model_part = title[model_start:].strip()
                # Clean up model name
                model = re.sub(r'^[-:\s]+', '', model_part)
                model = re.sub(r'\s+', ' ', model)
                return brand, model[:50]  # Limit model length
        
        # If no brand found, try to extract first word as brand
        words = title.split()
        if words:
            brand = words[0]
            model = ' '.join(words[1:]) if len(words) > 1 else ""
            return brand, model
        
        return "", title

    def extract_condition(self, html: str) -> str:
        """Extract condition from HTML"""
        condition_keywords = {
            'new': 'New',
            'excellent': 'Used - Excellent',
            'good': 'Used - Good',
            'fair': 'Used - Fair',
            'poor': 'Used - Poor',
            'refurbished': 'Refurbished',
            'reconditioned': 'Refurbished'
        }
        
        html_lower = html.lower()
        for keyword, condition in condition_keywords.items():
            if keyword in html_lower:
                return condition
        
        return 'Used - Good'  # Default

    def extract_location(self, html: str) -> str:
        """Extract location from HTML"""
        # Look for common location patterns
        location_patterns = [
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # City, Country
            r'([A-Z]{2},\s*USA)',  # State, USA
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        
        return 'Unknown'

    def extract_images(self, html: str) -> List[str]:
        """Extract image URLs from HTML"""
        img_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(img_pattern, html, re.IGNORECASE)
        
        images = []
        for match in matches:
            if match.startswith('http'):
                images.append(match)
            elif match.startswith('/'):
                images.append(urljoin(self.base_url, match))
        
        return images[:5]  # Limit to 5 images

    def parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        try:
            # Remove currency symbols and commas
            price_clean = re.sub(r'[^\d.]', '', price_str)
            return float(price_clean)
        except (ValueError, TypeError):
            return 0.0

    async def scrape_lasermatch(self) -> List[Dict[str, Any]]:
        """Main scraping function"""
        print("🕷️ Starting LaserMatch.io scraping...")
        
        # URLs to scrape
        urls_to_scrape = [
            f"{self.base_url}/",
            f"{self.base_url}/equipment",
            f"{self.base_url}/listings",
            f"{self.base_url}/search",
            f"{self.base_url}/lasers",
            f"{self.base_url}/aesthetic-equipment",
        ]
        
        all_items = []
        
        for url in urls_to_scrape:
            print(f"📄 Scraping: {url}")
            
            try:
                html = await self.get_page(url)
                if html:
                    items = self.extract_listings_from_html(html)
                    
                    # Add URL to each item
                    for item in items:
                        item['url'] = url
                    
                    all_items.extend(items)
                    print(f"✅ Found {len(items)} items on {url}")
                else:
                    print(f"❌ No content retrieved from {url}")
                
                # Be respectful - add delay between requests
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"❌ Error scraping {url}: {e}")
                continue
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_items = []
        for item in all_items:
            title_key = item.get('title', '').lower().strip()
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_items.append(item)
        
        print(f"🎯 Total unique items found: {len(unique_items)}")
        return unique_items

async def main():
    """Main function to run the scraper"""
    async with LaserMatchScraper() as scraper:
        items = await scraper.scrape_lasermatch()
        
        # Save results to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lasermatch_scraped_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(items, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {filename}")
        print(f"📊 Total items scraped: {len(items)}")
        
        # Print sample items
        if items:
            print("\n📋 Sample items:")
            for i, item in enumerate(items[:3]):
                print(f"{i+1}. {item.get('title', 'N/A')} - ${item.get('price', 0):,.2f}")
        
        return items

if __name__ == "__main__":
    asyncio.run(main())
