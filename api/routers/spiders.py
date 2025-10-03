from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from datetime import datetime
import subprocess
import json
import os
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()

@router.post("/search")
async def run_spider_search(search_request: Dict[str, Any]):
    """Run Scrapy spiders to search for laser equipment"""
    try:
        query = search_request.get('query', '').strip()
        limit = search_request.get('limit', 10)
        
        if not query:
            raise HTTPException(status_code=400, detail="Search query is required")
        
        # Get the laser-equipment-intelligence directory
        spider_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "laser-equipment-intelligence")
        
        if not os.path.exists(spider_dir):
            raise HTTPException(status_code=500, detail="Spider directory not found")
        
        # Run spiders in parallel
        results = await run_spiders_parallel(spider_dir, query, limit)
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "source": "spiders",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spider search failed: {str(e)}")

async def run_spiders_parallel(spider_dir: str, query: str, limit: int) -> List[Dict[str, Any]]:
    """Run multiple spiders in parallel"""
    
    # Define spider configurations
    spiders = [
        {"name": "ebay_laser", "query": query},
        {"name": "dotmed_auctions", "query": query},
        {"name": "bidspotter", "query": query}
    ]
    
    # Use ThreadPoolExecutor to run spiders in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all spider tasks
        futures = []
        for spider_config in spiders:
            future = executor.submit(run_single_spider, spider_dir, spider_config)
            futures.append(future)
        
        # Collect results from all spiders
        all_results = []
        for future in futures:
            try:
                spider_results = future.result(timeout=30)  # 30 second timeout per spider
                all_results.extend(spider_results)
            except Exception as e:
                print(f"Spider failed: {e}")
                continue
    
    # Sort by score and limit results
    all_results.sort(key=lambda x: x.get('score_overall', 0), reverse=True)
    return all_results[:limit]

def run_single_spider(spider_dir: str, spider_config: Dict[str, str]) -> List[Dict[str, Any]]:
    """Run a single spider and return results"""
    
    spider_name = spider_config["name"]
    query = spider_config["query"]
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        output_file = temp_file.name
    
    try:
        # Run scrapy crawl command using python3 -m scrapy
        cmd = [
            "python3", "-m", "scrapy", "crawl", spider_name,
            "-a", f"query={query}",
            "-o", output_file,
            "-s", "ROBOTSTXT_OBEY=False",  # Disable robots.txt for testing
            "-s", "DOWNLOAD_DELAY=0.5",    # Be respectful with delays
            "-s", "CONCURRENT_REQUESTS=1"   # Limit concurrent requests
        ]
        
        # Change to spider directory and run command
        result = subprocess.run(
            cmd,
            cwd=spider_dir,
            capture_output=True,
            text=True,
            timeout=25  # 25 second timeout
        )
        
        if result.returncode != 0:
            print(f"Spider {spider_name} failed: {result.stderr}")
            return []
        
        # Read results from output file
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                content = f.read().strip()
                if content:
                    try:
                        results = json.loads(content)
                        return results if isinstance(results, list) else []
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON from {spider_name}")
                        return []
        
        return []
        
    except subprocess.TimeoutExpired:
        print(f"Spider {spider_name} timed out")
        return []
    except Exception as e:
        print(f"Error running spider {spider_name}: {e}")
        return []
    finally:
        # Clean up temporary file
        if os.path.exists(output_file):
            os.unlink(output_file)

@router.get("/status")
async def get_spider_status():
    """Get spider system status"""
    try:
        spider_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "laser-equipment-intelligence")
        
        status = {
            "spiders_available": [],
            "spider_directory_exists": os.path.exists(spider_dir),
            "scrapy_installed": False,
            "timestamp": datetime.now().isoformat()
        }
        
        if os.path.exists(spider_dir):
            # Check for spider files
            spider_files = [
                "laser_intelligence/spiders/ebay_laser.py",
                "laser_intelligence/spiders/dotmed_auctions.py", 
                "laser_intelligence/spiders/bidspotter.py"
            ]
            
            for spider_file in spider_files:
                spider_path = os.path.join(spider_dir, spider_file)
                if os.path.exists(spider_path):
                    spider_name = os.path.basename(spider_file).replace('.py', '')
                    status["spiders_available"].append(spider_name)
            
            # Check if scrapy is available
            try:
                result = subprocess.run(
                    ["scrapy", "--version"],
                    cwd=spider_dir,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                status["scrapy_installed"] = result.returncode == 0
            except:
                status["scrapy_installed"] = False
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get spider status: {str(e)}")

@router.post("/test")
async def test_spider():
    """Test spider functionality with a simple query"""
    try:
        test_request = {
            "query": "laser equipment",
            "limit": 3
        }
        
        result = await run_spider_search(test_request)
        return {
            "message": "Spider test completed",
            "results_count": len(result.get("results", [])),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spider test failed: {str(e)}")
