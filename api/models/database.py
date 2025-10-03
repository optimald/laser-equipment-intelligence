import os
import asyncpg
from typing import Optional

async def init_db():
    """Initialize database connection and create tables"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not set")
            return False
            
        print(f"🔗 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        # Create lasermatch_items table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS lasermatch_items (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                brand VARCHAR(100),
                model VARCHAR(100),
                condition VARCHAR(50),
                price DECIMAL(12,2),
                location VARCHAR(200),
                description TEXT,
                url TEXT UNIQUE,
                images TEXT[],
                discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                source VARCHAR(100) DEFAULT 'LaserMatch.io',
                status VARCHAR(50) DEFAULT 'active',
                category VARCHAR(100),
                availability VARCHAR(50),
                assigned_rep VARCHAR(100),
                target_price DECIMAL(12,2),
                notes TEXT,
                spider_urls TEXT
            )
        """)
        
        # Create notes table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                item_id INTEGER REFERENCES lasermatch_items(id) ON DELETE CASCADE,
                user_name VARCHAR(100) NOT NULL,
                note_text TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create sources table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id SERIAL PRIMARY KEY,
                item_id INTEGER REFERENCES lasermatch_items(id) ON DELETE CASCADE,
                source_name VARCHAR(100) NOT NULL,
                contact_info TEXT,
                price DECIMAL(12,2),
                follow_up_date DATE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create spider_urls table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS spider_urls (
                id SERIAL PRIMARY KEY,
                item_id INTEGER REFERENCES lasermatch_items(id) ON DELETE CASCADE,
                url TEXT NOT NULL,
                source_name VARCHAR(100),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create indexes for better performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_lasermatch_items_brand ON lasermatch_items(brand);
            CREATE INDEX IF NOT EXISTS idx_lasermatch_items_model ON lasermatch_items(model);
            CREATE INDEX IF NOT EXISTS idx_lasermatch_items_status ON lasermatch_items(status);
            CREATE INDEX IF NOT EXISTS idx_lasermatch_items_assigned_rep ON lasermatch_items(assigned_rep);
            CREATE INDEX IF NOT EXISTS idx_lasermatch_items_discovered_at ON lasermatch_items(discovered_at);
        """)
        
        await conn.close()
        print("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

async def get_db_connection():
    """Get database connection"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return None
        return await asyncpg.connect(database_url)
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

async def test_db_connection():
    """Test database connection and return status"""
    try:
        conn = await get_db_connection()
        if not conn:
            return {"status": "error", "message": "No database connection"}
        
        # Test basic query
        result = await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items")
        await conn.close()
        
        return {
            "status": "success", 
            "message": "Database connected",
            "item_count": result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
