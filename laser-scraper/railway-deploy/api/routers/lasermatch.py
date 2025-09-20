"""
LaserMatch.io specific API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import subprocess
import os
import sys
import json
import logging

router = APIRouter()

class LaserMatchScrapeResponse(BaseModel):
    message: str
    items_scraped: int
    items_added: int
    execution_time: float

def run_lasermatch_scraper():
    """Run the LaserMatch scraper and return results"""
    try:
        # Get the path to the scraper
        scraper_path = os.path.join(os.getcwd(), 'laser-equipment-intelligence', 'src', 'laser_intelligence', 'spiders', 'lasermatch_scraper.py')
        
        if not os.path.exists(scraper_path):
            raise Exception(f"Scraper not found at {scraper_path}")
        
        # Run the scraper
        start_time = datetime.now()
        result = subprocess.run(
            [sys.executable, scraper_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        end_time = datetime.now()
        
        if result.returncode != 0:
            raise Exception(f"Scraper failed with return code {result.returncode}: {result.stderr}")
        
        # Parse the output
        try:
            output_data = json.loads(result.stdout)
            items_scraped = output_data.get('items_scraped', 0)
            items_added = output_data.get('items_added', 0)
        except json.JSONDecodeError:
            # Fallback if output is not JSON
            items_scraped = 0
            items_added = 0
        
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'items_scraped': items_scraped,
            'items_added': items_added,
            'execution_time': execution_time,
            'output': result.stdout,
            'errors': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        raise Exception("Scraper timed out after 5 minutes")
    except Exception as e:
        raise Exception(f"Scraper execution failed: {str(e)}")

@router.post("/scrape", response_model=LaserMatchScrapeResponse)
async def scrape_lasermatch(background_tasks: BackgroundTasks):
    """
    Scrape LaserMatch.io for new equipment listings
    """
    try:
        logging.info("Starting LaserMatch scraper")
        
        # Run the scraper
        result = run_lasermatch_scraper()
        
        response = LaserMatchScrapeResponse(
            message=f"Successfully scraped {result['items_scraped']} items, added {result['items_added']} new items",
            items_scraped=result['items_scraped'],
            items_added=result['items_added'],
            execution_time=result['execution_time']
        )
        
        logging.info(f"LaserMatch scraper completed: {response.message}")
        return response
        
    except Exception as e:
        logging.error(f"LaserMatch scraper failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraper failed: {str(e)}")

@router.get("/items")
async def get_lasermatch_items(skip: int = 0, limit: int = 100):
    """
    Get LaserMatch items from the database
    """
    try:
        # For now, return empty results until database is properly set up
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logging.error(f"Failed to get LaserMatch items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve items: {str(e)}")

@router.get("/stats")
async def get_lasermatch_stats():
    """
    Get LaserMatch statistics
    """
    try:
        # For now, return empty stats until database is properly set up
        return {
            "total_items": 0,
            "hot_list_items": 0,
            "in_demand_items": 0,
            "latest_update": None
        }
    except Exception as e:
        logging.error(f"Failed to get LaserMatch stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")