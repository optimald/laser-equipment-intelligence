#!/usr/bin/env python3
"""
Test Real Crawler Until We Get Actual Results
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
import signal


class PersistentEbayCrawler:
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
    
    def test_multiple_queries(self):
        """Test multiple queries until we get at least 1 result"""
        
        # Test queries - from specific to general
        test_queries = [
            "laser equipment",
            "medical laser",
            "aesthetic laser",
            "laser system",
            "laser machine",
            "beauty laser",
            "cosmetic laser",
            "laser device",
            "laser",
            "equipment"
        ]
        
        for i, query in enumerate(test_queries):
            print(f"\n🔍 Test {i+1}/{len(test_queries)}: '{query}'")
            print("-" * 50)
            
            results = self.search_ebay_comprehensive(query)
            
            if results:
                print(f"🎯 SUCCESS! Found {len(results)} results for '{query}'")
                return results, query
            else:
                print(f"❌ No results for '{query}'")
        
        return [], "No successful query found"
    
    def search_ebay_comprehensive(self, query: str) -> List[Dict[str, Any]]:
        """Comprehensive eBay search with multiple strategies"""
        if not self.driver:
            print("❌ Driver not initialized")
            return []
        
        try:
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
            print(f"🌐 Searching: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(5)  # Wait longer for page load
            
            print(f"📄 Page title: {self.driver.title}")
            print(f"🌐 Current URL: {self.driver.current_url}")
            
            # Check if blocked
            if 'challenge' in self.driver.current_url.lower():
                print("❌ Blocked by challenge page")
                return []
            
            # Strategy 1: Look for s-item elements
            items = self.find_items_strategy_1()
            if items:
                print(f"✅ Strategy 1 found {len(items)} items")
                return self.extract_items(items[:5])
            
            # Strategy 2: Look for links
            items = self.find_items_strategy_2()
            if items:
                print(f"✅ Strategy 2 found {len(items)} items")
                return self.extract_items(items[:5])
            
            # Strategy 3: Look for any meaningful content
            items = self.find_items_strategy_3()
            if items:
                print(f"✅ Strategy 3 found {len(items)} items")
                return self.extract_items(items[:5])
            
            # Strategy 4: Debug page structure
            self.debug_page_structure()
            
            return []
            
        except Exception as e:
            print(f"❌ Error searching eBay: {e}")
            return []
    
    def find_items_strategy_1(self):
        """Strategy 1: Look for s-item elements"""
        try:
            items = self.driver.find_elements(By.CSS_SELECTOR, "div.s-item:not(.s-item__sep)")
            print(f"📦 Strategy 1: Found {len(items)} s-item elements")
            return items
        except Exception as e:
            print(f"⚠️ Strategy 1 failed: {e}")
            return []
    
    def find_items_strategy_2(self):
        """Strategy 2: Look for eBay item links"""
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/itm/']")
            print(f"📦 Strategy 2: Found {len(links)} eBay item links")
            
            # Convert links to containers
            items = []
            for link in links[:20]:
                try:
                    # Find parent container
                    parent = link.find_element(By.XPATH, "./ancestor::div[1]")
                    if parent not in items:
                        items.append(parent)
                except:
                    items.append(link)
            
            return items
        except Exception as e:
            print(f"⚠️ Strategy 2 failed: {e}")
            return []
    
    def find_items_strategy_3(self):
        """Strategy 3: Look for any divs with meaningful content"""
        try:
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            print(f"📦 Strategy 3: Found {len(all_divs)} total divs")
            
            potential_items = []
            for div in all_divs:
                try:
                    text = div.text.strip()
                    links = div.find_elements(By.TAG_NAME, "a")
                    
                    # Look for divs with reasonable content
                    if (links and 
                        len(text) > 20 and 
                        len(text) < 300 and
                        not text.lower().startswith(('skip', 'sign in', 'daily deals', 'help', 'sell'))):
                        
                        # Check if any link looks like an item link
                        for link in links:
                            href = link.get_attribute('href') or ''
                            if '/itm/' in href or 'ebay.com' in href:
                                potential_items.append(div)
                                break
                except:
                    continue
            
            print(f"📦 Strategy 3: Found {len(potential_items)} potential items")
            return potential_items[:20]
        except Exception as e:
            print(f"⚠️ Strategy 3 failed: {e}")
            return []
    
    def debug_page_structure(self):
        """Debug page structure to understand what we're getting"""
        print("\n🔍 DEBUGGING PAGE STRUCTURE:")
        
        try:
            # Get page source info
            page_source = self.driver.page_source
            print(f"📄 Page source length: {len(page_source)}")
            
            # Look for common indicators
            indicators = ['s-item', 'item', 'listing', 'product', 'srp-item', 'result']
            for indicator in indicators:
                count = page_source.lower().count(indicator)
                print(f"🔍 Found '{indicator}': {count} occurrences")
            
            # Look for any links
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"🔗 Total links found: {len(all_links)}")
            
            # Check first few links
            for i, link in enumerate(all_links[:5]):
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    print(f"   Link {i+1}: {text[:50]}... -> {href}")
                except:
                    pass
            
            # Look for any text that might be titles
            all_text = self.driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            print(f"📄 Total text lines: {len(lines)}")
            
            # Show first few meaningful lines
            meaningful_lines = [line for line in lines if len(line) > 10 and not line.lower().startswith(('skip', 'sign', 'daily', 'help', 'sell', 'my ebay'))]
            print(f"📄 Meaningful lines: {len(meaningful_lines)}")
            
            for i, line in enumerate(meaningful_lines[:5]):
                print(f"   Line {i+1}: {line[:80]}...")
                
        except Exception as e:
            print(f"⚠️ Debug failed: {e}")
    
    def extract_items(self, items) -> List[Dict[str, Any]]:
        """Extract data from items"""
        results = []
        
        for i, item in enumerate(items):
            try:
                result = self.extract_item(item, i)
                if result:
                    results.append(result)
                    print(f"✅ Extracted item {i+1}: {result['title'][:50]}...")
            except Exception as e:
                print(f"⚠️ Error extracting item {i}: {e}")
                continue
        
        return results
    
    def extract_item(self, item_element, index: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single item element"""
        try:
            # Try multiple approaches to find title
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
                        if link_text and len(link_text) > 10:
                            title = link_text
                            url = link.get_attribute('href')
                            break
                except:
                    pass
            
            # Approach 3: Look for any text that might be a title
            if not title:
                try:
                    all_text = item_element.text.strip()
                    lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                    if lines:
                        for line in sorted(lines, key=len, reverse=True):
                            if len(line) > 10 and not line.lower().startswith(('$', 'free', 'shipping', 'skip', 'sign')):
                                title = line
                                break
                except:
                    pass
            
            if not title:
                return None
            
            # Try to find price
            price = None
            try:
                all_text = item_element.text
                price_match = re.search(r'\$[\d,]+\.?\d*', all_text)
                if price_match:
                    price = self.parse_price(price_match.group())
            except:
                pass
            
            # Extract brand and model
            brand, model = self.extract_brand_model(title)
            
            result = {
                'id': f"ebay_test_{index}",
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
                return brand.title(), "Unknown Model"
        
        return "Unknown", "Unknown"


def main():
    """Test until we get at least 1 actual result"""
    print("🚀 Testing Real Crawler Until We Get Actual Results")
    print("=" * 60)
    
    crawler = PersistentEbayCrawler()
    
    try:
        results, successful_query = crawler.test_multiple_queries()
        
        if results:
            print(f"\n🎯 SUCCESS! Found {len(results)} results for query: '{successful_query}'")
            print("=" * 60)
            
            for i, result in enumerate(results):
                print(f"\n{i+1}. {result['title']}")
                print(f"   Brand: {result['brand']}, Model: {result['model']}")
                print(f"   Price: ${result.get('price', 'N/A')}")
                print(f"   URL: {result.get('url', 'N/A')}")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"actual_results_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n💾 Results saved to: {filename}")
            return True
        else:
            print(f"\n❌ FAILED: No results found with any query")
            return False
            
    finally:
        crawler.close()


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ TEST SUCCESSFUL - Found actual results!")
    else:
        print("\n❌ TEST FAILED - No actual results found")
