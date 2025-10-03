#!/usr/bin/env python3
"""
Simple API to test Railway deployment and database connection
"""
import os
import asyncio
import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Simple Laser API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def init_database():
    """Initialize database tables"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ No DATABASE_URL found")
            return False
            
        print(f"🔗 Connecting to database...")
        conn = await asyncpg.connect(DATABASE_URL)
        
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
                url TEXT,
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
        
        # Insert some test data
        await conn.execute("""
            INSERT INTO lasermatch_items (title, brand, model, price, location, description, url)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT DO NOTHING
        """, 
        "Test Laser System", "Test Brand", "Model X", 50000.0, "Test Location", "Test description", "https://test.com")
        
        await conn.close()
        print("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Simple Laser API")
    await init_database()

@app.get("/")
async def root():
    return {
        "message": "Simple Laser API", 
        "version": "1.0.0", 
        "status": "running",
        "database": "connected" if os.getenv("DATABASE_URL") else "not_configured"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test-db")
async def test_db():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            return {"error": "No DATABASE_URL configured"}
            
        conn = await asyncpg.connect(DATABASE_URL)
        result = await conn.fetchval("SELECT COUNT(*) FROM lasermatch_items")
        await conn.close()
        
        return {
            "status": "success",
            "table_exists": True,
            "item_count": result
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
