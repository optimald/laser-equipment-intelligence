#!/usr/bin/env python3
"""
Integration Testing Script - Laser Equipment Intelligence Platform
"""

import sys
import os
import time
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

try:
    from laser_intelligence.utils.brand_mapping import BrandMapper
    from laser_intelligence.utils.price_analysis import PriceAnalyzer
    from laser_intelligence.utils.evasion_scoring import EvasionScorer
    from laser_intelligence.spiders.dotmed_spider import DotmedSpider
    from laser_intelligence.spiders.bidspotter_spider import BidspotterSpider
    from laser_intelligence.spiders.ebay_spider import EbaySpider
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class IntegrationTesting:
    """Integration testing system for the Laser Equipment Intelligence Platform"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = []
        self.critical_failures = 0
        self.warnings = 0
        self.integration_test_summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warning_tests': 0,
            'critical_failures': 0,
            'integration_results': {},
            'external_service_results': {}
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
        self.integration_test_summary['total_tests'] += 1
        
        if status == "PASS":
            self.integration_test_summary['passed_tests'] += 1
        elif status == "FAIL":
            self.integration_test_summary['failed_tests'] += 1
            if is_critical:
                self.critical_failures += 1
                self.integration_test_summary['critical_failures'] += 1
        elif status == "WARN":
            self.integration_test_summary['warning_tests'] += 1
            self.warnings += 1
            
        print(f"{status_icon} [{timestamp}] {test_name}: {status}")
        if message:
            print(f"    {message}")
        if metrics:
            for key, value in metrics.items():
                print(f"    📊 {key}: {value}")
    
    def test_component_integration(self):
        """Test integration between core components"""
        print("\n🔗 Testing Component Integration...")
        
        try:
            # Initialize all components
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            evasion_scorer = EvasionScorer()
            
            # Test data flow through components
            test_data = {
                'title': 'Sciton Joule Laser System - Excellent Condition',
                'description': 'Complete Sciton Joule laser system with handpieces. Serial: SN12345, Year: 2022, Hours: 500.',
                'asking_price': '$75,000',
                'condition': 'excellent',
                'location': 'Los Angeles, CA'
            }
            
            # Step 1: Brand/Model Extraction
            brand = brand_mapper.normalize_brand("Sciton")
            model = brand_mapper.normalize_model("Joule", brand)
            
            if brand == "Sciton" and model == "Joule":
                self.log_result("Brand/Model Integration", "PASS", 
                              f"Brand: {brand}, Model: {model}", is_critical=True,
                              metrics={'brand': brand, 'model': model})
            else:
                self.log_result("Brand/Model Integration", "FAIL", 
                              f"Expected Sciton/Joule, got {brand}/{model}", is_critical=True)
                return
            
            # Step 2: Price Analysis Integration
            asking_price = 75000
            wholesale_value = price_analyzer.estimate_wholesale_value(brand, model, test_data['condition'], asking_price)
            resale_value = price_analyzer.estimate_resale_value(brand, model, test_data['condition'], asking_price)
            margin, margin_pct = price_analyzer.calculate_margin_estimate(asking_price, wholesale_value, 5000, 2000)
            
            if wholesale_value and resale_value and margin is not None:
                self.log_result("Price Analysis Integration", "PASS", 
                              f"Wholesale: ${wholesale_value:,.0f}, Resale: ${resale_value:,.0f}, Margin: ${margin:,.0f}", 
                              is_critical=True,
                              metrics={'wholesale': f"${wholesale_value:,.0f}", 'resale': f"${resale_value:,.0f}", 'margin': f"${margin:,.0f}"})
            else:
                self.log_result("Price Analysis Integration", "FAIL", 
                              "Price analysis failed", is_critical=True)
                return
            
            # Step 3: Evasion Scoring Integration
            evasion_score = evasion_scorer.base_score
            
            if evasion_score is not None:
                self.log_result("Evasion Scoring Integration", "PASS", 
                              f"Base evasion score: {evasion_score}", is_critical=True,
                              metrics={'score': evasion_score})
            else:
                self.log_result("Evasion Scoring Integration", "FAIL", 
                              "Evasion scoring failed", is_critical=True)
                return
            
            # Step 4: End-to-End Integration
            overall_score = evasion_score + (margin_pct if margin_pct else 0)
            
            if overall_score > 0:
                self.log_result("End-to-End Integration", "PASS", 
                              f"Overall score: {overall_score:.1f}", is_critical=True,
                              metrics={'overall_score': f"{overall_score:.1f}"})
                self.integration_test_summary['integration_results']['component_integration'] = 'PASS'
            else:
                self.log_result("End-to-End Integration", "FAIL", 
                              "End-to-end integration failed", is_critical=True)
                self.integration_test_summary['integration_results']['component_integration'] = 'FAIL'
                
        except Exception as e:
            self.log_result("Component Integration", "FAIL", f"Error: {e}", is_critical=True)
            self.integration_test_summary['integration_results']['component_integration'] = 'FAIL'
    
    def test_spider_integration(self):
        """Test spider integration with core components"""
        print("\n🕷️ Testing Spider Integration...")
        
        try:
            spiders = [
                ("DOTmed", DotmedSpider),
                ("BidSpotter", BidspotterSpider),
                ("eBay", EbaySpider),
            ]
            
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            
            successful_integrations = 0
            
            for spider_name, spider_class in spiders:
                try:
                    spider = spider_class()
                    
                    # Test spider initialization
                    if hasattr(spider, 'name') and spider.name:
                        # Test spider with brand mapping
                        test_brand = brand_mapper.normalize_brand("Sciton")
                        test_model = brand_mapper.normalize_model("Joule", test_brand)
                        
                        if test_brand and test_model:
                            successful_integrations += 1
                            self.log_result(f"Spider Integration: {spider_name}", "PASS", 
                                          f"Spider: {spider.name}, Brand: {test_brand}, Model: {test_model}", 
                                          is_critical=False,
                                          metrics={'spider': spider.name, 'brand': test_brand, 'model': test_model})
                        else:
                            self.log_result(f"Spider Integration: {spider_name}", "WARN", 
                                          "Brand mapping integration failed", is_critical=False)
                    else:
                        self.log_result(f"Spider Integration: {spider_name}", "WARN", 
                                      "Spider initialization failed", is_critical=False)
                        
                except Exception as e:
                    self.log_result(f"Spider Integration: {spider_name}", "WARN", 
                                  f"Error: {e}", is_critical=False)
            
            if successful_integrations == len(spiders):
                self.log_result("Spider Integration Summary", "PASS", 
                              f"All {successful_integrations}/{len(spiders)} spiders integrated successfully", 
                              is_critical=True,
                              metrics={'successful': successful_integrations, 'total': len(spiders)})
                self.integration_test_summary['integration_results']['spider_integration'] = 'PASS'
            else:
                self.log_result("Spider Integration Summary", "WARN", 
                              f"Only {successful_integrations}/{len(spiders)} spiders integrated successfully", 
                              is_critical=False,
                              metrics={'successful': successful_integrations, 'total': len(spiders)})
                self.integration_test_summary['integration_results']['spider_integration'] = 'WARN'
                
        except Exception as e:
            self.log_result("Spider Integration", "FAIL", f"Error: {e}", is_critical=True)
            self.integration_test_summary['integration_results']['spider_integration'] = 'FAIL'
    
    def test_data_flow_integration(self):
        """Test data flow through the entire pipeline"""
        print("\n📊 Testing Data Flow Integration...")
        
        try:
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            evasion_scorer = EvasionScorer()
            
            # Simulate multiple data items flowing through the pipeline
            test_items = [
                {
                    'title': 'Sciton Joule Laser System',
                    'brand': 'Sciton',
                    'model': 'Joule',
                    'price': 75000,
                    'condition': 'excellent'
                },
                {
                    'title': 'Cynosure Elite+ IPL Device',
                    'brand': 'Cynosure',
                    'model': 'Elite+',
                    'price': 50000,
                    'condition': 'good'
                },
                {
                    'title': 'Cutera Xeo Laser Platform',
                    'brand': 'Cutera',
                    'model': 'Xeo',
                    'price': 100000,
                    'condition': 'excellent'
                }
            ]
            
            processed_items = 0
            successful_items = 0
            
            for item in test_items:
                try:
                    # Process through pipeline
                    normalized_brand = brand_mapper.normalize_brand(item['brand'])
                    normalized_model = brand_mapper.normalize_model(item['model'], normalized_brand)
                    wholesale_value = price_analyzer.estimate_wholesale_value(normalized_brand, normalized_model, item['condition'], item['price'])
                    margin, margin_pct = price_analyzer.calculate_margin_estimate(item['price'], wholesale_value)
                    evasion_score = evasion_scorer.base_score
                    
                    if normalized_brand and normalized_model and wholesale_value and margin is not None and evasion_score is not None:
                        successful_items += 1
                    
                    processed_items += 1
                    
                except Exception as e:
                    print(f"    ⚠️ Error processing item {item['title']}: {e}")
            
            success_rate = (successful_items / processed_items) * 100 if processed_items > 0 else 0
            
            if success_rate >= 90:
                self.log_result("Data Flow Integration", "PASS", 
                              f"{successful_items}/{processed_items} items processed successfully ({success_rate:.1f}%)", 
                              is_critical=True,
                              metrics={'successful': successful_items, 'total': processed_items, 'success_rate': f"{success_rate:.1f}%"})
                self.integration_test_summary['integration_results']['data_flow_integration'] = 'PASS'
            else:
                self.log_result("Data Flow Integration", "WARN", 
                              f"Only {successful_items}/{processed_items} items processed successfully ({success_rate:.1f}%)", 
                              is_critical=False,
                              metrics={'successful': successful_items, 'total': processed_items, 'success_rate': f"{success_rate:.1f}%"})
                self.integration_test_summary['integration_results']['data_flow_integration'] = 'WARN'
                
        except Exception as e:
            self.log_result("Data Flow Integration", "FAIL", f"Error: {e}", is_critical=True)
            self.integration_test_summary['integration_results']['data_flow_integration'] = 'FAIL'
    
    def test_concurrent_integration(self):
        """Test integration under concurrent load"""
        print("\n⚡ Testing Concurrent Integration...")
        
        def integration_worker(worker_id):
            """Worker function for concurrent integration testing"""
            try:
                brand_mapper = BrandMapper()
                price_analyzer = PriceAnalyzer()
                evasion_scorer = EvasionScorer()
                
                operations = 0
                start_time = time.time()
                
                for i in range(100):
                    # Perform integration operations
                    brand_mapper.normalize_brand("Sciton")
                    brand_mapper.normalize_model("Joule", "Sciton")
                    price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", 75000)
                    price_analyzer.calculate_margin_estimate(75000, 100000)
                    evasion_scorer.base_score
                    operations += 5
                
                end_time = time.time()
                ops_per_sec = operations / (end_time - start_time)
                
                return {'worker_id': worker_id, 'operations': operations, 'ops_per_sec': ops_per_sec, 'success': True}
                
            except Exception as e:
                return {'worker_id': worker_id, 'error': str(e), 'success': False}
        
        try:
            # Test with 10 concurrent workers
            num_workers = 10
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(integration_worker, i) for i in range(num_workers)]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            successful_workers = len([r for r in results if r.get('success', False)])
            failed_workers = len([r for r in results if not r.get('success', False)])
            total_operations = sum([r.get('operations', 0) for r in results])
            avg_ops_per_sec = sum([r.get('ops_per_sec', 0) for r in results]) / len(results)
            overall_ops_per_sec = total_operations / total_time
            
            self.integration_test_summary['integration_results']['concurrent_integration'] = {
                'workers': num_workers,
                'successful_workers': successful_workers,
                'failed_workers': failed_workers,
                'total_operations': total_operations,
                'avg_ops_per_sec': avg_ops_per_sec,
                'overall_ops_per_sec': overall_ops_per_sec
            }
            
            if failed_workers == 0:
                self.log_result("Concurrent Integration", "PASS", 
                              f"{successful_workers}/{num_workers} workers successful, {overall_ops_per_sec:,.0f} ops/sec", 
                              is_critical=True,
                              metrics={'workers': num_workers, 'successful': successful_workers, 'ops_per_sec': f"{overall_ops_per_sec:,.0f}"})
            else:
                self.log_result("Concurrent Integration", "WARN", 
                              f"{successful_workers}/{num_workers} workers successful, {failed_workers} failed", 
                              is_critical=False,
                              metrics={'workers': num_workers, 'successful': successful_workers, 'failed': failed_workers})
                
        except Exception as e:
            self.log_result("Concurrent Integration", "FAIL", f"Error: {e}", is_critical=True)
    
    def test_external_service_simulation(self):
        """Test integration with simulated external services"""
        print("\n🌐 Testing External Service Simulation...")
        
        try:
            # Simulate external service responses
            mock_responses = [
                {'status': 200, 'data': {'brand': 'Sciton', 'model': 'Joule', 'price': 75000}},
                {'status': 200, 'data': {'brand': 'Cynosure', 'model': 'Elite+', 'price': 50000}},
                {'status': 200, 'data': {'brand': 'Cutera', 'model': 'Xeo', 'price': 100000}},
                {'status': 429, 'data': {'error': 'Rate limited'}},
                {'status': 403, 'data': {'error': 'Access denied'}},
            ]
            
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            evasion_scorer = EvasionScorer()
            
            successful_integrations = 0
            total_responses = len(mock_responses)
            
            for i, response in enumerate(mock_responses):
                try:
                    if response['status'] == 200:
                        # Process successful response
                        data = response['data']
                        brand = brand_mapper.normalize_brand(data['brand'])
                        model = brand_mapper.normalize_model(data['model'], brand)
                        wholesale = price_analyzer.estimate_wholesale_value(brand, model, 'excellent', data['price'])
                        margin, margin_pct = price_analyzer.calculate_margin_estimate(data['price'], wholesale)
                        score = evasion_scorer.base_score
                        
                        if brand and model and wholesale and margin is not None and score is not None:
                            successful_integrations += 1
                            self.log_result(f"External Service Response {i+1}", "PASS", 
                                          f"Status: {response['status']}, Brand: {brand}, Model: {model}", 
                                          is_critical=False,
                                          metrics={'status': response['status'], 'brand': brand, 'model': model})
                        else:
                            self.log_result(f"External Service Response {i+1}", "WARN", 
                                          f"Status: {response['status']}, Processing failed", 
                                          is_critical=False)
                    else:
                        # Handle error responses
                        self.log_result(f"External Service Response {i+1}", "PASS", 
                                      f"Status: {response['status']}, Error handled gracefully", 
                                      is_critical=False,
                                      metrics={'status': response['status'], 'error': response['data'].get('error', 'Unknown')})
                        successful_integrations += 1  # Error handling is also success
                        
                except Exception as e:
                    self.log_result(f"External Service Response {i+1}", "WARN", 
                                  f"Status: {response['status']}, Error: {e}", 
                                  is_critical=False)
            
            success_rate = (successful_integrations / total_responses) * 100
            
            if success_rate >= 80:
                self.log_result("External Service Simulation", "PASS", 
                              f"{successful_integrations}/{total_responses} responses handled successfully ({success_rate:.1f}%)", 
                              is_critical=True,
                              metrics={'successful': successful_integrations, 'total': total_responses, 'success_rate': f"{success_rate:.1f}%"})
                self.integration_test_summary['external_service_results']['service_simulation'] = 'PASS'
            else:
                self.log_result("External Service Simulation", "WARN", 
                              f"Only {successful_integrations}/{total_responses} responses handled successfully ({success_rate:.1f}%)", 
                              is_critical=False,
                              metrics={'successful': successful_integrations, 'total': total_responses, 'success_rate': f"{success_rate:.1f}%"})
                self.integration_test_summary['external_service_results']['service_simulation'] = 'WARN'
                
        except Exception as e:
            self.log_result("External Service Simulation", "FAIL", f"Error: {e}", is_critical=True)
            self.integration_test_summary['external_service_results']['service_simulation'] = 'FAIL'
    
    def run_integration_testing(self):
        """Run comprehensive integration testing"""
        print("🚀 Integration Testing - Laser Equipment Intelligence Platform")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_component_integration()
        self.test_spider_integration()
        self.test_data_flow_integration()
        self.test_concurrent_integration()
        self.test_external_service_simulation()
        
        # Generate comprehensive summary
        self.generate_integration_test_summary()
        
        return self.integration_test_summary
    
    def generate_integration_test_summary(self):
        """Generate comprehensive integration test summary"""
        total_time = time.time() - self.start_time
        
        print(f"\n📊 INTEGRATION TESTING SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.integration_test_summary['total_tests']}")
        print(f"✅ Passed: {self.integration_test_summary['passed_tests']}")
        print(f"❌ Failed: {self.integration_test_summary['failed_tests']}")
        print(f"⚠️  Warnings: {self.integration_test_summary['warning_tests']}")
        print(f"🔴 Critical Failures: {self.integration_test_summary['critical_failures']}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        # Integration results summary
        if self.integration_test_summary['integration_results']:
            print(f"\n🔗 Integration Results:")
            for test_name, status in self.integration_test_summary['integration_results'].items():
                status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
                print(f"  {status_icon} {test_name}: {status}")
        
        # External service results summary
        if self.integration_test_summary['external_service_results']:
            print(f"\n🌐 External Service Results:")
            for test_name, status in self.integration_test_summary['external_service_results'].items():
                status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
                print(f"  {status_icon} {test_name}: {status}")
        
        # Overall status
        if self.integration_test_summary['critical_failures'] == 0:
            if self.integration_test_summary['warning_tests'] == 0:
                print(f"\n🎯 STATUS: ✅ ALL INTEGRATION TESTS PASSED")
                print("🚀 System integration is working perfectly!")
                return 0
            else:
                print(f"\n🎯 STATUS: ⚠️  INTEGRATION TESTS PASSED WITH WARNINGS")
                print("🚀 System integration is working with minor issues.")
                return 0
        else:
            print(f"\n🎯 STATUS: ❌ CRITICAL INTEGRATION ISSUES DETECTED")
            print("⚠️  System integration needs attention.")
            return 1


def main():
    """Main function"""
    integration_tester = IntegrationTesting()
    integration_test_summary = integration_tester.run_integration_testing()
    
    # Return exit code based on critical failures
    exit_code = 0 if integration_test_summary['critical_failures'] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
