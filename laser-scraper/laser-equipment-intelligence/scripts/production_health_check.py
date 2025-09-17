#!/usr/bin/env python3
"""
Production Health Check Script - Laser Equipment Intelligence Platform
"""

import sys
import os
import time
import psutil
import subprocess
from datetime import datetime

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
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class ProductionHealthCheck:
    """Production health check system"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = []
        self.critical_failures = 0
        self.warnings = 0
        
    def log_result(self, test_name: str, status: str, message: str = "", is_critical: bool = False):
        """Log test result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': timestamp,
            'critical': is_critical
        }
        
        self.results.append(result)
        
        if status == "FAIL" and is_critical:
            self.critical_failures += 1
        elif status == "WARN":
            self.warnings += 1
            
        print(f"{status_icon} [{timestamp}] {test_name}: {status}")
        if message:
            print(f"    {message}")
    
    def check_system_resources(self):
        """Check system resource usage"""
        print("\n🔍 Checking System Resources...")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent < 80:
            self.log_result("CPU Usage", "PASS", f"{cpu_percent}%", is_critical=True)
        else:
            self.log_result("CPU Usage", "FAIL", f"{cpu_percent}% - High CPU usage", is_critical=True)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        if memory_percent < 85:
            self.log_result("Memory Usage", "PASS", f"{memory_percent}% ({memory.used // (1024**3)}GB/{memory.total // (1024**3)}GB)", is_critical=True)
        else:
            self.log_result("Memory Usage", "FAIL", f"{memory_percent}% - High memory usage", is_critical=True)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent < 90:
            self.log_result("Disk Usage", "PASS", f"{disk_percent:.1f}% ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)", is_critical=True)
        else:
            self.log_result("Disk Usage", "FAIL", f"{disk_percent:.1f}% - Low disk space", is_critical=True)
    
    def check_python_environment(self):
        """Check Python environment"""
        print("\n🐍 Checking Python Environment...")
        
        # Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.log_result("Python Version", "PASS", f"{python_version.major}.{python_version.minor}.{python_version.micro}", is_critical=True)
        else:
            self.log_result("Python Version", "FAIL", f"{python_version.major}.{python_version.minor}.{python_version.micro} - Requires Python 3.8+", is_critical=True)
        
        # Virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.log_result("Virtual Environment", "PASS", "Virtual environment active", is_critical=False)
        else:
            self.log_result("Virtual Environment", "WARN", "No virtual environment detected", is_critical=False)
        
        # Required packages
        required_packages = [
            'scrapy', 'playwright', 'psutil', 'pytesseract', 
            'fitz', 'PIL', 'requests', 'torch', 'numpy'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.log_result(f"Package: {package}", "PASS", "Installed", is_critical=True)
            except ImportError:
                self.log_result(f"Package: {package}", "FAIL", "Not installed", is_critical=True)
    
    def check_core_modules(self):
        """Check core application modules"""
        print("\n🔧 Checking Core Modules...")
        
        # Brand Mapping
        try:
            brand_mapper = BrandMapper()
            test_brand = brand_mapper.normalize_brand("Sciton")
            if test_brand == "Sciton":
                self.log_result("Brand Mapping", "PASS", "Module functional", is_critical=True)
            else:
                self.log_result("Brand Mapping", "FAIL", f"Unexpected result: {test_brand}", is_critical=True)
        except Exception as e:
            self.log_result("Brand Mapping", "FAIL", f"Error: {e}", is_critical=True)
        
        # Price Analysis
        try:
            price_analyzer = PriceAnalyzer()
            wholesale = price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", 100000)
            if wholesale is not None and wholesale > 0:
                self.log_result("Price Analysis", "PASS", f"Wholesale estimate: ${wholesale:,.0f}", is_critical=True)
            else:
                self.log_result("Price Analysis", "FAIL", "Invalid wholesale estimate", is_critical=True)
        except Exception as e:
            self.log_result("Price Analysis", "FAIL", f"Error: {e}", is_critical=True)
        
        # Evasion Scoring
        try:
            evasion_scorer = EvasionScorer()
            score = evasion_scorer.base_score
            if score >= 0:
                self.log_result("Evasion Scoring", "PASS", f"Base score: {score}", is_critical=True)
            else:
                self.log_result("Evasion Scoring", "FAIL", "Invalid base score", is_critical=True)
        except Exception as e:
            self.log_result("Evasion Scoring", "FAIL", f"Error: {e}", is_critical=True)
    
    def check_spider_functionality(self):
        """Check spider functionality"""
        print("\n🕷️ Checking Spider Functionality...")
        
        spiders = [
            ("DOTmed", DotmedSpider),
            ("BidSpotter", BidspotterSpider),
            ("eBay", EbaySpider),
            ("GovDeals", GovdealsSpider),
        ]
        
        for spider_name, spider_class in spiders:
            try:
                spider = spider_class()
                if hasattr(spider, 'name') and spider.name:
                    self.log_result(f"Spider: {spider_name}", "PASS", f"Name: {spider.name}", is_critical=True)
                else:
                    self.log_result(f"Spider: {spider_name}", "FAIL", "No name attribute", is_critical=True)
            except Exception as e:
                self.log_result(f"Spider: {spider_name}", "FAIL", f"Error: {e}", is_critical=True)
    
    def check_performance(self):
        """Check performance benchmarks"""
        print("\n⚡ Checking Performance...")
        
        # Brand Mapping Performance
        try:
            brand_mapper = BrandMapper()
            start_time = time.time()
            
            for i in range(1000):
                brand_mapper.normalize_brand("Sciton")
            
            end_time = time.time()
            ops_per_sec = 1000 / (end_time - start_time)
            
            if ops_per_sec > 10000:
                self.log_result("Brand Mapping Performance", "PASS", f"{ops_per_sec:,.0f} ops/sec", is_critical=False)
            else:
                self.log_result("Brand Mapping Performance", "WARN", f"{ops_per_sec:,.0f} ops/sec - Below target", is_critical=False)
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
            
            if ops_per_sec > 1000:
                self.log_result("Price Analysis Performance", "PASS", f"{ops_per_sec:,.0f} ops/sec", is_critical=False)
            else:
                self.log_result("Price Analysis Performance", "WARN", f"{ops_per_sec:,.0f} ops/sec - Below target", is_critical=False)
        except Exception as e:
            self.log_result("Price Analysis Performance", "FAIL", f"Error: {e}", is_critical=False)
    
    def check_file_permissions(self):
        """Check file permissions and accessibility"""
        print("\n📁 Checking File Permissions...")
        
        critical_files = [
            "src/laser_intelligence/utils/brand_mapping.py",
            "src/laser_intelligence/utils/price_analysis.py",
            "src/laser_intelligence/utils/evasion_scoring.py",
            "requirements.txt",
            "scripts/production_health_check.py"
        ]
        
        for file_path in critical_files:
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
            if os.path.exists(full_path):
                if os.access(full_path, os.R_OK):
                    self.log_result(f"File Access: {file_path}", "PASS", "Readable", is_critical=True)
                else:
                    self.log_result(f"File Access: {file_path}", "FAIL", "Not readable", is_critical=True)
            else:
                self.log_result(f"File Access: {file_path}", "FAIL", "File not found", is_critical=True)
    
    def run_all_checks(self):
        """Run all health checks"""
        print("🚀 Production Health Check - Laser Equipment Intelligence Platform")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.check_system_resources()
        self.check_python_environment()
        self.check_core_modules()
        self.check_spider_functionality()
        self.check_performance()
        self.check_file_permissions()
        
        # Summary
        total_time = time.time() - self.start_time
        print(f"\n📊 HEALTH CHECK SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.results if r['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"🔴 Critical Failures: {self.critical_failures}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        # Overall status
        if self.critical_failures == 0:
            if self.warnings == 0:
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
    health_check = ProductionHealthCheck()
    exit_code = health_check.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
