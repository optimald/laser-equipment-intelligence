#!/usr/bin/env python3
"""
Simple test script for LaserMatch spider
"""

import subprocess
import sys
import os
import time

def run_spider_test():
    """Run the LaserMatch spider with verbose output"""
    print("🚀 Starting LaserMatch Spider Test")
    print("=" * 50)
    
    # Change to the correct directory
    spider_dir = os.path.join(os.path.dirname(__file__), 'src')
    print(f"📁 Working directory: {spider_dir}")
    
    # Run the spider with verbose logging
    command = [
        sys.executable, '-m', 'scrapy', 'crawl', 'lasermatch',
        '-s', 'LOG_LEVEL=INFO',
        '-s', 'CLOSESPIDER_PAGECOUNT=2',  # Only process 2 pages
        '-s', 'CLOSESPIDER_ITEMCOUNT=10',  # Only process 10 items
        '-L', 'INFO'  # Verbose logging
    ]
    
    print(f"🔧 Running command: {' '.join(command)}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command,
            cwd=spider_dir,
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=60  # 60 second timeout
        )
        end_time = time.time()
        
        print("-" * 50)
        print(f"⏱️  Spider completed in {end_time - start_time:.2f} seconds")
        print(f"📊 Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Spider test PASSED")
        else:
            print("❌ Spider test FAILED")
            
    except subprocess.TimeoutExpired:
        print("⏰ Spider test TIMEOUT (60 seconds)")
        print("❌ Spider appears to be hanging")
    except Exception as e:
        print(f"💥 Spider test ERROR: {e}")

if __name__ == "__main__":
    run_spider_test()
