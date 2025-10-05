#!/usr/bin/env python3
"""
Debug Individual eBay Item - See the actual structure
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus

def debug_individual_item():
    """Debug individual eBay item structure"""
    
    print("🔍 Debugging Individual eBay Item Structure")
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
        
        # Find s-item elements
        items = driver.find_elements(By.CSS_SELECTOR, "div[class*='s-item']")
        print(f"📦 Found {len(items)} s-item elements")
        
        if items:
            # Examine the first few items in detail
            for i, item in enumerate(items[:3]):
                print(f"\n🔍 Item {i+1} Analysis:")
                print("-" * 30)
                
                try:
                    # Get the HTML structure
                    html = item.get_attribute('outerHTML')
                    print(f"HTML length: {len(html)}")
                    print(f"HTML preview: {html[:200]}...")
                    
                    # Get all text
                    text = item.text.strip()
                    print(f"Text: {text}")
                    
                    # Look for specific elements
                    print("\nLooking for specific elements:")
                    
                    # Title elements
                    title_selectors = [
                        "h3",
                        "h2", 
                        "a",
                        ".s-item__title",
                        "[class*='title']"
                    ]
                    
                    for selector in title_selectors:
                        try:
                            elements = item.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                print(f"  {selector}: {len(elements)} elements")
                                for j, elem in enumerate(elements[:2]):
                                    elem_text = elem.text.strip()
                                    if elem_text:
                                        print(f"    {j+1}. {elem_text[:80]}...")
                        except:
                            pass
                    
                    # Price elements
                    price_selectors = [
                        ".s-item__price",
                        "[class*='price']",
                        ".notranslate",
                        "span"
                    ]
                    
                    print("\nPrice elements:")
                    for selector in price_selectors:
                        try:
                            elements = item.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                print(f"  {selector}: {len(elements)} elements")
                                for j, elem in enumerate(elements[:2]):
                                    elem_text = elem.text.strip()
                                    if elem_text and '$' in elem_text:
                                        print(f"    {j+1}. {elem_text}")
                        except:
                            pass
                    
                    # Link elements
                    links = item.find_elements(By.TAG_NAME, "a")
                    print(f"\nLinks: {len(links)} found")
                    for j, link in enumerate(links[:3]):
                        try:
                            href = link.get_attribute('href')
                            link_text = link.text.strip()
                            print(f"  {j+1}. {link_text[:50]}... -> {href}")
                        except:
                            pass
                    
                    print("\n" + "="*50)
                    
                except Exception as e:
                    print(f"Error analyzing item {i+1}: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_individual_item()
