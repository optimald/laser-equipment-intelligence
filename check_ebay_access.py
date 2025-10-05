#!/usr/bin/env python3
"""
Check if eBay is blocking us and what page we're actually getting
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus


def check_ebay_access():
    """Check if eBay is blocking us"""
    print("🔍 Checking eBay access...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Try different approaches
        urls_to_test = [
            "https://www.ebay.com",
            "https://www.ebay.com/sch/i.html?_nkw=laser+equipment",
            "https://www.ebay.com/sch/i.html?_nkw=test"
        ]
        
        for url in urls_to_test:
            print(f"\n🌐 Testing: {url}")
            driver.get(url)
            time.sleep(3)
            
            print(f"📄 Page title: {driver.title}")
            print(f"🌐 Current URL: {driver.current_url}")
            
            # Check if we're on a challenge page
            if 'challenge' in driver.current_url.lower() or 'captcha' in driver.current_url.lower():
                print("❌ BLOCKED: Challenge/captcha page detected")
            elif 'error' in driver.current_url.lower():
                print("❌ BLOCKED: Error page detected")
            elif driver.title == "www.ebay.com":
                print("⚠️ SUSPICIOUS: Generic title suggests possible blocking")
            else:
                print("✅ Appears to be normal eBay page")
            
            # Check page content
            page_source = driver.page_source
            print(f"📄 Page source length: {len(page_source)}")
            
            # Look for specific indicators
            if 'eBay' in page_source:
                print("✅ Contains 'eBay' text")
            else:
                print("⚠️ Does not contain 'eBay' text")
            
            if 'search' in page_source.lower():
                print("✅ Contains 'search' text")
            else:
                print("⚠️ Does not contain 'search' text")
            
            if 'item' in page_source.lower():
                print("✅ Contains 'item' text")
            else:
                print("⚠️ Does not contain 'item' text")
        
        # Try a simple search with different parameters
        print(f"\n🔍 Testing simple search...")
        simple_url = "https://www.ebay.com/sch/i.html?_nkw=test"
        driver.get(simple_url)
        time.sleep(5)
        
        print(f"📄 Simple search title: {driver.title}")
        print(f"🌐 Simple search URL: {driver.current_url}")
        
        # Try to find ANY elements
        all_elements = driver.find_elements("tag name", "div")
        print(f"📊 Total div elements: {len(all_elements)}")
        
        # Look for any text content
        body_text = driver.find_element("tag name", "body").text
        print(f"📄 Body text length: {len(body_text)}")
        print(f"📄 Body text preview: {body_text[:200]}...")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    check_ebay_access()
