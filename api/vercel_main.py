from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI app
app = FastAPI(title="Laser Equipment Intelligence API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Laser Equipment Intelligence API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "laser-intelligence-api"}

# Import the main app
from main import app as main_app

# Mount the main app
app.mount("/", main_app)
