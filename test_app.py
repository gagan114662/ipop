#!/usr/bin/env python3
"""
Simple test script to verify the application can start without database connections.
"""
import os
import sys
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Set environment variables
os.environ["SECRET_KEY"] = "your-super-secret-key-here-min-32-chars-ipop-media-buying-system"
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "True"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

# Create a simple FastAPI app for testing
app = FastAPI(
    title="IPOP Test App",
    version="1.0.0",
    description="Test application without database dependencies"
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "IPOP Test App is running!", "status": "success"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/test")
async def test():
    """Test endpoint."""
    return {"message": "Test endpoint working", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    print("Starting IPOP Test App...")
    print("Available endpoints:")
    print("  - http://localhost:8000/ (root)")
    print("  - http://localhost:8000/health (health check)")
    print("  - http://localhost:8000/test (test endpoint)")
    print("  - http://localhost:8000/docs (API documentation)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
