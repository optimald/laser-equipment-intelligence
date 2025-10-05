#!/usr/bin/env python3
"""
Real Crawlers for Magic Find - Using Selenium to handle JavaScript-rendered content
Modified version with better feedback and error handling
"""

import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

def test_selenium_import():
    """Test if Selenium can be imported and ChromeDriver is available"""
    try:
        print("🔍 Testing Selenium import...")
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        print("✅ Selenium imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Selenium import failed: {e}")
        return False

def test_chromedriver():
    """Test if ChromeDriver is available"""
    try:
        print("🔍 Testing ChromeDriver availability...")
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        print("🚀 Attempting to initialize Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ ChromeDriver initialized successfully")
        
        print("🌐 Testing basic navigation...")
        driver.get("https://www.google.com")
        print(f"📄 Page title: {driver.title}")
        
        driver.quit()
        print("✅ ChromeDriver test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver test failed: {e}")
        print("💡 Possible solutions:")
        print("   1. Install ChromeDriver: brew install chromedriver")
        print("   2. Or use webdriver-manager: pip install webdriver-manager")
        print("   3. Or download ChromeDriver manually from https://chromedriver.chromium.org/")
        return False

def test_requests_fallback():
    """Test if we can use requests as a fallback"""
    try:
        print("🔍 Testing requests fallback...")
        import requests
        
        # Test a simple request
        response = requests.get("https://httpbin.org/get", timeout=10)
        print(f"✅ Requests test successful: {response.status_code}")
        
        # Test eBay access
        print("🌐 Testing eBay access with requests...")
        ebay_response = requests.get("https://www.ebay.com", timeout=10)
        print(f"📄 eBay response: {ebay_response.status_code}")
        
        if ebay_response.status_code == 200:
            print("✅ eBay accessible via requests")
            return True
        else:
            print("⚠️ eBay returned non-200 status")
            return False
            
    except Exception as e:
        print(f"❌ Requests test failed: {e}")
        return False

def simple_ebay_search(query: str):
    """Simple eBay search using requests (no JavaScript)"""
    try:
        import requests
        from urllib.parse import quote_plus
        
        print(f"🔍 Searching eBay for: {query}")
        
        # Construct search URL
        search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
        print(f"🌐 URL: {search_url}")
        
        # Make request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"📄 Response status: {response.status_code}")
        print(f"📄 Response length: {len(response.text)}")
        
        if response.status_code == 200:
            # Look for item indicators in the HTML
            content = response.text.lower()
            
            if 's-item' in content:
                print("✅ Found s-item elements (eBay listings)")
            else:
                print("⚠️ No s-item elements found")
            
            if 'challenge' in content or 'captcha' in content:
                print("❌ Detected challenge/captcha page")
                return False
            else:
                print("✅ No challenge page detected")
                return True
        else:
            print(f"❌ Non-200 response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Simple eBay search failed: {e}")
        return False

def main():
    """Test different approaches to get real data"""
    print("🚀 Testing Real Crawler Approaches")
    print("=" * 50)
    
    # Test 1: Selenium import
    selenium_available = test_selenium_import()
    print()
    
    # Test 2: ChromeDriver
    chromedriver_available = False
    if selenium_available:
        chromedriver_available = test_chromedriver()
    print()
    
    # Test 3: Requests fallback
    requests_available = test_requests_fallback()
    print()
    
    # Test 4: Simple eBay search
    ebay_accessible = False
    if requests_available:
        ebay_accessible = simple_ebay_search("Alma Lasers Harmony XL")
    print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Selenium Import: {'✅' if selenium_available else '❌'}")
    print(f"ChromeDriver: {'✅' if chromedriver_available else '❌'}")
    print(f"Requests: {'✅' if requests_available else '❌'}")
    print(f"eBay Access: {'✅' if ebay_accessible else '❌'}")
    
    if chromedriver_available:
        print("\n🎯 RECOMMENDATION: Use Selenium with ChromeDriver")
        print("   This is the most effective approach for bypassing bot detection")
    elif requests_available and ebay_accessible:
        print("\n🎯 RECOMMENDATION: Use requests with improved parsing")
        print("   This is a simpler approach that might work for some sites")
    else:
        print("\n🎯 RECOMMENDATION: Focus on mock data and API integration")
        print("   Real scraping requires additional setup (ChromeDriver, proxies)")

if __name__ == "__main__":
    main()
