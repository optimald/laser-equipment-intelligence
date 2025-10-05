#!/usr/bin/env python3
"""
Find actual eBay product items
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus


def find_ebay_products():
    """Find actual eBay product items"""
    print("🔍 Finding actual eBay product items...")
    
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
        time.sleep(5)  # Wait longer for page to load
        
        print(f"📄 Page title: {driver.title}")
        
        # Look for actual product items (not separators)
        # eBay uses s-item but we need to exclude s-item__sep
        try:
            # Try to find items that are NOT separators
            items = driver.find_elements(By.CSS_SELECTOR, "div.s-item:not(.s-item__sep)")
            print(f"📦 Found {len(items)} s-item elements (excluding separators)")
            
            if items:
                for i, item in enumerate(items[:3]):  # Show first 3
                    try:
                        html = item.get_attribute('outerHTML')[:500]
                        print(f"\n🔍 Item {i+1}:")
                        print(f"   HTML: {html}...")
                        
                        # Try to find title
                        try:
                            title_element = item.find_element(By.CSS_SELECTOR, "h3 a, .s-item__title a")
                            title = title_element.text.strip()
                            print(f"   Title: {title}")
                        except:
                            print("   Title: Not found")
                        
                        # Try to find price
                        try:
                            price_element = item.find_element(By.CSS_SELECTOR, ".s-item__price")
                            price = price_element.text.strip()
                            print(f"   Price: {price}")
                        except:
                            print("   Price: Not found")
                            
                    except Exception as e:
                        print(f"   Error processing item {i+1}: {e}")
            
        except Exception as e:
            print(f"❌ Error finding s-item elements: {e}")
        
        # Try alternative approach - look for any elements with links
        try:
            print("\n🔍 Alternative approach - looking for links...")
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/itm/']")
            print(f"📦 Found {len(links)} eBay item links")
            
            if links:
                for i, link in enumerate(links[:3]):
                    try:
                        title = link.text.strip()
                        href = link.get_attribute('href')
                        print(f"   Link {i+1}: {title[:50]}...")
                        print(f"   URL: {href}")
                    except Exception as e:
                        print(f"   Error processing link {i+1}: {e}")
                        
        except Exception as e:
            print(f"❌ Error finding links: {e}")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    find_ebay_products()
