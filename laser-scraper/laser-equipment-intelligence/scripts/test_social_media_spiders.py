#!/usr/bin/env python3
"""
Test script for social media spiders (Reddit, Facebook Groups)
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_reddit_spider():
    """Test Reddit spider functionality"""
    print("🔍 Testing Reddit Spider...")
    
    try:
        # Test spider registration
        result = subprocess.run([
            'python', '-c', 
            'import sys; sys.path.insert(0, "src"); from laser_intelligence.spiders.reddit_spider import RedditSpider; print("✅ Reddit spider imported successfully")'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Reddit spider import: PASS")
        else:
            print(f"❌ Reddit spider import: FAIL - {result.stderr}")
            return False
        
        # Test spider check
        result = subprocess.run([
            'scrapy', 'check', 'reddit'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Reddit spider check: PASS")
        else:
            print(f"❌ Reddit spider check: FAIL - {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Reddit spider test failed: {e}")
        return False

def test_facebook_groups_api_spider():
    """Test Facebook Groups API spider functionality"""
    print("\n🔍 Testing Facebook Groups API Spider...")
    
    try:
        # Test spider registration
        result = subprocess.run([
            'python', '-c', 
            'import sys; sys.path.insert(0, "src"); from laser_intelligence.spiders.facebook_groups_api_spider import FacebookGroupsAPISpider; print("✅ Facebook Groups API spider imported successfully")'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Facebook Groups API spider import: PASS")
        else:
            print(f"❌ Facebook Groups API spider import: FAIL - {result.stderr}")
            return False
        
        # Test spider check
        result = subprocess.run([
            'scrapy', 'check', 'facebook_groups_api'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Facebook Groups API spider check: PASS")
        else:
            print(f"❌ Facebook Groups API spider check: FAIL - {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Facebook Groups API spider test failed: {e}")
        return False

def test_facebook_groups_session_spider():
    """Test Facebook Groups Session spider functionality"""
    print("\n🔍 Testing Facebook Groups Session Spider...")
    
    try:
        # Test spider registration
        result = subprocess.run([
            'python', '-c', 
            'import sys; sys.path.insert(0, "src"); from laser_intelligence.spiders.facebook_groups_session_spider import FacebookGroupsSessionSpider; print("✅ Facebook Groups Session spider imported successfully")'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Facebook Groups Session spider import: PASS")
        else:
            print(f"❌ Facebook Groups Session spider import: FAIL - {result.stderr}")
            return False
        
        # Test spider check
        result = subprocess.run([
            'scrapy', 'check', 'facebook_groups_session'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Facebook Groups Session spider check: PASS")
        else:
            print(f"❌ Facebook Groups Session spider check: FAIL - {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Facebook Groups Session spider test failed: {e}")
        return False

def test_facebook_marketplace_spider():
    """Test existing Facebook Marketplace spider"""
    print("\n🔍 Testing Facebook Marketplace Spider...")
    
    try:
        # Test spider check
        result = subprocess.run([
            'scrapy', 'check', 'facebook_marketplace'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Facebook Marketplace spider check: PASS")
            return True
        else:
            print(f"❌ Facebook Marketplace spider check: FAIL - {result.stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Facebook Marketplace spider test failed: {e}")
        return False

def test_environment_setup():
    """Test environment setup for social media spiders"""
    print("\n🔍 Testing Environment Setup...")
    
    # Check for required environment variables
    env_vars = {
        'FACEBOOK_ACCESS_TOKEN': 'Facebook API access token',
        'FACEBOOK_APP_ID': 'Facebook App ID',
        'FACEBOOK_APP_SECRET': 'Facebook App Secret',
        'FACEBOOK_EMAIL': 'Facebook email (for session-based access)',
        'FACEBOOK_PASSWORD': 'Facebook password (for session-based access)'
    }
    
    missing_vars = []
    for var, description in env_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Set these in your .env file or environment")
        print("   See docs/FACEBOOK_GROUPS_SETUP.md for details")
    else:
        print("✅ All environment variables found")
    
    return len(missing_vars) == 0

def main():
    """Run all social media spider tests"""
    print("🚀 Testing Social Media Spiders")
    print("=" * 50)
    
    results = []
    
    # Test environment setup
    results.append(test_environment_setup())
    
    # Test individual spiders
    results.append(test_reddit_spider())
    results.append(test_facebook_marketplace_spider())
    results.append(test_facebook_groups_api_spider())
    results.append(test_facebook_groups_session_spider())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All social media spider tests passed!")
        print("\n📋 Next Steps:")
        print("1. Set up Facebook API credentials (see docs/FACEBOOK_GROUPS_SETUP.md)")
        print("2. Join target Facebook groups manually")
        print("3. Test with real data: scrapy crawl reddit -L INFO")
        print("4. Test Facebook API: scrapy crawl facebook_groups_api -L INFO")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check Python path and imports")
        print("3. Verify Scrapy configuration")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
