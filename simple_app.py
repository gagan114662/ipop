#!/usr/bin/env python3
"""
Simplified IPOP application that can run without database dependencies.
This is a demonstration version for testing purposes.
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Set environment variables
os.environ["SECRET_KEY"] = "your-super-secret-key-here-min-32-chars-ipop-media-buying-system"
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "True"

# Pydantic models
class ClientCreate(BaseModel):
    company_name: str
    email: str
    password: str

class ClientResponse(BaseModel):
    id: str
    company_name: str
    email: str
    is_active: bool

class SKUCreate(BaseModel):
    sku_id: str
    name: str
    daily_budget: float
    monthly_budget: float
    target_roas: float

class SKUResponse(BaseModel):
    id: str
    sku_id: str
    name: str
    daily_budget: float
    monthly_budget: float
    target_roas: float
    client_id: str

class CampaignCreate(BaseModel):
    campaign_id: str
    name: str
    platform: str
    platform_campaign_id: str
    sku_id: str
    daily_budget: float
    target_roas: float

class CampaignResponse(BaseModel):
    id: str
    campaign_id: str
    name: str
    platform: str
    platform_campaign_id: str
    sku_id: str
    daily_budget: float
    target_roas: float
    client_id: str
    status: str

# In-memory storage (for demo purposes)
clients_db = {}
skus_db = {}
campaigns_db = {}

# Create FastAPI application
app = FastAPI(
    title="IPOP Media Buying Management System",
    version="1.0.0",
    description="Intelligent API-only media buying management system with multi-tenant support (Demo Version)"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "development",
        "database": "in-memory (demo mode)"
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "IPOP Media Buying Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "mode": "demo (in-memory storage)"
    }

# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=dict, tags=["Authentication"])
async def register_client(client: ClientCreate):
    """Register a new client."""
    client_id = f"client_{len(clients_db) + 1}"
    clients_db[client_id] = {
        "id": client_id,
        "company_name": client.company_name,
        "email": client.email,
        "is_active": True
    }
    
    return {
        "message": "Client registered successfully",
        "client_id": client_id,
        "access_token": f"demo_token_{client_id}",
        "token_type": "bearer"
    }

# SKU endpoints
@app.post("/api/v1/skus/", response_model=SKUResponse, tags=["SKUs"])
async def create_sku(sku: SKUCreate, client_id: str = "demo_client"):
    """Create a new SKU."""
    sku_id = f"sku_{len(skus_db) + 1}"
    skus_db[sku_id] = {
        "id": sku_id,
        "sku_id": sku.sku_id,
        "name": sku.name,
        "daily_budget": sku.daily_budget,
        "monthly_budget": sku.monthly_budget,
        "target_roas": sku.target_roas,
        "client_id": client_id
    }
    return skus_db[sku_id]

@app.get("/api/v1/skus/", response_model=List[SKUResponse], tags=["SKUs"])
async def list_skus(client_id: str = "demo_client"):
    """List all SKUs for a client."""
    return [sku for sku in skus_db.values() if sku["client_id"] == client_id]

# Campaign endpoints
@app.post("/api/v1/campaigns/", response_model=CampaignResponse, tags=["Campaigns"])
async def create_campaign(campaign: CampaignCreate, client_id: str = "demo_client"):
    """Create a new campaign."""
    campaign_id = f"campaign_{len(campaigns_db) + 1}"
    campaigns_db[campaign_id] = {
        "id": campaign_id,
        "campaign_id": campaign.campaign_id,
        "name": campaign.name,
        "platform": campaign.platform,
        "platform_campaign_id": campaign.platform_campaign_id,
        "sku_id": campaign.sku_id,
        "daily_budget": campaign.daily_budget,
        "target_roas": campaign.target_roas,
        "client_id": client_id,
        "status": "active"
    }
    return campaigns_db[campaign_id]

@app.get("/api/v1/campaigns/", response_model=List[CampaignResponse], tags=["Campaigns"])
async def list_campaigns(client_id: str = "demo_client"):
    """List all campaigns for a client."""
    return [campaign for campaign in campaigns_db.values() if campaign["client_id"] == client_id]

# Intelligence endpoints
@app.get("/api/v1/intelligence/recommendations/{campaign_id}", tags=["Intelligence"])
async def get_recommendations(campaign_id: str):
    """Get optimization recommendations for a campaign."""
    return {
        "campaign_id": campaign_id,
        "recommendations": [
            {
                "type": "budget_adjustment",
                "action": "increase",
                "percentage": 15,
                "reason": "High ROAS performance detected"
            },
            {
                "type": "bid_optimization",
                "action": "adjust",
                "target_cpa": 25.0,
                "reason": "Optimize for better conversion rates"
            }
        ],
        "mode": "EXPLOIT",
        "confidence": 0.85
    }

@app.post("/api/v1/intelligence/optimize/campaigns/{campaign_id}", tags=["Intelligence"])
async def optimize_campaign(campaign_id: str, apply: bool = False):
    """Run optimization for a campaign."""
    return {
        "campaign_id": campaign_id,
        "optimization_applied": apply,
        "changes": [
            {
                "type": "budget",
                "old_value": 100.0,
                "new_value": 115.0,
                "change_percentage": 15
            }
        ],
        "expected_improvement": {
            "roas": 0.2,
            "conversions": 0.15
        }
    }

# Metrics endpoints
@app.get("/api/v1/metrics/campaigns/{campaign_id}", tags=["Metrics"])
async def get_campaign_metrics(campaign_id: str):
    """Get performance metrics for a campaign."""
    return {
        "campaign_id": campaign_id,
        "metrics": {
            "impressions": 15000,
            "clicks": 450,
            "conversions": 25,
            "spend": 125.50,
            "roas": 3.2,
            "cpa": 5.02,
            "ctr": 0.03,
            "conversion_rate": 0.056
        },
        "period": "last_7_days",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    print("🚀 Starting IPOP Media Buying Management System (Demo Version)")
    print("📊 Available endpoints:")
    print("  - http://localhost:8000/ (root)")
    print("  - http://localhost:8000/health (health check)")
    print("  - http://localhost:8000/docs (API documentation)")
    print("  - http://localhost:8000/redoc (alternative docs)")
    print("\n🔑 Demo API endpoints:")
    print("  - POST /api/v1/auth/register (register client)")
    print("  - POST /api/v1/skus/ (create SKU)")
    print("  - POST /api/v1/campaigns/ (create campaign)")
    print("  - GET /api/v1/intelligence/recommendations/{campaign_id}")
    print("  - POST /api/v1/intelligence/optimize/campaigns/{campaign_id}")
    print("\n💡 This is a demo version with in-memory storage")
    print("   No database connection required!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
