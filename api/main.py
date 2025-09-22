from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager

# SIMPLIFIED API - VERSION 1.0.6 - NO DATABASE DEPENDENCIES
from api.routers import search, dashboard, configuration, lasermatch

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Simple initialization
    print("Starting Laser Equipment Intelligence API - Simplified Mode")
    print("No database dependencies - using in-memory storage")
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
# app.include_router(spiders.router, prefix="/api/v1/spiders", tags=["spiders"])  # Temporarily disabled
app.include_router(lasermatch.router, prefix="/api/v1/lasermatch", tags=["lasermatch"])

@app.get("/")
async def root():
    return {"message": "Laser Equipment Intelligence API", "version": "1.0.10", "build": "2025-09-22-full-scrape", "status": "all_items_enabled", "deploy_time": "2025-09-22-15:30:00"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "laser-intelligence-api", "timestamp": "2025-09-21-02:47:00", "magic_find_fix": "v3"}

# Direct search endpoints for testing
@app.get("/api/v1/search/test")
async def search_test():
    return {"message": "Search endpoint is working", "status": "ok"}

@app.post("/api/v1/search/equipment")
async def search_equipment_direct(search_request: dict):
    """Direct search endpoint for testing"""
    from datetime import datetime
    import random
    
    # Generate mock search results
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
