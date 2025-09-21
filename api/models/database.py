import os
import asyncpg
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Numeric, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/laser_intelligence")

# For local development without database, use a mock connection
LOCAL_DEV_MODE = not os.getenv("DATABASE_URL")

# SQLAlchemy setup - lazy initialization to avoid import errors
engine = None
SessionLocal = None

def get_sqlalchemy_engine():
    global engine
    if engine is None and not LOCAL_DEV_MODE:
        engine = create_engine(DATABASE_URL)
    return engine

def get_sqlalchemy_session():
    global SessionLocal
    if SessionLocal is None and not LOCAL_DEV_MODE:
        engine = get_sqlalchemy_engine()
        if engine:
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

Base = declarative_base()

# SQLAlchemy Models
class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    brand = Column(String(100))
    model = Column(String(100))
    condition = Column(String(50))
    price = Column(Numeric(12, 2))
    source = Column(String(100), nullable=False, index=True)
    location = Column(String(200))
    description = Column(Text)
    images = Column(ARRAY(String))
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    margin_estimate = Column(Numeric(12, 2))
    score_overall = Column(Integer)
    url = Column(Text)
    listing_id = Column(String(200))
    category = Column(String(100))  # For hot-list, in-demand, etc.
    status = Column(String(50), default='active')

class SearchConfiguration(Base):
    __tablename__ = "search_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    sources = Column(ARRAY(String), nullable=False)
    keywords = Column(ARRAY(String))
    max_price = Column(Numeric(12, 2))
    min_score = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SpiderRun(Base):
    __tablename__ = "spider_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    spider_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    items_scraped = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)

# Async database functions for compatibility
async def get_db_connection():
    """Get database connection"""
    if LOCAL_DEV_MODE:
        # Return a mock connection for local development
        class MockConnection:
            async def execute(self, query, *args):
                return None
            async def fetchval(self, query, *args):
                return 0
            async def fetch(self, query, *args):
                return []
            async def close(self):
                pass
        
        return MockConnection()
    else:
        return await asyncpg.connect(DATABASE_URL)

async def init_db():
    """Initialize database tables"""
    if LOCAL_DEV_MODE:
        print("Local development mode - skipping database initialization")
        return
    
    try:
        conn = await get_db_connection()
        print("Database connection successful during init")
    except Exception as e:
        print(f"Warning: Could not connect to database during init: {e}")
        print("API will start without database connection")
        return
    
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
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                margin_estimate DECIMAL(12,2),
                score_overall INTEGER,
                url TEXT,
                listing_id VARCHAR(200),
                category VARCHAR(100),
                status VARCHAR(50) DEFAULT 'active'
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
        
        # Create LaserMatch items table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS lasermatch_items (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                brand VARCHAR(100),
                model VARCHAR(100),
                condition VARCHAR(50),
                price DECIMAL(12,2),
                location VARCHAR(200),
                description TEXT,
                url TEXT NOT NULL,
                images TEXT,
                discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                source VARCHAR(100) DEFAULT 'LaserMatch.io',
                status VARCHAR(50) DEFAULT 'active',
                category VARCHAR(100),
                availability VARCHAR(50) DEFAULT 'available'
            )
        """)
        
        # Create indexes for better performance
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_source ON listings(source)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_title ON listings(title)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_discovered_at ON listings(discovered_at)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_score ON listings(score_overall)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_lasermatch_category ON lasermatch_items(category)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_lasermatch_brand ON lasermatch_items(brand)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_lasermatch_discovered_at ON lasermatch_items(discovered_at)")
        
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
