#!/usr/bin/env python3
"""
Performance testing for Laser Equipment Intelligence Platform
"""

import time
import threading
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from laser_intelligence.utils.brand_mapping import BrandMapper
from laser_intelligence.utils.evasion_scoring import EvasionScorer
from laser_intelligence.utils.price_analysis import PriceAnalyzer
from laser_intelligence.pipelines.normalization import LaserListingItem

class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.cpu_samples = []
        self.memory_samples = []
        self.monitoring = False
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        self.end_time = time.time()
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1)
            
    def _monitor_loop(self):
        """Monitor loop for performance metrics"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                self.cpu_samples.append(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.memory_samples.append(memory.percent)
                
                time.sleep(0.5)  # Sample every 500ms
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
                
    def get_stats(self):
        """Get performance statistics"""
        if not self.cpu_samples or not self.memory_samples:
            return {}
            
        duration = self.end_time - self.start_time if self.end_time else 0
        
        return {
            'duration': duration,
            'avg_cpu': sum(self.cpu_samples) / len(self.cpu_samples),
            'max_cpu': max(self.cpu_samples),
            'avg_memory': sum(self.memory_samples) / len(self.memory_samples),
            'max_memory': max(self.memory_samples),
            'samples': len(self.cpu_samples)
        }

def test_brand_mapping_performance():
    """Test brand mapping performance"""
    print("🔍 Testing Brand Mapping Performance...")
    
    bm = BrandMapper()
    test_brands = [
        'sciton', 'SCITON', 'Sciton Inc', 'Sciton Corporation',
        'cynosure', 'CYNOSURE', 'Cynosure Ltd', 'Cynosure Inc',
        'cutera', 'CUTERA', 'Cutera Inc', 'Cutera Corporation',
        'candela', 'CANDELA', 'Candela Corp', 'Candela Corporation',
        'lumenis', 'LUMENIS', 'Lumenis Ltd', 'Lumenis Inc'
    ] * 10  # 200 operations
    
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    start_time = time.time()
    
    for brand in test_brands:
        result = bm.normalize_brand(brand)
        # Test model normalization too
        model = bm.normalize_model('joule', brand)
        modality = bm.map_modality(brand, 'joule')
    
    end_time = time.time()
    monitor.stop_monitoring()
    
    stats = monitor.get_stats()
    operations_per_second = len(test_brands) / (end_time - start_time)
    
    print(f"  ✓ Processed {len(test_brands)} brand operations")
    print(f"  ✓ Operations per second: {operations_per_second:.2f}")
    print(f"  ✓ Average CPU: {stats.get('avg_cpu', 0):.1f}%")
    print(f"  ✓ Average Memory: {stats.get('avg_memory', 0):.1f}%")
    
    return operations_per_second > 100  # Should process >100 ops/sec

def test_evasion_scoring_performance():
    """Test evasion scoring performance"""
    print("\n🔍 Testing Evasion Scoring Performance...")
    
    es = EvasionScorer()
    
    # Create test responses
    from scrapy.http import Request, HtmlResponse
    
    test_responses = []
    for i in range(100):
        request = Request(url=f"https://example.com/test{i}")
        response = HtmlResponse(
            url=f"https://example.com/test{i}",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"</body></html>",
            status=200
        )
        test_responses.append((response, request))
    
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    start_time = time.time()
    
    for response, request in test_responses:
        score = es.calculate_score(response, request)
        report = es.get_evasion_report(response, request)
        recommendations = es._get_recommendations(score)
    
    end_time = time.time()
    monitor.stop_monitoring()
    
    stats = monitor.get_stats()
    operations_per_second = len(test_responses) / (end_time - start_time)
    
    print(f"  ✓ Processed {len(test_responses)} evasion scoring operations")
    print(f"  ✓ Operations per second: {operations_per_second:.2f}")
    print(f"  ✓ Average CPU: {stats.get('avg_cpu', 0):.1f}%")
    print(f"  ✓ Average Memory: {stats.get('avg_memory', 0):.1f}%")
    
    return operations_per_second > 50  # Should process >50 ops/sec

def test_price_analysis_performance():
    """Test price analysis performance"""
    print("\n🔍 Testing Price Analysis Performance...")
    
    pa = PriceAnalyzer()
    
    test_cases = [
        ('Sciton', 'Joule', 'excellent', 50000),
        ('Cynosure', 'PicoSure', 'good', 75000),
        ('Cutera', 'Excel V', 'fair', 30000),
        ('Candela', 'GentleMax', 'excellent', 100000),
        ('Lumenis', 'M22', 'good', 60000),
    ] * 20  # 100 operations
    
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    start_time = time.time()
    
    for brand, model, condition, asking_price in test_cases:
        wholesale = pa.estimate_wholesale_value(brand, model, condition, asking_price)
        resale = pa.estimate_resale_value(brand, model, condition, asking_price)
        margin, margin_pct = pa.calculate_margin_estimate(asking_price, wholesale, 5000, 2000)
    
    end_time = time.time()
    monitor.stop_monitoring()
    
    stats = monitor.get_stats()
    operations_per_second = len(test_cases) / (end_time - start_time)
    
    print(f"  ✓ Processed {len(test_cases)} price analysis operations")
    print(f"  ✓ Operations per second: {operations_per_second:.2f}")
    print(f"  ✓ Average CPU: {stats.get('avg_cpu', 0):.1f}%")
    print(f"  ✓ Average Memory: {stats.get('avg_memory', 0):.1f}%")
    
    return operations_per_second > 20  # Should process >20 ops/sec

def test_concurrent_operations():
    """Test concurrent operations performance"""
    print("\n🔍 Testing Concurrent Operations Performance...")
    
    def worker_task(task_id):
        """Worker task for concurrent testing"""
        bm = BrandMapper()
        es = EvasionScorer()
        pa = PriceAnalyzer()
        
        # Simulate mixed operations
        results = []
        for i in range(10):
            # Brand mapping
            brand = bm.normalize_brand(f'brand_{task_id}_{i}')
            
            # Evasion scoring
            from scrapy.http import Request, HtmlResponse
            request = Request(url=f"https://example.com/{task_id}/{i}")
            response = HtmlResponse(
                url=f"https://example.com/{task_id}/{i}",
                request=request,
                body=b"<html><body>Test content</body></html>",
                status=200
            )
            score = es.calculate_score(response, request)
            
            # Price analysis
            wholesale = pa.estimate_wholesale_value('Sciton', 'Joule', 'excellent', 50000)
            
            results.append((brand, score, wholesale))
        
        return results
    
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    start_time = time.time()
    
    # Test with different concurrency levels
    concurrency_levels = [1, 5, 10]
    results = {}
    
    for concurrency in concurrency_levels:
        print(f"  Testing {concurrency} concurrent workers...")
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker_task, i) for i in range(concurrency)]
            task_results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        operations_per_second = (concurrency * 10) / duration
        
        results[concurrency] = {
            'duration': duration,
            'ops_per_sec': operations_per_second,
            'tasks_completed': len(task_results)
        }
        
        print(f"    ✓ {concurrency} workers: {operations_per_second:.2f} ops/sec")
        start_time = time.time()  # Reset for next test
    
    monitor.stop_monitoring()
    stats = monitor.get_stats()
    
    print(f"  ✓ Average CPU: {stats.get('avg_cpu', 0):.1f}%")
    print(f"  ✓ Average Memory: {stats.get('avg_memory', 0):.1f}%")
    
    # Check if performance scales reasonably
    return results[10]['ops_per_sec'] > results[1]['ops_per_sec'] * 0.5

def test_memory_usage():
    """Test memory usage under load"""
    print("\n🔍 Testing Memory Usage...")
    
    initial_memory = psutil.virtual_memory().percent
    print(f"  Initial memory usage: {initial_memory:.1f}%")
    
    # Create many objects to test memory usage
    objects = []
    for i in range(1000):
        bm = BrandMapper()
        es = EvasionScorer()
        pa = PriceAnalyzer()
        item = LaserListingItem()
        
        objects.append((bm, es, pa, item))
    
    peak_memory = psutil.virtual_memory().percent
    print(f"  Peak memory usage: {peak_memory:.1f}%")
    
    # Clean up
    del objects
    
    final_memory = psutil.virtual_memory().percent
    print(f"  Final memory usage: {final_memory:.1f}%")
    
    memory_increase = peak_memory - initial_memory
    print(f"  Memory increase: {memory_increase:.1f}%")
    
    return memory_increase < 20  # Should not increase memory by more than 20%

def main():
    """Run all performance tests"""
    print("🚀 Performance Testing - Laser Equipment Intelligence Platform")
    print("=" * 70)
    
    start_time = time.time()
    
    tests = [
        ("Brand Mapping", test_brand_mapping_performance),
        ("Evasion Scoring", test_evasion_scoring_performance),
        ("Price Analysis", test_price_analysis_performance),
        ("Concurrent Operations", test_concurrent_operations),
        ("Memory Usage", test_memory_usage),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status} {test_name}")
        except Exception as e:
            print(f"\n❌ FAILED {test_name}: {e}")
            results[test_name] = False
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    print(f"Total duration: {total_duration:.2f} seconds")
    
    if passed == total:
        print("\n🎯 All performance tests passed! System is ready for production.")
    else:
        print(f"\n⚠️  {total - passed} performance tests failed. Review before production.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
