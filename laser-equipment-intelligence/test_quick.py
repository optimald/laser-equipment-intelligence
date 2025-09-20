#!/usr/bin/env python3
"""
Quick diagnostic test to identify hanging issues
"""

import sys
import time
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    """Context manager for timeout"""
    def signal_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restore the old signal handler
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)

def test_imports():
    """Test basic imports with timeout"""
    print("🔍 Testing imports...")
    
    try:
        with timeout(5):
            print("  Testing LaserListingItem...")
            from laser_intelligence.pipelines.normalization import LaserListingItem
            print("  ✓ LaserListingItem imported successfully")
            
            print("  Testing PriceAnalyzer...")
            from laser_intelligence.utils.price_analysis import PriceAnalyzer
            print("  ✓ PriceAnalyzer imported successfully")
            
            print("  Testing BrandMapper...")
            from laser_intelligence.utils.brand_mapping import BrandMapper
            print("  ✓ BrandMapper imported successfully")
            
            print("  Testing EvasionScorer...")
            from laser_intelligence.utils.evasion_scoring import EvasionScorer
            print("  ✓ EvasionScorer imported successfully")
            
    except TimeoutError as e:
        print(f"  ✗ Import timed out: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality with timeout"""
    print("\n🔍 Testing basic functionality...")
    
    try:
        with timeout(10):
            print("  Testing BrandMapper...")
            from laser_intelligence.utils.brand_mapping import BrandMapper
            bm = BrandMapper()
            result = bm.normalize_brand('sciton')
            print(f"  ✓ BrandMapper works: {result}")
            
            print("  Testing EvasionScorer...")
            from laser_intelligence.utils.evasion_scoring import EvasionScorer
            es = EvasionScorer()
            print("  ✓ EvasionScorer created successfully")
            
            print("  Testing PriceAnalyzer...")
            from laser_intelligence.utils.price_analysis import PriceAnalyzer
            pa = PriceAnalyzer()
            print("  ✓ PriceAnalyzer created successfully")
            
    except TimeoutError as e:
        print(f"  ✗ Functionality test timed out: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Functionality test failed: {e}")
        return False
    
    return True

def test_integration_simple():
    """Test simple integration without external dependencies"""
    print("\n🔍 Testing simple integration...")
    
    try:
        with timeout(15):
            print("  Testing LaserListingItem creation...")
            from laser_intelligence.pipelines.normalization import LaserListingItem
            
            item = LaserListingItem()
            item['brand'] = 'Sciton'
            item['model'] = 'Joule'
            item['asking_price'] = 150000.0
            print("  ✓ LaserListingItem created and populated")
            
            print("  Testing brand mapping integration...")
            from laser_intelligence.utils.brand_mapping import BrandMapper
            bm = BrandMapper()
            brand = bm.normalize_brand('sciton')
            model = bm.normalize_model('joule', 'sciton')
            print(f"  ✓ Brand mapping works: {brand} {model}")
            
    except TimeoutError as e:
        print(f"  ✗ Integration test timed out: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Quick Diagnostic Test")
    print("=" * 50)
    
    start_time = time.time()
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed - stopping")
        sys.exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality tests failed - stopping")
        sys.exit(1)
    
    # Test simple integration
    if not test_integration_simple():
        print("\n❌ Integration tests failed - stopping")
        sys.exit(1)
    
    end_time = time.time()
    print(f"\n✅ All tests passed in {end_time - start_time:.2f} seconds")
    print("\n🎯 The hanging issue is likely in the full integration test suite")
    print("   Recommendation: Run individual test methods instead of the full suite")
