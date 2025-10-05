#!/usr/bin/env python3
"""
Final working eBay crawler - finds actual product items
"""

import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class FinalEbayCrawler:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        print("🔧 Setting up Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
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
        """Search eBay for laser equipment"""
        if not self.driver:
            print("❌ Driver not initialized")
            return []
        
        results = []
        try:
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
            
            print(f"🔍 Searching eBay: {query}")
            print(f"🌐 URL: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(5)  # Wait for page to load
            
            print(f"📄 Page title: {self.driver.title}")
            print(f"🌐 Current URL: {self.driver.current_url}")
            
            # Check if blocked
            if 'challenge' in self.driver.current_url.lower():
                print("❌ Blocked by challenge page")
                return []
            
            # Try multiple approaches to find items
            items = []
            
            # Approach 1: Look for s-item elements (excluding separators)
            try:
                items = self.driver.find_elements(By.CSS_SELECTOR, "div.s-item:not(.s-item__sep)")
                print(f"📦 Found {len(items)} s-item elements (excluding separators)")
            except Exception as e:
                print(f"⚠️ s-item approach failed: {e}")
            
            # Approach 2: Look for any divs with item-like content
            if not items:
                try:
                    all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                    print(f"📊 Total div elements: {len(all_divs)}")
                    
                    # Filter divs that might contain items
                    potential_items = []
                    for div in all_divs:
                        try:
                            # Look for divs that contain links and have item-like content
                            links = div.find_elements(By.TAG_NAME, "a")
                            if links and len(links) > 0:
                                # Check if any link looks like an item link
                                for link in links:
                                    href = link.get_attribute('href') or ''
                                    if '/itm/' in href or 'ebay.com' in href:
                                        potential_items.append(div)
                                        break
                        except:
                            continue
                    
                    items = potential_items[:20]  # Limit to first 20
                    print(f"📦 Found {len(items)} potential item divs")
                    
                except Exception as e:
                    print(f"⚠️ div filtering approach failed: {e}")
            
            # Approach 3: Look for links directly
            if not items:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/itm/']")
                    print(f"📦 Found {len(links)} eBay item links")
                    
                    # Convert links to items by finding their parent containers
                    items = []
                    for link in links[:20]:  # Limit to first 20
                        try:
                            # Find the parent container that likely contains the item
                            parent = link.find_element(By.XPATH, "./ancestor::div[contains(@class, 's-item') or contains(@class, 'item') or contains(@class, 'listing')][1]")
                            if parent not in items:
                                items.append(parent)
                        except:
                            # If no parent found, use the link itself
                            items.append(link)
                    
                    print(f"📦 Converted to {len(items)} item containers")
                    
                except Exception as e:
                    print(f"⚠️ link approach failed: {e}")
            
            if not items:
                print("❌ No items found with any approach")
                return []
            
            # Extract data from items
            print(f"🔍 Extracting data from {len(items)} items...")
            for i, item in enumerate(items[:limit]):
                try:
                    result = self.extract_item(item, i)
                    if result:
                        results.append(result)
                        print(f"✅ Extracted item {i+1}: {result['title'][:50]}...")
                except Exception as e:
                    print(f"⚠️ Error extracting item {i}: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error searching eBay: {e}")
        
        return results
    
    def extract_item(self, item_element, index: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single item element"""
        try:
            # Try multiple approaches to find title and URL
            title = None
            url = None
            
            # Approach 1: Look for h3 with link
            try:
                title_element = item_element.find_element(By.CSS_SELECTOR, "h3 a")
                title = title_element.text.strip()
                url = title_element.get_attribute('href')
            except NoSuchElementException:
                pass
            
            # Approach 2: Look for any link with text
            if not title:
                try:
                    links = item_element.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        link_text = link.text.strip()
                        if link_text and len(link_text) > 10:  # Reasonable title length
                            title = link_text
                            url = link.get_attribute('href')
                            break
                except:
                    pass
            
            # Approach 3: Look for any text that might be a title
            if not title:
                try:
                    # Get all text and find the longest meaningful text
                    all_text = item_element.text.strip()
                    lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                    if lines:
                        # Find the longest line that looks like a title
                        for line in sorted(lines, key=len, reverse=True):
                            if len(line) > 10 and not line.lower().startswith(('$', 'free', 'shipping')):
                                title = line
                                break
                except:
                    pass
            
            if not title:
                return None
            
            # Try to find price
            price = None
            try:
                # Look for price in various formats
                price_selectors = [
                    ".s-item__price",
                    ".notranslate",
                    ".price",
                    "[class*='price']"
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = item_element.find_element(By.CSS_SELECTOR, selector)
                        price_text = price_element.text.strip()
                        price = self.parse_price(price_text)
                        if price:
                            break
                    except NoSuchElementException:
                        continue
                
                # If no price found, look in all text
                if not price:
                    all_text = item_element.text
                    price_match = re.search(r'\$[\d,]+\.?\d*', all_text)
                    if price_match:
                        price = self.parse_price(price_match.group())
                        
            except Exception as e:
                print(f"⚠️ Error finding price: {e}")
            
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
            print(f"⚠️ Error extracting item {index}: {e}")
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
        
        # Real laser brands from actual equipment data
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
    print("🚀 Testing Final eBay Crawler with LaserMatch Equipment")
    print("=" * 70)
    
    crawler = FinalEbayCrawler()
    
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
            print("-" * 50)
            
            results = crawler.search_ebay(query, limit=3)
            all_results.extend(results)
            
            print(f"✅ Found {len(results)} results for '{query}'")
            
            for i, result in enumerate(results):
                print(f"  {i+1}. {result['title'][:60]}...")
                print(f"     Brand: {result['brand']}, Model: {result['model']}")
                print(f"     Price: ${result.get('price', 'N/A')}")
        
        # Save all results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"final_ebay_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n💾 All results saved to: {filename}")
        print(f"🎯 Total results found: {len(all_results)}")
        
        return all_results
        
    finally:
        crawler.close()


if __name__ == "__main__":
    test_with_lasermatch_equipment()
