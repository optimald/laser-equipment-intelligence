from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager

from api.routers import search, dashboard, configuration, spiders
from api.models.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
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

@app.get("/")
async def root():
    return {"message": "Laser Equipment Intelligence API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "laser-intelligence-api"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
