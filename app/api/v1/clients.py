"""
Client management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.client import ClientUpdate, ClientResponse

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/me", response_model=ClientResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current client's profile."""
    client_doc = await db.clients.find_one({"client_id": current_user["client_id"]})
    
    if not client_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return ClientResponse(**client_doc)


@router.put("/me", response_model=ClientResponse)
async def update_my_profile(
    updates: ClientUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update current client's profile."""
    update_data = updates.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Check if email is being changed
    if "email" in update_data:
        existing = await db.clients.find_one({
            "email": update_data["email"],
            "client_id": {"$ne": current_user["client_id"]}
        })
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Update client
    result = await db.clients.update_one(
        {"client_id": current_user["client_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found or no changes made"
        )
    
    # Fetch updated client
    updated_doc = await db.clients.find_one({"client_id": current_user["client_id"]})
    
    logger.info("client_updated", client_id=current_user["client_id"])
    
    return ClientResponse(**updated_doc)
