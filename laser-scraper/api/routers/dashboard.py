from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from api.models.database import get_db_connection

router = APIRouter()

class DashboardStats(BaseModel):
    total_listings: int
    new_listings: int
    high_value_listings: int
    avg_margin: float
    top_sources: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    price_trends: List[Dict[str, Any]]

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        conn = await get_db_connection()
        
        # Total listings
        total_listings = await conn.fetchval("SELECT COUNT(*) FROM listings")
        
        # New listings (last 24 hours)
        new_listings = await conn.fetchval("""
            SELECT COUNT(*) FROM listings 
            WHERE discovered_at >= NOW() - INTERVAL '24 hours'
        """)
        
        # High-value listings (price > $50,000)
        high_value_listings = await conn.fetchval("""
            SELECT COUNT(*) FROM listings 
            WHERE price > 50000
        """)
        
        # Average margin
        avg_margin = await conn.fetchval("""
            SELECT AVG(margin_estimate) FROM listings 
            WHERE margin_estimate IS NOT NULL
        """) or 0
        
        # Top sources
        top_sources_rows = await conn.fetch("""
            SELECT source, COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM listings), 1) as percentage
            FROM listings 
            GROUP BY source 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        top_sources = []
        for row in top_sources_rows:
            top_sources.append({
                "name": row['source'],
                "count": row['count'],
                "percentage": float(row['percentage'])
            })
        
        # Recent activity (last 50 listings)
        recent_activity_rows = await conn.fetch("""
            SELECT id, title, source, discovered_at, price, score_overall
            FROM listings 
            ORDER BY discovered_at DESC 
            LIMIT 50
        """)
        
        recent_activity = []
        for row in recent_activity_rows:
            activity_type = "New listing discovered"
            if row['price'] and row['price'] > 100000:
                activity_type = "High-value alert triggered"
            elif row['score_overall'] and row['score_overall'] >= 80:
                activity_type = "High-score listing found"
            
            recent_activity.append({
                "id": str(row['id']),
                "action": activity_type,
                "item": row['title'],
                "timestamp": row['discovered_at'].isoformat(),
                "source": row['source']
            })
        
        # Price trends (last 7 days)
        price_trends_rows = await conn.fetch("""
            SELECT DATE(discovered_at) as date,
                   AVG(price) as avg_price,
                   COUNT(*) as count
            FROM listings 
            WHERE discovered_at >= NOW() - INTERVAL '7 days'
            AND price IS NOT NULL
            GROUP BY DATE(discovered_at)
            ORDER BY date
        """)
        
        price_trends = []
        for row in price_trends_rows:
            price_trends.append({
                "date": row['date'].isoformat(),
                "avg_price": float(row['avg_price']) if row['avg_price'] else 0,
                "count": row['count']
            })
        
        await conn.close()
        
        return DashboardStats(
            total_listings=total_listings,
            new_listings=new_listings,
            high_value_listings=high_value_listings,
            avg_margin=float(avg_margin),
            top_sources=top_sources,
            recent_activity=recent_activity,
            price_trends=price_trends
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@router.get("/activity")
async def get_recent_activity(limit: int = 20):
    """Get recent system activity"""
    try:
        conn = await get_db_connection()
        
        # Recent listings
        listings = await conn.fetch("""
            SELECT id, title, source, discovered_at, price, score_overall
            FROM listings 
            ORDER BY discovered_at DESC 
            LIMIT $1
        """, limit)
        
        # Recent spider runs
        spider_runs = await conn.fetch("""
            SELECT spider_name, status, items_scraped, started_at, completed_at
            FROM spider_runs 
            ORDER BY started_at DESC 
            LIMIT 10
        """)
        
        await conn.close()
        
        activity = []
        
        # Add listing activities
        for listing in listings:
            activity.append({
                "type": "listing",
                "action": "New listing discovered",
                "item": listing['title'],
                "source": listing['source'],
                "timestamp": listing['discovered_at'].isoformat(),
                "metadata": {
                    "price": float(listing['price']) if listing['price'] else None,
                    "score": listing['score_overall']
                }
            })
        
        # Add spider run activities
        for run in spider_runs:
            activity.append({
                "type": "spider",
                "action": f"Spider {run['status']}",
                "item": run['spider_name'],
                "source": "System",
                "timestamp": run['started_at'].isoformat(),
                "metadata": {
                    "items_scraped": run['items_scraped'],
                    "duration": (run['completed_at'] - run['started_at']).total_seconds() if run['completed_at'] else None
                }
            })
        
        # Sort by timestamp
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {"activity": activity[:limit]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get activity: {str(e)}")
