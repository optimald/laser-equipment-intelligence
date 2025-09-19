"""
LaserMatch.io specific API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..models.database import SessionLocal, Listing
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
        
        # Check if the data file was created
        data_file = os.path.join(os.getcwd(), 'laser-equipment-intelligence', 'lasermatch_database_items.json')
        if not os.path.exists(data_file):
            raise Exception("Scraper did not create data file")
        
        # Load the scraped data
        with open(data_file, 'r') as f:
            scraped_items = json.load(f)
        
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'success': True,
            'items_scraped': len(scraped_items),
            'execution_time': execution_time,
            'data': scraped_items
        }
        
    except subprocess.TimeoutExpired:
        raise Exception("Scraper timed out after 5 minutes")
    except Exception as e:
        raise Exception(f"Error running scraper: {str(e)}")

def populate_database_with_scraped_data(scraped_data: list, db: Session):
    """Populate database with scraped LaserMatch data"""
    items_added = 0
    
    for item_data in scraped_data:
        try:
            # Check if item already exists
            existing_item = db.query(Listing).filter(
                Listing.source == 'LaserMatch.io',
                Listing.title == item_data['title']
            ).first()
            
            if existing_item:
                # Update existing item
                existing_item.description = item_data['description']
                existing_item.last_updated = datetime.utcnow()
                existing_item.status = 'active'
            else:
                # Create new item
                new_item = Listing(
                    id=item_data['id'],
                    title=item_data['title'],
                    brand=item_data['brand'],
                    model=item_data['model'],
                    condition=item_data['condition'],
                    price=item_data['price'],
                    source=item_data['source'],
                    url=item_data['url'],
                    location=item_data['location'],
                    description=item_data['description'],
                    images=item_data['images'],
                    discovered_at=datetime.fromisoformat(item_data['discovered_at'].replace('Z', '+00:00')),
                    last_updated=datetime.utcnow(),
                    margin_estimate=None,
                    score_overall=85,  # High score for demand items
                    status='active'
                )
                db.add(new_item)
                items_added += 1
                
        except Exception as e:
            logging.error(f"Error processing item {item_data.get('title', 'unknown')}: {e}")
            continue
    
    db.commit()
    return items_added

@router.post("/scrape", response_model=LaserMatchScrapeResponse)
async def scrape_lasermatch(background_tasks: BackgroundTasks):
    """
    Run the LaserMatch scraper and populate the database
    """
    try:
        # Run the scraper
        scrape_result = run_lasermatch_scraper()
        
        if not scrape_result['success']:
            raise HTTPException(status_code=500, detail=f"Scraper failed: {scrape_result}")
        
        # Populate database in background
        background_tasks.add_task(
            populate_database_with_scraped_data,
            scrape_result['data'],
            SessionLocal()
        )
        
        return LaserMatchScrapeResponse(
            message=f"Scraper completed successfully. {scrape_result['items_scraped']} items scraped.",
            items_scraped=scrape_result['items_scraped'],
            items_added=0,  # Will be updated by background task
            execution_time=scrape_result['execution_time']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items")
async def get_lasermatch_items(skip: int = 0, limit: int = 100):
    """
    Get LaserMatch items from database
    """
    db = SessionLocal()
    try:
        items = db.query(Listing).filter(
            Listing.source == 'LaserMatch.io'
        ).offset(skip).limit(limit).all()
        
        return {
            'items': items,
            'total': len(items)
        }
    finally:
        db.close()

@router.get("/stats")
async def get_lasermatch_stats():
    """
    Get LaserMatch statistics
    """
    db = SessionLocal()
    try:
        total_items = db.query(Listing).filter(Listing.source == 'LaserMatch.io').count()
        
        # Get items by category
        hot_list_items = db.query(Listing).filter(
            Listing.source == 'LaserMatch.io',
            Listing.category == 'hot-list'
        ).count()
        
        in_demand_items = db.query(Listing).filter(
            Listing.source == 'LaserMatch.io',
            Listing.category == 'in-demand'
        ).count()
        
        # Get latest update time
        latest_item = db.query(Listing).filter(
            Listing.source == 'LaserMatch.io'
        ).order_by(Listing.last_updated.desc()).first()
        
        latest_update = latest_item.last_updated.isoformat() if latest_item else None
        
        return {
            'total_items': total_items,
            'hot_list_items': hot_list_items,
            'in_demand_items': in_demand_items,
            'latest_update': latest_update
        }
    finally:
        db.close()
