#!/usr/bin/env python3
"""
Debug Actual eBay Product Items - Skip separators
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus

def debug_actual_items():
    """Debug actual eBay product items (not separators)"""
    
    print("🔍 Debugging Actual eBay Product Items")
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
        
        # Find s-item elements but exclude separators
        all_items = driver.find_elements(By.CSS_SELECTOR, "div[class*='s-item']")
        print(f"📦 Found {len(all_items)} total s-item elements")
        
        # Filter out separators
        actual_items = []
        for item in all_items:
            try:
                class_name = item.get_attribute('class')
                if 's-item__sep' not in class_name:
                    actual_items.append(item)
            except:
                pass
        
        print(f"📦 Found {len(actual_items)} actual product items (excluding separators)")
        
        if actual_items:
            # Examine the first few actual items
            for i, item in enumerate(actual_items[:5]):
                print(f"\n🔍 Actual Item {i+1} Analysis:")
                print("-" * 40)
                
                try:
                    # Get the HTML structure
                    html = item.get_attribute('outerHTML')
                    print(f"HTML length: {len(html)}")
                    
                    # Get all text
                    text = item.text.strip()
                    print(f"Text: {text[:200]}...")
                    
                    # Look for title
                    print("\nLooking for title:")
                    title_selectors = [
                        "h3 a",
                        "h3",
                        "a[role='link']",
                        "a",
                        ".s-item__title",
                        "[class*='title']"
                    ]
                    
                    title_found = False
                    for selector in title_selectors:
                        try:
                            elements = item.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                for elem in elements:
                                    elem_text = elem.text.strip()
                                    if elem_text and len(elem_text) > 10:
                                        print(f"  ✅ Title found with {selector}: {elem_text[:100]}...")
                                        title_found = True
                                        
                                        # Get URL if it's a link
                                        try:
                                            href = elem.get_attribute('href')
                                            if href:
                                                print(f"     URL: {href}")
                                        except:
                                            pass
                                        break
                                if title_found:
                                    break
                        except:
                            pass
                    
                    if not title_found:
                        print("  ❌ No title found")
                    
                    # Look for price
                    print("\nLooking for price:")
                    price_found = False
                    try:
                        all_text = item.text
                        import re
                        prices = re.findall(r'\$[\d,]+\.?\d*', all_text)
                        if prices:
                            print(f"  ✅ Prices found: {prices}")
                            price_found = True
                    except:
                        pass
                    
                    if not price_found:
                        print("  ❌ No price found")
                    
                    # Look for links
                    links = item.find_elements(By.TAG_NAME, "a")
                    print(f"\nLinks: {len(links)} found")
                    for j, link in enumerate(links[:3]):
                        try:
                            href = link.get_attribute('href')
                            link_text = link.text.strip()
                            if href and '/itm/' in href:
                                print(f"  ✅ Item link {j+1}: {link_text[:50]}... -> {href}")
                        except:
                            pass
                    
                    print("\n" + "="*60)
                    
                except Exception as e:
                    print(f"Error analyzing item {i+1}: {e}")
        
        # Also try the link-based approach
        print(f"\n🔗 Link-based approach:")
        print("-" * 30)
        
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/itm/']")
        print(f"Found {len(links)} eBay item links")
        
        for i, link in enumerate(links[:3]):
            try:
                href = link.get_attribute('href')
                link_text = link.text.strip()
                print(f"Link {i+1}: {link_text[:80]}... -> {href}")
                
                # Find parent container
                parent = link.find_element(By.XPATH, "./ancestor::div[1]")
                parent_text = parent.text.strip()
                print(f"  Parent text: {parent_text[:100]}...")
                
            except Exception as e:
                print(f"Error with link {i+1}: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_actual_items()
