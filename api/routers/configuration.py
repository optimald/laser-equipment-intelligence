from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
# from api.models.database import get_db_connection  # Disabled for mock data mode

router = APIRouter()

class SourceConfiguration(BaseModel):
    id: str
    name: str
    priority: str
    enabled: bool
    last_run: Optional[str] = None
    status: str = "inactive"

class SearchConfiguration(BaseModel):
    id: Optional[int] = None
    name: str
    sources: List[str]
    keywords: Optional[List[str]] = None
    max_price: Optional[float] = None
    min_score: Optional[int] = None
    is_active: bool = True

class SearchConfigurationResponse(SearchConfiguration):
    id: int
    created_at: str
    updated_at: str

@router.get("/sources", response_model=List[SourceConfiguration])
async def get_source_configurations():
    """Get configuration for all available data sources"""
    try:
        # This would typically come from a configuration file or database
        # For now, returning hardcoded sources based on your spider implementations
        sources = [
            {
                "id": "lasermatch",
                "name": "LaserMatch.io",
                "priority": "HIGH",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "dotmed_auctions",
                "name": "DOTmed Auctions",
                "priority": "HIGH",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "bidspotter",
                "name": "BidSpotter",
                "priority": "HIGH",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "ebay_laser",
                "name": "eBay",
                "priority": "MEDIUM",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "govdeals",
                "name": "GovDeals",
                "priority": "MEDIUM",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "facebook_marketplace",
                "name": "Facebook Marketplace",
                "priority": "LOW",
                "enabled": False,
                "last_run": None,
                "status": "inactive"
            },
            {
                "id": "craigslist",
                "name": "Craigslist",
                "priority": "LOW",
                "enabled": False,
                "last_run": None,
                "status": "inactive"
            },
            {
                "id": "thelaserwarehouse",
                "name": "The Laser Warehouse",
                "priority": "HIGH",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "laser_agent",
                "name": "Laser Agent",
                "priority": "HIGH",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "medwow",
                "name": "Medwow",
                "priority": "MEDIUM",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "iron_horse_auction",
                "name": "Iron Horse Auction",
                "priority": "HIGH",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "kurtz_auction",
                "name": "Kurtz Auction",
                "priority": "HIGH",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "asset_recovery_services",
                "name": "Asset Recovery Services",
                "priority": "HIGH",
                "enabled": True,
                "last_run": None,
                "status": "active"
            },
            {
                "id": "hilditch_group",
                "name": "Hilditch Group",
                "priority": "MEDIUM",
                "enabled": True,
                "last_run": None,
                "status": "active"
            }
        ]
        
        return [SourceConfiguration(**source) for source in sources]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get source configurations: {str(e)}")

@router.get("/search-configurations", response_model=List[SearchConfigurationResponse])
async def get_search_configurations():
    """Get all saved search configurations"""
    try:
        # conn = await get_db_connection()  # Disabled for mock data mode
        
        rows = await conn.fetch("""
            SELECT id, name, sources, keywords, max_price, min_score, is_active, created_at, updated_at
            FROM search_configurations 
            ORDER BY created_at DESC
        """)
        
        await conn.close()
        
        configurations = []
        for row in rows:
            configurations.append(SearchConfigurationResponse(
                id=row['id'],
                name=row['name'],
                sources=row['sources'],
                keywords=row['keywords'],
                max_price=float(row['max_price']) if row['max_price'] else None,
                min_score=row['min_score'],
                is_active=row['is_active'],
                created_at=row['created_at'].isoformat(),
                updated_at=row['updated_at'].isoformat()
            ))
        
        return configurations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get search configurations: {str(e)}")

@router.post("/search-configurations", response_model=SearchConfigurationResponse)
async def create_search_configuration(config: SearchConfiguration):
    """Create a new search configuration"""
    try:
        # conn = await get_db_connection()  # Disabled for mock data mode
        
        row = await conn.fetchrow("""
            INSERT INTO search_configurations (name, sources, keywords, max_price, min_score, is_active)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, name, sources, keywords, max_price, min_score, is_active, created_at, updated_at
        """, config.name, config.sources, config.keywords, config.max_price, config.min_score, config.is_active)
        
        await conn.close()
        
        return SearchConfigurationResponse(
            id=row['id'],
            name=row['name'],
            sources=row['sources'],
            keywords=row['keywords'],
            max_price=float(row['max_price']) if row['max_price'] else None,
            min_score=row['min_score'],
            is_active=row['is_active'],
            created_at=row['created_at'].isoformat(),
            updated_at=row['updated_at'].isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create search configuration: {str(e)}")

@router.put("/search-configurations/{config_id}", response_model=SearchConfigurationResponse)
async def update_search_configuration(config_id: int, config: SearchConfiguration):
    """Update an existing search configuration"""
    try:
        # conn = await get_db_connection()  # Disabled for mock data mode
        
        row = await conn.fetchrow("""
            UPDATE search_configurations 
            SET name = $1, sources = $2, keywords = $3, max_price = $4, min_score = $5, is_active = $6, updated_at = NOW()
            WHERE id = $7
            RETURNING id, name, sources, keywords, max_price, min_score, is_active, created_at, updated_at
        """, config.name, config.sources, config.keywords, config.max_price, config.min_score, config.is_active, config_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Search configuration not found")
        
        await conn.close()
        
        return SearchConfigurationResponse(
            id=row['id'],
            name=row['name'],
            sources=row['sources'],
            keywords=row['keywords'],
            max_price=float(row['max_price']) if row['max_price'] else None,
            min_score=row['min_score'],
            is_active=row['is_active'],
            created_at=row['created_at'].isoformat(),
            updated_at=row['updated_at'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update search configuration: {str(e)}")

@router.delete("/search-configurations/{config_id}")
async def delete_search_configuration(config_id: int):
    """Delete a search configuration"""
    try:
        # conn = await get_db_connection()  # Disabled for mock data mode
        
        result = await conn.execute("""
            DELETE FROM search_configurations WHERE id = $1
        """, config_id)
        
        await conn.close()
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Search configuration not found")
        
        return {"message": "Search configuration deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete search configuration: {str(e)}")
