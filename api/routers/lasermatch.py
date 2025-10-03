from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
import asyncio
import asyncpg
import os
from datetime import datetime
import json

router = APIRouter()

# In-memory storage for fallback when database is unavailable
lasermatch_items_memory = []
_lasermatch_items = []
_last_refresh = None

async def get_db_connection():
    """Get database connection with fallback to in-memory storage"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return None
        return await asyncpg.connect(database_url)
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

async def init_lasermatch_table():
    """Initialize LaserMatch items table"""
    conn = await get_db_connection()
    if not conn:
        return False
    
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS lasermatch_items (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                brand VARCHAR(100),
                model VARCHAR(100),
                condition VARCHAR(50),
                price DECIMAL(12,2),
                location VARCHAR(200),
                description TEXT,
                url TEXT,
                images TEXT[],
                discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                source VARCHAR(100) DEFAULT 'LaserMatch.io',
                status VARCHAR(50) DEFAULT 'active',
                category VARCHAR(100),
                availability VARCHAR(50),
                assigned_rep VARCHAR(100),
                target_price DECIMAL(12,2),
                notes TEXT,
                spider_urls TEXT
            )
        """)
        await conn.close()
        return True
    except Exception as e:
        print(f"Table creation failed: {e}")
        if conn:
            await conn.close()
        return False

@router.get("/items")
async def get_lasermatch_items(
    limit: int = 100,
    offset: int = 0,
    assigned_rep: Optional[str] = None,
    status: Optional[str] = None
):
    """Get LaserMatch items from database or memory"""
    try:
        # Try database first
        conn = await get_db_connection()
        if conn:
            try:
                # Build query with filters
                query = "SELECT * FROM lasermatch_items WHERE 1=1"
                params = []
                param_count = 0
                
                if assigned_rep:
                    param_count += 1
                    query += f" AND assigned_rep = ${param_count}"
                    params.append(assigned_rep)
                
                if status:
                    param_count += 1
                    query += f" AND status = ${param_count}"
                    params.append(status)
                
                query += f" ORDER BY discovered_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
                params.extend([limit, offset])
                
                rows = await conn.fetch(query, *params)
                await conn.close()
                
                # Convert to list of dicts
                items = []
                for row in rows:
                    item = dict(row)
                    # Convert datetime objects to ISO strings
                    if item.get('discovered_at'):
                        item['discovered_at'] = item['discovered_at'].isoformat()
                    if item.get('last_updated'):
                        item['last_updated'] = item['last_updated'].isoformat()
                    items.append(item)
                
                return {
                    "items": items,
                    "total": len(items),
                    "source": "database"
                }
            except Exception as e:
                print(f"Database query failed: {e}")
                if conn:
                    await conn.close()
        
        # Fallback to in-memory storage - load scraped data if available
        global _lasermatch_items
        if not _lasermatch_items:
            try:
                import json
                import os
                
                # Get the project root directory
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                
                # Try to load the prepared API data file first
                api_data_file = os.path.join(project_root, "lasermatch_api_data.json")
                if os.path.exists(api_data_file):
                    print(f"Loading API data from: lasermatch_api_data.json")
                    with open(api_data_file, 'r') as f:
                        _lasermatch_items = json.load(f)
                    print(f"✅ Loaded {len(_lasermatch_items)} items from API data file")
                else:
                    # Fall back to finding the most recent scraped file
                    scraped_files = [f for f in os.listdir(project_root) if f.startswith("lasermatch_scraped_") and f.endswith(".json")]
                    if scraped_files:
                        latest_file = max(scraped_files)
                        file_path = os.path.join(project_root, latest_file)
                        
                        print(f"Loading scraped data from: {latest_file}")
                        
                        with open(file_path, 'r') as f:
                            raw_data = json.load(f)
                        
                        # Convert to API format
                        _lasermatch_items = []
                        for item in raw_data:
                            _lasermatch_items.append({
                                "id": i + 1,
                                "title": item["title"],
                                "brand": item["brand"],
                                "model": item["model"],
                                "condition": item["condition"],
                                "price": item["price"] if item["price"] > 0 else 25000.0,
                                "location": item["location"],
                                "description": item["description"],
                                "url": item["url"],
                                "images": item["images"],
                                "source": item["source"],
                                "status": item["status"],
                                "category": item["category"],
                                "availability": item["availability"],
                                "assigned_rep": item["assigned_rep"],
                                "target_price": item["target_price"],
                                "notes": item["notes"],
                                "spider_urls": item["spider_urls"]
                            })
                        
                        print(f"✅ Loaded {len(_lasermatch_items)} items from scraper")
            except Exception as e:
                print(f"Failed to load scraped data: {e}")
                _lasermatch_items = []
        
        # Use scraped data if available, otherwise fall back to memory
        items_to_use = _lasermatch_items if _lasermatch_items else lasermatch_items_memory
        
        # Apply filters
        filtered_items = items_to_use
        if assigned_rep:
            filtered_items = [item for item in filtered_items if item.get("assigned_rep") == assigned_rep]
        if status:
            filtered_items = [item for item in filtered_items if item.get("status") == status]
        
        items = filtered_items[offset:offset + limit]
        return {
            "items": items,
            "total": len(filtered_items),
            "source": "memory"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve items: {str(e)}")

@router.post("/refresh")
async def refresh_lasermatch_items(background_tasks: BackgroundTasks):
    """Trigger LaserMatch items refresh (scraping)"""
    try:
        # Add background task to scrape LaserMatch
        background_tasks.add_task(scrape_lasermatch_items)
        
        return {
            "message": "LaserMatch refresh started",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start refresh: {str(e)}")

@router.post("/load-scraped-data")
async def load_scraped_data():
    """Directly load the most recent scraped data"""
    try:
        import json
        import os
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Find the most recent scraped file
        scraped_files = [f for f in os.listdir(project_root) if f.startswith("lasermatch_scraped_") and f.endswith(".json")]
        if not scraped_files:
            raise HTTPException(status_code=404, detail="No scraped files found")
        
        latest_file = max(scraped_files)
        file_path = os.path.join(project_root, latest_file)
        
        print(f"Loading scraped data from: {latest_file}")
        
        with open(file_path, 'r') as f:
            scraped_items = json.load(f)
        
        # Update global variables
        global _lasermatch_items, _last_refresh
        _lasermatch_items = scraped_items
        _last_refresh = datetime.now()
        
        # Also save to database if available
        conn = await get_db_connection()
        if conn:
            try:
                await init_lasermatch_table()
                for item in scraped_items:
                    await conn.execute("""
                        INSERT INTO lasermatch_items (
                            title, brand, model, condition, price, location, 
                            description, url, images, source, status, category, 
                            availability, assigned_rep, target_price, notes, spider_urls
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                        ON CONFLICT (url) DO UPDATE SET
                            title = EXCLUDED.title,
                            price = EXCLUDED.price,
                            last_updated = NOW()
                    """, 
                    item["title"], item["brand"], item["model"], item["condition"], 
                    item["price"], item["location"], item["description"], item["url"], 
                    item["images"], item["source"], item["status"], item["category"], 
                    item["availability"], item["assigned_rep"], item["target_price"], 
                    item["notes"], item["spider_urls"])
                
                await conn.close()
                print(f"✅ Saved {len(scraped_items)} items to database")
            except Exception as e:
                print(f"Database save failed: {e}")
                if conn:
                    await conn.close()
        
        return {
            "message": f"Loaded {len(scraped_items)} items from {latest_file}",
            "status": "success",
            "total_items": len(scraped_items),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load scraped data: {str(e)}")

async def scrape_lasermatch_items():
    """Background task to scrape LaserMatch items"""
    print("🕷️ Starting LaserMatch scraping...")
    
    try:
        # Initialize database table
        await init_lasermatch_table()
        
        # Load scraped data directly
        import json
        import os
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Try to load the prepared API data file first
        api_data_file = os.path.join(project_root, "lasermatch_api_data.json")
        if os.path.exists(api_data_file):
            print(f"Loading API data from: lasermatch_api_data.json")
            with open(api_data_file, 'r') as f:
                mock_items = json.load(f)
            print(f"✅ Loaded {len(mock_items)} items from API data file")
        else:
            # Fall back to finding the most recent scraped file
            scraped_files = [f for f in os.listdir(project_root) if f.startswith("lasermatch_scraped_") and f.endswith(".json")]
            if scraped_files:
                latest_file = max(scraped_files)
                file_path = os.path.join(project_root, latest_file)
                
                print(f"Loading scraped data from: {latest_file}")
                
                with open(file_path, 'r') as f:
                    raw_data = json.load(f)
                
                # Convert to API format
                mock_items = []
                for item in raw_data:
                    mock_items.append({
                        "id": i + 1,
                        "title": item["title"],
                        "brand": item["brand"],
                        "model": item["model"],
                        "condition": item["condition"],
                        "price": item["price"] if item["price"] > 0 else 25000.0,
                        "location": item["location"],
                        "description": item["description"],
                        "url": item["url"],
                        "images": item["images"],
                        "source": item["source"],
                        "status": item["status"],
                        "category": item["category"],
                        "availability": item["availability"],
                        "assigned_rep": item["assigned_rep"],
                        "target_price": item["target_price"],
                        "notes": item["notes"],
                        "spider_urls": item["spider_urls"]
                    })
                
                print(f"✅ Loaded {len(mock_items)} items from scraper")
            else:
                print("❌ No scraped files found, using mock data")
                mock_items = [
                    {
                        "title": "Aerolase Lightpod Neo Elite Laser System",
                        "brand": "Aerolase",
                        "model": "Lightpod Neo Elite",
                        "condition": "Used - Excellent",
                        "price": 45000.00,
                        "location": "California, USA",
                        "description": "Professional Aerolase Lightpod Neo Elite laser system in excellent condition. Includes all accessories and documentation.",
                        "url": "https://lasermatch.io/listing/aerolase-lightpod-neo-elite",
                        "images": ["https://lasermatch.io/images/aerolase-neo-elite-1.jpg"],
                        "source": "LaserMatch.io",
                        "status": "active",
                        "category": "Laser System",
                        "availability": "Available",
                        "assigned_rep": None,
                        "target_price": None,
                        "notes": None,
                        "spider_urls": None
                    }
                ]
        
        # Try to save to database
        conn = await get_db_connection()
        if conn:
            try:
                for item in mock_items:
                    await conn.execute("""
                        INSERT INTO lasermatch_items (
                            title, brand, model, condition, price, location, 
                            description, url, images, source, status, category, 
                            availability, assigned_rep, target_price, notes, spider_urls
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                        ON CONFLICT (url) DO UPDATE SET
                            title = EXCLUDED.title,
                            price = EXCLUDED.price,
                            last_updated = NOW()
                    """, 
                    item["title"], item["brand"], item["model"], item["condition"], 
                    item["price"], item["location"], item["description"], item["url"], 
                    item["images"], item["source"], item["status"], item["category"], 
                    item["availability"], item["assigned_rep"], item["target_price"], 
                    item["notes"], item["spider_urls"])
                
                await conn.close()
                print(f"✅ Saved {len(mock_items)} items to database")
            except Exception as e:
                print(f"Database save failed: {e}")
                if conn:
                    await conn.close()
        
        # Also save to memory as fallback
        global lasermatch_items_memory
        lasermatch_items_memory = mock_items
        print(f"✅ Saved {len(mock_items)} items to memory")
        
        # Update the global variable for immediate access
        global _lasermatch_items
        _lasermatch_items = mock_items
        global _last_refresh
        _last_refresh = datetime.now()
        
    except Exception as e:
        print(f"❌ LaserMatch scraping failed: {e}")

@router.put("/items/{item_id}")
async def update_lasermatch_item(item_id: int, updates: Dict[str, Any]):
    """Update a LaserMatch item"""
    try:
        conn = await get_db_connection()
        if conn:
            try:
                # Build update query dynamically
                set_clauses = []
                params = []
                param_count = 0
                
                for key, value in updates.items():
                    if key in ['assigned_rep', 'target_price', 'notes', 'status']:
                        param_count += 1
                        set_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                if not set_clauses:
                    raise HTTPException(status_code=400, detail="No valid fields to update")
                
                param_count += 1
                query = f"UPDATE lasermatch_items SET {', '.join(set_clauses)}, last_updated = NOW() WHERE id = ${param_count}"
                params.append(item_id)
                
                result = await conn.execute(query, *params)
                await conn.close()
                
                if "UPDATE 0" in result:
                    raise HTTPException(status_code=404, detail="Item not found")
                
                return {"message": "Item updated successfully", "item_id": item_id}
            except Exception as e:
                if conn:
                    await conn.close()
                raise e
        
        # Fallback to memory update
        if 0 <= item_id < len(lasermatch_items_memory):
            for key, value in updates.items():
                if key in lasermatch_items_memory[item_id]:
                    lasermatch_items_memory[item_id][key] = value
            return {"message": "Item updated in memory", "item_id": item_id}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")

@router.get("/stats")
async def get_lasermatch_stats():
    """Get LaserMatch statistics"""
    try:
        conn = await get_db_connection()
        if conn:
            try:
                # Get total count
                total_count = await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items")
                
                # Get count by status
                status_counts = await conn.fetch("""
                    SELECT status, COUNT(*) as count 
                    FROM lasermatch_items 
                    GROUP BY status
                """)
                
                # Get count by assigned rep
                rep_counts = await conn.fetch("""
                    SELECT assigned_rep, COUNT(*) as count 
                    FROM lasermatch_items 
                    WHERE assigned_rep IS NOT NULL
                    GROUP BY assigned_rep
                """)
                
                await conn.close()
                
                return {
                    "total_items": total_count,
                    "status_breakdown": [dict(row) for row in status_counts],
                    "rep_breakdown": [dict(row) for row in rep_counts],
                    "source": "database"
                }
            except Exception as e:
                if conn:
                    await conn.close()
                raise e
        
        # Fallback to memory stats - use the same data source as items endpoint
        global _lasermatch_items
        if not _lasermatch_items:
            # Load scraped data if available (same logic as items endpoint)
            try:
                import json
                import os
                
                # Get the project root directory
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                
                # Try to load the prepared API data file first
                api_data_file = os.path.join(project_root, "lasermatch_api_data.json")
                if os.path.exists(api_data_file):
                    with open(api_data_file, 'r') as f:
                        _lasermatch_items = json.load(f)
                else:
                    # Fall back to finding the most recent scraped file
                    scraped_files = [f for f in os.listdir(project_root) if f.startswith("lasermatch_scraped_") and f.endswith(".json")]
                    if scraped_files:
                        latest_file = max(scraped_files)
                        file_path = os.path.join(project_root, latest_file)
                        
                        with open(file_path, 'r') as f:
                            raw_data = json.load(f)
                        
                        # Convert to API format
                        _lasermatch_items = []
                        for item in raw_data:
                            _lasermatch_items.append({
                                "id": i + 1,
                                "title": item["title"],
                                "brand": item["brand"],
                                "model": item["model"],
                                "condition": item["condition"],
                                "price": item["price"] if item["price"] > 0 else 25000.0,
                                "location": item["location"],
                                "description": item["description"],
                                "url": item["url"],
                                "images": item["images"],
                                "source": item["source"],
                                "status": item["status"],
                                "category": item["category"],
                                "availability": item["availability"],
                                "assigned_rep": item["assigned_rep"],
                                "target_price": item["target_price"],
                                "notes": item["notes"],
                                "spider_urls": item["spider_urls"]
                            })
            except Exception as e:
                print(f"Failed to load scraped data for stats: {e}")
                _lasermatch_items = []
        
        # Use scraped data if available, otherwise fall back to memory
        items_to_use = _lasermatch_items if _lasermatch_items else lasermatch_items_memory
        
        total_count = len(items_to_use)
        status_counts = [{"status": "active", "count": total_count}]
        rep_counts = []
        
        return {
            "total_items": total_count,
            "status_breakdown": status_counts,
            "rep_breakdown": rep_counts,
            "source": "memory"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
