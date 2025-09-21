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
    
    else:
        try:
            # Try database connection first
            try:
                conn = await get_db_connection()
                print("Database connection successful")
            
            # Build dynamic query
            query_parts = ["SELECT * FROM listings WHERE 1=1"]
            params = []
            param_count = 0
            
            if search_request.query:
                param_count += 1
                query_parts.append(f"AND (title ILIKE ${param_count} OR description ILIKE ${param_count})")
                params.append(f"%{search_request.query}%")
            
            if search_request.brand:
                param_count += 1
                query_parts.append(f"AND brand ILIKE ${param_count}")
                params.append(f"%{search_request.brand}%")
            
            if search_request.model:
                param_count += 1
                query_parts.append(f"AND model ILIKE ${param_count}")
                params.append(f"%{search_request.model}%")
            
            if search_request.condition:
                param_count += 1
                query_parts.append(f"AND condition = ${param_count}")
                params.append(search_request.condition)
            
            if search_request.max_price:
                param_count += 1
                query_parts.append(f"AND price <= ${param_count}")
                params.append(search_request.max_price)
            
            if search_request.min_price:
                param_count += 1
                query_parts.append(f"AND price >= ${param_count}")
                params.append(search_request.min_price)
            
            if search_request.location:
                param_count += 1
                query_parts.append(f"AND location ILIKE ${param_count}")
                params.append(f"%{search_request.location}%")
            
            if search_request.sources:
                param_count += 1
                query_parts.append(f"AND source = ANY(${param_count})")
                params.append(search_request.sources)
            
            if search_request.min_score:
                param_count += 1
                query_parts.append(f"AND score_overall >= ${param_count}")
                params.append(search_request.min_score)
            
            query_parts.append("ORDER BY discovered_at DESC")
            query_parts.append(f"LIMIT {search_request.limit}")
            
            final_query = " ".join(query_parts)
            
            rows = await conn.fetch(final_query, *params)
            await conn.close()
            
            results = []
            for row in rows:
                results.append(SearchResponse(
                    id=row['id'],
                    title=row['title'],
                    brand=row['brand'],
                    model=row['model'],
                    condition=row['condition'],
                    price=float(row['price']) if row['price'] else None,
                    source=row['source'],
                    location=row['location'],
                    description=row['description'],
                    images=row['images'] or [],
                    discovered_at=row['discovered_at'].isoformat(),
                    margin_estimate=float(row['margin_estimate']) if row['margin_estimate'] else None,
                    score_overall=row['score_overall'],
                    url=row['url']
                ))
            
            return results
            
        except Exception as db_error:
            print(f"Database connection failed: {db_error}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(db_error)}")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

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
