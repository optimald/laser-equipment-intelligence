#!/usr/bin/env python3
"""
Real Crawlers for Magic Find - Using Selenium to handle JavaScript-rendered content
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


class RealCrawler:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
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
            print("💡 Make sure ChromeDriver is installed and in PATH")
            self.driver = None
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
    
    def search_ebay(self, query: str, max_price: Optional[float] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search eBay for laser equipment using real browser automation"""
        if not self.driver:
            print("❌ Driver not initialized")
            return []
        
        results = []
        try:
            # Construct eBay search URL
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
            if max_price:
                search_url += f"&_udlo=0&_udhi={max_price}"
            
            print(f"🔍 Searching eBay: {search_url}")
            self.driver.get(search_url)
            
            # Wait a bit for page to load
            time.sleep(5)
            
            # Debug: Print page title and URL
            print(f"📄 Page title: {self.driver.title}")
            print(f"🌐 Current URL: {self.driver.current_url}")
            
            # Try multiple selectors for eBay items
            item_selectors = [
                "[data-testid='item']",
                ".s-item",
                ".srp-results .s-item",
                ".srp-item",
                ".item"
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
                # Debug: Print page source snippet
                page_source = self.driver.page_source
                print(f"🔍 Page source snippet (first 1000 chars): {page_source[:1000]}")
                
                # Try to find any elements that might be items
                all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                print(f"📊 Total div elements found: {len(all_divs)}")
                
                # Look for divs with item-like classes
                item_like_divs = [div for div in all_divs if any(cls in div.get_attribute('class') or '' for cls in ['item', 'listing', 'product'])]
                print(f"📦 Found {len(item_like_divs)} item-like divs")
                
                if item_like_divs:
                    items = item_like_divs[:10]  # Take first 10
            
            for i, item in enumerate(items[:limit]):
                try:
                    result = self.extract_ebay_item(item, i)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"⚠️ Error extracting item {i}: {e}")
                    continue
            
        except TimeoutException:
            print("⏰ Timeout waiting for eBay results to load")
        except Exception as e:
            print(f"❌ Error searching eBay: {e}")
        
        return results
    
    def extract_ebay_item(self, item_element, index: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single eBay item element"""
        try:
            # Debug: Print element HTML
            element_html = item_element.get_attribute('outerHTML')[:500]
            print(f"🔍 Item {index} HTML: {element_html}...")
            
            # Try multiple selectors for title
            title_selectors = [
                "[data-testid='item-title'] a",
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
                print(f"⚠️ Could not find title for item {index}")
                return None
            
            # Try multiple selectors for price
            price_selectors = [
                "[data-testid='item-price']",
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
            
            # Try to find condition
            condition_selectors = [
                "[data-testid='item-condition']",
                ".s-item__condition",
                ".condition"
            ]
            
            condition = "Used"
            for selector in condition_selectors:
                try:
                    condition_element = item_element.find_element(By.CSS_SELECTOR, selector)
                    condition = condition_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Try to find location
            location_selectors = [
                "[data-testid='item-location']",
                ".s-item__location",
                ".location"
            ]
            
            location = "Unknown"
            for selector in location_selectors:
                try:
                    location_element = item_element.find_element(By.CSS_SELECTOR, selector)
                    location = location_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Try to find image
            image_selectors = [
                "[data-testid='item-image'] img",
                ".s-item__image img",
                "img"
            ]
            
            image_url = None
            for selector in image_selectors:
                try:
                    image_element = item_element.find_element(By.CSS_SELECTOR, selector)
                    image_url = image_element.get_attribute('src')
                    if image_url:
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
                'condition': condition,
                'price': price,
                'location': location,
                'description': f"eBay listing: {title}",
                'url': url,
                'images': [image_url] if image_url else [],
                'source': 'eBay',
                'discovered_at': datetime.now().isoformat(),
                'score_overall': 85 if price and price < 50000 else 75
            }
            
            print(f"✅ Extracted item {index}: {title} - ${price}")
            return result
            
        except Exception as e:
            print(f"⚠️ Error extracting eBay item {index}: {e}")
            return None
    
    def search_equipment_network(self, query: str, max_price: Optional[float] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Equipment Network for laser equipment"""
        if not self.driver:
            return []
        
        results = []
        try:
            # Equipment Network search
            search_url = f"https://www.equipmentnetwork.com/search?q={quote_plus(query)}"
            print(f"🔍 Searching Equipment Network: {search_url}")
            self.driver.get(search_url)
            
            # Wait for results
            time.sleep(3)
            
            # Look for equipment listings
            items = self.driver.find_elements(By.CSS_SELECTOR, ".equipment-listing, .listing-item, .product-item")
            print(f"📦 Found {len(items)} items on Equipment Network")
            
            for i, item in enumerate(items[:limit]):
                try:
                    result = self.extract_equipment_network_item(item, i)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"⚠️ Error extracting Equipment Network item {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error searching Equipment Network: {e}")
        
        return results
    
    def extract_equipment_network_item(self, item_element, index: int) -> Optional[Dict[str, Any]]:
        """Extract data from Equipment Network item"""
        try:
            # This is a simplified extractor - would need to be customized based on actual site structure
            title_element = item_element.find_element(By.CSS_SELECTOR, "h3, h2, .title")
            title = title_element.text.strip()
            
            # Try to find price
            try:
                price_element = item_element.find_element(By.CSS_SELECTOR, ".price, .cost, .amount")
                price_text = price_element.text.strip()
                price = self.parse_price(price_text)
            except NoSuchElementException:
                price = None
            
            # Extract brand and model
            brand, model = self.extract_brand_model(title)
            
            return {
                'id': f"equipment_network_{index}",
                'title': title,
                'brand': brand,
                'model': model,
                'condition': "Used - Good",
                'price': price,
                'location': "Equipment Network",
                'description': f"Equipment Network listing: {title}",
                'url': "https://www.equipmentnetwork.com",
                'images': [],
                'source': 'Equipment Network',
                'discovered_at': datetime.now().isoformat(),
                'score_overall': 80 if price and price < 40000 else 70
            }
            
        except Exception as e:
            print(f"⚠️ Error extracting Equipment Network item {index}: {e}")
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
        """Extract brand and model from title"""
        title_lower = title.lower()
        
        # Common laser brands
        brands = [
            'aerolase', 'candela', 'cynosure', 'lumenis', 'syneron', 
            'alma', 'cutera', 'sciton', 'palomar', 'cooltouch', 
            'allergan', 'btl', 'apyx', 'venus', 'solta'
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
    
    def search_all_sources(self, query: str, max_price: Optional[float] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search all available sources for laser equipment"""
        all_results = []
        
        print(f"🚀 Starting comprehensive search for: '{query}'")
        if max_price:
            print(f"💰 Target price limit: ${max_price:,.2f}")
        
        # Search eBay
        print("\n📦 Searching eBay...")
        ebay_results = self.search_ebay(query, max_price, limit)
        all_results.extend(ebay_results)
        print(f"✅ Found {len(ebay_results)} items on eBay")
        
        # Search Equipment Network
        print("\n🏭 Searching Equipment Network...")
        equipment_results = self.search_equipment_network(query, max_price, limit)
        all_results.extend(equipment_results)
        print(f"✅ Found {len(equipment_results)} items on Equipment Network")
        
        # Sort by score and price
        all_results.sort(key=lambda x: (x.get('score_overall', 0), -(x.get('price', 0) or 0)), reverse=True)
        
        print(f"\n🎯 Total results found: {len(all_results)}")
        return all_results


def main():
    """Test the real crawlers"""
    crawler = RealCrawler()
    
    try:
        # Test search
        results = crawler.search_all_sources("aerolase lightpod", max_price=30000, limit=5)
        
        print("\n📋 Sample results:")
        for i, result in enumerate(results[:3]):
            print(f"{i+1}. {result['title']} - ${result.get('price', 'N/A')} ({result['source']})")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"real_crawler_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
