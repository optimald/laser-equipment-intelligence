from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import asyncio
import asyncpg
import os
from datetime import datetime

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

@router.get("/status")
async def get_system_status():
    """Get system configuration and status"""
    try:
        # Test database connection
        db_status = "disconnected"
        db_info = {}
        
        conn = await get_db_connection()
        if conn:
            try:
                # Get database info
                db_info = {
                    "connected": True,
                    "item_count": await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items"),
                    "last_update": await conn.fetchval("SELECT MAX(last_updated) FROM lasermatch_items")
                }
                db_status = "connected"
                await conn.close()
            except Exception as e:
                db_info = {"connected": False, "error": str(e)}
                db_status = "error"
                if conn:
                    await conn.close()
        
        return {
            "system_status": "operational",
            "database": {
                "status": db_status,
                "info": db_info
            },
            "api_version": "1.0.14",
            "build": "2025-09-23-database-persistent",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/sources")
async def get_configured_sources():
    """Get configured data sources"""
    try:
        # Mock source configuration
        sources = [
            {
                "id": "lasermatch",
                "name": "LaserMatch.io",
                "enabled": True,
                "last_crawl": "2025-09-23T15:30:00Z",
                "items_found": 150,
                "status": "active"
            },
            {
                "id": "ebay",
                "name": "eBay",
                "enabled": True,
                "last_crawl": "2025-09-23T14:45:00Z",
                "items_found": 89,
                "status": "active"
            },
            {
                "id": "dotmed",
                "name": "DOTmed Auctions",
                "enabled": True,
                "last_crawl": "2025-09-23T13:20:00Z",
                "items_found": 67,
                "status": "active"
            },
            {
                "id": "bidspotter",
                "name": "BidSpotter",
                "enabled": True,
                "last_crawl": "2025-09-23T12:15:00Z",
                "items_found": 45,
                "status": "active"
            },
            {
                "id": "laserwarehouse",
                "name": "The Laser Warehouse",
                "enabled": True,
                "last_crawl": "2025-09-23T11:30:00Z",
                "items_found": 32,
                "status": "active"
            }
        ]
        
        return {
            "sources": sources,
            "total_sources": len(sources),
            "enabled_sources": len([s for s in sources if s["enabled"]]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sources: {str(e)}")

@router.get("/users")
async def get_users():
    """Get system users"""
    try:
        # Mock user data
        users = [
            {
                "id": 1,
                "name": "Admin User",
                "email": "admin@lasermatch.com",
                "role": "admin",
                "last_login": "2025-09-23T15:30:00Z",
                "status": "active"
            },
            {
                "id": 2,
                "name": "Sales Rep 1",
                "email": "rep1@lasermatch.com",
                "role": "sales",
                "last_login": "2025-09-23T14:20:00Z",
                "status": "active"
            },
            {
                "id": 3,
                "name": "Sales Rep 2",
                "email": "rep2@lasermatch.com",
                "role": "sales",
                "last_login": "2025-09-23T13:45:00Z",
                "status": "active"
            }
        ]
        
        return {
            "users": users,
            "total_users": len(users),
            "active_users": len([u for u in users if u["status"] == "active"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@router.get("/settings")
async def get_settings():
    """Get system settings"""
    try:
        settings = {
            "crawl_interval": "6 hours",
            "max_items_per_source": 1000,
            "price_alerts": {
                "enabled": True,
                "threshold_percentage": 20
            },
            "notifications": {
                "email": True,
                "slack": False,
                "webhook": False
            },
            "data_retention": {
                "items": "90 days",
                "logs": "30 days"
            }
        }
        
        return {
            "settings": settings,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")
