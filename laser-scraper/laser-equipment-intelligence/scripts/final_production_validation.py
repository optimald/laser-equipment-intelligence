#!/usr/bin/env python3
"""
Final Production Validation Script - Laser Equipment Intelligence Platform
"""

import sys
import os
import time
import psutil
import subprocess
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

try:
    from laser_intelligence.utils.brand_mapping import BrandMapper
    from laser_intelligence.utils.price_analysis import PriceAnalyzer
    from laser_intelligence.utils.evasion_scoring import EvasionScorer
    from laser_intelligence.spiders.dotmed_spider import DotmedSpider
    from laser_intelligence.spiders.bidspotter_spider import BidspotterSpider
    from laser_intelligence.spiders.ebay_spider import EbaySpider
    from laser_intelligence.spiders.govdeals_spider import GovdealsSpider
    from laser_intelligence.spiders.facebook_marketplace_spider import FacebookMarketplaceSpider
    from laser_intelligence.spiders.craigslist_spider import CraigslistSpider
    from laser_intelligence.spiders.labx_spider import LabXSpider
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class FinalProductionValidation:
    """Final production validation system"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = []
        self.critical_failures = 0
        self.warnings = 0
        self.validation_summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warning_tests': 0,
            'critical_failures': 0,
            'performance_metrics': {},
            'spider_status': {},
            'module_status': {}
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
        self.validation_summary['total_tests'] += 1
        
        if status == "PASS":
            self.validation_summary['passed_tests'] += 1
        elif status == "FAIL":
            self.validation_summary['failed_tests'] += 1
            if is_critical:
                self.critical_failures += 1
                self.validation_summary['critical_failures'] += 1
        elif status == "WARN":
            self.validation_summary['warning_tests'] += 1
            self.warnings += 1
            
        print(f"{status_icon} [{timestamp}] {test_name}: {status}")
        if message:
            print(f"    {message}")
        if metrics:
            for key, value in metrics.items():
                print(f"    📊 {key}: {value}")
    
    def validate_core_modules(self):
        """Validate all core modules functionality"""
        print("\n🔧 Validating Core Modules...")
        
        # Brand Mapping Validation
        try:
            brand_mapper = BrandMapper()
            start_time = time.time()
            
            # Test various brand scenarios
            test_cases = [
                ("Sciton", "Sciton"),
                ("sciton", "Sciton"),
                ("Cynosure Inc.", "Cynosure"),
                ("cutera", "Cutera"),
                ("Unknown Brand", "Unknown_brand")
            ]
            
            passed_tests = 0
            for input_brand, expected in test_cases:
                result = brand_mapper.normalize_brand(input_brand)
                if result == expected:
                    passed_tests += 1
            
            end_time = time.time()
            ops_per_sec = len(test_cases) / (end_time - start_time)
            
            if passed_tests == len(test_cases):
                self.log_result("Brand Mapping Validation", "PASS", 
                              f"All {passed_tests}/{len(test_cases)} test cases passed", 
                              is_critical=True,
                              metrics={'accuracy': f"{passed_tests}/{len(test_cases)}", 'ops_per_sec': f"{ops_per_sec:.0f}"})
                self.validation_summary['module_status']['brand_mapping'] = 'PASS'
            else:
                self.log_result("Brand Mapping Validation", "FAIL", 
                              f"Only {passed_tests}/{len(test_cases)} test cases passed", 
                              is_critical=True)
                self.validation_summary['module_status']['brand_mapping'] = 'FAIL'
        except Exception as e:
            self.log_result("Brand Mapping Validation", "FAIL", f"Error: {e}", is_critical=True)
            self.validation_summary['module_status']['brand_mapping'] = 'FAIL'
        
        # Price Analysis Validation
        try:
            price_analyzer = PriceAnalyzer()
            start_time = time.time()
            
            # Test price analysis scenarios
            wholesale = price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", 100000)
            resale = price_analyzer.estimate_resale_value("Sciton", "Joule", "excellent", 100000)
            margin, margin_pct = price_analyzer.calculate_margin_estimate(80000, wholesale, 5000, 2000)
            
            end_time = time.time()
            ops_per_sec = 3 / (end_time - start_time)
            
            if wholesale and resale and margin and wholesale > 0 and resale > wholesale:
                self.log_result("Price Analysis Validation", "PASS", 
                              f"Wholesale: ${wholesale:,.0f}, Resale: ${resale:,.0f}, Margin: ${margin:,.0f} ({margin_pct:.1f}%)", 
                              is_critical=True,
                              metrics={'wholesale': f"${wholesale:,.0f}", 'resale': f"${resale:,.0f}", 'margin_pct': f"{margin_pct:.1f}%", 'ops_per_sec': f"{ops_per_sec:.0f}"})
                self.validation_summary['module_status']['price_analysis'] = 'PASS'
            else:
                self.log_result("Price Analysis Validation", "FAIL", 
                              "Invalid price analysis results", is_critical=True)
                self.validation_summary['module_status']['price_analysis'] = 'FAIL'
        except Exception as e:
            self.log_result("Price Analysis Validation", "FAIL", f"Error: {e}", is_critical=True)
            self.validation_summary['module_status']['price_analysis'] = 'FAIL'
        
        # Evasion Scoring Validation
        try:
            evasion_scorer = EvasionScorer()
            score = evasion_scorer.base_score
            
            if score >= 0:
                self.log_result("Evasion Scoring Validation", "PASS", 
                              f"Base score: {score}", is_critical=True,
                              metrics={'base_score': score})
                self.validation_summary['module_status']['evasion_scoring'] = 'PASS'
            else:
                self.log_result("Evasion Scoring Validation", "FAIL", 
                              "Invalid base score", is_critical=True)
                self.validation_summary['module_status']['evasion_scoring'] = 'FAIL'
        except Exception as e:
            self.log_result("Evasion Scoring Validation", "FAIL", f"Error: {e}", is_critical=True)
            self.validation_summary['module_status']['evasion_scoring'] = 'FAIL'
    
    def validate_spider_fleet(self):
        """Validate all spider implementations"""
        print("\n🕷️ Validating Spider Fleet...")
        
        spiders = [
            ("DOTmed", DotmedSpider),
            ("BidSpotter", BidspotterSpider),
            ("eBay", EbaySpider),
            ("GovDeals", GovdealsSpider),
            ("Facebook Marketplace", FacebookMarketplaceSpider),
            ("Craigslist", CraigslistSpider),
            ("LabX", LabXSpider),
        ]
        
        functional_spiders = 0
        total_spiders = len(spiders)
        
        for spider_name, spider_class in spiders:
            try:
                spider = spider_class()
                if hasattr(spider, 'name') and spider.name:
                    functional_spiders += 1
                    self.log_result(f"Spider: {spider_name}", "PASS", 
                                  f"Name: {spider.name}", is_critical=True,
                                  metrics={'spider_name': spider.name})
                    self.validation_summary['spider_status'][spider_name] = 'PASS'
                else:
                    self.log_result(f"Spider: {spider_name}", "FAIL", 
                                  "No name attribute", is_critical=True)
                    self.validation_summary['spider_status'][spider_name] = 'FAIL'
            except Exception as e:
                self.log_result(f"Spider: {spider_name}", "FAIL", 
                              f"Error: {e}", is_critical=True)
                self.validation_summary['spider_status'][spider_name] = 'FAIL'
        
        # Overall spider fleet status
        if functional_spiders == total_spiders:
            self.log_result("Spider Fleet Status", "PASS", 
                          f"All {functional_spiders}/{total_spiders} spiders functional", 
                          is_critical=True,
                          metrics={'functional_spiders': functional_spiders, 'total_spiders': total_spiders})
        else:
            self.log_result("Spider Fleet Status", "WARN", 
                          f"Only {functional_spiders}/{total_spiders} spiders functional", 
                          is_critical=False,
                          metrics={'functional_spiders': functional_spiders, 'total_spiders': total_spiders})
    
    def validate_performance_benchmarks(self):
        """Validate performance benchmarks"""
        print("\n⚡ Validating Performance Benchmarks...")
        
        # Brand Mapping Performance
        try:
            brand_mapper = BrandMapper()
            start_time = time.time()
            
            for i in range(1000):
                brand_mapper.normalize_brand("Sciton")
            
            end_time = time.time()
            ops_per_sec = 1000 / (end_time - start_time)
            
            self.validation_summary['performance_metrics']['brand_mapping'] = ops_per_sec
            
            if ops_per_sec > 10000:
                self.log_result("Brand Mapping Performance", "PASS", 
                              f"{ops_per_sec:,.0f} ops/sec", is_critical=False,
                              metrics={'ops_per_sec': f"{ops_per_sec:,.0f}", 'target': '10,000'})
            else:
                self.log_result("Brand Mapping Performance", "WARN", 
                              f"{ops_per_sec:,.0f} ops/sec - Below target", is_critical=False,
                              metrics={'ops_per_sec': f"{ops_per_sec:,.0f}", 'target': '10,000'})
        except Exception as e:
            self.log_result("Brand Mapping Performance", "FAIL", f"Error: {e}", is_critical=False)
        
        # Price Analysis Performance
        try:
            price_analyzer = PriceAnalyzer()
            start_time = time.time()
            
            for i in range(100):
                price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", 100000)
            
            end_time = time.time()
            ops_per_sec = 100 / (end_time - start_time)
            
            self.validation_summary['performance_metrics']['price_analysis'] = ops_per_sec
            
            if ops_per_sec > 1000:
                self.log_result("Price Analysis Performance", "PASS", 
                              f"{ops_per_sec:,.0f} ops/sec", is_critical=False,
                              metrics={'ops_per_sec': f"{ops_per_sec:,.0f}", 'target': '1,000'})
            else:
                self.log_result("Price Analysis Performance", "WARN", 
                              f"{ops_per_sec:,.0f} ops/sec - Below target", is_critical=False,
                              metrics={'ops_per_sec': f"{ops_per_sec:,.0f}", 'target': '1,000'})
        except Exception as e:
            self.log_result("Price Analysis Performance", "FAIL", f"Error: {e}", is_critical=False)
    
    def validate_system_resources(self):
        """Validate system resource usage"""
        print("\n💻 Validating System Resources...")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent < 80:
            self.log_result("CPU Usage", "PASS", f"{cpu_percent}%", is_critical=True,
                          metrics={'cpu_percent': f"{cpu_percent}%", 'threshold': '80%'})
        else:
            self.log_result("CPU Usage", "FAIL", f"{cpu_percent}% - High CPU usage", is_critical=True,
                          metrics={'cpu_percent': f"{cpu_percent}%", 'threshold': '80%'})
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        if memory_percent < 85:
            self.log_result("Memory Usage", "PASS", 
                          f"{memory_percent}% ({memory.used // (1024**3)}GB/{memory.total // (1024**3)}GB)", 
                          is_critical=True,
                          metrics={'memory_percent': f"{memory_percent}%", 'used_gb': f"{memory.used // (1024**3)}", 'total_gb': f"{memory.total // (1024**3)}", 'threshold': '85%'})
        else:
            self.log_result("Memory Usage", "FAIL", f"{memory_percent}% - High memory usage", is_critical=True,
                          metrics={'memory_percent': f"{memory_percent}%", 'threshold': '85%'})
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent < 90:
            self.log_result("Disk Usage", "PASS", 
                          f"{disk_percent:.1f}% ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)", 
                          is_critical=True,
                          metrics={'disk_percent': f"{disk_percent:.1f}%", 'used_gb': f"{disk.used // (1024**3)}", 'total_gb': f"{disk.total // (1024**3)}", 'threshold': '90%'})
        else:
            self.log_result("Disk Usage", "FAIL", f"{disk_percent:.1f}% - Low disk space", is_critical=True,
                          metrics={'disk_percent': f"{disk_percent:.1f}%", 'threshold': '90%'})
    
    def validate_file_system(self):
        """Validate file system and permissions"""
        print("\n📁 Validating File System...")
        
        critical_files = [
            "src/laser_intelligence/utils/brand_mapping.py",
            "src/laser_intelligence/utils/price_analysis.py",
            "src/laser_intelligence/utils/evasion_scoring.py",
            "src/laser_intelligence/spiders/dotmed_spider.py",
            "src/laser_intelligence/spiders/bidspotter_spider.py",
            "src/laser_intelligence/spiders/ebay_spider.py",
            "src/laser_intelligence/spiders/govdeals_spider.py",
            "requirements.txt",
            "scripts/production_health_check.py",
            "scripts/final_production_validation.py"
        ]
        
        accessible_files = 0
        total_files = len(critical_files)
        
        for file_path in critical_files:
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
            if os.path.exists(full_path):
                if os.access(full_path, os.R_OK):
                    accessible_files += 1
                    self.log_result(f"File Access: {file_path}", "PASS", "Readable", is_critical=True)
                else:
                    self.log_result(f"File Access: {file_path}", "FAIL", "Not readable", is_critical=True)
            else:
                self.log_result(f"File Access: {file_path}", "FAIL", "File not found", is_critical=True)
        
        # Overall file system status
        if accessible_files == total_files:
            self.log_result("File System Status", "PASS", 
                          f"All {accessible_files}/{total_files} critical files accessible", 
                          is_critical=True,
                          metrics={'accessible_files': accessible_files, 'total_files': total_files})
        else:
            self.log_result("File System Status", "FAIL", 
                          f"Only {accessible_files}/{total_files} critical files accessible", 
                          is_critical=True,
                          metrics={'accessible_files': accessible_files, 'total_files': total_files})
    
    def run_comprehensive_validation(self):
        """Run comprehensive production validation"""
        print("🚀 Final Production Validation - Laser Equipment Intelligence Platform")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.validate_system_resources()
        self.validate_core_modules()
        self.validate_spider_fleet()
        self.validate_performance_benchmarks()
        self.validate_file_system()
        
        # Generate comprehensive summary
        self.generate_final_summary()
        
        return self.validation_summary
    
    def generate_final_summary(self):
        """Generate comprehensive final summary"""
        total_time = time.time() - self.start_time
        
        print(f"\n📊 FINAL PRODUCTION VALIDATION SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.validation_summary['total_tests']}")
        print(f"✅ Passed: {self.validation_summary['passed_tests']}")
        print(f"❌ Failed: {self.validation_summary['failed_tests']}")
        print(f"⚠️  Warnings: {self.validation_summary['warning_tests']}")
        print(f"🔴 Critical Failures: {self.validation_summary['critical_failures']}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        # Performance metrics summary
        if self.validation_summary['performance_metrics']:
            print(f"\n⚡ Performance Metrics:")
            for module, ops_per_sec in self.validation_summary['performance_metrics'].items():
                print(f"  {module}: {ops_per_sec:,.0f} ops/sec")
        
        # Module status summary
        if self.validation_summary['module_status']:
            print(f"\n🔧 Module Status:")
            for module, status in self.validation_summary['module_status'].items():
                status_icon = "✅" if status == "PASS" else "❌"
                print(f"  {status_icon} {module}: {status}")
        
        # Spider status summary
        if self.validation_summary['spider_status']:
            print(f"\n🕷️ Spider Status:")
            for spider, status in self.validation_summary['spider_status'].items():
                status_icon = "✅" if status == "PASS" else "❌"
                print(f"  {status_icon} {spider}: {status}")
        
        # Overall status
        if self.validation_summary['critical_failures'] == 0:
            if self.validation_summary['warning_tests'] == 0:
                print(f"\n🎯 STATUS: ✅ ALL SYSTEMS OPERATIONAL")
                print("🚀 Platform is ready for production deployment!")
                return 0
            else:
                print(f"\n🎯 STATUS: ⚠️  OPERATIONAL WITH WARNINGS")
                print("🚀 Platform is ready for production deployment with minor issues.")
                return 0
        else:
            print(f"\n🎯 STATUS: ❌ CRITICAL ISSUES DETECTED")
            print("⚠️  Platform needs attention before production deployment.")
            return 1


def main():
    """Main function"""
    validator = FinalProductionValidation()
    validation_summary = validator.run_comprehensive_validation()
    
    # Save validation summary to file
    summary_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'FINAL_VALIDATION_SUMMARY.json')
    with open(summary_file, 'w') as f:
        json.dump(validation_summary, f, indent=2)
    
    print(f"\n📄 Validation summary saved to: {summary_file}")
    
    # Return exit code based on critical failures
    exit_code = 0 if validation_summary['critical_failures'] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
