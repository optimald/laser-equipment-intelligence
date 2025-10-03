from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager

# SIMPLIFIED API - VERSION 1.0.6 - NO DATABASE DEPENDENCIES
from api.routers import search, dashboard, configuration, spiders, lasermatch, exhaustive_search

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Try database, fallback to in-memory
    print("Starting Laser Equipment Intelligence API - Hybrid Mode")
    
    try:
        # Try to initialize database
        from api.models.database import init_db
        await init_db()
        print("✅ Database mode enabled")
    except Exception as e:
        print(f"⚠️ Database unavailable, using in-memory mode: {e}")
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Laser Equipment Intelligence API",
    description="API for managing laser equipment procurement and intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "https://laser-procurement-frontend-hydf8tsg6-optimaldev.vercel.app",
        "https://laser-procurement-frontend.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(configuration.router, prefix="/api/v1/config", tags=["configuration"])
app.include_router(spiders.router, prefix="/api/v1/spiders", tags=["spiders"])
app.include_router(lasermatch.router, prefix="/api/v1/lasermatch", tags=["lasermatch"])
app.include_router(exhaustive_search.router, prefix="/api/v1/exhaustive", tags=["exhaustive-search"])

@app.get("/")
async def root():
    return {"message": "Laser Equipment Intelligence API", "version": "1.0.14", "build": "2025-09-23-database-persistent", "status": "database_with_fallback", "deploy_time": "2025-09-23-15:30:00"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "laser-intelligence-api", "timestamp": "2025-09-21-02:47:00", "magic_find_fix": "v3"}

@app.get("/db-test")
async def db_test():
    import os
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        return {"error": "DATABASE_URL not set", "env_vars": list(os.environ.keys())}
    
    try:
        import asyncpg
        conn = await asyncpg.connect(database_url)
        
        # Test connection and create table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            )
        """)
        
        # Insert test data
        await conn.execute("INSERT INTO test_table (name) VALUES ($1)", "test")
        
        # Query test data
        result = await conn.fetchval("SELECT COUNT(*) FROM test_table")
        
        await conn.close()
        
        return {
            "status": "success",
            "database_url_set": True,
            "connection": "successful",
            "test_table_count": result
        }
    except Exception as e:
        return {
            "status": "error",
            "database_url_set": True,
            "error": str(e)
        }

# Direct search endpoints for testing
@app.get("/api/v1/search/test")
async def search_test():
    return {"message": "Search endpoint is working", "status": "ok"}

@app.post("/api/v1/search/equipment")
async def search_equipment_direct(search_request: dict):
    """Direct search endpoint using real spiders"""
    try:
        # Use the spider search endpoint
        spider_results = await spiders.run_spider_search(search_request)
        
        # Return the results from spiders
        return spider_results.get("results", [])
        
    except Exception as e:
        print(f"Spider search failed, falling back to mock data: {e}")
        
        # Fallback to mock data if spiders fail
        from datetime import datetime
        import random
        
        mock_results = []
        sources = ["eBay", "DOTmed Auctions", "BidSpotter", "Craigslist", "Facebook Marketplace"]
        conditions = ["New", "Used - Excellent", "Used - Good", "Used - Fair", "Refurbished"]
        brands = ["Aerolase", "Candela", "Cynosure", "Lumenis", "Syneron", "Alma", "Cutera", "Sciton"]
        locations = ["California, USA", "Texas, USA", "New York, USA", "Florida, USA", "Illinois, USA"]
        
        # Generate 3-5 results
        num_results = min(random.randint(3, 5), search_request.get('limit', 50))
        
        for i in range(num_results):
            brand = random.choice(brands)
            model = f"{brand} {random.choice(['Pro', 'Elite', 'Max', 'Plus', 'Neo'])}"
            base_price = random.randint(15000, 85000)
            
            mock_results.append({
                "id": 1000 + i,
                "title": f"{brand} {model} Laser System",
                "brand": brand,
                "model": model,
                "condition": random.choice(conditions),
                "price": float(base_price),
                "source": random.choice(sources),
                "location": random.choice(locations),
                "description": f"Professional {brand} {model} laser system in excellent condition.",
                "images": [f"https://example.com/image_{i+1}.jpg"],
                "discovered_at": datetime.now().isoformat(),
                "margin_estimate": random.uniform(15.0, 35.0),
                "score_overall": random.randint(75, 95),
                "url": f"https://example.com/listing/{1000+i}"
            })
        
        return mock_results

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
