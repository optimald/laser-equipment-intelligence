#!/usr/bin/env python3
"""
Debug eBay with Longer Wait - Try to get actual content
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from urllib.parse import quote_plus

def debug_with_wait():
    """Debug eBay with longer wait times"""
    
    print("🔍 Debugging eBay with Longer Wait Times")
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
        
        # Wait longer for content to load
        print("⏳ Waiting 10 seconds for content to load...")
        time.sleep(10)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        # Check if we got blocked
        if 'challenge' in driver.current_url.lower():
            print("❌ Blocked by challenge page")
            return
        
        # Try to wait for specific elements
        print("\n🔍 Waiting for specific elements...")
        
        try:
            # Wait for any s-item elements
            wait = WebDriverWait(driver, 10)
            items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='s-item']")))
            print(f"✅ Found {len(items)} s-item elements after wait")
        except TimeoutException:
            print("❌ Timeout waiting for s-item elements")
            items = driver.find_elements(By.CSS_SELECTOR, "div[class*='s-item']")
            print(f"📦 Found {len(items)} s-item elements without wait")
        
        # Filter out separators and examine actual items
        actual_items = []
        for item in items:
            try:
                class_name = item.get_attribute('class')
                if 's-item__sep' not in class_name:
                    actual_items.append(item)
            except:
                pass
        
        print(f"📦 Found {len(actual_items)} actual product items")
        
        # Examine actual items
        for i, item in enumerate(actual_items[:5]):
            print(f"\n🔍 Item {i+1} Analysis:")
            print("-" * 30)
            
            try:
                # Get text content
                text = item.text.strip()
                print(f"Text content: {text[:200]}...")
                
                # Look for any links
                links = item.find_elements(By.TAG_NAME, "a")
                print(f"Links found: {len(links)}")
                
                for j, link in enumerate(links[:3]):
                    try:
                        href = link.get_attribute('href')
                        link_text = link.text.strip()
                        print(f"  Link {j+1}: '{link_text}' -> {href}")
                    except Exception as e:
                        print(f"  Link {j+1}: Error - {e}")
                
                # Look for any text elements
                all_elements = item.find_elements(By.XPATH, ".//*")
                print(f"Total elements: {len(all_elements)}")
                
                # Find elements with text
                text_elements = []
                for elem in all_elements:
                    try:
                        elem_text = elem.text.strip()
                        if elem_text and len(elem_text) > 5:
                            text_elements.append((elem.tag_name, elem_text[:50]))
                    except:
                        pass
                
                print(f"Elements with text: {len(text_elements)}")
                for tag, text in text_elements[:5]:
                    print(f"  {tag}: {text}...")
                
            except Exception as e:
                print(f"Error analyzing item {i+1}: {e}")
        
        # Try a different approach - look for any divs with meaningful content
        print(f"\n🔍 Alternative approach - looking for meaningful divs:")
        print("-" * 60)
        
        all_divs = driver.find_elements(By.TAG_NAME, "div")
        meaningful_divs = []
        
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
                        if '/itm/' in href:
                            meaningful_divs.append(div)
                            break
            except:
                continue
        
        print(f"Found {len(meaningful_divs)} meaningful divs")
        
        for i, div in enumerate(meaningful_divs[:3]):
            try:
                text = div.text.strip()
                print(f"\nMeaningful div {i+1}:")
                print(f"  Text: {text[:150]}...")
                
                links = div.find_elements(By.TAG_NAME, "a")
                for j, link in enumerate(links[:2]):
                    href = link.get_attribute('href')
                    link_text = link.text.strip()
                    print(f"  Link {j+1}: '{link_text}' -> {href}")
                    
            except Exception as e:
                print(f"Error with meaningful div {i+1}: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_with_wait()
