#!/usr/bin/env python3
"""
Debug eBay page structure to find correct selectors
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus


def debug_ebay_structure():
    """Debug eBay page structure to find correct selectors"""
    print("🔍 Debugging eBay page structure...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Search for a common item
        query = "laser equipment"
        search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
        
        print(f"🌐 Loading: {search_url}")
        driver.get(search_url)
        time.sleep(3)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        # Check if blocked
        if 'challenge' in driver.current_url.lower():
            print("❌ Blocked by challenge page")
            return
        
        # Get page source snippet
        page_source = driver.page_source
        print(f"📄 Page source length: {len(page_source)}")
        
        # Look for common item indicators
        indicators = ['s-item', 'item', 'listing', 'product', 'srp-item']
        for indicator in indicators:
            count = page_source.lower().count(indicator)
            print(f"🔍 Found '{indicator}': {count} occurrences")
        
        # Try to find any div elements
        all_divs = driver.find_elements(By.TAG_NAME, "div")
        print(f"📊 Total div elements: {len(all_divs)}")
        
        # Look for divs with item-like classes
        item_classes = ['item', 'listing', 'product', 's-item', 'srp-item']
        for class_name in item_classes:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, f"div[class*='{class_name}']")
                print(f"📦 Found {len(elements)} divs with class containing '{class_name}'")
                
                if elements:
                    # Show first element's HTML
                    first_element = elements[0]
                    html = first_element.get_attribute('outerHTML')[:200]
                    print(f"   First element HTML: {html}...")
                    
            except Exception as e:
                print(f"⚠️ Error with class '{class_name}': {e}")
        
        # Try different selectors
        selectors_to_try = [
            "div[class*='s-item']",
            "div[class*='item']",
            "div[class*='listing']",
            "div[class*='product']",
            ".s-item",
            ".item",
            ".listing",
            ".product",
            "[data-testid*='item']",
            "[data-testid*='listing']"
        ]
        
        print("\n🔍 Testing selectors:")
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"   {selector}: {len(elements)} elements")
                
                if elements and len(elements) > 0:
                    # Show first element
                    first_element = elements[0]
                    html = first_element.get_attribute('outerHTML')[:300]
                    print(f"      First: {html}...")
                    
            except Exception as e:
                print(f"   {selector}: Error - {e}")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    debug_ebay_structure()
