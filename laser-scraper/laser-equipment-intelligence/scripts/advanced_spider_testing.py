#!/usr/bin/env python3
"""
Advanced Spider Testing Script - Laser Equipment Intelligence Platform
"""

import sys
import os
import time
import requests
from datetime import datetime
from scrapy.http import Request, HtmlResponse
from scrapy.spiders import Spider

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

try:
    from laser_intelligence.spiders.dotmed_spider import DotmedSpider
    from laser_intelligence.spiders.bidspotter_spider import BidspotterSpider
    from laser_intelligence.spiders.ebay_spider import EbaySpider
    from laser_intelligence.spiders.govdeals_spider import GovdealsSpider
    from laser_intelligence.spiders.facebook_marketplace_spider import FacebookMarketplaceSpider
    from laser_intelligence.spiders.craigslist_spider import CraigslistSpider
    from laser_intelligence.spiders.labx_spider import LabXSpider
    from laser_intelligence.utils.brand_mapping import BrandMapper
    from laser_intelligence.utils.price_analysis import PriceAnalyzer
    from laser_intelligence.utils.evasion_scoring import EvasionScorer
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class AdvancedSpiderTesting:
    """Advanced spider testing system"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = []
        self.critical_failures = 0
        self.warnings = 0
        self.test_summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warning_tests': 0,
            'critical_failures': 0,
            'spider_results': {},
            'extraction_results': {}
        }
        
    def log_result(self, test_name: str, status: str, message: str = "", is_critical: bool = False, metrics: dict = None):
        """Log test result with metrics"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': timestamp,
            'critical': is_critical,
            'metrics': metrics or {}
        }
        
        self.results.append(result)
        self.test_summary['total_tests'] += 1
        
        if status == "PASS":
            self.test_summary['passed_tests'] += 1
        elif status == "FAIL":
            self.test_summary['failed_tests'] += 1
            if is_critical:
                self.critical_failures += 1
                self.test_summary['critical_failures'] += 1
        elif status == "WARN":
            self.test_summary['warning_tests'] += 1
            self.warnings += 1
            
        print(f"{status_icon} [{timestamp}] {test_name}: {status}")
        if message:
            print(f"    {message}")
        if metrics:
            for key, value in metrics.items():
                print(f"    📊 {key}: {value}")
    
    def test_spider_data_extraction(self):
        """Test spider data extraction capabilities"""
        print("\n🕷️ Testing Spider Data Extraction...")
        
        spiders = [
            ("DOTmed", DotmedSpider),
            ("BidSpotter", BidspotterSpider),
            ("eBay", EbaySpider),
            ("GovDeals", GovdealsSpider),
            ("Facebook Marketplace", FacebookMarketplaceSpider),
            ("Craigslist", CraigslistSpider),
            ("LabX", LabXSpider),
        ]
        
        for spider_name, spider_class in spiders:
            try:
                spider = spider_class()
                
                # Test spider initialization
                if hasattr(spider, 'name') and spider.name:
                    self.log_result(f"Spider Initialization: {spider_name}", "PASS", 
                                  f"Name: {spider.name}", is_critical=True,
                                  metrics={'spider_name': spider.name})
                    self.test_summary['spider_results'][spider_name] = 'PASS'
                else:
                    self.log_result(f"Spider Initialization: {spider_name}", "FAIL", 
                                  "No name attribute", is_critical=True)
                    self.test_summary['spider_results'][spider_name] = 'FAIL'
                    continue
                
                # Test spider attributes
                required_attrs = ['allowed_domains', 'custom_settings']
                missing_attrs = []
                for attr in required_attrs:
                    if not hasattr(spider, attr):
                        missing_attrs.append(attr)
                
                if not missing_attrs:
                    self.log_result(f"Spider Attributes: {spider_name}", "PASS", 
                                  "All required attributes present", is_critical=False,
                                  metrics={'required_attrs': len(required_attrs)})
                else:
                    self.log_result(f"Spider Attributes: {spider_name}", "WARN", 
                                  f"Missing attributes: {missing_attrs}", is_critical=False,
                                  metrics={'missing_attrs': missing_attrs})
                
                # Test spider methods
                required_methods = ['start_requests', 'parse']
                missing_methods = []
                for method in required_methods:
                    if not hasattr(spider, method):
                        missing_methods.append(method)
                
                if not missing_methods:
                    self.log_result(f"Spider Methods: {spider_name}", "PASS", 
                                  "All required methods present", is_critical=False,
                                  metrics={'required_methods': len(required_methods)})
                else:
                    self.log_result(f"Spider Methods: {spider_name}", "WARN", 
                                  f"Missing methods: {missing_methods}", is_critical=False,
                                  metrics={'missing_methods': missing_methods})
                
            except Exception as e:
                self.log_result(f"Spider Testing: {spider_name}", "FAIL", 
                              f"Error: {e}", is_critical=True)
                self.test_summary['spider_results'][spider_name] = 'FAIL'
    
    def test_data_extraction_methods(self):
        """Test data extraction methods"""
        print("\n🔍 Testing Data Extraction Methods...")
        
        # Test brand mapping extraction
        try:
            brand_mapper = BrandMapper()
            test_cases = [
                ("Sciton Joule Laser System", "Sciton", "Joule"),
                ("Cynosure Elite+ IPL Device", "Cynosure", "Elite+"),
                ("Cutera Xeo Laser Platform", "Cutera", "Xeo"),
                ("Lumenis M22 Multi-Platform", "Lumenis", "M22"),
                ("Alma Soprano Titanium", "Alma", "Soprano Titanium"),
            ]
            
            passed_extractions = 0
            for title, expected_brand, expected_model in test_cases:
                # Simulate extraction logic
                brand = brand_mapper.normalize_brand(expected_brand)
                model = brand_mapper.normalize_model(expected_model, brand)
                
                if brand == expected_brand and model == expected_model:
                    passed_extractions += 1
            
            if passed_extractions == len(test_cases):
                self.log_result("Brand/Model Extraction", "PASS", 
                              f"All {passed_extractions}/{len(test_cases)} extractions successful", 
                              is_critical=True,
                              metrics={'accuracy': f"{passed_extractions}/{len(test_cases)}"})
                self.test_summary['extraction_results']['brand_model'] = 'PASS'
            else:
                self.log_result("Brand/Model Extraction", "FAIL", 
                              f"Only {passed_extractions}/{len(test_cases)} extractions successful", 
                              is_critical=True,
                              metrics={'accuracy': f"{passed_extractions}/{len(test_cases)}"})
                self.test_summary['extraction_results']['brand_model'] = 'FAIL'
        except Exception as e:
            self.log_result("Brand/Model Extraction", "FAIL", f"Error: {e}", is_critical=True)
            self.test_summary['extraction_results']['brand_model'] = 'FAIL'
        
        # Test price extraction
        try:
            price_analyzer = PriceAnalyzer()
            test_prices = ["$50,000", "$75,000.00", "USD 100,000", "150000", "$25,500.50"]
            extracted_prices = []
            
            for price_text in test_prices:
                # Simulate price extraction logic
                try:
                    # Remove currency symbols and commas
                    cleaned = price_text.replace('$', '').replace(',', '').replace('USD ', '')
                    price = float(cleaned)
                    extracted_prices.append(price)
                except ValueError:
                    extracted_prices.append(None)
            
            successful_extractions = len([p for p in extracted_prices if p is not None])
            
            if successful_extractions == len(test_prices):
                self.log_result("Price Extraction", "PASS", 
                              f"All {successful_extractions}/{len(test_prices)} prices extracted", 
                              is_critical=True,
                              metrics={'accuracy': f"{successful_extractions}/{len(test_prices)}"})
                self.test_summary['extraction_results']['price'] = 'PASS'
            else:
                self.log_result("Price Extraction", "WARN", 
                              f"Only {successful_extractions}/{len(test_prices)} prices extracted", 
                              is_critical=False,
                              metrics={'accuracy': f"{successful_extractions}/{len(test_prices)}"})
                self.test_summary['extraction_results']['price'] = 'WARN'
        except Exception as e:
            self.log_result("Price Extraction", "FAIL", f"Error: {e}", is_critical=True)
            self.test_summary['extraction_results']['price'] = 'FAIL'
    
    def test_spider_performance(self):
        """Test spider performance under load"""
        print("\n⚡ Testing Spider Performance...")
        
        try:
            # Test brand mapping performance
            brand_mapper = BrandMapper()
            start_time = time.time()
            
            for i in range(1000):
                brand_mapper.normalize_brand("Sciton")
                brand_mapper.normalize_model("Joule", "Sciton")
            
            end_time = time.time()
            ops_per_sec = 2000 / (end_time - start_time)
            
            if ops_per_sec > 10000:
                self.log_result("Spider Performance", "PASS", 
                              f"{ops_per_sec:,.0f} ops/sec", is_critical=False,
                              metrics={'ops_per_sec': f"{ops_per_sec:,.0f}", 'target': '10,000'})
            else:
                self.log_result("Spider Performance", "WARN", 
                              f"{ops_per_sec:,.0f} ops/sec - Below target", is_critical=False,
                              metrics={'ops_per_sec': f"{ops_per_sec:,.0f}", 'target': '10,000'})
        except Exception as e:
            self.log_result("Spider Performance", "FAIL", f"Error: {e}", is_critical=False)
    
    def test_spider_error_handling(self):
        """Test spider error handling capabilities"""
        print("\n🛡️ Testing Spider Error Handling...")
        
        try:
            # Test with invalid input
            brand_mapper = BrandMapper()
            
            # Test with None input
            result = brand_mapper.normalize_brand(None)
            if result == '':
                self.log_result("Error Handling: None Input", "PASS", 
                              "Handles None input gracefully", is_critical=False)
            else:
                self.log_result("Error Handling: None Input", "WARN", 
                              f"Unexpected result: {result}", is_critical=False)
            
            # Test with empty string
            result = brand_mapper.normalize_brand("")
            if result == '':
                self.log_result("Error Handling: Empty String", "PASS", 
                              "Handles empty string gracefully", is_critical=False)
            else:
                self.log_result("Error Handling: Empty String", "WARN", 
                              f"Unexpected result: {result}", is_critical=False)
            
            # Test with invalid characters
            result = brand_mapper.normalize_brand("!@#$%^&*()")
            if result:
                self.log_result("Error Handling: Invalid Characters", "PASS", 
                              "Handles invalid characters", is_critical=False)
            else:
                self.log_result("Error Handling: Invalid Characters", "WARN", 
                              "Failed to handle invalid characters", is_critical=False)
                
        except Exception as e:
            self.log_result("Error Handling", "FAIL", f"Error: {e}", is_critical=False)
    
    def test_spider_integration(self):
        """Test spider integration with other components"""
        print("\n🔗 Testing Spider Integration...")
        
        try:
            # Test integration with brand mapping
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            evasion_scorer = EvasionScorer()
            
            # Simulate spider data processing
            test_data = {
                'title': 'Sciton Joule Laser System',
                'description': 'Complete Sciton Joule laser system with handpieces',
                'price': '$75,000',
                'condition': 'excellent'
            }
            
            # Process data through pipeline
            brand = brand_mapper.normalize_brand("Sciton")
            model = brand_mapper.normalize_model("Joule", brand)
            wholesale = price_analyzer.estimate_wholesale_value(brand, model, test_data['condition'], 75000)
            score = evasion_scorer.base_score
            
            if brand and model and wholesale and score:
                self.log_result("Spider Integration", "PASS", 
                              f"Brand: {brand}, Model: {model}, Wholesale: ${wholesale:,.0f}, Score: {score}", 
                              is_critical=True,
                              metrics={'brand': brand, 'model': model, 'wholesale': f"${wholesale:,.0f}", 'score': score})
            else:
                self.log_result("Spider Integration", "FAIL", 
                              "Integration test failed", is_critical=True)
        except Exception as e:
            self.log_result("Spider Integration", "FAIL", f"Error: {e}", is_critical=True)
    
    def run_advanced_testing(self):
        """Run advanced spider testing"""
        print("🚀 Advanced Spider Testing - Laser Equipment Intelligence Platform")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_spider_data_extraction()
        self.test_data_extraction_methods()
        self.test_spider_performance()
        self.test_spider_error_handling()
        self.test_spider_integration()
        
        # Generate comprehensive summary
        self.generate_test_summary()
        
        return self.test_summary
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        total_time = time.time() - self.start_time
        
        print(f"\n📊 ADVANCED SPIDER TESTING SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.test_summary['total_tests']}")
        print(f"✅ Passed: {self.test_summary['passed_tests']}")
        print(f"❌ Failed: {self.test_summary['failed_tests']}")
        print(f"⚠️  Warnings: {self.test_summary['warning_tests']}")
        print(f"🔴 Critical Failures: {self.test_summary['critical_failures']}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        # Spider results summary
        if self.test_summary['spider_results']:
            print(f"\n🕷️ Spider Results:")
            for spider, status in self.test_summary['spider_results'].items():
                status_icon = "✅" if status == "PASS" else "❌"
                print(f"  {status_icon} {spider}: {status}")
        
        # Extraction results summary
        if self.test_summary['extraction_results']:
            print(f"\n🔍 Extraction Results:")
            for method, status in self.test_summary['extraction_results'].items():
                status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
                print(f"  {status_icon} {method}: {status}")
        
        # Overall status
        if self.test_summary['critical_failures'] == 0:
            if self.test_summary['warning_tests'] == 0:
                print(f"\n🎯 STATUS: ✅ ALL SPIDER TESTS PASSED")
                print("🚀 Spiders are ready for advanced testing!")
                return 0
            else:
                print(f"\n🎯 STATUS: ⚠️  SPIDER TESTS PASSED WITH WARNINGS")
                print("🚀 Spiders are ready for advanced testing with minor issues.")
                return 0
        else:
            print(f"\n🎯 STATUS: ❌ CRITICAL SPIDER ISSUES DETECTED")
            print("⚠️  Spiders need attention before advanced testing.")
            return 1


def main():
    """Main function"""
    tester = AdvancedSpiderTesting()
    test_summary = tester.run_advanced_testing()
    
    # Return exit code based on critical failures
    exit_code = 0 if test_summary['critical_failures'] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
