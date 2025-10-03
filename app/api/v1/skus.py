"""
SKU management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.sku import (
    SKUCreate,
    SKUUpdate,
    SKUResponse,
    SKUInDB,
    SKUList,
    SKUStatus
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/", response_model=SKUResponse, status_code=status.HTTP_201_CREATED)
async def create_sku(
    sku_data: SKUCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new SKU for product-level campaign management."""
    client_id = current_user["client_id"]
    
    # Check if SKU ID already exists for this client
    existing = await db.skus.find_one({
        "client_id": client_id,
        "sku_id": sku_data.sku_id
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SKU ID '{sku_data.sku_id}' already exists for this client"
        )
    
    # Create SKU document
    sku = SKUInDB(
        client_id=client_id,
        **sku_data.dict()
    )
    
    # Insert into database
    result = await db.skus.insert_one(
        sku.dict(by_alias=True, exclude={"id"})
    )
    sku.id = result.inserted_id
    
    logger.info("sku_created", client_id=client_id, sku_id=sku_data.sku_id)
    
    return SKUResponse(**sku.dict())


@router.get("/", response_model=SKUList)
async def list_skus(
    status_filter: Optional[SKUStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all SKUs for the current client."""
    client_id = current_user["client_id"]
    
    # Build query
    query = {"client_id": client_id}
    if status_filter:
        query["status"] = status_filter.value
    
    # Get total count
    total = await db.skus.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * page_size
    cursor = db.skus.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    skus = await cursor.to_list(length=page_size)
    
    items = [SKUResponse(**sku) for sku in skus]
    has_more = (skip + len(items)) < total
    
    return SKUList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.get("/{sku_id}", response_model=SKUResponse)
async def get_sku(
    sku_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific SKU by ID."""
    client_id = current_user["client_id"]
    
    sku_doc = await db.skus.find_one({
        "client_id": client_id,
        "sku_id": sku_id
    })
    
    if not sku_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU not found"
        )
    
    return SKUResponse(**sku_doc)


@router.put("/{sku_id}", response_model=SKUResponse)
async def update_sku(
    sku_id: str,
    updates: SKUUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a SKU."""
    client_id = current_user["client_id"]
    
    update_data = updates.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update SKU
    result = await db.skus.update_one(
        {"client_id": client_id, "sku_id": sku_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU not found"
        )
    
    # Fetch updated SKU
    updated_doc = await db.skus.find_one({
        "client_id": client_id,
        "sku_id": sku_id
    })
    
    logger.info("sku_updated", client_id=client_id, sku_id=sku_id)
    
    return SKUResponse(**updated_doc)


@router.delete("/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sku(
    sku_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Delete (archive) a SKU.
    
    Note: This doesn't delete campaigns, it archives the SKU.
    """
    client_id = current_user["client_id"]
    
    # Archive instead of delete
    result = await db.skus.update_one(
        {"client_id": client_id, "sku_id": sku_id},
        {"$set": {"status": SKUStatus.ARCHIVED.value, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU not found"
        )
    
    logger.info("sku_archived", client_id=client_id, sku_id=sku_id)
