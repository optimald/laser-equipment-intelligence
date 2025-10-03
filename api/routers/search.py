from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import asyncio
import asyncpg
import os
from datetime import datetime
import json

router = APIRouter()

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

@router.post("/equipment")
async def search_equipment(search_request: Dict[str, Any]):
    """Search for laser equipment across all sources"""
    try:
        query = search_request.get('query', '').strip()
        limit = search_request.get('limit', 50)
        
        if not query:
            raise HTTPException(status_code=400, detail="Search query is required")
        
        # Try database search first
        conn = await get_db_connection()
        if conn:
            try:
                # Search in LaserMatch items
                lasermatch_results = await conn.fetch("""
                    SELECT 
                        id, title, brand, model, condition, price, location, 
                        description, url, images, discovered_at, source, status
                    FROM lasermatch_items 
                    WHERE 
                        (LOWER(title) LIKE LOWER($1) OR 
                         LOWER(brand) LIKE LOWER($1) OR 
                         LOWER(model) LIKE LOWER($1) OR 
                         LOWER(description) LIKE LOWER($1))
                        AND status = 'active'
                    ORDER BY 
                        CASE 
                            WHEN LOWER(brand) LIKE LOWER($1) THEN 1
                            WHEN LOWER(model) LIKE LOWER($1) THEN 2
                            WHEN LOWER(title) LIKE LOWER($1) THEN 3
                            ELSE 4
                        END,
                        discovered_at DESC
                    LIMIT $2
                """, f"%{query}%", limit)
                
                await conn.close()
                
                # Convert to list of dicts
                results = []
                for row in lasermatch_results:
                    item = dict(row)
                    # Convert datetime objects to ISO strings
                    if item.get('discovered_at'):
                        item['discovered_at'] = item['discovered_at'].isoformat()
                    results.append(item)
                
                return {
                    "query": query,
                    "results": results,
                    "total": len(results),
                    "source": "database",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                print(f"Database search failed: {e}")
                if conn:
                    await conn.close()
        
        # Fallback to mock search results
        mock_results = generate_mock_search_results(query, limit)
        
        return {
            "query": query,
            "results": mock_results,
            "total": len(mock_results),
            "source": "mock",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

def generate_mock_search_results(query: str, limit: int) -> List[Dict[str, Any]]:
    """Generate mock search results for testing"""
    import random
    
    # Generate realistic laser equipment data based on the search query
    query_lower = query.lower()
    
    # Determine brand from query
    if 'aerolase' in query_lower:
        brand = 'Aerolase'
    elif 'candela' in query_lower:
        brand = 'Candela'
    elif 'cynosure' in query_lower:
        brand = 'Cynosure'
    elif 'lumenis' in query_lower:
        brand = 'Lumenis'
    elif 'syneron' in query_lower:
        brand = 'Syneron'
    elif 'alma' in query_lower:
        brand = 'Alma'
    elif 'cutera' in query_lower:
        brand = 'Cutera'
    elif 'sciton' in query_lower:
        brand = 'Sciton'
    else:
        brand = random.choice(['Aerolase', 'Candela', 'Cynosure', 'Lumenis', 'Syneron', 'Alma', 'Cutera', 'Sciton'])
    
    # Realistic laser equipment models by brand
    brand_models = {
        'Aerolase': ['LightPod Neo Elite', 'LightPod Neo', 'LightPod Elite', 'LightPod Pro'],
        'Candela': ['GentleLase Pro', 'GentleMax Pro', 'VBeam Perfecta', 'CoolGlide Excel'],
        'Cynosure': ['Picosure', 'Picoway', 'SmartLipo', 'Monolith'],
        'Lumenis': ['LightSheer Duet', 'M22', 'UltraPulse', 'AcuPulse'],
        'Syneron': ['eTwo', 'eMatrix', 'VelaShape', 'ReFirme'],
        'Alma': ['Harmony XL', 'Harmony', 'Soprano', 'Accent'],
        'Cutera': ['Excel V', 'Titan', 'Genesis Plus', 'Laser Genesis'],
        'Sciton': ['Profile', 'Contour TRL', 'Joule', 'Halo']
    }
    
    models = brand_models.get(brand, ['Professional', 'Elite', 'Pro', 'Max'])
    
    results = []
    sources = ["eBay", "DOTmed Auctions", "BidSpotter", "Equipment Network", "MedWOW"]
    conditions = ["New", "Used - Excellent", "Used - Good", "Used - Fair", "Refurbished"]
    locations = ["California, USA", "Texas, USA", "New York, USA", "Florida, USA", "Illinois, USA", "Nevada, USA"]
    
    # Generate 3-5 realistic results
    num_results = min(random.randint(3, 5), limit)
    
    for i in range(num_results):
        model = random.choice(models)
        condition = random.choice(conditions)
        
        # Realistic pricing based on brand and condition
        if brand == 'Aerolase':
            base_price = random.randint(25000, 45000)
        elif brand in ['Candela', 'Cynosure']:
            base_price = random.randint(35000, 65000)
        elif brand in ['Lumenis', 'Sciton']:
            base_price = random.randint(40000, 80000)
        else:
            base_price = random.randint(20000, 60000)
        
        # Adjust price based on condition
        if condition == "New":
            price = base_price
        elif condition == "Used - Excellent":
            price = int(base_price * 0.75)
        elif condition == "Used - Good":
            price = int(base_price * 0.60)
        elif condition == "Used - Fair":
            price = int(base_price * 0.45)
        else:  # Refurbished
            price = int(base_price * 0.70)
        
        source = random.choice(sources)
        location = random.choice(locations)
        
        results.append({
            "id": f"mock_{brand.lower()}_{i+1}",
            "title": f"{brand} {model} Laser System",
            "brand": brand,
            "model": model,
            "condition": condition,
            "price": float(price),
            "source": source,
            "location": location,
            "description": f"Professional {brand} {model} laser system in {condition.lower()} condition. Perfect for aesthetic treatments.",
            "images": [f"https://example.com/{brand.lower()}_{model.lower().replace(' ', '_')}_{i+1}.jpg"],
            "discovered_at": datetime.now().isoformat(),
            "margin_estimate": random.uniform(20.0, 40.0),
            "score_overall": random.randint(80, 95),
            "url": f"https://{source.lower().replace(' ', '')}.com/listing/{brand.lower()}_{model.lower().replace(' ', '_')}_{i+1}",
            "status": "active"
        })
    
    # Sort by relevance score
    results.sort(key=lambda x: x['score_overall'], reverse=True)
    
    return results

@router.get("/sources")
async def get_search_sources():
    """Get available search sources"""
    try:
        conn = await get_db_connection()
        if conn:
            try:
                # Get source statistics from database
                source_stats = await conn.fetch("""
                    SELECT 
                        source,
                        COUNT(*) as item_count,
                        AVG(price) as avg_price,
                        MIN(price) as min_price,
                        MAX(price) as max_price
                    FROM lasermatch_items 
                    WHERE status = 'active'
                    GROUP BY source
                    ORDER BY item_count DESC
                """)
                
                await conn.close()
                
                sources = []
                for row in source_stats:
                    sources.append({
                        "name": row['source'],
                        "item_count": row['item_count'],
                        "avg_price": float(row['avg_price']) if row['avg_price'] else 0,
                        "min_price": float(row['min_price']) if row['min_price'] else 0,
                        "max_price": float(row['max_price']) if row['max_price'] else 0,
                        "status": "active"
                    })
                
                return {
                    "sources": sources,
                    "total_sources": len(sources),
                    "source": "database"
                }
            except Exception as e:
                if conn:
                    await conn.close()
                raise e
        
        # Fallback to mock sources
        mock_sources = [
            {"name": "LaserMatch.io", "item_count": 150, "avg_price": 45000, "min_price": 15000, "max_price": 85000, "status": "active"},
            {"name": "eBay", "item_count": 89, "avg_price": 38000, "min_price": 12000, "max_price": 75000, "status": "active"},
            {"name": "DOTmed Auctions", "item_count": 67, "avg_price": 52000, "min_price": 20000, "max_price": 90000, "status": "active"},
            {"name": "BidSpotter", "item_count": 45, "avg_price": 41000, "min_price": 18000, "max_price": 80000, "status": "active"},
            {"name": "The Laser Warehouse", "item_count": 32, "avg_price": 48000, "min_price": 25000, "max_price": 85000, "status": "active"},
        ]
        
        return {
            "sources": mock_sources,
            "total_sources": len(mock_sources),
            "source": "mock"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sources: {str(e)}")

@router.get("/test")
async def search_test():
    """Test search endpoint"""
    return {
        "message": "Search endpoint is working",
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }
