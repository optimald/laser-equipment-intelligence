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
                        # Get the raw text from both cells
                        item_name_raw = cells[0].get_text().strip()
                        description_raw = cells[1].get_text().strip()
                        
                        # Debug: log what we're getting
                        logging.info(f"Raw item_name: '{item_name_raw[:100]}...'")
                        logging.info(f"Raw description: '{description_raw[:100]}...'")
                        
                        # The item name should be just the first part before any long description
                        # First, split on newlines and take the first non-empty line (equipment name)
                        lines = item_name_raw.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                        item_name = None
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('-') and not line.lower().startswith('looking for'):
                                item_name = line
                                break
                        
                        # If we didn't find a good line, fall back to other methods
                        if not item_name:
                            if ' - ' in item_name_raw:
                                item_name = item_name_raw.split(' - ')[0].strip()
                            elif ' Looking for ' in item_name_raw:
                                item_name = item_name_raw.split(' Looking for ')[0].strip()
                            else:
                                # If no clear separator, take first reasonable length (equipment names are usually short)
                                words = item_name_raw.split()
                                if len(words) > 6:  # If more than 6 words, it's probably including description
                                    item_name = ' '.join(words[:4])  # Take first 4 words as item name
                                else:
                                    item_name = item_name_raw
                        
                        # Parse brand and model from the item name
                        if ':' in item_name:
                            brand, model = item_name.split(':', 1)
                            brand = brand.strip()
                            model = model.strip()
                        else:
                            brand = item_name.split()[0] if item_name.split() else 'Unknown'
                            model = item_name
                        
                        # Clean up description - remove the item name from the beginning if it's repeated
                        clean_description = description_raw
                        
                        # Remove the exact item name from the beginning of description if it's there
                        if clean_description.startswith(item_name):
                            clean_description = clean_description[len(item_name):].strip()
                        
                        # Remove brand prefix if it's still there
                        if clean_description.startswith(brand + ':'):
                            clean_description = clean_description[len(brand + ':'):].strip()
                        
                        # Remove leading dash or hyphen
                        if clean_description.startswith('-'):
                            clean_description = clean_description[1:].strip()
                        
                        # If description is empty or too similar to title, create a meaningful one
                        if not clean_description or len(clean_description) < 10:
                            clean_description = f"In-demand laser equipment: {model}"
                        
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
                        # Get the raw text from both cells
                        item_name_raw = cells[0].get_text().strip()
                        description_raw = cells[1].get_text().strip()
                        
                        # Debug: log what we're getting
                        logging.info(f"Raw item_name: '{item_name_raw[:100]}...'")
                        logging.info(f"Raw description: '{description_raw[:100]}...'")
                        
                        # The item name should be just the first part before any long description
                        # First, split on newlines and take the first non-empty line (equipment name)
                        lines = item_name_raw.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                        item_name = None
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('-') and not line.lower().startswith('looking for'):
                                item_name = line
                                break
                        
                        # If we didn't find a good line, fall back to other methods
                        if not item_name:
                            if ' - ' in item_name_raw:
                                item_name = item_name_raw.split(' - ')[0].strip()
                            elif ' Looking for ' in item_name_raw:
                                item_name = item_name_raw.split(' Looking for ')[0].strip()
                            else:
                                # If no clear separator, take first reasonable length (equipment names are usually short)
                                words = item_name_raw.split()
                                if len(words) > 6:  # If more than 6 words, it's probably including description
                                    item_name = ' '.join(words[:4])  # Take first 4 words as item name
                                else:
                                    item_name = item_name_raw
                        
                        # Parse brand and model from the item name
                        if ':' in item_name:
                            brand, model = item_name.split(':', 1)
                            brand = brand.strip()
                            model = model.strip()
                        else:
                            brand = item_name.split()[0] if item_name.split() else 'Unknown'
                            model = item_name
                        
                        # Clean up description - remove the item name from the beginning if it's repeated
                        clean_description = description_raw
                        
                        # Remove the exact item name from the beginning of description if it's there
                        if clean_description.startswith(item_name):
                            clean_description = clean_description[len(item_name):].strip()
                        
                        # Remove brand prefix if it's still there
                        if clean_description.startswith(brand + ':'):
                            clean_description = clean_description[len(brand + ':'):].strip()
                        
                        # Remove leading dash or hyphen
                        if clean_description.startswith('-'):
                            clean_description = clean_description[1:].strip()
                        
                        # If description is empty or too similar to title, create a meaningful one
                        if not clean_description or len(clean_description) < 10:
                            clean_description = f"In-demand laser equipment: {model}"
                        
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
        logging.info("Starting LaserMatch scraper")
        
        # Run the scraper
        result = run_lasermatch_scraper()
        
        # Store items in global variable (in production, this would be saved to database)
        global _scraped_items
        _scraped_items = result['items']
        
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