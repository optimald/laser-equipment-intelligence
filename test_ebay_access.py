#!/usr/bin/env python3
import requests
from urllib.parse import quote_plus

def test_ebay_access():
    """Test if we can access eBay search results"""
    query = "Aerolase Lightpod Neo Elite"
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
    
    print(f"Testing eBay access for: {query}")
    print(f"URL: {search_url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        
        if response.status_code == 200:
            # Look for common eBay elements
            if 's-item' in response.text:
                print("✅ Found s-item elements (eBay listings)")
            else:
                print("❌ No s-item elements found")
                
            if 'ebay' in response.text.lower():
                print("✅ eBay content detected")
            else:
                print("❌ No eBay content detected")
                
            # Check if we got redirected to a challenge page
            if 'challenge' in response.text.lower() or 'captcha' in response.text.lower():
                print("⚠️ Possible bot detection/challenge page")
                
        else:
            print(f"❌ Failed to access eBay: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing eBay: {e}")

if __name__ == "__main__":
    test_ebay_access()
