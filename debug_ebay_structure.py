#!/usr/bin/env python3
"""
Debug eBay Page Structure - See what we're actually getting
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus

def debug_ebay_structure():
    """Debug what we're actually getting from eBay"""
    
    print("🔍 Debugging eBay Page Structure")
    print("=" * 50)
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Test with a simple query
        query = "laser equipment"
        search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
        
        print(f"🌐 Searching: {search_url}")
        driver.get(search_url)
        time.sleep(5)  # Wait for page load
        
        print(f"📄 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        # Check if we got blocked
        if 'challenge' in driver.current_url.lower():
            print("❌ Blocked by challenge page")
            return
        
        # Get page source info
        page_source = driver.page_source
        print(f"📄 Page source length: {len(page_source)}")
        
        # Look for common eBay selectors
        selectors_to_test = [
            "div.s-item:not(.s-item__sep)",
            "div.s-item",
            "div[data-view*='item']",
            "div.srp-river-answer",
            "div[data-testid='item']",
            "div.item",
            "div[class*='s-item']",
            "div[class*='srp-item']",
            "a[href*='/itm/']"
        ]
        
        print("\n🔍 Testing Selectors:")
        print("-" * 30)
        
        for selector in selectors_to_test:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"✅ {selector}: {len(elements)} elements")
                
                # Show first few elements for debugging
                if elements and len(elements) > 0:
                    for i, element in enumerate(elements[:3]):
                        try:
                            text = element.text.strip()
                            print(f"   Element {i+1}: {text[:100]}...")
                            
                            # Check for links
                            links = element.find_elements(By.TAG_NAME, "a")
                            if links:
                                for j, link in enumerate(links[:2]):
                                    href = link.get_attribute('href')
                                    link_text = link.text.strip()
                                    print(f"     Link {j+1}: {link_text[:50]}... -> {href}")
                        except Exception as e:
                            print(f"   Element {i+1}: Error reading - {e}")
                            
            except Exception as e:
                print(f"❌ {selector}: Error - {e}")
        
        # Look for any text that might be titles
        print("\n📄 Looking for potential titles:")
        print("-" * 40)
        
        try:
            all_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            # Filter for lines that look like titles
            potential_titles = []
            for line in lines:
                if (len(line) > 20 and 
                    len(line) < 200 and 
                    not line.lower().startswith(('skip', 'sign', 'daily', 'help', 'sell', 'my ebay', 'ebay motors', 'fashion', 'electronics')) and
                    not line.lower().endswith(('free shipping', 'buy it now', 'or best offer'))):
                    potential_titles.append(line)
            
            print(f"Found {len(potential_titles)} potential titles:")
            for i, title in enumerate(potential_titles[:10]):
                print(f"  {i+1}. {title}")
                
        except Exception as e:
            print(f"Error analyzing text: {e}")
        
        # Look for price patterns
        print("\n💰 Looking for prices:")
        print("-" * 25)
        
        try:
            import re
            all_text = driver.find_element(By.TAG_NAME, "body").text
            prices = re.findall(r'\$[\d,]+\.?\d*', all_text)
            print(f"Found {len(prices)} price patterns:")
            for i, price in enumerate(prices[:10]):
                print(f"  {i+1}. {price}")
        except Exception as e:
            print(f"Error finding prices: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_ebay_structure()
