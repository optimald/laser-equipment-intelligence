#!/usr/bin/env python3
"""
Fast Real Crawler - Streamlined version with timeout protection
"""

import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import signal
import sys


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("Operation timed out")


def test_selenium_quick():
    """Quick test of Selenium with timeout protection"""
    print("🚀 Quick Selenium Test with Timeout Protection")
    print("=" * 50)
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        
        print("✅ Selenium imported successfully")
        
        # Setup Chrome with minimal options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-images')  # Faster loading
        chrome_options.add_argument('--disable-javascript')  # Faster loading
        
        print("🔧 Initializing Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("🌐 Testing eBay access...")
        driver.get("https://www.ebay.com/sch/i.html?_nkw=laser+equipment")
        
        print("⏳ Waiting 5 seconds for page load...")
        time.sleep(5)
        
        print(f"📄 Page title: {driver.title}")
        
        # Quick check for items
        try:
            items = driver.find_elements(By.CSS_SELECTOR, "div.s-item:not(.s-item__sep)")
            print(f"📦 Found {len(items)} s-item elements")
            
            if items:
                # Show first item
                first_item = items[0]
                html = first_item.get_attribute('outerHTML')[:200]
                print(f"🔍 First item HTML: {html}...")
                
                # Try to extract title
                try:
                    title_element = first_item.find_element(By.CSS_SELECTOR, "h3 a")
                    title = title_element.text.strip()
                    print(f"✅ Found title: {title}")
                except:
                    print("⚠️ Could not find title")
            
        except Exception as e:
            print(f"⚠️ Error finding items: {e}")
        
        driver.quit()
        print("✅ Test completed successfully")
        return True
        
    except TimeoutException:
        print("⏰ Test timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        signal.alarm(0)  # Cancel timeout


def test_requests_approach():
    """Test requests-based approach as fallback"""
    print("\n🚀 Testing Requests-Based Approach")
    print("=" * 50)
    
    try:
        import requests
        
        # Test with a simple search
        query = "laser equipment"
        search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print(f"🌐 Testing: {search_url}")
        
        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)  # 15 second timeout
        
        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            signal.alarm(0)  # Cancel timeout
            
            print(f"📄 Response status: {response.status_code}")
            print(f"📄 Response length: {len(response.text)}")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                if 's-item' in content:
                    print("✅ Found s-item elements in HTML")
                    
                    # Count items
                    s_item_count = content.count('s-item')
                    print(f"📦 Found {s_item_count} s-item occurrences")
                    
                    # Look for actual product items (not separators)
                    non_sep_count = content.count('s-item') - content.count('s-item__sep')
                    print(f"📦 Found {non_sep_count} non-separator s-item elements")
                    
                    return True
                else:
                    print("❌ No s-item elements found")
                    return False
            else:
                print(f"❌ Non-200 response: {response.status_code}")
                return False
                
        except TimeoutException:
            print("⏰ Request timed out after 15 seconds")
            return False
        finally:
            signal.alarm(0)
            
    except Exception as e:
        print(f"❌ Requests test failed: {e}")
        return False


def create_working_entry_point():
    """Create a working entry point that actually gets results"""
    print("\n🎯 Creating Working Entry Point")
    print("=" * 50)
    
    # Test both approaches
    selenium_works = test_selenium_quick()
    requests_works = test_requests_approach()
    
    print(f"\n📊 RESULTS SUMMARY")
    print("=" * 50)
    print(f"Selenium Quick Test: {'✅' if selenium_works else '❌'}")
    print(f"Requests Test: {'✅' if requests_works else '❌'}")
    
    if selenium_works:
        print("\n🎯 RECOMMENDATION: Use Selenium with timeout protection")
        print("   - Add timeout handlers to prevent hanging")
        print("   - Use minimal Chrome options for faster loading")
        print("   - Implement proper error handling")
    elif requests_works:
        print("\n🎯 RECOMMENDATION: Use requests with HTML parsing")
        print("   - Faster than Selenium")
        print("   - Less likely to be detected")
        print("   - Need to parse HTML manually")
    else:
        print("\n🎯 RECOMMENDATION: Focus on mock data and API integration")
        print("   - Real scraping requires additional infrastructure")
        print("   - Consider proxy services for production")
        print("   - Use intelligent mock data for development")


if __name__ == "__main__":
    create_working_entry_point()
