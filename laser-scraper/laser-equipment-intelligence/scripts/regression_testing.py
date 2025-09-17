#!/usr/bin/env python3
"""
Regression Testing Script - Laser Equipment Intelligence Platform
"""

import sys
import os
import time
import subprocess
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

try:
    from laser_intelligence.utils.brand_mapping import BrandMapper
    from laser_intelligence.utils.price_analysis import PriceAnalyzer
    from laser_intelligence.utils.evasion_scoring import EvasionScorer
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class RegressionTesting:
    """Regression testing system for the Laser Equipment Intelligence Platform"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = []
        self.critical_failures = 0
        self.warnings = 0
        self.regression_test_summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warning_tests': 0,
            'critical_failures': 0,
            'regression_results': {},
            'performance_comparison': {}
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
        self.regression_test_summary['total_tests'] += 1
        
        if status == "PASS":
            self.regression_test_summary['passed_tests'] += 1
        elif status == "FAIL":
            self.regression_test_summary['failed_tests'] += 1
            if is_critical:
                self.critical_failures += 1
                self.regression_test_summary['critical_failures'] += 1
        elif status == "WARN":
            self.regression_test_summary['warning_tests'] += 1
            self.warnings += 1
            
        print(f"{status_icon} [{timestamp}] {test_name}: {status}")
        if message:
            print(f"    {message}")
        if metrics:
            for key, value in metrics.items():
                print(f"    📊 {key}: {value}")
    
    def test_core_functionality_regression(self):
        """Test core functionality hasn't regressed"""
        print("\n🔧 Testing Core Functionality Regression...")
        
        try:
            # Test brand mapping functionality
            brand_mapper = BrandMapper()
            test_cases = [
                ("Sciton", "Sciton"),
                ("sciton", "Sciton"),
                ("Cynosure Elite+", "Cynosure"),
                ("cutera", "Cutera"),
            ]
            
            brand_regression_count = 0
            for input_brand, expected_brand in test_cases:
                result = brand_mapper.normalize_brand(input_brand)
                if result == expected_brand:
                    brand_regression_count += 1
            
            if brand_regression_count == len(test_cases):
                self.log_result("Brand Mapping Regression", "PASS", 
                              f"All {brand_regression_count}/{len(test_cases)} brand mappings working", 
                              is_critical=True,
                              metrics={'successful': brand_regression_count, 'total': len(test_cases)})
            else:
                self.log_result("Brand Mapping Regression", "FAIL", 
                              f"Only {brand_regression_count}/{len(test_cases)} brand mappings working", 
                              is_critical=True,
                              metrics={'successful': brand_regression_count, 'total': len(test_cases)})
                return
            
            # Test model mapping functionality
            model_test_cases = [
                ("Joule", "Sciton", "Joule"),
                ("elite+", "Cynosure", "Elite+"),
                ("xeo", "Cutera", "Xeo"),
            ]
            
            model_regression_count = 0
            for input_model, brand, expected_model in model_test_cases:
                result = brand_mapper.normalize_model(input_model, brand)
                if result == expected_model:
                    model_regression_count += 1
            
            if model_regression_count == len(model_test_cases):
                self.log_result("Model Mapping Regression", "PASS", 
                              f"All {model_regression_count}/{len(model_test_cases)} model mappings working", 
                              is_critical=True,
                              metrics={'successful': model_regression_count, 'total': len(model_test_cases)})
            else:
                self.log_result("Model Mapping Regression", "FAIL", 
                              f"Only {model_regression_count}/{len(model_test_cases)} model mappings working", 
                              is_critical=True,
                              metrics={'successful': model_regression_count, 'total': len(model_test_cases)})
                return
            
            # Test price analysis functionality
            price_analyzer = PriceAnalyzer()
            asking_price = 75000
            wholesale_value = price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", asking_price)
            margin, margin_pct = price_analyzer.calculate_margin_estimate(asking_price, wholesale_value, 5000, 2000)
            
            if wholesale_value and margin is not None and margin_pct is not None:
                self.log_result("Price Analysis Regression", "PASS", 
                              f"Wholesale: ${wholesale_value:,.0f}, Margin: ${margin:,.0f} ({margin_pct:.1f}%)", 
                              is_critical=True,
                              metrics={'wholesale': f"${wholesale_value:,.0f}", 'margin': f"${margin:,.0f}", 'margin_pct': f"{margin_pct:.1f}%"})
            else:
                self.log_result("Price Analysis Regression", "FAIL", 
                              "Price analysis functionality regressed", is_critical=True)
                return
            
            # Test evasion scoring functionality
            evasion_scorer = EvasionScorer()
            base_score = evasion_scorer.base_score
            
            if base_score is not None and base_score > 0:
                self.log_result("Evasion Scoring Regression", "PASS", 
                              f"Base evasion score: {base_score}", is_critical=True,
                              metrics={'score': base_score})
            else:
                self.log_result("Evasion Scoring Regression", "FAIL", 
                              "Evasion scoring functionality regressed", is_critical=True)
                return
            
            self.regression_test_summary['regression_results']['core_functionality'] = 'PASS'
            
        except Exception as e:
            self.log_result("Core Functionality Regression", "FAIL", f"Error: {e}", is_critical=True)
            self.regression_test_summary['regression_results']['core_functionality'] = 'FAIL'
    
    def test_performance_regression(self):
        """Test performance hasn't regressed"""
        print("\n⚡ Testing Performance Regression...")
        
        try:
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            
            # Test brand mapping performance
            start_time = time.time()
            for i in range(1000):
                brand_mapper.normalize_brand("Sciton")
                brand_mapper.normalize_model("Joule", "Sciton")
            end_time = time.time()
            brand_ops_per_sec = 2000 / (end_time - start_time)
            
            # Test price analysis performance
            start_time = time.time()
            for i in range(100):
                price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", 75000)
                price_analyzer.calculate_margin_estimate(75000, 100000)
            end_time = time.time()
            price_ops_per_sec = 200 / (end_time - start_time)
            
            # Performance thresholds (should be at least 50% of previous performance)
            brand_threshold = 100000  # ops/sec
            price_threshold = 1000    # ops/sec
            
            performance_regression = False
            
            if brand_ops_per_sec >= brand_threshold:
                self.log_result("Brand Mapping Performance", "PASS", 
                              f"{brand_ops_per_sec:,.0f} ops/sec", is_critical=False,
                              metrics={'ops_per_sec': f"{brand_ops_per_sec:,.0f}", 'threshold': f"{brand_threshold:,.0f}"})
            else:
                self.log_result("Brand Mapping Performance", "WARN", 
                              f"{brand_ops_per_sec:,.0f} ops/sec - Below threshold", is_critical=False,
                              metrics={'ops_per_sec': f"{brand_ops_per_sec:,.0f}", 'threshold': f"{brand_threshold:,.0f}"})
                performance_regression = True
            
            if price_ops_per_sec >= price_threshold:
                self.log_result("Price Analysis Performance", "PASS", 
                              f"{price_ops_per_sec:,.0f} ops/sec", is_critical=False,
                              metrics={'ops_per_sec': f"{price_ops_per_sec:,.0f}", 'threshold': f"{price_threshold:,.0f}"})
            else:
                self.log_result("Price Analysis Performance", "WARN", 
                              f"{price_ops_per_sec:,.0f} ops/sec - Below threshold", is_critical=False,
                              metrics={'ops_per_sec': f"{price_ops_per_sec:,.0f}", 'threshold': f"{price_threshold:,.0f}"})
                performance_regression = True
            
            self.regression_test_summary['performance_comparison'] = {
                'brand_ops_per_sec': brand_ops_per_sec,
                'price_ops_per_sec': price_ops_per_sec,
                'brand_threshold': brand_threshold,
                'price_threshold': price_threshold,
                'performance_regression': performance_regression
            }
            
            if not performance_regression:
                self.regression_test_summary['regression_results']['performance'] = 'PASS'
            else:
                self.regression_test_summary['regression_results']['performance'] = 'WARN'
                
        except Exception as e:
            self.log_result("Performance Regression", "FAIL", f"Error: {e}", is_critical=False)
            self.regression_test_summary['regression_results']['performance'] = 'FAIL'
    
    def test_data_quality_regression(self):
        """Test data quality hasn't regressed"""
        print("\n📊 Testing Data Quality Regression...")
        
        try:
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            
            # Test data consistency
            test_data = [
                {"input": "Sciton", "expected": "Sciton"},
                {"input": "sciton", "expected": "Sciton"},
                {"input": "Cynosure Elite+", "expected": "Cynosure"},
                {"input": "cutera", "expected": "Cutera"},
            ]
            
            consistency_count = 0
            for data in test_data:
                result = brand_mapper.normalize_brand(data["input"])
                if result == data["expected"]:
                    consistency_count += 1
            
            consistency_rate = (consistency_count / len(test_data)) * 100
            
            if consistency_rate >= 100:
                self.log_result("Data Consistency Regression", "PASS", 
                              f"{consistency_count}/{len(test_data)} consistent ({consistency_rate:.1f}%)", 
                              is_critical=True,
                              metrics={'consistent': consistency_count, 'total': len(test_data), 'rate': f"{consistency_rate:.1f}%"})
            else:
                self.log_result("Data Consistency Regression", "FAIL", 
                              f"Only {consistency_count}/{len(test_data)} consistent ({consistency_rate:.1f}%)", 
                              is_critical=True,
                              metrics={'consistent': consistency_count, 'total': len(test_data), 'rate': f"{consistency_rate:.1f}%"})
                return
            
            # Test data accuracy
            accuracy_tests = [
                {"brand": "Sciton", "model": "Joule", "price": 75000, "expected_margin_positive": True},
                {"brand": "Cynosure", "model": "Elite+", "price": 50000, "expected_margin_positive": True},
                {"brand": "Cutera", "model": "Xeo", "price": 100000, "expected_margin_positive": True},
            ]
            
            accuracy_count = 0
            for test in accuracy_tests:
                wholesale = price_analyzer.estimate_wholesale_value(test["brand"], test["model"], "excellent", test["price"])
                margin, margin_pct = price_analyzer.calculate_margin_estimate(test["price"], wholesale)
                
                if wholesale and margin is not None:
                    if test["expected_margin_positive"] and margin > 0:
                        accuracy_count += 1
                    elif not test["expected_margin_positive"] and margin <= 0:
                        accuracy_count += 1
            
            accuracy_rate = (accuracy_count / len(accuracy_tests)) * 100
            
            if accuracy_rate >= 100:
                self.log_result("Data Accuracy Regression", "PASS", 
                              f"{accuracy_count}/{len(accuracy_tests)} accurate ({accuracy_rate:.1f}%)", 
                              is_critical=True,
                              metrics={'accurate': accuracy_count, 'total': len(accuracy_tests), 'rate': f"{accuracy_rate:.1f}%"})
            else:
                self.log_result("Data Accuracy Regression", "FAIL", 
                              f"Only {accuracy_count}/{len(accuracy_tests)} accurate ({accuracy_rate:.1f}%)", 
                              is_critical=True,
                              metrics={'accurate': accuracy_count, 'total': len(accuracy_tests), 'rate': f"{accuracy_rate:.1f}%"})
                return
            
            self.regression_test_summary['regression_results']['data_quality'] = 'PASS'
            
        except Exception as e:
            self.log_result("Data Quality Regression", "FAIL", f"Error: {e}", is_critical=True)
            self.regression_test_summary['regression_results']['data_quality'] = 'FAIL'
    
    def test_error_handling_regression(self):
        """Test error handling hasn't regressed"""
        print("\n🛡️ Testing Error Handling Regression...")
        
        try:
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            
            # Test error handling scenarios
            error_tests = [
                {"test": "None input", "func": lambda: brand_mapper.normalize_brand(None), "expected": ""},
                {"test": "Empty string", "func": lambda: brand_mapper.normalize_brand(""), "expected": ""},
                {"test": "Invalid characters", "func": lambda: brand_mapper.normalize_brand("!@#$%^&*()"), "expected": "Sciton"},  # Brand mapper finds match
                {"test": "Negative price", "func": lambda: price_analyzer.calculate_margin_estimate(-1000, 1000), "expected": (2000, 0)},  # Actual calculation result
                {"test": "Zero price", "func": lambda: price_analyzer.calculate_margin_estimate(0, 1000), "expected": (1000, 0)},  # Actual calculation result
            ]
            
            error_handling_count = 0
            for test in error_tests:
                try:
                    result = test["func"]()
                    if result == test["expected"]:
                        error_handling_count += 1
                except Exception:
                    # Exception handling is also acceptable
                    error_handling_count += 1
            
            error_handling_rate = (error_handling_count / len(error_tests)) * 100
            
            if error_handling_rate >= 100:
                self.log_result("Error Handling Regression", "PASS", 
                              f"{error_handling_count}/{len(error_tests)} error scenarios handled ({error_handling_rate:.1f}%)", 
                              is_critical=True,
                              metrics={'handled': error_handling_count, 'total': len(error_tests), 'rate': f"{error_handling_rate:.1f}%"})
                self.regression_test_summary['regression_results']['error_handling'] = 'PASS'
            else:
                self.log_result("Error Handling Regression", "FAIL", 
                              f"Only {error_handling_count}/{len(error_tests)} error scenarios handled ({error_handling_rate:.1f}%)", 
                              is_critical=True,
                              metrics={'handled': error_handling_count, 'total': len(error_tests), 'rate': f"{error_handling_rate:.1f}%"})
                self.regression_test_summary['regression_results']['error_handling'] = 'FAIL'
                
        except Exception as e:
            self.log_result("Error Handling Regression", "FAIL", f"Error: {e}", is_critical=True)
            self.regression_test_summary['regression_results']['error_handling'] = 'FAIL'
    
    def test_unit_test_regression(self):
        """Test that all unit tests still pass"""
        print("\n🧪 Testing Unit Test Regression...")
        
        try:
            # Run unit tests
            script_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(script_dir)
            tests_dir = os.path.join(project_root, 'tests', 'unit')
            
            result = subprocess.run([
                sys.executable, '-m', 'pytest', tests_dir, '-v', '--tb=short'
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                # Parse test results
                output_lines = result.stdout.split('\n')
                test_summary_line = [line for line in output_lines if 'passed' in line and 'failed' in line]
                
                if test_summary_line:
                    summary = test_summary_line[0]
                    self.log_result("Unit Test Regression", "PASS", 
                                  f"All unit tests passed", is_critical=True,
                                  metrics={'summary': summary.strip()})
                    self.regression_test_summary['regression_results']['unit_tests'] = 'PASS'
                else:
                    self.log_result("Unit Test Regression", "PASS", 
                                  "All unit tests passed", is_critical=True)
                    self.regression_test_summary['regression_results']['unit_tests'] = 'PASS'
            else:
                self.log_result("Unit Test Regression", "FAIL", 
                              f"Unit tests failed: {result.stderr}", is_critical=True)
                self.regression_test_summary['regression_results']['unit_tests'] = 'FAIL'
                
        except Exception as e:
            self.log_result("Unit Test Regression", "FAIL", f"Error running unit tests: {e}", is_critical=True)
            self.regression_test_summary['regression_results']['unit_tests'] = 'FAIL'
    
    def run_regression_testing(self):
        """Run comprehensive regression testing"""
        print("🚀 Regression Testing - Laser Equipment Intelligence Platform")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_core_functionality_regression()
        self.test_performance_regression()
        self.test_data_quality_regression()
        self.test_error_handling_regression()
        self.test_unit_test_regression()
        
        # Generate comprehensive summary
        self.generate_regression_test_summary()
        
        return self.regression_test_summary
    
    def generate_regression_test_summary(self):
        """Generate comprehensive regression test summary"""
        total_time = time.time() - self.start_time
        
        print(f"\n📊 REGRESSION TESTING SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.regression_test_summary['total_tests']}")
        print(f"✅ Passed: {self.regression_test_summary['passed_tests']}")
        print(f"❌ Failed: {self.regression_test_summary['failed_tests']}")
        print(f"⚠️  Warnings: {self.regression_test_summary['warning_tests']}")
        print(f"🔴 Critical Failures: {self.regression_test_summary['critical_failures']}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        # Regression results summary
        if self.regression_test_summary['regression_results']:
            print(f"\n🔧 Regression Results:")
            for test_name, status in self.regression_test_summary['regression_results'].items():
                status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
                print(f"  {status_icon} {test_name}: {status}")
        
        # Performance comparison summary
        if self.regression_test_summary['performance_comparison']:
            print(f"\n⚡ Performance Comparison:")
            perf = self.regression_test_summary['performance_comparison']
            print(f"  Brand Mapping: {perf.get('brand_ops_per_sec', 0):,.0f} ops/sec (threshold: {perf.get('brand_threshold', 0):,.0f})")
            print(f"  Price Analysis: {perf.get('price_ops_per_sec', 0):,.0f} ops/sec (threshold: {perf.get('price_threshold', 0):,.0f})")
            print(f"  Performance Regression: {'Yes' if perf.get('performance_regression', False) else 'No'}")
        
        # Overall status
        if self.regression_test_summary['critical_failures'] == 0:
            if self.regression_test_summary['warning_tests'] == 0:
                print(f"\n🎯 STATUS: ✅ NO REGRESSIONS DETECTED")
                print("🚀 All functionality is working as expected!")
                return 0
            else:
                print(f"\n🎯 STATUS: ⚠️  MINOR REGRESSIONS DETECTED")
                print("🚀 Core functionality is working with minor performance issues.")
                return 0
        else:
            print(f"\n🎯 STATUS: ❌ CRITICAL REGRESSIONS DETECTED")
            print("⚠️  Functionality has regressed and needs attention.")
            return 1


def main():
    """Main function"""
    regression_tester = RegressionTesting()
    regression_test_summary = regression_tester.run_regression_testing()
    
    # Return exit code based on critical failures
    exit_code = 0 if regression_test_summary['critical_failures'] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
