import os
import asyncpg
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/laser_intelligence")

async def get_db_connection():
    """Get database connection"""
    return await asyncpg.connect(DATABASE_URL)

async def init_db():
    """Initialize database tables"""
    conn = await get_db_connection()
    
    try:
        # Create listings table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                brand VARCHAR(100),
                model VARCHAR(100),
                condition VARCHAR(50),
                price DECIMAL(12,2),
                source VARCHAR(100) NOT NULL,
                location VARCHAR(200),
                description TEXT,
                images TEXT[],
                discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                margin_estimate DECIMAL(12,2),
                score_overall INTEGER,
                url TEXT,
                listing_id VARCHAR(200),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create search configurations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS search_configurations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                sources TEXT[] NOT NULL,
                keywords TEXT[],
                max_price DECIMAL(12,2),
                min_score INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create spider runs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS spider_runs (
                id SERIAL PRIMARY KEY,
                spider_name VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL,
                items_scraped INTEGER DEFAULT 0,
                started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE,
                error_message TEXT
            )
        """)
        
        # Create indexes for better performance
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_source ON listings(source)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_discovered_at ON listings(discovered_at)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_score ON listings(score_overall)")
        
    finally:
        await conn.close()

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def init_pool(self):
        """Initialize connection pool"""
        self.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()

db = Database()
