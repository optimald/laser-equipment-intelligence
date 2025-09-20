#!/usr/bin/env python3
"""
Simple test API for Railway deployment
"""
from fastapi import FastAPI
import os

app = FastAPI(title="Simple Test API")

@app.get("/")
async def root():
    return {"message": "Simple API is working!", "port": os.environ.get("PORT", "unknown")}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "simple-test-api"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
