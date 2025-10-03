from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio
import asyncpg
import os
from datetime import datetime, timedelta

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

@router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        conn = await get_db_connection()
        if conn:
            try:
                # Get total items
                total_items = await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items")
                
                # Get active items
                active_items = await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items WHERE status = 'active'")
                
                # Get items by source
                source_stats = await conn.fetch("""
                    SELECT source, COUNT(*) as count 
                    FROM lasermatch_items 
                    GROUP BY source 
                    ORDER BY count DESC
                """)
                
                # Get price statistics
                price_stats = await conn.fetchval("""
                    SELECT 
                        AVG(price) as avg_price,
                        MIN(price) as min_price,
                        MAX(price) as max_price
                    FROM lasermatch_items 
                    WHERE price IS NOT NULL AND status = 'active'
                """)
                
                # Get recent items (last 7 days)
                recent_items = await conn.fetchval("""
                    SELECT COUNT(*) 
                    FROM lasermatch_items 
                    WHERE discovered_at >= NOW() - INTERVAL '7 days'
                """)
                
                await conn.close()
                
                return {
                    "total_items": total_items,
                    "active_items": active_items,
                    "recent_items": recent_items,
                    "source_breakdown": [dict(row) for row in source_stats],
                    "price_stats": {
                        "avg_price": float(price_stats['avg_price']) if price_stats['avg_price'] else 0,
                        "min_price": float(price_stats['min_price']) if price_stats['min_price'] else 0,
                        "max_price": float(price_stats['max_price']) if price_stats['max_price'] else 0,
                    },
                    "source": "database",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                if conn:
                    await conn.close()
                raise e
        
        # Fallback to mock stats
        return {
            "total_items": 150,
            "active_items": 142,
            "recent_items": 23,
            "source_breakdown": [
                {"source": "LaserMatch.io", "count": 150},
                {"source": "eBay", "count": 89},
                {"source": "DOTmed Auctions", "count": 67},
                {"source": "BidSpotter", "count": 45},
                {"source": "The Laser Warehouse", "count": 32}
            ],
            "price_stats": {
                "avg_price": 45000,
                "min_price": 15000,
                "max_price": 85000
            },
            "source": "mock",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@router.get("/recent-activity")
async def get_recent_activity():
    """Get recent activity feed"""
    try:
        conn = await get_db_connection()
        if conn:
            try:
                # Get recent items
                recent_items = await conn.fetch("""
                    SELECT 
                        id, title, brand, model, price, source, discovered_at
                    FROM lasermatch_items 
                    ORDER BY discovered_at DESC 
                    LIMIT 10
                """)
                
                await conn.close()
                
                activities = []
                for row in recent_items:
                    activities.append({
                        "type": "item_discovered",
                        "title": f"New {row['brand']} {row['model']} found",
                        "description": f"Discovered on {row['source']} for ${row['price']:,.0f}",
                        "timestamp": row['discovered_at'].isoformat(),
                        "item_id": row['id']
                    })
                
                return {
                    "activities": activities,
                    "source": "database"
                }
            except Exception as e:
                if conn:
                    await conn.close()
                raise e
        
        # Fallback to mock activity
        mock_activities = [
            {
                "type": "item_discovered",
                "title": "New Aerolase Lightpod Neo Elite found",
                "description": "Discovered on LaserMatch.io for $45,000",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "item_id": 1
            },
            {
                "type": "item_discovered",
                "title": "New Agnes Agnes RF System found",
                "description": "Discovered on eBay for $38,000",
                "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                "item_id": 2
            },
            {
                "type": "item_discovered",
                "title": "New Allergan DiamondGlow System found",
                "description": "Discovered on DOTmed Auctions for $52,000",
                "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
                "item_id": 3
            }
        ]
        
        return {
            "activities": mock_activities,
            "source": "mock"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent activity: {str(e)}")
