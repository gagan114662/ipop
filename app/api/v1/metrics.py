"""
Performance metrics API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Optional
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.metrics import (
    PerformanceMetricsResponse,
    MetricsSummary,
    CampaignBurnRate,
    SKUBurnRate
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/campaigns/{campaign_id}", response_model=list[PerformanceMetricsResponse])
async def get_campaign_metrics(
    campaign_id: str,
    hours: int = Query(24, ge=1, le=720, description="Hours to look back"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get performance metrics for a specific campaign."""
    client_id = current_user["client_id"]
    
    # Verify campaign belongs to client
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Get metrics
    since = datetime.utcnow() - timedelta(hours=hours)
    cursor = db.performance_metrics.find({
        "client_id": client_id,
        "campaign_id": campaign_id,
        "timestamp": {"$gte": since}
    }).sort("timestamp", -1)
    
    metrics = await cursor.to_list(length=1000)
    
    return [PerformanceMetricsResponse(**m) for m in metrics]


@router.get("/campaigns/{campaign_id}/summary", response_model=MetricsSummary)
async def get_campaign_summary(
    campaign_id: str,
    hours: int = Query(24, ge=1, le=720, description="Hours to look back"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get aggregated performance summary for a campaign."""
    client_id = current_user["client_id"]
    
    # Verify campaign belongs to client
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Aggregate metrics
    since = datetime.utcnow() - timedelta(hours=hours)
    pipeline = [
        {
            "$match": {
                "client_id": client_id,
                "campaign_id": campaign_id,
                "timestamp": {"$gte": since}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_impressions": {"$sum": "$impressions"},
                "total_clicks": {"$sum": "$clicks"},
                "total_conversions": {"$sum": "$conversions"},
                "total_spend": {"$sum": "$spend"},
                "total_revenue": {"$sum": "$revenue"},
                "avg_ctr": {"$avg": "$ctr"},
                "avg_cpc": {"$avg": "$cpc"},
                "avg_cpa": {"$avg": "$cpa"},
                "avg_cvr": {"$avg": "$cvr"},
                "avg_roas": {"$avg": "$roas"}
            }
        }
    ]
    
    cursor = db.performance_metrics.aggregate(pipeline)
    results = await cursor.to_list(length=1)
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics found for this period"
        )
    
    result = results[0]
    
    return MetricsSummary(
        total_impressions=result.get("total_impressions", 0),
        total_clicks=result.get("total_clicks", 0),
        total_conversions=result.get("total_conversions", 0),
        total_spend=result.get("total_spend", 0.0),
        total_revenue=result.get("total_revenue", 0.0),
        avg_ctr=result.get("avg_ctr", 0.0),
        avg_cpc=result.get("avg_cpc", 0.0),
        avg_cpa=result.get("avg_cpa", 0.0),
        avg_cvr=result.get("avg_cvr", 0.0),
        avg_roas=result.get("avg_roas", 0.0),
        period_start=since,
        period_end=datetime.utcnow()
    )


@router.get("/burn-rate/campaigns/{campaign_id}", response_model=CampaignBurnRate)
async def get_campaign_burn_rate(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get budget burn rate for a campaign."""
    client_id = current_user["client_id"]
    
    # Get campaign
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Get today's spend
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    pipeline = [
        {
            "$match": {
                "client_id": client_id,
                "campaign_id": campaign_id,
                "timestamp": {"$gte": today_start}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_spend": {"$sum": "$spend"}
            }
        }
    ]
    
    cursor = db.performance_metrics.aggregate(pipeline)
    results = await cursor.to_list(length=1)
    
    current_spend = results[0].get("total_spend", 0.0) if results else 0.0
    daily_budget = campaign.get("daily_budget", 0.0)
    
    # Calculate burn rate
    burn_rate_pct = (current_spend / daily_budget * 100) if daily_budget > 0 else 0
    
    # Determine status
    if burn_rate_pct < 80:
        status_str = "on_track"
    elif burn_rate_pct < 95:
        status_str = "on_track"
    elif burn_rate_pct < 105:
        status_str = "on_track"
    else:
        status_str = "over_spending"
    
    # Calculate projected end time
    now = datetime.utcnow()
    hours_passed = (now - today_start).total_seconds() / 3600
    
    if current_spend > 0 and hours_passed > 0:
        spend_rate = current_spend / hours_passed
        hours_remaining = (daily_budget - current_spend) / spend_rate if spend_rate > 0 else None
        projected_end = now + timedelta(hours=hours_remaining) if hours_remaining and hours_remaining > 0 else None
    else:
        hours_remaining = None
        projected_end = None
    
    return CampaignBurnRate(
        campaign_id=campaign_id,
        daily_budget=daily_budget,
        current_spend_today=current_spend,
        burn_rate_percent=round(burn_rate_pct, 2),
        projected_end_time=projected_end,
        hours_remaining=hours_remaining,
        status=status_str,
        recommendation=f"Budget is being spent at a {'normal' if status_str == 'on_track' else 'high'} rate"
    )


@router.get("/burn-rate/skus/{sku_id}", response_model=SKUBurnRate)
async def get_sku_burn_rate(
    sku_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get budget burn rate for all campaigns under a SKU."""
    client_id = current_user["client_id"]
    
    # Get SKU
    sku = await db.skus.find_one({
        "client_id": client_id,
        "sku_id": sku_id
    })
    
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU not found"
        )
    
    # Get all campaigns for this SKU
    campaigns_cursor = db.campaigns.find({
        "client_id": client_id,
        "sku_id": sku_id,
        "status": "active"
    })
    campaigns = await campaigns_cursor.to_list(length=100)
    
    # Get burn rate for each campaign
    campaign_burn_rates = []
    total_spend = 0.0
    
    for campaign in campaigns:
        burn_rate = await get_campaign_burn_rate(
            campaign["campaign_id"],
            current_user,
            db
        )
        campaign_burn_rates.append(burn_rate)
        total_spend += burn_rate.current_spend_today
    
    daily_budget = sku.get("daily_budget", 0.0)
    burn_rate_pct = (total_spend / daily_budget * 100) if daily_budget > 0 else 0
    
    # Determine overall status
    if burn_rate_pct < 85:
        status_str = "on_track"
    elif burn_rate_pct < 100:
        status_str = "on_track"
    else:
        status_str = "over_spending"
    
    return SKUBurnRate(
        sku_id=sku_id,
        daily_budget=daily_budget,
        current_spend_today=total_spend,
        burn_rate_percent=round(burn_rate_pct, 2),
        campaigns=campaign_burn_rates,
        status=status_str
    )
