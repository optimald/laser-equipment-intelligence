#!/usr/bin/env python3
"""
Working Real Crawler - Selenium-based with feedback
"""

import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class WorkingRealCrawler:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        print("🔧 Setting up Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Chrome driver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            self.driver = None
    
    def close(self):
        """Close the driver"""
        if self.driver:
            print("🔒 Closing Chrome driver...")
            self.driver.quit()
    
    def search_ebay(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search eBay for laser equipment using real browser automation"""
        if not self.driver:
            print("❌ Driver not initialized")
            return []
        
        results = []
        try:
            # Construct eBay search URL
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
            
            print(f"🔍 Searching eBay: {query}")
            print(f"🌐 URL: {search_url}")
            
            self.driver.get(search_url)
            
            # Wait for page to load
            print("⏳ Waiting for page to load...")
            time.sleep(3)
            
            # Debug: Print page info
            print(f"📄 Page title: {self.driver.title}")
            print(f"🌐 Current URL: {self.driver.current_url}")
            
            # Check if we got blocked
            if 'challenge' in self.driver.current_url.lower() or 'captcha' in self.driver.current_url.lower():
                print("❌ Blocked by eBay challenge page")
                return []
            
            # Try multiple selectors for eBay items
            item_selectors = [
                ".s-item:not(.s-item__sep)",
                "[data-testid='item']",
                ".srp-results .s-item",
                ".srp-item"
            ]
            
            items = []
            for selector in item_selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        print(f"📦 Found {len(items)} items using selector: {selector}")
                        break
                except Exception as e:
                    print(f"⚠️ Selector {selector} failed: {e}")
                    continue
            
            if not items:
                print("⚠️ No items found with any selector")
                return []
            
            # Extract data from items
            for i, item in enumerate(items[:limit]):
                try:
                    result = self.extract_ebay_item(item, i)
                    if result:
                        results.append(result)
                        print(f"✅ Extracted item {i+1}: {result['title'][:50]}...")
                except Exception as e:
                    print(f"⚠️ Error extracting item {i}: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error searching eBay: {e}")
        
        return results
    
    def extract_ebay_item(self, item_element, index: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single eBay item element"""
        try:
            # Try multiple selectors for title
            title_selectors = [
                "h3 a",
                ".s-item__title a",
                "a[role='link']",
                "a"
            ]
            
            title = None
            url = None
            for selector in title_selectors:
                try:
                    title_element = item_element.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip()
                    url = title_element.get_attribute('href')
                    if title and url:
                        break
                except NoSuchElementException:
                    continue
            
            if not title:
                return None
            
            # Try to find price
            price_selectors = [
                ".s-item__price",
                ".notranslate",
                ".price"
            ]
            
            price = None
            for selector in price_selectors:
                try:
                    price_element = item_element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_element.text.strip()
                    price = self.parse_price(price_text)
                    if price:
                        break
                except NoSuchElementException:
                    continue
            
            # Extract brand and model from title
            brand, model = self.extract_brand_model(title)
            
            result = {
                'id': f"ebay_real_{index}",
                'title': title,
                'brand': brand,
                'model': model,
                'condition': "Used",
                'price': price,
                'location': "eBay",
                'description': f"eBay listing: {title}",
                'url': url,
                'images': [],
                'source': 'eBay',
                'discovered_at': datetime.now().isoformat(),
                'score_overall': 85 if price and price < 50000 else 75
            }
            
            return result
            
        except Exception as e:
            print(f"⚠️ Error extracting eBay item {index}: {e}")
            return None
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Parse price text to float"""
        try:
            # Remove currency symbols and extract numbers
            price_clean = re.sub(r'[^\d.,]', '', price_text)
            if price_clean:
                return float(price_clean.replace(',', ''))
        except (ValueError, TypeError):
            pass
        return None
    
    def extract_brand_model(self, title: str) -> tuple:
        """Extract brand and model from title using real equipment data"""
        title_lower = title.lower()
        
        # Real laser brands from actual equipment data (57 brands)
        brands = [
            'aerolase', 'aesthetic', 'agnes', 'allergan', 'alma', 'apyx', 'btl', 'bluecore', 'buffalo', 
            'candela', 'canfield', 'cocoon', 'cutera', 'cynosure', 'cytrellis', 'deka', 'dusa', 'edge', 
            'ellman', 'energist', 'envy', 'fotona', 'hk', 'ilooda', 'inmode', 'iridex', 'jeisys', 
            'laseroptek', 'lumenis', 'lutronic', 'luvo', 'merz', 'microaire', 'mixto', 'mrp', 'new', 
            'novoxel', 'ohmeda', 'perigee', 'pronox', 'quanta', 'quantel', 'rohrer', 'sandstone', 
            'sciton', 'she', 'sinclair', 'solta', 'syl', 'syneron', 'thermi', 'venus', 'wells', 
            'wontech', 'zimmer'
        ]
        
        for brand in brands:
            if brand in title_lower:
                # Try to extract model
                brand_index = title_lower.find(brand)
                remaining_text = title[brand_index + len(brand):].strip()
                
                # Look for model patterns
                model_match = re.search(r'([a-zA-Z0-9\s\-]+)', remaining_text)
                if model_match:
                    model = model_match.group(1).strip().title()
                    return brand.title(), model
                
                return brand.title(), "Unknown Model"
        
        return "Unknown", "Unknown"


def test_with_lasermatch_equipment():
    """Test with actual LaserMatch equipment"""
    print("🚀 Testing Real Crawler with LaserMatch Equipment")
    print("=" * 60)
    
    crawler = WorkingRealCrawler()
    
    try:
        # Test with actual LaserMatch equipment
        test_queries = [
            "Alma Lasers Harmony XL",
            "Candela GentleMax Pro", 
            "Sciton Joule"
        ]
        
        all_results = []
        
        for query in test_queries:
            print(f"\n🔍 Testing: {query}")
            print("-" * 40)
            
            results = crawler.search_ebay(query, limit=3)
            all_results.extend(results)
            
            print(f"✅ Found {len(results)} results for '{query}'")
            
            for i, result in enumerate(results):
                print(f"  {i+1}. {result['title'][:60]}...")
                print(f"     Brand: {result['brand']}, Model: {result['model']}")
                print(f"     Price: ${result.get('price', 'N/A')}")
        
        # Save all results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"real_crawler_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n💾 All results saved to: {filename}")
        print(f"🎯 Total results found: {len(all_results)}")
        
        return all_results
        
    finally:
        crawler.close()


if __name__ == "__main__":
    test_with_lasermatch_equipment()
