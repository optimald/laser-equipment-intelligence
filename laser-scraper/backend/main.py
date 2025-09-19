from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Laser Equipment Intelligence API",
    description="API for managing laser equipment procurement and intelligence",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://laser-procurement-frontend-hydf8tsg6-optimaldev.vercel.app",
        "https://laser-procurement-frontend.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Laser Equipment Intelligence API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "laser-intelligence-api"}

@app.get("/api/v1/search/equipment")
async def search_equipment():
    """Mock search endpoint for testing"""
    return {
        "results": [
            {
                "id": 1,
                "title": "Sciton Joule Laser System",
                "brand": "Sciton",
                "model": "Joule",
                "condition": "excellent",
                "price": 85000,
                "source": "LaserMatch.io",
                "location": "California, USA",
                "description": "Complete Sciton Joule laser system with multiple handpieces",
                "discovered_at": "2024-09-19T17:00:00Z",
                "score_overall": 85
            }
        ]
    }

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """Mock dashboard stats for testing"""
    return {
        "total_listings": 1247,
        "new_listings": 89,
        "high_value_listings": 23,
        "avg_margin": 28.5,
        "top_sources": [
            {"name": "LaserMatch.io", "count": 234, "percentage": 18.8},
            {"name": "DOTmed Auctions", "count": 198, "percentage": 15.9}
        ]
    }

@app.get("/api/v1/config/sources")
async def get_source_configurations():
    """Mock source configurations"""
    return [
        {
            "id": "lasermatch",
            "name": "LaserMatch.io",
            "priority": "HIGH",
            "enabled": True,
            "status": "active"
        },
        {
            "id": "dotmed_auctions",
            "name": "DOTmed Auctions",
            "priority": "HIGH",
            "enabled": True,
            "status": "active"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
