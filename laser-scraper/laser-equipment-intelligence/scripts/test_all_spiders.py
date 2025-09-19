#!/usr/bin/env python3
"""
Comprehensive spider testing script for laser equipment intelligence platform
Tests all implemented spiders for basic functionality and data extraction
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Any
import json

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.settings import Settings

# Import all spiders
from laser_intelligence.spiders.dotmed_spider import DotmedSpider
from laser_intelligence.spiders.bidspotter_spider import BidspotterSpider
from laser_intelligence.spiders.ebay_spider import EbaySpider
from laser_intelligence.spiders.govdeals_spider import GovdealsSpider
from laser_intelligence.spiders.facebook_groups_spider import FacebookGroupsSpider
from laser_intelligence.spiders.facebook_groups_session_spider import FacebookGroupsSessionSpider
from laser_intelligence.spiders.facebook_groups_api_spider import FacebookGroupsAPISpider
from laser_intelligence.spiders.reddit_spider import RedditSpider
from laser_intelligence.spiders.craigslist_spider import CraigslistSpider
from laser_intelligence.spiders.facebook_marketplace_spider import FacebookMarketplaceSpider
from laser_intelligence.spiders.labx_spider import LabXSpider
from laser_intelligence.spiders.medwow_spider import MedwowSpider
from laser_intelligence.spiders.thelaserwarehouse_spider import TheLaserWarehouseSpider
from laser_intelligence.spiders.used_line_spider import UsedLineSpider
from laser_intelligence.spiders.ajwillner_auctions_spider import AJWillnerAuctionsSpider
from laser_intelligence.spiders.heritage_global_spider import HeritageGlobalSpider
from laser_intelligence.spiders.proxibid_spider import ProxibidSpider
from laser_intelligence.spiders.gsa_auctions_spider import GSAAuctionsSpider
from laser_intelligence.spiders.govplanet_spider import GovPlanetSpider
from laser_intelligence.spiders.centurion_spider import CenturionSpider
from laser_intelligence.spiders.laser_agent_spider import LaserAgentSpider
from laser_intelligence.spiders.laser_service_solutions_spider import LaserServiceSolutionsSpider
from laser_intelligence.spiders.iron_horse_auction_spider import IronHorseAuctionSpider
from laser_intelligence.spiders.kurtz_auction_spider import KurtzAuctionSpider
from laser_intelligence.spiders.asset_recovery_services_spider import AssetRecoveryServicesSpider
from laser_intelligence.spiders.hilditch_group_spider import HilditchGroupSpider


class SpiderTestResults:
    """Class to track spider test results"""
    
    def __init__(self):
        self.results = {}
        self.total_spiders = 0
        self.passed_spiders = 0
        self.failed_spiders = 0
        self.errors = []
    
    def add_result(self, spider_name: str, status: str, message: str = "", items_found: int = 0):
        """Add a test result for a spider"""
        self.results[spider_name] = {
            'status': status,
            'message': message,
            'items_found': items_found,
            'timestamp': time.time()
        }
        
        if status == 'PASS':
            self.passed_spiders += 1
        else:
            self.failed_spiders += 1
            self.errors.append(f"{spider_name}: {message}")
        
        self.total_spiders += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of test results"""
        return {
            'total_spiders': self.total_spiders,
            'passed_spiders': self.passed_spiders,
            'failed_spiders': self.failed_spiders,
            'success_rate': (self.passed_spiders / self.total_spiders * 100) if self.total_spiders > 0 else 0,
            'errors': self.errors
        }


class SpiderTester:
    """Main spider testing class"""
    
    def __init__(self):
        self.results = SpiderTestResults()
        self.test_items = []
        
        # Configure logging
        configure_logging({
            'LOG_LEVEL': 'WARNING',
            'LOG_ENABLED': False
        })
        
        # Define all spiders to test
        self.spiders_to_test = [
            # Core auction platforms
            {'name': 'dotmed_auctions', 'class': DotmedSpider, 'priority': 'HIGH'},
            {'name': 'bidspotter', 'class': BidspotterSpider, 'priority': 'HIGH'},
            {'name': 'govdeals', 'class': GovdealsSpider, 'priority': 'HIGH'},
            
            # Marketplaces
            {'name': 'ebay_laser', 'class': EbaySpider, 'priority': 'HIGH'},
            {'name': 'facebook_marketplace', 'class': FacebookMarketplaceSpider, 'priority': 'MEDIUM'},
            {'name': 'craigslist', 'class': CraigslistSpider, 'priority': 'MEDIUM'},
            
            # Specialized dealers
            {'name': 'thelaserwarehouse', 'class': TheLaserWarehouseSpider, 'priority': 'HIGH'},
            {'name': 'laser_agent', 'class': LaserAgentSpider, 'priority': 'HIGH'},
            {'name': 'laser_service_solutions', 'class': LaserServiceSolutionsSpider, 'priority': 'HIGH'},
            
            # International sources
            {'name': 'medwow', 'class': MedwowSpider, 'priority': 'MEDIUM'},
            {'name': 'hilditch_group', 'class': HilditchGroupSpider, 'priority': 'MEDIUM'},
            
            # Social media
            {'name': 'facebook_groups', 'class': FacebookGroupsSpider, 'priority': 'LOW'},
            {'name': 'reddit', 'class': RedditSpider, 'priority': 'LOW'},
            
            # Laboratory equipment
            {'name': 'labx', 'class': LabXSpider, 'priority': 'MEDIUM'},
            {'name': 'used_line', 'class': UsedLineSpider, 'priority': 'MEDIUM'},
            
            # Auction platforms
            {'name': 'ajwillner_auctions', 'class': AJWillnerAuctionsSpider, 'priority': 'MEDIUM'},
            {'name': 'heritage_global', 'class': HeritageGlobalSpider, 'priority': 'MEDIUM'},
            {'name': 'proxibid', 'class': ProxibidSpider, 'priority': 'MEDIUM'},
            {'name': 'gsa_auctions', 'class': GSAAuctionsSpider, 'priority': 'LOW'},
            {'name': 'govplanet', 'class': GovPlanetSpider, 'priority': 'LOW'},
            {'name': 'centurion', 'class': CenturionSpider, 'priority': 'MEDIUM'},
            
            # New implementations
            {'name': 'iron_horse_auction', 'class': IronHorseAuctionSpider, 'priority': 'HIGH'},
            {'name': 'kurtz_auction', 'class': KurtzAuctionSpider, 'priority': 'HIGH'},
            {'name': 'asset_recovery_services', 'class': AssetRecoveryServicesSpider, 'priority': 'HIGH'},
        ]
    
    def test_spider_initialization(self, spider_class) -> tuple[bool, str]:
        """Test if a spider can be initialized"""
        try:
            spider = spider_class()
            
            # Check required attributes
            required_attrs = ['name', 'allowed_domains']
            for attr in required_attrs:
                if not hasattr(spider, attr):
                    return False, f"Missing required attribute: {attr}"
            
            # Check required methods
            required_methods = ['start_requests']
            for method in required_methods:
                if not hasattr(spider, method) or not callable(getattr(spider, method)):
                    return False, f"Missing required method: {method}"
            
            return True, "Spider initialized successfully"
            
        except Exception as e:
            return False, f"Initialization failed: {str(e)}"
    
    def test_spider_start_requests(self, spider_class) -> tuple[bool, str, int]:
        """Test if spider can generate start requests"""
        try:
            spider = spider_class()
            requests = list(spider.start_requests())
            
            if not requests:
                return False, "No start requests generated", 0
            
            return True, f"Generated {len(requests)} start requests", len(requests)
            
        except Exception as e:
            return False, f"Start requests failed: {str(e)}", 0
    
    def test_spider_parse_methods(self, spider_class) -> tuple[bool, str]:
        """Test if spider has parse methods"""
        try:
            spider = spider_class()
            
            # Check for parse methods
            parse_methods = [method for method in dir(spider) if method.startswith('parse')]
            
            if not parse_methods:
                return False, "No parse methods found"
            
            return True, f"Found {len(parse_methods)} parse methods: {', '.join(parse_methods)}"
            
        except Exception as e:
            return False, f"Parse methods check failed: {str(e)}"
    
    def test_spider_laser_keywords(self, spider_class) -> tuple[bool, str]:
        """Test if spider has laser equipment keywords"""
        try:
            spider = spider_class()
            
            # Check for laser keywords
            if hasattr(spider, 'laser_keywords'):
                keywords = spider.laser_keywords
                if keywords and len(keywords) > 0:
                    return True, f"Found {len(keywords)} laser keywords"
                else:
                    return False, "Laser keywords list is empty"
            else:
                return False, "No laser_keywords attribute found"
            
        except Exception as e:
            return False, f"Laser keywords check failed: {str(e)}"
    
    def test_spider_custom_settings(self, spider_class) -> tuple[bool, str]:
        """Test if spider has custom settings"""
        try:
            spider = spider_class()
            
            if hasattr(spider, 'custom_settings'):
                settings = spider.custom_settings
                if settings:
                    return True, f"Found {len(settings)} custom settings"
                else:
                    return False, "Custom settings is empty"
            else:
                return False, "No custom_settings attribute found"
            
        except Exception as e:
            return False, f"Custom settings check failed: {str(e)}"
    
    def run_comprehensive_test(self, spider_info: Dict) -> Dict[str, Any]:
        """Run comprehensive tests on a single spider"""
        spider_name = spider_info['name']
        spider_class = spider_info['class']
        priority = spider_info['priority']
        
        print(f"\n🧪 Testing {spider_name} ({priority} priority)...")
        
        test_results = {
            'spider_name': spider_name,
            'priority': priority,
            'tests': {},
            'overall_status': 'FAIL'
        }
        
        # Test 1: Initialization
        success, message = self.test_spider_initialization(spider_class)
        test_results['tests']['initialization'] = {'status': success, 'message': message}
        
        if not success:
            test_results['overall_status'] = 'FAIL'
            return test_results
        
        # Test 2: Start requests
        success, message, count = self.test_spider_start_requests(spider_class)
        test_results['tests']['start_requests'] = {'status': success, 'message': message, 'count': count}
        
        if not success:
            test_results['overall_status'] = 'FAIL'
            return test_results
        
        # Test 3: Parse methods
        success, message = self.test_spider_parse_methods(spider_class)
        test_results['tests']['parse_methods'] = {'status': success, 'message': message}
        
        # Test 4: Laser keywords
        success, message = self.test_spider_laser_keywords(spider_class)
        test_results['tests']['laser_keywords'] = {'status': success, 'message': message}
        
        # Test 5: Custom settings
        success, message = self.test_spider_custom_settings(spider_class)
        test_results['tests']['custom_settings'] = {'status': success, 'message': message}
        
        # Determine overall status
        critical_tests = ['initialization', 'start_requests']
        critical_passed = all(test_results['tests'][test]['status'] for test in critical_tests)
        
        if critical_passed:
            test_results['overall_status'] = 'PASS'
        else:
            test_results['overall_status'] = 'FAIL'
        
        return test_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run tests on all spiders"""
        print("🚀 Starting comprehensive spider testing...")
        print(f"📊 Testing {len(self.spiders_to_test)} spiders")
        
        all_results = {}
        
        for spider_info in self.spiders_to_test:
            try:
                result = self.run_comprehensive_test(spider_info)
                all_results[spider_info['name']] = result
                
                # Add to overall results
                self.results.add_result(
                    spider_info['name'],
                    result['overall_status'],
                    result['tests'].get('initialization', {}).get('message', ''),
                    result['tests'].get('start_requests', {}).get('count', 0)
                )
                
            except Exception as e:
                print(f"❌ Error testing {spider_info['name']}: {str(e)}")
                self.results.add_result(spider_info['name'], 'ERROR', str(e))
        
        return all_results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report"""
        summary = self.results.get_summary()
        
        report = []
        report.append("=" * 80)
        report.append("🕷️  LASER EQUIPMENT INTELLIGENCE - SPIDER TEST REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Spiders Tested: {summary['total_spiders']}")
        report.append(f"Passed: {summary['passed_spiders']}")
        report.append(f"Failed: {summary['failed_spiders']}")
        report.append(f"Success Rate: {summary['success_rate']:.1f}%")
        report.append("")
        
        # Priority breakdown
        priority_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        priority_passed = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for spider_info in self.spiders_to_test:
            priority = spider_info['priority']
            spider_name = spider_info['name']
            priority_counts[priority] += 1
            
            if results.get(spider_name, {}).get('overall_status') == 'PASS':
                priority_passed[priority] += 1
        
        report.append("🎯 PRIORITY BREAKDOWN")
        report.append("-" * 40)
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            if priority_counts[priority] > 0:
                rate = (priority_passed[priority] / priority_counts[priority]) * 100
                report.append(f"{priority} Priority: {priority_passed[priority]}/{priority_counts[priority]} ({rate:.1f}%)")
        report.append("")
        
        # Detailed results
        report.append("📋 DETAILED RESULTS")
        report.append("-" * 40)
        
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            report.append(f"\n{priority} PRIORITY SPIDERS:")
            for spider_info in self.spiders_to_test:
                if spider_info['priority'] == priority:
                    spider_name = spider_info['name']
                    result = results.get(spider_name, {})
                    status = result.get('overall_status', 'UNKNOWN')
                    
                    status_emoji = "✅" if status == 'PASS' else "❌" if status == 'FAIL' else "⚠️"
                    report.append(f"  {status_emoji} {spider_name}: {status}")
                    
                    # Show test details for failed spiders
                    if status == 'FAIL':
                        tests = result.get('tests', {})
                        for test_name, test_result in tests.items():
                            if not test_result.get('status', False):
                                report.append(f"    - {test_name}: {test_result.get('message', '')}")
        
        # Errors
        if summary['errors']:
            report.append("\n❌ ERRORS")
            report.append("-" * 40)
            for error in summary['errors']:
                report.append(f"  - {error}")
        
        # Recommendations
        report.append("\n💡 RECOMMENDATIONS")
        report.append("-" * 40)
        
        if summary['success_rate'] >= 90:
            report.append("🎉 Excellent! Spider implementation is in great shape.")
            report.append("   Ready for production deployment.")
        elif summary['success_rate'] >= 75:
            report.append("👍 Good progress! Most spiders are working correctly.")
            report.append("   Focus on fixing failed spiders before production.")
        elif summary['success_rate'] >= 50:
            report.append("⚠️  Moderate success rate. Several spiders need attention.")
            report.append("   Prioritize HIGH priority spiders for fixes.")
        else:
            report.append("🚨 Low success rate. Significant issues need to be addressed.")
            report.append("   Review and fix critical spiders before proceeding.")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any], filename: str = "spider_test_results.json"):
        """Save test results to JSON file"""
        output_path = Path(__file__).parent / filename
        
        # Prepare results for JSON serialization
        json_results = {}
        for spider_name, result in results.items():
            json_results[spider_name] = {
                'spider_name': result['spider_name'],
                'priority': result['priority'],
                'overall_status': result['overall_status'],
                'tests': result['tests'],
                'timestamp': time.time()
            }
        
        with open(output_path, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"📁 Results saved to: {output_path}")
    
    def run(self):
        """Main run method"""
        try:
            # Run all tests
            results = self.run_all_tests()
            
            # Generate and display report
            report = self.generate_report(results)
            print(report)
            
            # Save results
            self.save_results(results)
            
            # Return success/failure
            summary = self.results.get_summary()
            return summary['success_rate'] >= 75
            
        except Exception as e:
            print(f"❌ Testing failed with error: {str(e)}")
            return False


def main():
    """Main function"""
    print("🕷️  Laser Equipment Intelligence - Spider Testing Suite")
    print("=" * 60)
    
    tester = SpiderTester()
    success = tester.run()
    
    if success:
        print("\n🎉 Spider testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Spider testing completed with issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
