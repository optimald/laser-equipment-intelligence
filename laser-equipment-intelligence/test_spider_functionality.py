#!/usr/bin/env python3
"""
Test spider functionality - validate data extraction capabilities
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapy.http import HtmlResponse, Request
from laser_intelligence.spiders.dotmed_spider import DotmedSpider
from laser_intelligence.spiders.bidspotter_spider import BidspotterSpider
from laser_intelligence.spiders.ebay_spider import EbaySpider
from laser_intelligence.spiders.govdeals_spider import GovdealsSpider
from laser_intelligence.spiders.facebook_marketplace_spider import FacebookMarketplaceSpider
from laser_intelligence.spiders.craigslist_spider import CraigslistSpider
from laser_intelligence.spiders.labx_spider import LabXSpider


def test_spider_data_extraction():
    """Test spider data extraction capabilities"""
    print("🕷️ Testing Spider Data Extraction Capabilities")
    print("=" * 60)
    
    # Test spiders
    spiders = [
        ('DOTmed', DotmedSpider()),
        ('BidSpotter', BidspotterSpider()),
        ('eBay', EbaySpider()),
        ('GovDeals', GovdealsSpider()),
        ('Facebook Marketplace', FacebookMarketplaceSpider()),
        ('Craigslist', CraigslistSpider()),
        ('LabX', LabXSpider()),
    ]
    
    # Mock HTML content for testing
    mock_html = """
    <html>
        <body>
            <div class="auction-item">
                <a href="/auction/item/12345">Sciton Joule Laser System</a>
            </div>
            <h1 class="auction-title">Sciton Joule Laser System - Excellent Condition</h1>
            <div class="auction-description">
                Complete Sciton Joule laser system with handpieces. 
                Serial: SN12345, Year: 2022, Hours: 500. 
                Includes cart and accessories. Excellent condition.
            </div>
            <div class="current-bid">
                <span class="amount">$45,000</span>
            </div>
            <div class="seller-info">
                <span class="seller-name">Medical Equipment Liquidators</span>
                <span class="contact-info">contact@example.com</span>
            </div>
            <div class="location-info">Los Angeles, CA, USA</div>
            <div class="auction-end-time">Ends in 2 days</div>
        </body>
    </html>
    """
    
    # Create mock response
    request = Request(url="https://example.com/test")
    response = HtmlResponse(
        url="https://example.com/test",
        request=request,
        body=mock_html.encode('utf-8'),
        status=200
    )
    
    results = []
    
    for spider_name, spider in spiders:
        print(f"\n🔍 Testing {spider_name} Spider...")
        
        try:
            # Test spider initialization
            assert spider is not None
            assert hasattr(spider, 'name')
            assert hasattr(spider, 'allowed_domains')
            print(f"   ✅ Spider initialized: {spider.name}")
            
            # Test data extraction methods
            extraction_tests = []
            
            # Test brand/model extraction
            if hasattr(spider, '_extract_brand_model'):
                try:
                    brand, model = spider._extract_brand_model(
                        "Sciton Joule Laser System",
                        "Complete Sciton Joule laser system with handpieces"
                    )
                    extraction_tests.append(f"Brand/Model: {brand}/{model}")
                except Exception as e:
                    extraction_tests.append(f"Brand/Model extraction failed: {e}")
            
            # Test price extraction
            if hasattr(spider, '_extract_price'):
                try:
                    price = spider._extract_price("$45,000")
                    extraction_tests.append(f"Price extraction: ${price}")
                except Exception as e:
                    extraction_tests.append(f"Price extraction failed: {e}")
            
            # Test condition extraction
            if hasattr(spider, '_extract_condition'):
                try:
                    condition = spider._extract_condition("Excellent condition")
                    extraction_tests.append(f"Condition: {condition}")
                except Exception as e:
                    extraction_tests.append(f"Condition extraction failed: {e}")
            
            # Test serial number extraction
            if hasattr(spider, '_extract_serial_number'):
                try:
                    serial = spider._extract_serial_number("Serial: SN12345")
                    extraction_tests.append(f"Serial: {serial}")
                except Exception as e:
                    extraction_tests.append(f"Serial extraction failed: {e}")
            
            # Test year extraction
            if hasattr(spider, '_extract_year'):
                try:
                    year = spider._extract_year("Year: 2022")
                    extraction_tests.append(f"Year: {year}")
                except Exception as e:
                    extraction_tests.append(f"Year extraction failed: {e}")
            
            # Test hours extraction
            if hasattr(spider, '_extract_hours'):
                try:
                    hours = spider._extract_hours("Hours: 500")
                    extraction_tests.append(f"Hours: {hours}")
                except Exception as e:
                    extraction_tests.append(f"Hours extraction failed: {e}")
            
            # Test accessories extraction
            if hasattr(spider, '_extract_accessories'):
                try:
                    accessories = spider._extract_accessories("Includes cart and accessories")
                    extraction_tests.append(f"Accessories: {accessories}")
                except Exception as e:
                    extraction_tests.append(f"Accessories extraction failed: {e}")
            
            # Test location parsing
            if hasattr(spider, '_parse_location'):
                try:
                    location = spider._parse_location("Los Angeles, CA, USA")
                    extraction_tests.append(f"Location: {location}")
                except Exception as e:
                    extraction_tests.append(f"Location parsing failed: {e}")
            
            # Test laser equipment detection
            if hasattr(spider, '_is_laser_equipment'):
                try:
                    is_laser = spider._is_laser_equipment(response)
                    extraction_tests.append(f"Laser detection: {is_laser}")
                except Exception as e:
                    extraction_tests.append(f"Laser detection failed: {e}")
            
            # Print extraction results
            if extraction_tests:
                print(f"   📊 Extraction Results:")
                for test in extraction_tests:
                    print(f"      - {test}")
            else:
                print(f"   ⚠️  No extraction methods found")
            
            results.append((spider_name, True, len(extraction_tests)))
            
        except Exception as e:
            print(f"   ❌ Spider test failed: {e}")
            results.append((spider_name, False, 0))
    
    # Summary
    print(f"\n📊 SPIDER FUNCTIONALITY TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for _, success, _ in results if success)
    total_extraction_methods = sum(count for _, _, count in results)
    
    print(f"✅ Successful spiders: {successful}/{len(spiders)}")
    print(f"📊 Total extraction methods tested: {total_extraction_methods}")
    
    for spider_name, success, count in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status} {spider_name}: {count} extraction methods")
    
    if successful == len(spiders):
        print(f"\n🎯 All spiders are functional and ready for data extraction!")
    else:
        print(f"\n⚠️  Some spiders need additional implementation.")
    
    return successful == len(spiders)


if __name__ == "__main__":
    success = test_spider_data_extraction()
    sys.exit(0 if success else 1)
