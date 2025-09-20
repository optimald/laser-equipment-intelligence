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
import requests
from bs4 import BeautifulSoup
import time

router = APIRouter()

class LaserMatchScrapeResponse(BaseModel):
    message: str
    items_scraped: int
    items_added: int
    execution_time: float

def fetch_and_extract_lasermatch():
    """Fetch and extract LaserMatch data"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    logging.info("🌐 Fetching LaserMatch.io homepage...")
    response = requests.get('https://lasermatch.io/', headers=headers, timeout=10)
    logging.info(f"✅ Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    all_items = []
    
    # Extract Hot List items
    logging.info("🔥 Extracting Hot List items...")
    hot_table = soup.find('table', id='dt-hotlist-items')
    if hot_table:
        tbody = hot_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            logging.info(f"📋 Processing {len(rows)} Hot List rows")
            
            for i, row in enumerate(rows):
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Extract text from <a> tag inside each <td> specifically
                        item_link = cells[0].find('a')
                        desc_link = cells[1].find('a')
                        
                        item_name = item_link.get_text().strip() if item_link else cells[0].get_text().strip()
                        description_raw = desc_link.get_text().strip() if desc_link else cells[1].get_text().strip()
                        
                        logging.info(f"✅ LINK EXTRACT - Item: '{item_name}' | Desc: '{description_raw[:50]}...'")
                        
                        # Parse brand and model from the item name
                        if ':' in item_name:
                            brand, model = item_name.split(':', 1)
                            brand = brand.strip()
                            model = model.strip()
                        else:
                            brand = item_name.split()[0] if item_name.split() else 'Unknown'
                            model = item_name
                        
                        # Description is already clean from the second cell
                        clean_description = description_raw
                        
                        item = {
                            'id': f"hot_list_{i+1:03d}",
                            'title': item_name,
                            'brand': brand,
                            'model': model,
                            'condition': 'any',
                            'price': None,
                            'location': 'Various',
                            'description': clean_description,
                            'url': 'https://lasermatch.io/',
                            'images': [],
                            'discovered_at': datetime.now().isoformat(),
                            'last_updated': datetime.now().isoformat(),
                            'source': 'LaserMatch.io',
                            'status': 'active',
                            'category': 'hot-list',
                            'availability': 'in-demand'
                        }
                        
                        all_items.append(item)
                        logging.info(f"✅ Hot: {brand}: {model}")
                        
                except Exception as e:
                    logging.warning(f"⚠️ Error processing Hot List row {i}: {e}")
    
    # Extract In Demand items
    logging.info("📈 Extracting In Demand items...")
    demand_table = soup.find('table', id='dt-demand-items')
    if demand_table:
        tbody = demand_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            logging.info(f"📋 Processing {len(rows)} In Demand rows")
            
            for i, row in enumerate(rows):
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Extract text from <a> tag inside each <td> specifically
                        item_link = cells[0].find('a')
                        desc_link = cells[1].find('a')
                        
                        item_name = item_link.get_text().strip() if item_link else cells[0].get_text().strip()
                        description_raw = desc_link.get_text().strip() if desc_link else cells[1].get_text().strip()
                        
                        logging.info(f"✅ LINK EXTRACT - Item: '{item_name}' | Desc: '{description_raw[:50]}...'")
                        
                        # Parse brand and model from the item name
                        if ':' in item_name:
                            brand, model = item_name.split(':', 1)
                            brand = brand.strip()
                            model = model.strip()
                        else:
                            brand = item_name.split()[0] if item_name.split() else 'Unknown'
                            model = item_name
                        
                        # Description is already clean from the second cell
                        clean_description = description_raw
                        
                        item = {
                            'id': f"in_demand_{i+1:03d}",
                            'title': item_name,
                            'brand': brand,
                            'model': model,
                            'condition': 'any',
                            'price': None,
                            'location': 'Various',
                            'description': clean_description,
                            'url': 'https://lasermatch.io/',
                            'images': [],
                            'discovered_at': datetime.now().isoformat(),
                            'last_updated': datetime.now().isoformat(),
                            'source': 'LaserMatch.io',
                            'status': 'active',
                            'category': 'in-demand',
                            'availability': 'in-demand'
                        }
                        
                        all_items.append(item)
                        logging.info(f"✅ Demand: {brand}: {model}")
                        
                except Exception as e:
                    logging.warning(f"⚠️ Error processing In Demand row {i}: {e}")
    
    return all_items

def run_lasermatch_scraper():
    """Run the LaserMatch scraper and return results"""
    try:
        start_time = datetime.now()
        
        # Run the actual scraper
        items = fetch_and_extract_lasermatch()
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'items_scraped': len(items),
            'items_added': len(items),  # For now, assume all are new
            'execution_time': execution_time,
            'output': f'Successfully scraped {len(items)} items from LaserMatch.io',
            'errors': '',
            'items': items
        }
        
    except Exception as e:
        logging.error(f"LaserMatch scraper failed: {str(e)}")
        raise Exception(f"Scraper execution failed: {str(e)}")

@router.post("/scrape", response_model=LaserMatchScrapeResponse)
async def scrape_lasermatch(background_tasks: BackgroundTasks):
    """
    Scrape LaserMatch.io for new equipment listings
    """
    try:
        logging.info("Starting LaserMatch scraper - clearing cache first")
        
        # Clear cache first to ensure fresh data
        global _scraped_items
        _scraped_items = []
        
        # Run the scraper
        result = run_lasermatch_scraper()
        
        # Store items in global variable (in production, this would be saved to database)
        _scraped_items = result['items']
        
        response = LaserMatchScrapeResponse(
            message=f"VERSION_2.0 - Successfully scraped {result['items_scraped']} items, added {result['items_added']} new items",
            items_scraped=result['items_scraped'],
            items_added=result['items_added'],
            execution_time=result['execution_time']
        )
        
        logging.info(f"LaserMatch scraper completed: {response.message}")
        return response
        
    except Exception as e:
        logging.error(f"LaserMatch scraper failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraper failed: {str(e)}")

# Global variable to store scraped items (in production, this would be in a database)
_scraped_items = []

@router.get("/items")
async def get_lasermatch_items(skip: int = 0, limit: int = 100):
    """
    Get LaserMatch items from the database
    """
    try:
        # Return scraped items with pagination
        total = len(_scraped_items)
        items = _scraped_items[skip:skip + limit]
        
        return {
            "items": items,
            "total": total,
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
        # Calculate stats from scraped items
        total_items = len(_scraped_items)
        hot_list_items = len([item for item in _scraped_items if item.get('category') == 'hot-list'])
        in_demand_items = len([item for item in _scraped_items if item.get('category') == 'in-demand'])
        
        # Get latest update time
        latest_update = None
        if _scraped_items:
            latest_update = max(item.get('last_updated', '') for item in _scraped_items)
        
        return {
            "total_items": total_items,
            "hot_list_items": hot_list_items,
            "in_demand_items": in_demand_items,
            "latest_update": latest_update
        }
    except Exception as e:
        logging.error(f"Failed to get LaserMatch stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")