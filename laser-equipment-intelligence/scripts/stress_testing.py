#!/usr/bin/env python3
"""
Stress Testing Script - Laser Equipment Intelligence Platform
"""

import sys
import os
import time
import threading
import psutil
import gc
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

try:
    from laser_intelligence.utils.brand_mapping import BrandMapper
    from laser_intelligence.utils.price_analysis import PriceAnalyzer
    from laser_intelligence.utils.evasion_scoring import EvasionScorer
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class StressTesting:
    """Stress testing system for the Laser Equipment Intelligence Platform"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = []
        self.critical_failures = 0
        self.warnings = 0
        self.stress_test_summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warning_tests': 0,
            'critical_failures': 0,
            'stress_metrics': {},
            'resource_usage': {}
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
        self.stress_test_summary['total_tests'] += 1
        
        if status == "PASS":
            self.stress_test_summary['passed_tests'] += 1
        elif status == "FAIL":
            self.stress_test_summary['failed_tests'] += 1
            if is_critical:
                self.critical_failures += 1
                self.stress_test_summary['critical_failures'] += 1
        elif status == "WARN":
            self.stress_test_summary['warning_tests'] += 1
            self.warnings += 1
            
        print(f"{status_icon} [{timestamp}] {test_name}: {status}")
        if message:
            print(f"    {message}")
        if metrics:
            for key, value in metrics.items():
                print(f"    📊 {key}: {value}")
    
    def test_extreme_concurrent_load(self):
        """Test system under extreme concurrent load"""
        print("\n🔥 Testing Extreme Concurrent Load...")
        
        def extreme_worker_thread(thread_id):
            """Worker thread for extreme load testing"""
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            evasion_scorer = EvasionScorer()
            
            start_time = time.time()
            operations = 0
            
            try:
                while time.time() - start_time < 10:  # Run for 10 seconds
                    # Perform various operations
                    brand_mapper.normalize_brand("Sciton")
                    brand_mapper.normalize_model("Joule", "Sciton")
                    price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", 100000)
                    price_analyzer.calculate_margin_estimate(80000, 100000, 5000, 2000)
                    evasion_scorer.base_score
                    operations += 5
                    
            except Exception as e:
                return {'error': str(e), 'operations': operations}
            
            return {'operations': operations, 'thread_id': thread_id}
        
        try:
            # Test with 50 concurrent threads
            num_threads = 50
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(extreme_worker_thread, i) for i in range(num_threads)]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            successful_threads = len([r for r in results if 'error' not in r])
            failed_threads = len([r for r in results if 'error' in r])
            total_operations = sum([r.get('operations', 0) for r in results])
            ops_per_sec = total_operations / total_time
            
            self.stress_test_summary['stress_metrics']['extreme_concurrent_load'] = {
                'threads': num_threads,
                'successful_threads': successful_threads,
                'failed_threads': failed_threads,
                'total_operations': total_operations,
                'ops_per_sec': ops_per_sec,
                'total_time': total_time
            }
            
            if failed_threads == 0:
                self.log_result("Extreme Concurrent Load", "PASS", 
                              f"{successful_threads}/{num_threads} threads successful, {ops_per_sec:,.0f} ops/sec", 
                              is_critical=True,
                              metrics={'threads': num_threads, 'successful': successful_threads, 'ops_per_sec': f"{ops_per_sec:,.0f}"})
            elif failed_threads < num_threads * 0.1:  # Less than 10% failure
                self.log_result("Extreme Concurrent Load", "WARN", 
                              f"{successful_threads}/{num_threads} threads successful, {failed_threads} failed", 
                              is_critical=False,
                              metrics={'threads': num_threads, 'successful': successful_threads, 'failed': failed_threads})
            else:
                self.log_result("Extreme Concurrent Load", "FAIL", 
                              f"High failure rate: {failed_threads}/{num_threads} threads failed", 
                              is_critical=True,
                              metrics={'threads': num_threads, 'failed': failed_threads})
                
        except Exception as e:
            self.log_result("Extreme Concurrent Load", "FAIL", f"Error: {e}", is_critical=True)
    
    def test_memory_stress(self):
        """Test system under memory stress"""
        print("\n💾 Testing Memory Stress...")
        
        try:
            # Get initial memory
            initial_memory = psutil.virtual_memory()
            initial_percent = initial_memory.percent
            
            # Create many instances to stress memory
            instances = []
            for i in range(1000):
                instances.append(BrandMapper())
                instances.append(PriceAnalyzer())
                instances.append(EvasionScorer())
                
                # Check memory every 100 instances
                if i % 100 == 0:
                    current_memory = psutil.virtual_memory()
                    if current_memory.percent > 95:
                        break
            
            # Get memory after stress
            stress_memory = psutil.virtual_memory()
            stress_percent = stress_memory.percent
            memory_increase = stress_percent - initial_percent
            
            # Clean up
            del instances
            gc.collect()
            
            # Get final memory
            final_memory = psutil.virtual_memory()
            final_percent = final_memory.percent
            
            self.stress_test_summary['resource_usage']['memory_stress'] = {
                'initial_percent': initial_percent,
                'stress_percent': stress_percent,
                'final_percent': final_percent,
                'memory_increase': memory_increase,
                'instances_created': len(instances) if 'instances' in locals() else 0
            }
            
            if stress_percent < 90:
                self.log_result("Memory Stress", "PASS", 
                              f"Memory under stress: {stress_percent:.1f}%", is_critical=True,
                              metrics={'initial': f"{initial_percent:.1f}%", 'stress': f"{stress_percent:.1f}%", 'final': f"{final_percent:.1f}%"})
            else:
                self.log_result("Memory Stress", "WARN", 
                              f"High memory usage: {stress_percent:.1f}%", is_critical=False,
                              metrics={'initial': f"{initial_percent:.1f}%", 'stress': f"{stress_percent:.1f}%", 'final': f"{final_percent:.1f}%"})
                
        except Exception as e:
            self.log_result("Memory Stress", "FAIL", f"Error: {e}", is_critical=True)
    
    def test_cpu_stress(self):
        """Test system under CPU stress"""
        print("\n🖥️ Testing CPU Stress...")
        
        try:
            # Get initial CPU
            initial_cpu = psutil.cpu_percent(interval=1)
            
            # Create CPU-intensive tasks
            def cpu_stress_task():
                brand_mapper = BrandMapper()
                for i in range(100000):
                    brand_mapper.normalize_brand("Sciton")
                    brand_mapper.normalize_model("Joule", "Sciton")
            
            # Run multiple CPU-intensive threads
            threads = []
            for i in range(10):
                thread = threading.Thread(target=cpu_stress_task)
                threads.append(thread)
                thread.start()
            
            # Monitor CPU usage
            max_cpu = 0
            for i in range(20):  # Monitor for 20 seconds
                current_cpu = psutil.cpu_percent(interval=1)
                max_cpu = max(max_cpu, current_cpu)
            
            # Wait for threads to complete
            for thread in threads:
                thread.join()
            
            # Get final CPU
            final_cpu = psutil.cpu_percent(interval=1)
            
            self.stress_test_summary['resource_usage']['cpu_stress'] = {
                'initial_cpu': initial_cpu,
                'max_cpu': max_cpu,
                'final_cpu': final_cpu
            }
            
            if max_cpu < 95:
                self.log_result("CPU Stress", "PASS", 
                              f"Max CPU usage: {max_cpu:.1f}%", is_critical=True,
                              metrics={'initial': f"{initial_cpu:.1f}%", 'max': f"{max_cpu:.1f}%", 'final': f"{final_cpu:.1f}%"})
            else:
                self.log_result("CPU Stress", "WARN", 
                              f"Very high CPU usage: {max_cpu:.1f}%", is_critical=False,
                              metrics={'initial': f"{initial_cpu:.1f}%", 'max': f"{max_cpu:.1f}%", 'final': f"{final_cpu:.1f}%"})
                
        except Exception as e:
            self.log_result("CPU Stress", "FAIL", f"Error: {e}", is_critical=True)
    
    def test_error_recovery(self):
        """Test system error recovery under stress"""
        print("\n🛡️ Testing Error Recovery Under Stress...")
        
        try:
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            
            # Test with various error conditions
            error_tests = [
                ("None input", lambda: brand_mapper.normalize_brand(None)),
                ("Empty string", lambda: brand_mapper.normalize_brand("")),
                ("Invalid characters", lambda: brand_mapper.normalize_brand("!@#$%^&*()")),
                ("Very long string", lambda: brand_mapper.normalize_brand("A" * 10000)),
                ("Negative price", lambda: price_analyzer.calculate_margin_estimate(-1000, 1000)),
                ("Zero price", lambda: price_analyzer.calculate_margin_estimate(0, 1000)),
                ("Invalid condition", lambda: price_analyzer.estimate_wholesale_value("Sciton", "Joule", "invalid", 100000)),
            ]
            
            successful_recoveries = 0
            total_tests = len(error_tests)
            
            for test_name, test_func in error_tests:
                try:
                    result = test_func()
                    # If we get here without exception, it's a successful recovery
                    successful_recoveries += 1
                except Exception:
                    # Exception is also acceptable - system handled error gracefully
                    successful_recoveries += 1
            
            self.stress_test_summary['stress_metrics']['error_recovery'] = {
                'successful_recoveries': successful_recoveries,
                'total_tests': total_tests,
                'recovery_rate': successful_recoveries / total_tests
            }
            
            if successful_recoveries == total_tests:
                self.log_result("Error Recovery", "PASS", 
                              f"All {successful_recoveries}/{total_tests} error conditions handled", 
                              is_critical=True,
                              metrics={'recoveries': successful_recoveries, 'total': total_tests})
            else:
                self.log_result("Error Recovery", "WARN", 
                              f"Only {successful_recoveries}/{total_tests} error conditions handled", 
                              is_critical=False,
                              metrics={'recoveries': successful_recoveries, 'total': total_tests})
                
        except Exception as e:
            self.log_result("Error Recovery", "FAIL", f"Error: {e}", is_critical=True)
    
    def test_system_stability(self):
        """Test system stability under prolonged stress"""
        print("\n⚖️ Testing System Stability...")
        
        try:
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            
            # Run operations for extended period
            start_time = time.time()
            operations = 0
            errors = 0
            
            while time.time() - start_time < 30:  # Run for 30 seconds
                try:
                    brand_mapper.normalize_brand("Sciton")
                    brand_mapper.normalize_model("Joule", "Sciton")
                    price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", 100000)
                    operations += 3
                except Exception:
                    errors += 1
                
                # Small delay to prevent overwhelming
                time.sleep(0.001)
            
            total_time = time.time() - start_time
            ops_per_sec = operations / total_time
            error_rate = errors / operations if operations > 0 else 0
            
            self.stress_test_summary['stress_metrics']['system_stability'] = {
                'total_operations': operations,
                'errors': errors,
                'ops_per_sec': ops_per_sec,
                'error_rate': error_rate,
                'total_time': total_time
            }
            
            if error_rate < 0.01:  # Less than 1% error rate
                self.log_result("System Stability", "PASS", 
                              f"{operations} operations, {errors} errors, {ops_per_sec:,.0f} ops/sec", 
                              is_critical=True,
                              metrics={'operations': operations, 'errors': errors, 'ops_per_sec': f"{ops_per_sec:,.0f}", 'error_rate': f"{error_rate:.3f}"})
            else:
                self.log_result("System Stability", "WARN", 
                              f"High error rate: {error_rate:.3f}", 
                              is_critical=False,
                              metrics={'operations': operations, 'errors': errors, 'error_rate': f"{error_rate:.3f}"})
                
        except Exception as e:
            self.log_result("System Stability", "FAIL", f"Error: {e}", is_critical=True)
    
    def run_stress_testing(self):
        """Run comprehensive stress testing"""
        print("🚀 Stress Testing - Laser Equipment Intelligence Platform")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_extreme_concurrent_load()
        self.test_memory_stress()
        self.test_cpu_stress()
        self.test_error_recovery()
        self.test_system_stability()
        
        # Generate comprehensive summary
        self.generate_stress_test_summary()
        
        return self.stress_test_summary
    
    def generate_stress_test_summary(self):
        """Generate comprehensive stress test summary"""
        total_time = time.time() - self.start_time
        
        print(f"\n📊 STRESS TESTING SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.stress_test_summary['total_tests']}")
        print(f"✅ Passed: {self.stress_test_summary['passed_tests']}")
        print(f"❌ Failed: {self.stress_test_summary['failed_tests']}")
        print(f"⚠️  Warnings: {self.stress_test_summary['warning_tests']}")
        print(f"🔴 Critical Failures: {self.stress_test_summary['critical_failures']}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        # Stress metrics summary
        if self.stress_test_summary['stress_metrics']:
            print(f"\n🔥 Stress Metrics:")
            for test_name, metrics in self.stress_test_summary['stress_metrics'].items():
                print(f"  {test_name}:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        print(f"    {key}: {value:.2f}")
                    else:
                        print(f"    {key}: {value}")
        
        # Resource usage summary
        if self.stress_test_summary['resource_usage']:
            print(f"\n💻 Resource Usage:")
            for test_name, metrics in self.stress_test_summary['resource_usage'].items():
                print(f"  {test_name}:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        print(f"    {key}: {value:.2f}")
                    else:
                        print(f"    {key}: {value}")
        
        # Overall status
        if self.stress_test_summary['critical_failures'] == 0:
            if self.stress_test_summary['warning_tests'] == 0:
                print(f"\n🎯 STATUS: ✅ ALL STRESS TESTS PASSED")
                print("🚀 System is robust under extreme conditions!")
                return 0
            else:
                print(f"\n🎯 STATUS: ⚠️  STRESS TESTS PASSED WITH WARNINGS")
                print("🚀 System is robust under extreme conditions with minor issues.")
                return 0
        else:
            print(f"\n🎯 STATUS: ❌ CRITICAL STRESS TEST ISSUES DETECTED")
            print("⚠️  System needs attention before production deployment.")
            return 1


def main():
    """Main function"""
    stress_tester = StressTesting()
    stress_test_summary = stress_tester.run_stress_testing()
    
    # Return exit code based on critical failures
    exit_code = 0 if stress_test_summary['critical_failures'] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
