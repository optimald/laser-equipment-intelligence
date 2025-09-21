from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from api.models.database import get_db_connection
import asyncpg

router = APIRouter()

class SearchRequest(BaseModel):
    query: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    condition: Optional[str] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    location: Optional[str] = None
    sources: Optional[List[str]] = None
    min_score: Optional[int] = None
    limit: int = 50

class SearchResponse(BaseModel):
    id: int
    title: str
    brand: Optional[str]
    model: Optional[str]
    condition: Optional[str]
    price: Optional[float]
    source: str
    location: Optional[str]
    description: Optional[str]
    images: Optional[List[str]]
    discovered_at: str
    margin_estimate: Optional[float]
    score_overall: Optional[int]
    url: Optional[str]

@router.post("/equipment", response_model=List[SearchResponse])
async def search_equipment(search_request: SearchRequest):
    """Search for laser equipment based on criteria with fallback mock data"""
    print(f"Search request received: {search_request}")
    
    # Always use fallback mock data for now until database is properly configured
    # TODO: Re-enable database connection once Railway PostgreSQL is set up
    use_mock_data = True
    
    if use_mock_data:
        # Use mock data directly
        print("Using mock data (database disabled)")
        from datetime import datetime
        import random
        
        # Generate mock search results based on search criteria
        mock_results = []
        sources = ["eBay", "DOTmed Auctions", "BidSpotter", "Craigslist", "Facebook Marketplace"]
        conditions = ["New", "Used - Excellent", "Used - Good", "Used - Fair", "Refurbished"]
        brands = ["Aerolase", "Candela", "Cynosure", "Lumenis", "Syneron", "Alma", "Cutera", "Sciton"]
        locations = ["California, USA", "Texas, USA", "New York, USA", "Florida, USA", "Illinois, USA"]
        
        # Generate 3-8 results based on search criteria
        num_results = min(random.randint(3, 8), search_request.limit)
        
        for i in range(num_results):
            # Use search criteria to make results more relevant
            brand = search_request.brand if search_request.brand else random.choice(brands)
            model = search_request.model if search_request.model else f"{brand} {random.choice(['Pro', 'Elite', 'Max', 'Plus', 'Neo'])}"
            
            # Generate realistic price based on search criteria
            base_price = random.randint(15000, 85000)
            if search_request.min_price:
                base_price = max(base_price, int(search_request.min_price))
            if search_request.max_price:
                base_price = min(base_price, int(search_request.max_price))
            
            condition = search_request.condition if search_request.condition else random.choice(conditions)
            source = random.choice(search_request.sources) if search_request.sources else random.choice(sources)
            
            # Create title based on search query or generate one
            if search_request.query:
                title = f"{brand} {model} - {search_request.query}"
            else:
                title = f"{brand} {model} Laser System"
            
            mock_results.append(SearchResponse(
                id=1000 + i,
                title=title,
                brand=brand,
                model=model,
                condition=condition,
                price=float(base_price),
                source=source,
                location=random.choice(locations),
                description=f"Professional {brand} {model} laser system in {condition.lower()} condition. Includes all standard accessories and documentation.",
                images=[f"https://example.com/image_{i+1}.jpg"],
                discovered_at=datetime.now().isoformat(),
                margin_estimate=random.uniform(15.0, 35.0),
                score_overall=random.randint(75, 95),
                url=f"https://{source.lower().replace(' ', '')}.com/listing/{1000+i}"
            ))
        
        print(f"Generated {len(mock_results)} mock results")
        return mock_results
    

@router.get("/sources")
async def get_available_sources():
    """Get list of available data sources"""
    try:
        conn = await get_db_connection()
        rows = await conn.fetch("SELECT DISTINCT source FROM listings ORDER BY source")
        await conn.close()
        
        sources = [row['source'] for row in rows]
        return {"sources": sources}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sources: {str(e)}")

@router.get("/brands")
async def get_available_brands():
    """Get list of available equipment brands"""
    try:
        conn = await get_db_connection()
        rows = await conn.fetch("SELECT DISTINCT brand FROM listings WHERE brand IS NOT NULL ORDER BY brand")
        await conn.close()
        
        brands = [row['brand'] for row in rows]
        return {"brands": brands}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get brands: {str(e)}")

@router.get("/stats")
async def get_search_stats():
    """Get search statistics"""
    try:
        conn = await get_db_connection()
        
        # Total listings
        total_listings = await conn.fetchval("SELECT COUNT(*) FROM listings")
        
        # Listings by source
        source_stats = await conn.fetch("""
            SELECT source, COUNT(*) as count 
            FROM listings 
            GROUP BY source 
            ORDER BY count DESC
        """)
        
        # Recent listings (last 24 hours)
        recent_listings = await conn.fetchval("""
            SELECT COUNT(*) FROM listings 
            WHERE discovered_at >= NOW() - INTERVAL '24 hours'
        """)
        
        await conn.close()
        
        return {
            "total_listings": total_listings,
            "recent_listings": recent_listings,
            "source_stats": [{"source": row['source'], "count": row['count']} for row in source_stats]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
