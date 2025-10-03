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
