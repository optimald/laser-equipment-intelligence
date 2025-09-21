import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()

class LaserMatchItem(BaseModel):
    id: str
    title: str
    brand: str
    model: str
    condition: str
    price: Optional[float]
    location: str
    description: str
    url: str
    images: List[str]
    discovered_at: str
    last_updated: str
    source: str
    status: str
    category: str
    availability: str

class LaserMatchScrapeResponse(BaseModel):
    message: str
    items_scraped: int
    items_added: int
    execution_time: float

def extract_brand_from_text(full_text):
    """Extract clean brand name from full text"""
    if ':' in full_text:
        # Get everything before the first colon
        brand_part = full_text.split(':', 1)[0].strip()
        # Remove any newlines and get just the first line
        brand = brand_part.split('\n')[0].strip()
        return brand
    else:
        # Fallback: use first word
        words = full_text.split()
        return words[0] if words else 'Unknown'

def fetch_and_extract_lasermatch():
    """Fetch and extract LaserMatch data with SIMPLE parsing logic"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get('https://lasermatch.io/', headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        all_items = []
        
        # Process Hot List section
        hot_list_section = soup.find('div', {'id': 'hot-list'})
        if hot_list_section:
            tbody = hot_list_section.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                logging.info(f"🔥 Processing {len(rows)} Hot List rows")
                
                for i, row in enumerate(rows):
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            full_text = cells[0].get_text().strip()
                            description_text = cells[1].get_text().strip()
                            
                            # Extract clean brand name
                            brand_name = extract_brand_from_text(full_text)
                            
                            item = {
                                'id': f"hot_list_{i+1:03d}",
                                'title': brand_name,  # ONLY the brand name
                                'brand': brand_name,
                                'model': brand_name,
                                'condition': 'any',
                                'price': None,
                                'location': 'Various',
                                'description': description_text,  # Clean description
                                'url': 'https://lasermatch.io/',
                                'images': [],
                                'discovered_at': datetime.now().isoformat(),
                                'last_updated': datetime.now().isoformat(),
                                'source': 'LaserMatch.io',
                                'status': 'active',
                                'category': 'hot-list',
                                'availability': 'available'
                            }
                            
                            all_items.append(item)
                            logging.info(f"✅ Hot: '{brand_name}' | Desc: '{description_text[:30]}...'")
                            
                    except Exception as e:
                        logging.warning(f"⚠️ Error processing Hot List row {i}: {e}")
        
        # Process In Demand section
        in_demand_section = soup.find('div', {'id': 'in-demand'})
        if in_demand_section:
            tbody = in_demand_section.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                logging.info(f"📋 Processing {len(rows)} In Demand rows")
                
                for i, row in enumerate(rows):
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            full_text = cells[0].get_text().strip()
                            description_text = cells[1].get_text().strip()
                            
                            # Extract clean brand name
                            brand_name = extract_brand_from_text(full_text)
                            
                            item = {
                                'id': f"in_demand_{i+1:03d}",
                                'title': brand_name,  # ONLY the brand name
                                'brand': brand_name,
                                'model': brand_name,
                                'condition': 'any',
                                'price': None,
                                'location': 'Various',
                                'description': description_text,  # Clean description
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
                            logging.info(f"✅ Demand: '{brand_name}' | Desc: '{description_text[:30]}...'")
                            
                    except Exception as e:
                        logging.warning(f"⚠️ Error processing In Demand row {i}: {e}")
        
        logging.info(f"🎉 Successfully extracted {len(all_items)} items from LaserMatch.io")
        return all_items
        
    except Exception as e:
        logging.error(f"❌ Error fetching LaserMatch data: {e}")
        raise Exception(f"Failed to fetch LaserMatch data: {e}")

def run_lasermatch_scraper():
    """Run the LaserMatch scraper and return results"""
    try:
        start_time = datetime.now()
        logging.info("🚀 Starting LaserMatch scraper...")
        
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
            message=f"SIMPLE_VERSION_v2 - Successfully scraped {result['items_scraped']} items, added {result['items_added']} new items",
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
# Initialize with mock data for testing
_scraped_items = [
    {
        'id': 'mock_001',
        'title': 'Aerolase LightPod Neo',
        'brand': 'Aerolase',
        'model': 'LightPod Neo',
        'condition': 'Used - Excellent',
        'price': 45000.0,
        'location': 'California, USA',
        'description': 'Professional Aerolase LightPod Neo laser system in excellent condition. Includes all accessories.',
        'url': 'https://lasermatch.io/listing/001',
        'images': ['https://example.com/aerolase1.jpg'],
        'discovered_at': '2025-09-21T11:50:00',
        'last_updated': '2025-09-21T11:50:00',
        'source': 'LaserMatch.io',
        'status': 'active',
        'category': 'hot-list',
        'availability': 'available'
    },
    {
        'id': 'mock_002',
        'title': 'Cynosure Icon',
        'brand': 'Cynosure',
        'model': 'Icon',
        'condition': 'Refurbished',
        'price': 65000.0,
        'location': 'Texas, USA',
        'description': 'Cynosure Icon laser system, professionally refurbished with warranty.',
        'url': 'https://lasermatch.io/listing/002',
        'images': ['https://example.com/cynosure1.jpg'],
        'discovered_at': '2025-09-21T11:51:00',
        'last_updated': '2025-09-21T11:51:00',
        'source': 'LaserMatch.io',
        'status': 'active',
        'category': 'in-demand',
        'availability': 'available'
    },
    {
        'id': 'mock_003',
        'title': 'Lumenis M22',
        'brand': 'Lumenis',
        'model': 'M22',
        'condition': 'Used - Good',
        'price': 55000.0,
        'location': 'Florida, USA',
        'description': 'Lumenis M22 multi-platform laser system in good working condition.',
        'url': 'https://lasermatch.io/listing/003',
        'images': ['https://example.com/lumenis1.jpg'],
        'discovered_at': '2025-09-21T11:52:00',
        'last_updated': '2025-09-21T11:52:00',
        'source': 'LaserMatch.io',
        'status': 'active',
        'category': 'hot-list',
        'availability': 'available'
    }
]

@router.get("/items")
async def get_lasermatch_items(
    page: int = 1,
    per_page: int = 20,
    category: Optional[str] = None,
    brand: Optional[str] = None
):
    """
    Get paginated LaserMatch items
    """
    try:
        # Filter items if needed
        filtered_items = _scraped_items
        
        if category:
            filtered_items = [item for item in filtered_items if item.get('category') == category]
        
        if brand:
            filtered_items = [item for item in filtered_items if item.get('brand', '').lower() == brand.lower()]
        
        # Calculate pagination
        total_items = len(filtered_items)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_items = filtered_items[start_idx:end_idx]
        
        return {
            'items': paginated_items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': (total_items + per_page - 1) // per_page
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting LaserMatch items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get items: {str(e)}")

@router.get("/stats")
async def get_lasermatch_stats():
    """
    Get LaserMatch statistics
    """
    try:
        total_items = len(_scraped_items)
        hot_list_count = len([item for item in _scraped_items if item.get('category') == 'hot-list'])
        in_demand_count = len([item for item in _scraped_items if item.get('category') == 'in-demand'])
        
        # Get unique brands
        brands = set(item.get('brand', 'Unknown') for item in _scraped_items)
        
        return {
            'total_items': total_items,
            'hot_list_count': hot_list_count,
            'in_demand_count': in_demand_count,
            'unique_brands': len(brands),
            'brands': sorted(list(brands)),
            'last_updated': datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting LaserMatch stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
