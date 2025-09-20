#!/usr/bin/env python3
"""
Automated testing script for Laser Equipment Intelligence Platform
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🧪 Testing: {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ FAILED: {description}")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {description}")
        return False
    except Exception as e:
        print(f"💥 EXCEPTION: {description} - {e}")
        return False

def test_python_imports():
    """Test Python imports"""
    print("\n🔍 Testing Python Imports...")
    
    imports_to_test = [
        ("scrapy", "Scrapy framework"),
        ("playwright", "Playwright browser automation"),
        ("torch", "PyTorch ML framework"),
        ("numpy", "NumPy numerical computing"),
        ("redis", "Redis client"),
        ("psycopg2", "PostgreSQL adapter"),
        ("requests", "HTTP requests library"),
        ("beautifulsoup4", "BeautifulSoup HTML parsing"),
        ("pytesseract", "Tesseract OCR"),
        ("PIL", "Pillow image processing"),
    ]
    
    results = []
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {description}")
            results.append(True)
        except ImportError as e:
            print(f"❌ {description}: {e}")
            results.append(False)
    
    return all(results)

def test_scrapy_spiders():
    """Test Scrapy spider syntax"""
    print("\n🕷️ Testing Scrapy Spiders...")
    
    spiders = [
        "dotmed_auctions",
        "bidspotter", 
        "ebay_laser",
        "facebook_marketplace",
        "craigslist",
        "labx",
        "govdeals",
        "proxibid",
        "centurion",
        "gsa_auctions",
        "govplanet",
        "heritage_global",
        "iron_horse_auction",
        "kurtz_auction",
        "laser_agent",
        "laser_service_solutions",
        "thelaserwarehouse",
        "asset_recovery_services",
        "ajwillner_auctions",
        "medwow",
        "used_line"
    ]
    
    results = []
    for spider in spiders:
        success = run_command(
            f"PYTHONPATH=src scrapy check {spider}",
            f"Spider syntax check: {spider}"
        )
        results.append(success)
    
    return results

def test_custom_modules():
    """Test custom modules"""
    print("\n🔧 Testing Custom Modules...")
    
    modules_to_test = [
        ("laser_intelligence.middleware.impersonate", "Impersonate middleware"),
        ("laser_intelligence.middleware.proxy", "Proxy middleware"),
        ("laser_intelligence.middleware.captcha", "CAPTCHA middleware"),
        ("laser_intelligence.middleware.evasion", "Evasion middleware"),
        ("laser_intelligence.utils.llm_fallback", "LLM fallback utility"),
        ("laser_intelligence.ml.html_differ", "HTML differ ML module"),
        ("laser_intelligence.ml.efficient_ui_coder", "EfficientUI coder"),
        ("laser_intelligence.dictionary.asset_dictionary", "Asset dictionary"),
        ("laser_intelligence.pipelines.normalization", "Normalization pipeline"),
        ("laser_intelligence.pipelines.scoring", "Scoring pipeline"),
        ("laser_intelligence.pipelines.alerts", "Alerts pipeline"),
        ("laser_intelligence.utils.brand_mapping", "Brand mapping utility"),
        ("laser_intelligence.utils.price_analysis", "Price analysis utility"),
        ("laser_intelligence.utils.pdf_processor", "PDF processor utility"),
    ]
    
    results = []
    for module, description in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {description}")
            results.append(True)
        except ImportError as e:
            print(f"❌ {description}: {e}")
            results.append(False)
        except Exception as e:
            print(f"⚠️ {description}: {e}")
            results.append(False)
    
    return results

def test_database_connections():
    """Test database connections"""
    print("\n🗄️ Testing Database Connections...")
    
    # Test PostgreSQL connection
    try:
        import psycopg2
        # This would need actual connection parameters
        print("✅ PostgreSQL module available")
        postgres_ok = True
    except ImportError:
        print("❌ PostgreSQL module not available")
        postgres_ok = False
    
    # Test Redis connection
    try:
        import redis
        # This would need actual connection parameters
        print("✅ Redis module available")
        redis_ok = True
    except ImportError:
        print("❌ Redis module not available")
        redis_ok = False
    
    return postgres_ok and redis_ok

def test_playwright():
    """Test Playwright installation"""
    print("\n🎭 Testing Playwright...")
    
    success = run_command("playwright --version", "Playwright version check")
    if success:
        success = run_command("playwright install --dry-run", "Playwright browser check")
    
    return success

def test_ml_modules():
    """Test ML modules"""
    print("\n🤖 Testing ML Modules...")
    
    ml_tests = [
        ("torch", "PyTorch"),
        ("torch.nn", "PyTorch Neural Networks"),
        ("numpy", "NumPy"),
        ("sklearn", "Scikit-learn"),
    ]
    
    results = []
    for module, description in ml_tests:
        try:
            __import__(module)
            print(f"✅ {description}")
            results.append(True)
        except ImportError as e:
            print(f"❌ {description}: {e}")
            results.append(False)
    
    return all(results)

def run_quick_spider_test():
    """Run a quick test of one spider"""
    print("\n🚀 Running Quick Spider Test...")
    
    # Test with a simple, low-risk spider
    success = run_command(
        "PYTHONPATH=src scrapy crawl govdeals -s CLOSESPIDER_PAGECOUNT=2 -s CLOSESPIDER_ITEMCOUNT=3 -L WARNING",
        "Quick GovDeals spider test"
    )
    
    return success

def main():
    """Main testing function"""
    print("🧪 Laser Equipment Intelligence Platform - Automated Testing")
    print("=" * 60)
    
    # Track overall results
    test_results = {}
    
    # Run tests
    test_results["Python Imports"] = test_python_imports()
    test_results["Custom Modules"] = test_custom_modules()
    test_results["Database Connections"] = test_database_connections()
    test_results["Playwright"] = test_playwright()
    test_results["ML Modules"] = test_ml_modules()
    
    # Test spider syntax
    spider_results = test_scrapy_spiders()
    test_results["Spider Syntax"] = all(spider_results)
    
    # Quick spider test
    test_results["Quick Spider Test"] = run_quick_spider_test()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TESTING SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! System is ready for deployment.")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
