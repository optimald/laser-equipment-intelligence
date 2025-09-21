import requests
from bs4 import BeautifulSoup
import time
import logging
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from api.models.database import get_db_connection

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

async def run_lasermatch_scraper():
    """Run the LaserMatch scraper and save to database"""
    try:
        start_time = datetime.now()
        logging.info("🚀 Starting LaserMatch scraper...")
        
        items = fetch_and_extract_lasermatch()
        
        # Save items to database
        conn = await get_db_connection()
        items_added = 0
        
        for item in items:
            try:
                # Check if item already exists
                existing = await conn.fetchval(
                    "SELECT id FROM lasermatch_items WHERE url = $1", 
                    item['url']
                )
                
                if not existing:
                    # Insert new item
                    await conn.execute("""
                        INSERT INTO lasermatch_items 
                        (id, title, brand, model, condition, price, location, description, 
                         url, images, discovered_at, last_updated, source, status, category, availability)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    """, 
                    item['id'], item['title'], item['brand'], item['model'], 
                    item['condition'], item['price'], item['location'], item['description'],
                    item['url'], json.dumps(item['images']), item['discovered_at'], 
                    item['last_updated'], item['source'], item['status'], 
                    item['category'], item['availability']
                    )
                    items_added += 1
                    logging.info(f"✅ Added new item: {item['title']}")
                else:
                    logging.info(f"⏭️ Item already exists: {item['title']}")
                    
            except Exception as e:
                logging.warning(f"⚠️ Error saving item {item['title']}: {e}")
        
        await conn.close()
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'items_scraped': len(items),
            'items_added': items_added,
            'execution_time': execution_time,
            'output': f'Successfully scraped {len(items)} items, added {items_added} new items',
            'errors': '',
            'items': items
        }
        
    except Exception as e:
        logging.error(f"❌ LaserMatch scraper failed: {e}")
        return {
            'items_scraped': 0,
            'items_added': 0,
            'execution_time': 0,
            'output': f'Scraper failed: {e}',
            'errors': str(e),
            'items': []
        }

@router.post("/scrape", response_model=LaserMatchScrapeResponse)
async def scrape_lasermatch(background_tasks: BackgroundTasks):
    """
    Scrape LaserMatch.io for new equipment listings
    """
    try:
        logging.info("Starting LaserMatch scraper")
        
        # Run the scraper
        result = await run_lasermatch_scraper()
        
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

# Database operations for LaserMatch items

@router.get("/items")
async def get_lasermatch_items(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    brand: Optional[str] = None
):
    """
    Get paginated LaserMatch items from database
    """
    try:
        conn = await get_db_connection()
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if category:
            where_conditions.append("category = $%d" % (len(params) + 1))
            params.append(category)
        
        if brand:
            where_conditions.append("LOWER(brand) = LOWER($%d)" % (len(params) + 1))
            params.append(brand)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Check if we're in local dev mode (no database)
        if hasattr(conn, '__class__') and 'MockConnection' in str(conn.__class__):
            # Return mock data for local development
            mock_items = [
                {
                    'id': 'dev_001',
                    'title': 'Aerolase LightPod Neo',
                    'brand': 'Aerolase',
                    'model': 'LightPod Neo',
                    'condition': 'Used - Excellent',
                    'price': 45000.0,
                    'location': 'California, USA',
                    'description': 'Professional Aerolase LightPod Neo laser system in excellent condition.',
                    'url': 'https://lasermatch.io/listing/001',
                    'images': ['https://example.com/aerolase1.jpg'],
                    'discovered_at': '2025-09-21T12:00:00',
                    'last_updated': '2025-09-21T12:00:00',
                    'source': 'LaserMatch.io',
                    'status': 'active',
                    'category': 'hot-list',
                    'availability': 'available'
                },
                {
                    'id': 'dev_002',
                    'title': 'Cynosure Icon',
                    'brand': 'Cynosure',
                    'model': 'Icon',
                    'condition': 'Refurbished',
                    'price': 65000.0,
                    'location': 'Texas, USA',
                    'description': 'Cynosure Icon laser system, professionally refurbished.',
                    'url': 'https://lasermatch.io/listing/002',
                    'images': ['https://example.com/cynosure1.jpg'],
                    'discovered_at': '2025-09-21T12:01:00',
                    'last_updated': '2025-09-21T12:01:00',
                    'source': 'LaserMatch.io',
                    'status': 'active',
                    'category': 'in-demand',
                    'availability': 'available'
                }
            ]
            
            # Apply filters
            filtered_items = mock_items
            if category:
                filtered_items = [item for item in filtered_items if item.get('category') == category]
            if brand:
                filtered_items = [item for item in filtered_items if item.get('brand', '').lower() == brand.lower()]
            
            # Apply pagination
            start_idx = skip
            end_idx = skip + limit
            paginated_items = filtered_items[start_idx:end_idx]
            
            return {
                'items': paginated_items,
                'total': len(filtered_items)
            }
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM lasermatch_items {where_clause}"
        total_items = await conn.fetchval(count_query, *params)
        
        # Get paginated items
        items_query = f"""
            SELECT id, title, brand, model, condition, price, location, 
                   description, url, images, discovered_at, last_updated, 
                   source, status, category, availability
            FROM lasermatch_items 
            {where_clause}
            ORDER BY discovered_at DESC 
            LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """
        params.extend([limit, skip])
        
        rows = await conn.fetch(items_query, *params)
        
        # Convert to list of dicts
        items = []
        for row in rows:
            item = dict(row)
            # Convert images from string to list if needed
            if item.get('images') and isinstance(item['images'], str):
                try:
                    import json
                    item['images'] = json.loads(item['images'])
                except:
                    item['images'] = [item['images']]
            items.append(item)
        
        await conn.close()
        
        return {
            'items': items,
            'total': total_items
        }
        
    except Exception as e:
        logging.error(f"Error getting LaserMatch items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get items: {str(e)}")

@router.get("/stats")
async def get_lasermatch_stats():
    """
    Get LaserMatch statistics from database
    """
    try:
        conn = await get_db_connection()
        
        # Check if we're in local dev mode (no database)
        if hasattr(conn, '__class__') and 'MockConnection' in str(conn.__class__):
            # Return mock stats for local development
            return {
                'total_items': 2,
                'hot_list_count': 1,
                'in_demand_count': 1,
                'unique_brands': 2,
                'brands': ['Aerolase', 'Cynosure'],
                'last_updated': datetime.now().isoformat()
            }
        
        # Get total items count
        total_items = await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items")
        
        # Get hot list count
        hot_list_count = await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items WHERE category = 'hot-list'")
        
        # Get in demand count
        in_demand_count = await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items WHERE category = 'in-demand'")
        
        # Get unique brands
        brands_result = await conn.fetch("SELECT DISTINCT brand FROM lasermatch_items WHERE brand IS NOT NULL")
        brands = [row['brand'] for row in brands_result]
        
        # Get latest update time
        latest_update = await conn.fetchval("SELECT MAX(discovered_at) FROM lasermatch_items")
        
        await conn.close()
        
        return {
            'total_items': total_items or 0,
            'hot_list_count': hot_list_count or 0,
            'in_demand_count': in_demand_count or 0,
            'unique_brands': len(brands),
            'brands': sorted(brands),
            'last_updated': latest_update.isoformat() if latest_update else datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting LaserMatch stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
