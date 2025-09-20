#!/usr/bin/env python3
"""
Debug Error Handling for UAT
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from laser_intelligence.utils.brand_mapping import BrandMapper

def debug_error_handling():
    """Debug error handling behavior for UAT"""
    brand_mapper = BrandMapper()
    
    print("🔍 Debug Error Handling for UAT:")
    print("=" * 50)
    
    # Test error handling scenarios from UAT
    error_test_cases = [
        ('', ''),
        (None, ''),
        ('!@#$%^&*()', '!@#$%^&*()'),
    ]
    
    for i, (input_brand, expected_result) in enumerate(error_test_cases, 1):
        print(f"\nTest {i}: Input='{input_brand}', Expected='{expected_result}'")
        try:
            result = brand_mapper.normalize_brand(input_brand)
            print(f"Result: '{result}'")
            print(f"Match: {result == expected_result}")
            print(f"Type: {type(result)}")
        except Exception as e:
            print(f"Exception: {e}")
            print(f"Exception Type: {type(e)}")

if __name__ == "__main__":
    debug_error_handling()
