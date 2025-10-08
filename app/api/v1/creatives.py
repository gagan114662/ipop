"""
Creative management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Optional, List
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.mediabuying.manager import handle_new_creative
from app.models.creative import (
    CreativeCreate,
    CreativeUpdate,
    CreativeResponse,
    CreativeList,
    CreativeInDB,
    CreativeStatus,
    CreativeType,
    CreativePerformance,
    CreativeComparison,
    CreativeComparisonResponse
)
from app.models.creative_metrics import (
    CreativeMetricsResponse,
    CreativeMetricsTimeseries,
    CreativeMetricsSummary
)
from app.models.campaign import Platform

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/", response_model=CreativeResponse, status_code=status.HTTP_201_CREATED)
async def create_creative(
    creative_data: CreativeCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Create a new creative asset.

    If no campaign_id is provided, this will trigger the automated
    media buying workflow to create a new campaign and A/B test.
    """
    client_id = current_user["client_id"]

    # Check if creative ID already exists for this client
    existing = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_data.creative_id
    })

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Creative ID '{creative_data.creative_id}' already exists"
        )

    # If campaign_id provided, verify it exists
    if creative_data.campaign_id:
        campaign = await db.campaigns.find_one({
            "client_id": client_id,
            "campaign_id": creative_data.campaign_id
        })
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

    # Create creative document
    creative = CreativeInDB(
        client_id=client_id,
        **creative_data.dict(exclude={"campaign_id"})
    )

    # Add to campaign_ids if provided
    if creative_data.campaign_id:
        creative.campaign_ids = [creative_data.campaign_id]

    # Insert into database
    result = await db.creatives.insert_one(
        creative.dict(by_alias=True, exclude={"id"})
    )
    creative.id = result.inserted_id

    logger.info(
        "creative_created",
        client_id=client_id,
        creative_id=creative_data.creative_id,
        creative_type=creative_data.creative_type.value,
        platform=creative_data.platform.value
    )

    # If no campaign is assigned, trigger the automated workflow
    if not creative_data.campaign_id:
        background_tasks.add_task(handle_new_creative, creative, client_id, db)
        logger.info(
            "triggered_media_buying_automation",
            client_id=client_id,
            creative_id=creative.creative_id
        )

    return CreativeResponse(**creative.dict())


@router.get("/", response_model=CreativeList)
async def list_creatives(
    campaign_id: Optional[str] = Query(None, description="Filter by campaign"),
    platform: Optional[Platform] = Query(None, description="Filter by platform"),
    creative_type: Optional[CreativeType] = Query(None, description="Filter by type"),
    status_filter: Optional[CreativeStatus] = Query(None, description="Filter by status"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all creatives for the current client with optional filters."""
    client_id = current_user["client_id"]

    # Build query
    query = {"client_id": client_id}

    if campaign_id:
        query["campaign_ids"] = campaign_id
    if platform:
        query["platform"] = platform.value
    if creative_type:
        query["creative_type"] = creative_type.value
    if status_filter:
        query["status"] = status_filter.value
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query["tags"] = {"$in": tag_list}

    # Count total
    total = await db.creatives.count_documents(query)

    # Fetch paginated results
    skip = (page - 1) * page_size
    cursor = db.creatives.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    creatives = await cursor.to_list(length=page_size)

    # Convert to response models
    creative_responses = [
        CreativeResponse(**{**creative, "id": str(creative["_id"])})
        for creative in creatives
    ]

    total_pages = (total + page_size - 1) // page_size

    return CreativeList(
        creatives=creative_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{creative_id}", response_model=CreativeResponse)
async def get_creative(
    creative_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific creative by ID."""
    client_id = current_user["client_id"]

    creative = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )

    return CreativeResponse(**{**creative, "id": str(creative["_id"])})


@router.put("/{creative_id}", response_model=CreativeResponse)
async def update_creative(
    creative_id: str,
    update_data: CreativeUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a creative."""
    client_id = current_user["client_id"]

    # Verify creative exists
    creative = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )

    # Prepare update
    update_dict = update_data.dict(exclude_unset=True)
    if update_dict:
        update_dict["updated_at"] = datetime.utcnow()

        # Update in database
        await db.creatives.update_one(
            {"client_id": client_id, "creative_id": creative_id},
            {"$set": update_dict}
        )

        logger.info(
            "creative_updated",
            client_id=client_id,
            creative_id=creative_id,
            fields_updated=list(update_dict.keys())
        )

    # Fetch updated creative
    updated = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    return CreativeResponse(**{**updated, "id": str(updated["_id"])})


@router.patch("/{creative_id}/status", response_model=CreativeResponse)
async def update_creative_status(
    creative_id: str,
    new_status: CreativeStatus,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update creative status (activate, pause, archive)."""
    client_id = current_user["client_id"]

    # Verify creative exists
    creative = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )

    # Update status
    update_dict = {
        "status": new_status.value,
        "updated_at": datetime.utcnow()
    }

    # Set status-specific timestamps
    if new_status == CreativeStatus.ACTIVE:
        if not creative.get("first_seen_at"):
            update_dict["first_seen_at"] = datetime.utcnow()
        update_dict["last_active_at"] = datetime.utcnow()
    elif new_status == CreativeStatus.PAUSED:
        update_dict["paused_at"] = datetime.utcnow()
    elif new_status == CreativeStatus.ARCHIVED:
        update_dict["archived_at"] = datetime.utcnow()

    await db.creatives.update_one(
        {"client_id": client_id, "creative_id": creative_id},
        {"$set": update_dict}
    )

    logger.info(
        "creative_status_updated",
        client_id=client_id,
        creative_id=creative_id,
        old_status=creative.get("status"),
        new_status=new_status.value
    )

    # Fetch updated creative
    updated = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    return CreativeResponse(**{**updated, "id": str(updated["_id"])})


@router.delete("/{creative_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_creative(
    creative_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Archive a creative (soft delete)."""
    client_id = current_user["client_id"]

    # Verify creative exists
    creative = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )

    # Archive instead of delete
    await db.creatives.update_one(
        {"client_id": client_id, "creative_id": creative_id},
        {"$set": {
            "status": CreativeStatus.ARCHIVED.value,
            "archived_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }}
    )

    logger.info(
        "creative_archived",
        client_id=client_id,
        creative_id=creative_id
    )


@router.get("/{creative_id}/metrics", response_model=CreativeMetricsResponse)
async def get_creative_metrics(
    creative_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current performance metrics for a creative."""
    client_id = current_user["client_id"]

    # Verify creative exists
    creative = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )

    # Return current performance from creative document
    performance = creative.get("current_performance", {})

    return CreativeMetricsResponse(
        creative_id=creative_id,
        campaign_id=creative.get("campaign_ids", [""])[0] if creative.get("campaign_ids") else "",
        platform=creative["platform"],
        date=datetime.utcnow(),
        aggregation_period="current",
        **performance
    )


@router.get("/{creative_id}/metrics/timeseries", response_model=CreativeMetricsTimeseries)
async def get_creative_metrics_timeseries(
    creative_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get time-series performance metrics for a creative."""
    client_id = current_user["client_id"]

    # Verify creative exists
    creative = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )

    # Default date range: last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Fetch metrics from creative_metrics collection
    query = {
        "client_id": client_id,
        "creative_id": creative_id,
        "date": {"$gte": start_date, "$lte": end_date}
    }

    cursor = db.creative_metrics.find(query).sort("date", 1)
    metrics = await cursor.to_list(length=1000)

    data_points = [
        CreativeMetricsResponse(**{**m, "id": str(m["_id"])})
        for m in metrics
    ]

    return CreativeMetricsTimeseries(
        creative_id=creative_id,
        campaign_id=creative.get("campaign_ids", [""])[0] if creative.get("campaign_ids") else "",
        start_date=start_date,
        end_date=end_date,
        data_points=data_points,
        total_points=len(data_points)
    )


@router.get("/{creative_id}/metrics/summary", response_model=CreativeMetricsSummary)
async def get_creative_metrics_summary(
    creative_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get aggregated performance summary for a creative."""
    client_id = current_user["client_id"]

    # Verify creative exists
    creative = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Fetch metrics
    query = {
        "client_id": client_id,
        "creative_id": creative_id,
        "date": {"$gte": start_date, "$lte": end_date}
    }

    cursor = db.creative_metrics.find(query).sort("date", 1)
    metrics = await cursor.to_list(length=1000)

    if not metrics:
        # Return empty summary
        return CreativeMetricsSummary(
            creative_id=creative_id,
            campaign_id=creative.get("campaign_ids", [""])[0] if creative.get("campaign_ids") else "",
            period_start=start_date,
            period_end=end_date,
            days_active=0,
            total_impressions=0,
            total_clicks=0,
            total_conversions=0,
            total_spend=0.0,
            total_revenue=0.0,
            avg_ctr=0.0,
            avg_cpc=0.0,
            avg_cpa=0.0,
            avg_roas=0.0,
            avg_engagement_rate=0.0,
            ctr_trend="stable",
            roas_trend="stable",
            spend_trend="stable",
            best_roas=0.0,
            worst_roas=0.0
        )

    # Calculate totals
    total_impressions = sum(m.get("impressions", 0) for m in metrics)
    total_clicks = sum(m.get("clicks", 0) for m in metrics)
    total_conversions = sum(m.get("conversions", 0) for m in metrics)
    total_spend = sum(m.get("spend", 0.0) for m in metrics)
    total_revenue = sum(m.get("revenue", 0.0) for m in metrics)

    # Calculate averages
    avg_ctr = sum(m.get("ctr", 0.0) for m in metrics) / len(metrics) if metrics else 0
    avg_cpc = sum(m.get("cpc", 0.0) for m in metrics) / len(metrics) if metrics else 0
    avg_cpa = sum(m.get("cpa", 0.0) for m in metrics) / len(metrics) if metrics else 0
    avg_roas = sum(m.get("roas", 0.0) for m in metrics) / len(metrics) if metrics else 0
    avg_engagement = sum(m.get("engagement_rate", 0.0) for m in metrics) / len(metrics) if metrics else 0

    # Analyze trends (simple: compare first half vs second half)
    mid_point = len(metrics) // 2
    if mid_point > 0:
        first_half_ctr = sum(m.get("ctr", 0.0) for m in metrics[:mid_point]) / mid_point
        second_half_ctr = sum(m.get("ctr", 0.0) for m in metrics[mid_point:]) / (len(metrics) - mid_point)

        if second_half_ctr > first_half_ctr * 1.1:
            ctr_trend = "increasing"
        elif second_half_ctr < first_half_ctr * 0.9:
            ctr_trend = "decreasing"
        else:
            ctr_trend = "stable"

        first_half_roas = sum(m.get("roas", 0.0) for m in metrics[:mid_point]) / mid_point
        second_half_roas = sum(m.get("roas", 0.0) for m in metrics[mid_point:]) / (len(metrics) - mid_point)

        if second_half_roas > first_half_roas * 1.1:
            roas_trend = "increasing"
        elif second_half_roas < first_half_roas * 0.9:
            roas_trend = "decreasing"
        else:
            roas_trend = "stable"
    else:
        ctr_trend = "stable"
        roas_trend = "stable"

    # Find best/worst days
    roas_values = [m.get("roas", 0.0) for m in metrics if m.get("roas", 0) > 0]
    best_roas = max(roas_values) if roas_values else 0.0
    worst_roas = min(roas_values) if roas_values else 0.0

    # Detect fatigue (CTR declining)
    is_fatigued = ctr_trend == "decreasing" and avg_ctr > 0
    fatigue_score = 0.0
    if is_fatigued:
        # Simple fatigue score: how much CTR has declined
        if mid_point > 0:
            decline_pct = ((first_half_ctr - second_half_ctr) / first_half_ctr * 100) if first_half_ctr > 0 else 0
            fatigue_score = min(decline_pct * 2, 100.0)  # Scale to 0-100

    recommendation = None
    if is_fatigued:
        if fatigue_score > 70:
            recommendation = "High fatigue detected. Consider pausing and creating a new variant."
        elif fatigue_score > 40:
            recommendation = "Moderate fatigue detected. Consider refreshing creative or testing a new variant."
    elif avg_roas < creative.get("min_roas", 0):
        recommendation = f"ROAS ({avg_roas:.2f}) below minimum threshold ({creative.get('min_roas')}). Consider pausing."
    elif avg_ctr < creative.get("min_ctr", 0):
        recommendation = f"CTR ({avg_ctr:.2f}%) below minimum threshold ({creative.get('min_ctr')}%). Consider pausing."

    return CreativeMetricsSummary(
        creative_id=creative_id,
        campaign_id=creative.get("campaign_ids", [""])[0] if creative.get("campaign_ids") else "",
        period_start=start_date,
        period_end=end_date,
        days_active=len(metrics),
        total_impressions=total_impressions,
        total_clicks=total_clicks,
        total_conversions=total_conversions,
        total_spend=total_spend,
        total_revenue=total_revenue,
        avg_ctr=round(avg_ctr, 2),
        avg_cpc=round(avg_cpc, 2),
        avg_cpa=round(avg_cpa, 2),
        avg_roas=round(avg_roas, 2),
        avg_engagement_rate=round(avg_engagement, 2),
        ctr_trend=ctr_trend,
        roas_trend=roas_trend,
        spend_trend="stable",  # TODO: Implement spend trend
        best_roas=round(best_roas, 2),
        worst_roas=round(worst_roas, 2),
        is_fatigued=is_fatigued,
        fatigue_score=round(fatigue_score, 2),
        recommendation=recommendation
    )


@router.get("/top-performers", response_model=List[CreativeResponse])
async def get_top_performing_creatives(
    metric: str = Query("roas", description="Metric to rank by"),
    limit: int = Query(10, ge=1, le=100, description="Number of creatives to return"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get top performing creatives ranked by specified metric."""
    client_id = current_user["client_id"]

    # Map metric to database field
    metric_map = {
        "roas": "current_performance.roas",
        "ctr": "current_performance.ctr",
        "conversions": "current_performance.conversions",
        "revenue": "current_performance.revenue"
    }

    sort_field = metric_map.get(metric, "current_performance.roas")

    # Fetch top performers
    cursor = db.creatives.find({
        "client_id": client_id,
        "status": {"$ne": "archived"}
    }).sort(sort_field, -1).limit(limit)

    creatives = await cursor.to_list(length=limit)

    return [
        CreativeResponse(**{**creative, "id": str(creative["_id"])})
        for creative in creatives
    ]


@router.post("/compare")
async def compare_creatives(
    request_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Compare performance of multiple creatives."""
    client_id = current_user["client_id"]
    creative_ids = request_data.get("creative_ids", [])

    if not creative_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="creative_ids list is required"
        )

    # Fetch creatives
    cursor = db.creatives.find({
        "client_id": client_id,
        "creative_id": {"$in": creative_ids}
    })

    creatives = await cursor.to_list(length=100)

    if not creatives:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No creatives found"
        )

    comparison = []
    for creative in creatives:
        perf = creative.get("current_performance", {})
        comparison.append({
            "creative_id": creative["creative_id"],
            "name": creative["name"],
            "impressions": perf.get("impressions", 0),
            "clicks": perf.get("clicks", 0),
            "conversions": perf.get("conversions", 0),
            "spend": perf.get("spend", 0.0),
            "revenue": perf.get("revenue", 0.0),
            "ctr": perf.get("ctr", 0.0),
            "cpc": perf.get("cpc", 0.0),
            "cpa": perf.get("cpa", 0.0),
            "roas": perf.get("roas", 0.0)
        })

    return {"comparison": comparison}


@router.post("/bulk-update")
async def bulk_update_creatives(
    request_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Bulk update multiple creatives."""
    client_id = current_user["client_id"]
    creative_ids = request_data.get("creative_ids", [])
    updates = request_data.get("updates", {})

    if not creative_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="creative_ids list is required"
        )

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="updates dict is required"
        )

    # Add updated_at timestamp
    updates["updated_at"] = datetime.utcnow()

    # Perform bulk update
    result = await db.creatives.update_many(
        {
            "client_id": client_id,
            "creative_id": {"$in": creative_ids}
        },
        {"$set": updates}
    )

    logger.info(
        "creatives_bulk_updated",
        client_id=client_id,
        count=result.modified_count,
        updates=list(updates.keys())
    )

    return {
        "success": True,
        "modified_count": result.modified_count,
        "creative_ids": creative_ids
    }
