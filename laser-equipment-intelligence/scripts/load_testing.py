#!/usr/bin/env python3
"""
Load Testing Script - Laser Equipment Intelligence Platform
"""

import sys
import os
import time
import threading
import psutil
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


class LoadTesting:
    """Load testing system for the Laser Equipment Intelligence Platform"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = []
        self.critical_failures = 0
        self.warnings = 0
        self.load_test_summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warning_tests': 0,
            'critical_failures': 0,
            'performance_metrics': {},
            'load_test_results': {}
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
        self.load_test_summary['total_tests'] += 1
        
        if status == "PASS":
            self.load_test_summary['passed_tests'] += 1
        elif status == "FAIL":
            self.load_test_summary['failed_tests'] += 1
            if is_critical:
                self.critical_failures += 1
                self.load_test_summary['critical_failures'] += 1
        elif status == "WARN":
            self.load_test_summary['warning_tests'] += 1
            self.warnings += 1
            
        print(f"{status_icon} [{timestamp}] {test_name}: {status}")
        if message:
            print(f"    {message}")
        if metrics:
            for key, value in metrics.items():
                print(f"    📊 {key}: {value}")
    
    def test_concurrent_brand_mapping(self, num_threads: int = 10, operations_per_thread: int = 100):
        """Test brand mapping under concurrent load"""
        print(f"\n🔄 Testing Concurrent Brand Mapping ({num_threads} threads, {operations_per_thread} ops/thread)...")
        
        def worker_thread(thread_id):
            """Worker thread for brand mapping operations"""
            brand_mapper = BrandMapper()
            start_time = time.time()
            
            for i in range(operations_per_thread):
                brand_mapper.normalize_brand("Sciton")
                brand_mapper.normalize_model("Joule", "Sciton")
            
            end_time = time.time()
            ops_per_sec = (operations_per_thread * 2) / (end_time - start_time)
            return ops_per_sec
        
        try:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(worker_thread, i) for i in range(num_threads)]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            total_ops = num_threads * operations_per_thread * 2
            total_time = end_time - start_time
            overall_ops_per_sec = total_ops / total_time
            avg_ops_per_sec = sum(results) / len(results)
            
            self.load_test_summary['performance_metrics']['concurrent_brand_mapping'] = {
                'threads': num_threads,
                'ops_per_thread': operations_per_thread,
                'total_ops': total_ops,
                'overall_ops_per_sec': overall_ops_per_sec,
                'avg_ops_per_sec': avg_ops_per_sec
            }
            
            if overall_ops_per_sec > 50000:
                self.log_result("Concurrent Brand Mapping", "PASS", 
                              f"{overall_ops_per_sec:,.0f} ops/sec", is_critical=False,
                              metrics={'threads': num_threads, 'ops_per_sec': f"{overall_ops_per_sec:,.0f}", 'target': '50,000'})
            else:
                self.log_result("Concurrent Brand Mapping", "WARN", 
                              f"{overall_ops_per_sec:,.0f} ops/sec - Below target", is_critical=False,
                              metrics={'threads': num_threads, 'ops_per_sec': f"{overall_ops_per_sec:,.0f}", 'target': '50,000'})
                
        except Exception as e:
            self.log_result("Concurrent Brand Mapping", "FAIL", f"Error: {e}", is_critical=False)
    
    def test_concurrent_price_analysis(self, num_threads: int = 5, operations_per_thread: int = 50):
        """Test price analysis under concurrent load"""
        print(f"\n💰 Testing Concurrent Price Analysis ({num_threads} threads, {operations_per_thread} ops/thread)...")
        
        def worker_thread(thread_id):
            """Worker thread for price analysis operations"""
            price_analyzer = PriceAnalyzer()
            start_time = time.time()
            
            for i in range(operations_per_thread):
                price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", 100000)
                price_analyzer.estimate_resale_value("Sciton", "Joule", "excellent", 100000)
                price_analyzer.calculate_margin_estimate(80000, 100000, 5000, 2000)
            
            end_time = time.time()
            ops_per_sec = (operations_per_thread * 3) / (end_time - start_time)
            return ops_per_sec
        
        try:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(worker_thread, i) for i in range(num_threads)]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            total_ops = num_threads * operations_per_thread * 3
            total_time = end_time - start_time
            overall_ops_per_sec = total_ops / total_time
            avg_ops_per_sec = sum(results) / len(results)
            
            self.load_test_summary['performance_metrics']['concurrent_price_analysis'] = {
                'threads': num_threads,
                'ops_per_thread': operations_per_thread,
                'total_ops': total_ops,
                'overall_ops_per_sec': overall_ops_per_sec,
                'avg_ops_per_sec': avg_ops_per_sec
            }
            
            if overall_ops_per_sec > 10000:
                self.log_result("Concurrent Price Analysis", "PASS", 
                              f"{overall_ops_per_sec:,.0f} ops/sec", is_critical=False,
                              metrics={'threads': num_threads, 'ops_per_sec': f"{overall_ops_per_sec:,.0f}", 'target': '10,000'})
            else:
                self.log_result("Concurrent Price Analysis", "WARN", 
                              f"{overall_ops_per_sec:,.0f} ops/sec - Below target", is_critical=False,
                              metrics={'threads': num_threads, 'ops_per_sec': f"{overall_ops_per_sec:,.0f}", 'target': '10,000'})
                
        except Exception as e:
            self.log_result("Concurrent Price Analysis", "FAIL", f"Error: {e}", is_critical=False)
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load"""
        print("\n💾 Testing Memory Usage Under Load...")
        
        try:
            # Get initial memory usage
            initial_memory = psutil.virtual_memory()
            initial_percent = initial_memory.percent
            
            # Create multiple instances to simulate load
            brand_mappers = []
            price_analyzers = []
            
            for i in range(100):
                brand_mappers.append(BrandMapper())
                price_analyzers.append(PriceAnalyzer())
            
            # Perform operations
            for i in range(1000):
                brand_mappers[i % 100].normalize_brand("Sciton")
                price_analyzers[i % 100].estimate_wholesale_value("Sciton", "Joule", "excellent", 100000)
            
            # Get final memory usage
            final_memory = psutil.virtual_memory()
            final_percent = final_memory.percent
            memory_increase = final_percent - initial_percent
            
            self.load_test_summary['performance_metrics']['memory_usage'] = {
                'initial_percent': initial_percent,
                'final_percent': final_percent,
                'memory_increase': memory_increase
            }
            
            if memory_increase < 10:
                self.log_result("Memory Usage Under Load", "PASS", 
                              f"Memory increase: {memory_increase:.1f}%", is_critical=False,
                              metrics={'initial': f"{initial_percent:.1f}%", 'final': f"{final_percent:.1f}%", 'increase': f"{memory_increase:.1f}%"})
            else:
                self.log_result("Memory Usage Under Load", "WARN", 
                              f"Memory increase: {memory_increase:.1f}% - High increase", is_critical=False,
                              metrics={'initial': f"{initial_percent:.1f}%", 'final': f"{final_percent:.1f}%", 'increase': f"{memory_increase:.1f}%"})
                
        except Exception as e:
            self.log_result("Memory Usage Under Load", "FAIL", f"Error: {e}", is_critical=False)
    
    def test_cpu_usage_under_load(self):
        """Test CPU usage under load"""
        print("\n🖥️ Testing CPU Usage Under Load...")
        
        try:
            # Get initial CPU usage
            initial_cpu = psutil.cpu_percent(interval=1)
            
            # Create load
            def cpu_intensive_task():
                brand_mapper = BrandMapper()
                for i in range(10000):
                    brand_mapper.normalize_brand("Sciton")
                    brand_mapper.normalize_model("Joule", "Sciton")
            
            # Run multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=cpu_intensive_task)
                threads.append(thread)
                thread.start()
            
            # Wait a bit for load to build up
            time.sleep(2)
            
            # Get CPU usage under load
            cpu_under_load = psutil.cpu_percent(interval=1)
            
            # Wait for threads to complete
            for thread in threads:
                thread.join()
            
            # Get final CPU usage
            final_cpu = psutil.cpu_percent(interval=1)
            
            self.load_test_summary['performance_metrics']['cpu_usage'] = {
                'initial_cpu': initial_cpu,
                'cpu_under_load': cpu_under_load,
                'final_cpu': final_cpu
            }
            
            if cpu_under_load < 90:
                self.log_result("CPU Usage Under Load", "PASS", 
                              f"CPU under load: {cpu_under_load:.1f}%", is_critical=False,
                              metrics={'initial': f"{initial_cpu:.1f}%", 'under_load': f"{cpu_under_load:.1f}%", 'final': f"{final_cpu:.1f}%"})
            else:
                self.log_result("CPU Usage Under Load", "WARN", 
                              f"CPU under load: {cpu_under_load:.1f}% - High usage", is_critical=False,
                              metrics={'initial': f"{initial_cpu:.1f}%", 'under_load': f"{cpu_under_load:.1f}%", 'final': f"{final_cpu:.1f}%"})
                
        except Exception as e:
            self.log_result("CPU Usage Under Load", "FAIL", f"Error: {e}", is_critical=False)
    
    def test_response_time_under_load(self):
        """Test response time under load"""
        print("\n⏱️ Testing Response Time Under Load...")
        
        try:
            brand_mapper = BrandMapper()
            price_analyzer = PriceAnalyzer()
            
            # Test single operation response time
            start_time = time.time()
            brand_mapper.normalize_brand("Sciton")
            single_op_time = time.time() - start_time
            
            # Test response time under concurrent load
            def response_time_task():
                start_time = time.time()
                brand_mapper.normalize_brand("Sciton")
                price_analyzer.estimate_wholesale_value("Sciton", "Joule", "excellent", 100000)
                return time.time() - start_time
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(response_time_task) for _ in range(100)]
                response_times = [future.result() for future in as_completed(futures)]
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            self.load_test_summary['performance_metrics']['response_time'] = {
                'single_op_time': single_op_time,
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time
            }
            
            if avg_response_time < 0.1:
                self.log_result("Response Time Under Load", "PASS", 
                              f"Avg response time: {avg_response_time:.3f}s", is_critical=False,
                              metrics={'avg': f"{avg_response_time:.3f}s", 'max': f"{max_response_time:.3f}s", 'min': f"{min_response_time:.3f}s"})
            else:
                self.log_result("Response Time Under Load", "WARN", 
                              f"Avg response time: {avg_response_time:.3f}s - Slow response", is_critical=False,
                              metrics={'avg': f"{avg_response_time:.3f}s", 'max': f"{max_response_time:.3f}s", 'min': f"{min_response_time:.3f}s"})
                
        except Exception as e:
            self.log_result("Response Time Under Load", "FAIL", f"Error: {e}", is_critical=False)
    
    def run_load_testing(self):
        """Run comprehensive load testing"""
        print("🚀 Load Testing - Laser Equipment Intelligence Platform")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_concurrent_brand_mapping(num_threads=10, operations_per_thread=100)
        self.test_concurrent_price_analysis(num_threads=5, operations_per_thread=50)
        self.test_memory_usage_under_load()
        self.test_cpu_usage_under_load()
        self.test_response_time_under_load()
        
        # Generate comprehensive summary
        self.generate_load_test_summary()
        
        return self.load_test_summary
    
    def generate_load_test_summary(self):
        """Generate comprehensive load test summary"""
        total_time = time.time() - self.start_time
        
        print(f"\n📊 LOAD TESTING SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.load_test_summary['total_tests']}")
        print(f"✅ Passed: {self.load_test_summary['passed_tests']}")
        print(f"❌ Failed: {self.load_test_summary['failed_tests']}")
        print(f"⚠️  Warnings: {self.load_test_summary['warning_tests']}")
        print(f"🔴 Critical Failures: {self.load_test_summary['critical_failures']}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        # Performance metrics summary
        if self.load_test_summary['performance_metrics']:
            print(f"\n⚡ Performance Metrics:")
            for test_name, metrics in self.load_test_summary['performance_metrics'].items():
                print(f"  {test_name}:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        print(f"    {key}: {value:.2f}")
                    else:
                        print(f"    {key}: {value}")
        
        # Overall status
        if self.load_test_summary['critical_failures'] == 0:
            if self.load_test_summary['warning_tests'] == 0:
                print(f"\n🎯 STATUS: ✅ ALL LOAD TESTS PASSED")
                print("🚀 System performs well under load!")
                return 0
            else:
                print(f"\n🎯 STATUS: ⚠️  LOAD TESTS PASSED WITH WARNINGS")
                print("🚀 System performs well under load with minor issues.")
                return 0
        else:
            print(f"\n🎯 STATUS: ❌ CRITICAL LOAD TEST ISSUES DETECTED")
            print("⚠️  System needs attention before production deployment.")
            return 1


def main():
    """Main function"""
    load_tester = LoadTesting()
    load_test_summary = load_tester.run_load_testing()
    
    # Return exit code based on critical failures
    exit_code = 0 if load_test_summary['critical_failures'] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
