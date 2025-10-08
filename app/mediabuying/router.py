"""
API Endpoints for the Media Buying module.
"""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.mediabuying.schemas import MediaBuyingStatus
from app.models.campaign import CampaignStatus
from app.models.creative_test import TestStatus

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.get("/status", response_model=MediaBuyingStatus)
async def get_mediabuying_status(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get the status of the automated media buying process for the current client.
    """
    client_id = current_user["client_id"]

    # Count automated campaigns
    automated_campaigns_created = await db.campaigns.count_documents({
        "client_id": client_id,
        "campaign_id": {"$regex": "^auto-campaign-"}
    })

    # Count automated tests that are running
    automated_tests_running = await db.creative_tests.count_documents({
        "client_id": client_id,
        "test_id": {"$regex": "^auto-test-"},
        "status": TestStatus.RUNNING
    })

    return MediaBuyingStatus(
        client_id=client_id,
        automated_campaigns_created=automated_campaigns_created,
        automated_tests_running=automated_tests_running,
    )