#!/usr/bin/env python3
"""
Railway Worker for LaserMatch Data Updates
This script runs periodically to scrape and update LaserMatch data
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
import asyncpg

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.models.database import get_db_connection, init_db
from api.routers.lasermatch import scrape_lasermatch_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def update_lasermatch_data():
    """Update LaserMatch data from the scraper"""
    try:
        logger.info("🚀 Starting LaserMatch data update...")
        
        # Initialize database
        await init_db()
        
        # Get database connection
        conn = await get_db_connection()
        if not conn:
            logger.error("❌ Failed to connect to database")
            return False
        
        # Get current item count
        current_count = await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items")
        logger.info(f"📊 Current items in database: {current_count}")
        
        # Run the scraper
        logger.info("🕷️ Running LaserMatch scraper...")
        scraped_data = await scrape_lasermatch_data()
        
        if not scraped_data or not scraped_data.get('items'):
            logger.warning("⚠️ No data returned from scraper")
            await conn.close()
            return False
        
        items = scraped_data['items']
        logger.info(f"📥 Scraped {len(items)} items from LaserMatch")
        
        # Update database with new data
        updated_count = 0
        new_count = 0
        
        for item in items:
            try:
                # Check if item already exists
                existing = await conn.fetchrow(
                    "SELECT id FROM lasermatch_items WHERE url = $1",
                    item.get('url', '')
                )
                
                if existing:
                    # Update existing item
                    await conn.execute("""
                        UPDATE lasermatch_items SET
                            title = $1,
                            brand = $2,
                            model = $3,
                            condition = $4,
                            price = $5,
                            location = $6,
                            description = $7,
                            last_updated = NOW()
                        WHERE url = $8
                    """, 
                    item.get('title', ''),
                    item.get('brand', ''),
                    item.get('model', ''),
                    item.get('condition', ''),
                    item.get('price', 0),
                    item.get('location', ''),
                    item.get('description', ''),
                    item.get('url', '')
                    )
                    updated_count += 1
                else:
                    # Insert new item
                    await conn.execute("""
                        INSERT INTO lasermatch_items (
                            title, brand, model, condition, price, location, 
                            description, url, images, source, status, category, availability
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    """,
                    item.get('title', ''),
                    item.get('brand', ''),
                    item.get('model', ''),
                    item.get('condition', ''),
                    item.get('price', 0),
                    item.get('location', ''),
                    item.get('description', ''),
                    item.get('url', ''),
                    item.get('images', []),
                    item.get('source', 'LaserMatch.io'),
                    item.get('status', 'active'),
                    item.get('category', 'Laser System'),
                    item.get('availability', 'Available')
                    )
                    new_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Error processing item {item.get('title', 'Unknown')}: {e}")
                continue
        
        await conn.close()
        
        logger.info(f"✅ Update complete: {new_count} new items, {updated_count} updated items")
        return True
        
    except Exception as e:
        logger.error(f"❌ Update failed: {e}")
        return False

async def cleanup_old_data():
    """Clean up old or inactive data"""
    try:
        logger.info("🧹 Starting data cleanup...")
        
        conn = await get_db_connection()
        if not conn:
            logger.error("❌ Failed to connect to database")
            return False
        
        # Remove items older than 30 days that are inactive
        result = await conn.execute("""
            DELETE FROM lasermatch_items 
            WHERE status = 'inactive' 
            AND last_updated < NOW() - INTERVAL '30 days'
        """)
        
        deleted_count = int(result.split()[-1])
        logger.info(f"🗑️ Cleaned up {deleted_count} old inactive items")
        
        await conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        return False

async def main():
    """Main worker function"""
    logger.info("🏗️ Railway Worker starting...")
    
    # Update LaserMatch data
    success = await update_lasermatch_data()
    
    if success:
        # Clean up old data
        await cleanup_old_data()
        logger.info("✅ Worker completed successfully")
    else:
        logger.error("❌ Worker failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
