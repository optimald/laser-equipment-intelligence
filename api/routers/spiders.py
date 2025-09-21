from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
# from api.models.database import get_db_connection  # Disabled for mock data mode
import subprocess
import asyncio
from datetime import datetime

router = APIRouter()

class SpiderRun(BaseModel):
    id: Optional[int] = None
    spider_name: str
    status: str
    items_scraped: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

class SpiderStatus(BaseModel):
    name: str
    status: str
    last_run: Optional[str] = None
    items_last_run: int = 0
    avg_items_per_run: float = 0
    success_rate: float = 0

async def run_spider_background(spider_name: str):
    """Run spider in background and update database"""
    # conn = await get_db_connection()  # Disabled for mock data mode
    
    try:
        # Create spider run record
        run_id = await conn.fetchval("""
            INSERT INTO spider_runs (spider_name, status, started_at)
            VALUES ($1, 'running', NOW())
            RETURNING id
        """, spider_name)
        
        # Run the spider
        process = await asyncio.create_subprocess_exec(
            'python', '-m', 'scrapy', 'crawl', spider_name,
            cwd='laser-equipment-intelligence',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Success
            await conn.execute("""
                UPDATE spider_runs 
                SET status = 'completed', completed_at = NOW()
                WHERE id = $1
            """, run_id)
        else:
            # Error
            error_msg = stderr.decode() if stderr else "Unknown error"
            await conn.execute("""
                UPDATE spider_runs 
                SET status = 'failed', completed_at = NOW(), error_message = $1
                WHERE id = $2
            """, error_msg, run_id)
            
    except Exception as e:
        # Update with error
        await conn.execute("""
            UPDATE spider_runs 
            SET status = 'failed', completed_at = NOW(), error_message = $1
            WHERE id = $2
        """, str(e), run_id)
    finally:
        await conn.close()

@router.get("/", response_model=List[SpiderStatus])
async def get_spider_status():
    """Get status of all spiders"""
    try:
        # conn = await get_db_connection()  # Disabled for mock data mode
        
        # Get list of available spiders
        spiders = [
            "lasermatch", "dotmed_auctions", "bidspotter", "ebay_laser", 
            "govdeals", "facebook_marketplace", "craigslist", "thelaserwarehouse",
            "laser_agent", "medwow", "iron_horse_auction", "kurtz_auction",
            "asset_recovery_services", "hilditch_group"
        ]
        
        spider_statuses = []
        
        for spider in spiders:
            # Get last run info
            last_run = await conn.fetchrow("""
                SELECT status, items_scraped, started_at, completed_at
                FROM spider_runs 
                WHERE spider_name = $1 
                ORDER BY started_at DESC 
                LIMIT 1
            """, spider)
            
            # Get average stats
            stats = await conn.fetchrow("""
                SELECT 
                    AVG(items_scraped) as avg_items,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate
                FROM spider_runs 
                WHERE spider_name = $1
            """, spider)
            
            status = "inactive"
            last_run_time = None
            items_last_run = 0
            
            if last_run:
                status = last_run['status']
                last_run_time = last_run['started_at'].isoformat()
                items_last_run = last_run['items_scraped'] or 0
            
            spider_statuses.append(SpiderStatus(
                name=spider,
                status=status,
                last_run=last_run_time,
                items_last_run=items_last_run,
                avg_items_per_run=float(stats['avg_items']) if stats['avg_items'] else 0,
                success_rate=float(stats['success_rate']) if stats['success_rate'] else 0
            ))
        
        await conn.close()
        return spider_statuses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get spider status: {str(e)}")

@router.post("/run/{spider_name}")
async def run_spider(spider_name: str, background_tasks: BackgroundTasks):
    """Run a specific spider"""
    try:
        # Check if spider is already running
        # conn = await get_db_connection()  # Disabled for mock data mode
        running_check = await conn.fetchval("""
            SELECT COUNT(*) FROM spider_runs 
            WHERE spider_name = $1 AND status = 'running'
        """, spider_name)
        
        if running_check > 0:
            await conn.close()
            raise HTTPException(status_code=400, detail=f"Spider {spider_name} is already running")
        
        await conn.close()
        
        # Start spider in background
        background_tasks.add_task(run_spider_background, spider_name)
        
        return {"message": f"Spider {spider_name} started successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start spider: {str(e)}")

@router.post("/run-all")
async def run_all_spiders(background_tasks: BackgroundTasks):
    """Run all enabled spiders"""
    try:
        # List of spiders to run (exclude low-priority ones by default)
        spiders_to_run = [
            "lasermatch", "dotmed_auctions", "bidspotter", 
            "thelaserwarehouse", "laser_agent", "iron_horse_auction", 
            "kurtz_auction", "asset_recovery_services"
        ]
        
        # Start all spiders in background
        for spider in spiders_to_run:
            background_tasks.add_task(run_spider_background, spider)
        
        return {"message": f"Started {len(spiders_to_run)} spiders successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start spiders: {str(e)}")

@router.get("/runs", response_model=List[SpiderRun])
async def get_spider_runs(limit: int = 50):
    """Get recent spider runs"""
    try:
        # conn = await get_db_connection()  # Disabled for mock data mode
        
        rows = await conn.fetch("""
            SELECT id, spider_name, status, items_scraped, started_at, completed_at, error_message
            FROM spider_runs 
            ORDER BY started_at DESC 
            LIMIT $1
        """, limit)
        
        await conn.close()
        
        runs = []
        for row in rows:
            runs.append(SpiderRun(
                id=row['id'],
                spider_name=row['spider_name'],
                status=row['status'],
                items_scraped=row['items_scraped'],
                started_at=row['started_at'].isoformat() if row['started_at'] else None,
                completed_at=row['completed_at'].isoformat() if row['completed_at'] else None,
                error_message=row['error_message']
            ))
        
        return runs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get spider runs: {str(e)}")

@router.get("/stats")
async def get_spider_stats():
    """Get spider statistics"""
    try:
        # conn = await get_db_connection()  # Disabled for mock data mode
        
        # Overall stats
        total_runs = await conn.fetchval("SELECT COUNT(*) FROM spider_runs")
        successful_runs = await conn.fetchval("SELECT COUNT(*) FROM spider_runs WHERE status = 'completed'")
        failed_runs = await conn.fetchval("SELECT COUNT(*) FROM spider_runs WHERE status = 'failed'")
        
        # Total items scraped
        total_items = await conn.fetchval("SELECT SUM(items_scraped) FROM spider_runs")
        
        # Runs by spider
        runs_by_spider = await conn.fetch("""
            SELECT spider_name, COUNT(*) as run_count, 
                   AVG(items_scraped) as avg_items,
                   COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_runs
            FROM spider_runs 
            GROUP BY spider_name 
            ORDER BY run_count DESC
        """)
        
        await conn.close()
        
        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
            "total_items_scraped": total_items or 0,
            "runs_by_spider": [
                {
                    "spider_name": row['spider_name'],
                    "run_count": row['run_count'],
                    "avg_items": float(row['avg_items']) if row['avg_items'] else 0,
                    "successful_runs": row['successful_runs']
                }
                for row in runs_by_spider
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get spider stats: {str(e)}")
