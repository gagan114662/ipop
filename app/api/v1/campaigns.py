"""
Campaign management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignInDB,
    CampaignList,
    CampaignStatus,
    Platform
)
from app.models.creative import CreativeResponse

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new advertising campaign."""
    client_id = current_user["client_id"]
    
    # Verify SKU exists and belongs to client
    sku_doc = await db.skus.find_one({
        "client_id": client_id,
        "sku_id": campaign_data.sku_id
    })
    
    if not sku_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU not found"
        )
    
    # Check if campaign ID already exists for this client
    existing = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_data.campaign_id
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campaign ID '{campaign_data.campaign_id}' already exists"
        )
    
    # Create campaign document
    campaign = CampaignInDB(
        client_id=client_id,
        **campaign_data.dict()
    )
    
    # Insert into database
    result = await db.campaigns.insert_one(
        campaign.dict(by_alias=True, exclude={"id"})
    )
    campaign.id = result.inserted_id
    
    logger.info(
        "campaign_created",
        client_id=client_id,
        campaign_id=campaign_data.campaign_id,
        platform=campaign_data.platform.value
    )
    
    return CampaignResponse(**campaign.dict())


@router.get("/", response_model=CampaignList)
async def list_campaigns(
    sku_id: Optional[str] = Query(None, description="Filter by SKU"),
    platform: Optional[Platform] = Query(None, description="Filter by platform"),
    status_filter: Optional[CampaignStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all campaigns for the current client."""
    client_id = current_user["client_id"]
    
    # Build query
    query = {"client_id": client_id}
    if sku_id:
        query["sku_id"] = sku_id
    if platform:
        query["platform"] = platform.value
    if status_filter:
        query["status"] = status_filter.value
    
    # Get total count
    total = await db.campaigns.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * page_size
    cursor = db.campaigns.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    campaigns = await cursor.to_list(length=page_size)
    
    items = [CampaignResponse(**campaign) for campaign in campaigns]
    has_more = (skip + len(items)) < total
    
    return CampaignList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific campaign by ID."""
    client_id = current_user["client_id"]
    
    campaign_doc = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })
    
    if not campaign_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignResponse(**campaign_doc)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    updates: CampaignUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a campaign."""
    client_id = current_user["client_id"]
    
    update_data = updates.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update campaign age if needed
    campaign_doc = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })
    
    if campaign_doc:
        created_at = campaign_doc.get("created_at")
        if created_at:
            campaign_age = datetime.utcnow() - created_at
            update_data["campaign_age_days"] = campaign_age.days
    
    # Update campaign
    result = await db.campaigns.update_one(
        {"client_id": client_id, "campaign_id": campaign_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Fetch updated campaign
    updated_doc = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })
    
    logger.info("campaign_updated", client_id=client_id, campaign_id=campaign_id)
    
    return CampaignResponse(**updated_doc)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Delete (archive) a campaign.
    """
    client_id = current_user["client_id"]
    
    # Archive instead of delete
    result = await db.campaigns.update_one(
        {"client_id": client_id, "campaign_id": campaign_id},
        {"$set": {
            "status": CampaignStatus.ARCHIVED.value,
            "updated_at": datetime.utcnow()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    logger.info("campaign_archived", client_id=client_id, campaign_id=campaign_id)


# Creative management endpoints

@router.post("/{campaign_id}/creatives", response_model=CampaignResponse)
async def link_creative_to_campaign(
    campaign_id: str,
    creative_id: str = Query(..., description="Creative ID to link"),
    set_as_primary: bool = Query(False, description="Set as primary creative"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Link a creative to a campaign.

    Adds the creative_id to the campaign's creative_ids array.
    Optionally sets it as the primary creative.
    """
    client_id = current_user["client_id"]

    # Verify campaign exists
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })

    if not campaign:
        raise HTTPException(404, "Campaign not found")

    # Verify creative exists and belongs to client
    creative = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    if not creative:
        raise HTTPException(404, f"Creative '{creative_id}' not found")

    # Check if already linked
    if creative_id in campaign.get("creative_ids", []):
        raise HTTPException(400, f"Creative '{creative_id}' already linked to campaign")

    # Update campaign
    update_data = {
        "$addToSet": {"creative_ids": creative_id},
        "$set": {"updated_at": datetime.utcnow()}
    }

    if set_as_primary:
        update_data["$set"]["primary_creative_id"] = creative_id

    await db.campaigns.update_one(
        {"client_id": client_id, "campaign_id": campaign_id},
        update_data
    )

    # Update creative's campaign_ids
    await db.creatives.update_one(
        {"client_id": client_id, "creative_id": creative_id},
        {
            "$addToSet": {"campaign_ids": campaign_id},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

    logger.info(
        "creative_linked_to_campaign",
        client_id=client_id,
        campaign_id=campaign_id,
        creative_id=creative_id,
        set_as_primary=set_as_primary,
    )

    # Fetch updated campaign
    updated = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })

    return CampaignResponse(**updated)


@router.delete("/{campaign_id}/creatives/{creative_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_creative_from_campaign(
    campaign_id: str,
    creative_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Unlink a creative from a campaign.

    Removes the creative_id from the campaign's creative_ids array.
    If it was the primary creative, clears primary_creative_id.
    """
    client_id = current_user["client_id"]

    # Verify campaign exists
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })

    if not campaign:
        raise HTTPException(404, "Campaign not found")

    # Check if creative is linked
    if creative_id not in campaign.get("creative_ids", []):
        raise HTTPException(400, f"Creative '{creative_id}' not linked to campaign")

    # Update campaign
    update_data = {
        "$pull": {"creative_ids": creative_id},
        "$set": {"updated_at": datetime.utcnow()}
    }

    # Clear primary if this was the primary creative
    if campaign.get("primary_creative_id") == creative_id:
        update_data["$set"]["primary_creative_id"] = None

    await db.campaigns.update_one(
        {"client_id": client_id, "campaign_id": campaign_id},
        update_data
    )

    # Update creative's campaign_ids
    await db.creatives.update_one(
        {"client_id": client_id, "creative_id": creative_id},
        {
            "$pull": {"campaign_ids": campaign_id},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

    logger.info(
        "creative_unlinked_from_campaign",
        client_id=client_id,
        campaign_id=campaign_id,
        creative_id=creative_id,
    )


@router.get("/{campaign_id}/creatives", response_model=list[CreativeResponse])
async def list_campaign_creatives(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    List all creatives linked to a campaign.
    """
    client_id = current_user["client_id"]

    # Verify campaign exists
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })

    if not campaign:
        raise HTTPException(404, "Campaign not found")

    creative_ids = campaign.get("creative_ids", [])

    if not creative_ids:
        return []

    # Fetch all linked creatives
    cursor = db.creatives.find({
        "client_id": client_id,
        "creative_id": {"$in": creative_ids}
    })

    creatives = await cursor.to_list(length=100)

    return [CreativeResponse(**creative) for creative in creatives]


@router.patch("/{campaign_id}/primary-creative", response_model=CampaignResponse)
async def set_primary_creative(
    campaign_id: str,
    creative_id: str = Query(..., description="Creative ID to set as primary"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Set the primary creative for a campaign.

    The creative must already be linked to the campaign.
    """
    client_id = current_user["client_id"]

    # Verify campaign exists
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })

    if not campaign:
        raise HTTPException(404, "Campaign not found")

    # Check if creative is linked
    if creative_id not in campaign.get("creative_ids", []):
        raise HTTPException(
            400,
            f"Creative '{creative_id}' must be linked to campaign before setting as primary"
        )

    # Update campaign
    await db.campaigns.update_one(
        {"client_id": client_id, "campaign_id": campaign_id},
        {
            "$set": {
                "primary_creative_id": creative_id,
                "updated_at": datetime.utcnow()
            }
        }
    )

    logger.info(
        "primary_creative_set",
        client_id=client_id,
        campaign_id=campaign_id,
        creative_id=creative_id,
    )

    # Fetch updated campaign
    updated = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })

    return CampaignResponse(**updated)


@router.get("/{campaign_id}/creatives/compare")
async def compare_campaign_creatives(
    campaign_id: str,
    days: int = Query(7, ge=1, le=90, description="Days to analyze"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Compare performance of all creatives in a campaign.

    Returns a comparison of key metrics for all linked creatives.
    """
    client_id = current_user["client_id"]

    # Verify campaign exists
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })

    if not campaign:
        raise HTTPException(404, "Campaign not found")

    creative_ids = campaign.get("creative_ids", [])

    if not creative_ids:
        return {
            "campaign_id": campaign_id,
            "days": days,
            "creatives": [],
            "best_ctr": None,
            "best_roas": None,
            "recommendation": "No creatives linked to campaign"
        }

    # Fetch all linked creatives
    creatives = await db.creatives.find({
        "client_id": client_id,
        "creative_id": {"$in": creative_ids}
    }).to_list(length=100)

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Aggregate metrics for each creative
    comparison = []

    for creative in creatives:
        # Get metrics from creative_metrics collection
        pipeline = [
            {
                "$match": {
                    "client_id": client_id,
                    "creative_id": creative["creative_id"],
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$creative_id",
                    "total_impressions": {"$sum": "$impressions"},
                    "total_clicks": {"$sum": "$clicks"},
                    "total_conversions": {"$sum": "$conversions"},
                    "total_spend": {"$sum": "$spend"},
                    "total_revenue": {"$sum": "$revenue"},
                }
            }
        ]

        result = await db.creative_metrics.aggregate(pipeline).to_list(length=1)

        if result:
            metrics = result[0]

            # Calculate rates
            ctr = (metrics["total_clicks"] / metrics["total_impressions"] * 100) if metrics["total_impressions"] > 0 else 0
            roas = (metrics["total_revenue"] / metrics["total_spend"]) if metrics["total_spend"] > 0 else 0
            cvr = (metrics["total_conversions"] / metrics["total_clicks"] * 100) if metrics["total_clicks"] > 0 else 0

            comparison.append({
                "creative_id": creative["creative_id"],
                "creative_name": creative["name"],
                "creative_type": creative["creative_type"],
                "status": creative["status"],
                "impressions": metrics["total_impressions"],
                "clicks": metrics["total_clicks"],
                "conversions": metrics["total_conversions"],
                "spend": metrics["total_spend"],
                "revenue": metrics["total_revenue"],
                "ctr": round(ctr, 2),
                "roas": round(roas, 2),
                "cvr": round(cvr, 2),
            })
        else:
            # No metrics yet
            comparison.append({
                "creative_id": creative["creative_id"],
                "creative_name": creative["name"],
                "creative_type": creative["creative_type"],
                "status": creative["status"],
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "spend": 0.0,
                "revenue": 0.0,
                "ctr": 0.0,
                "roas": 0.0,
                "cvr": 0.0,
            })

    # Find best performers
    best_ctr = max(comparison, key=lambda x: x["ctr"]) if comparison else None
    best_roas = max(comparison, key=lambda x: x["roas"]) if comparison else None

    # Generate recommendation
    recommendation = ""
    if best_roas and best_roas["roas"] > 0:
        recommendation = f"Consider setting '{best_roas['creative_name']}' as primary creative (ROAS: {best_roas['roas']})"
    elif best_ctr and best_ctr["ctr"] > 0:
        recommendation = f"'{best_ctr['creative_name']}' has best CTR ({best_ctr['ctr']}%), monitor for conversions"
    else:
        recommendation = "Insufficient data - continue running campaign to gather metrics"

    return {
        "campaign_id": campaign_id,
        "days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "creatives": comparison,
        "best_ctr": {
            "creative_id": best_ctr["creative_id"],
            "creative_name": best_ctr["creative_name"],
            "ctr": best_ctr["ctr"]
        } if best_ctr else None,
        "best_roas": {
            "creative_id": best_roas["creative_id"],
            "creative_name": best_roas["creative_name"],
            "roas": best_roas["roas"]
        } if best_roas else None,
        "recommendation": recommendation,
    }
