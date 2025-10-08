"""
Core logic for the Media Buying module.
"""
import structlog
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import uuid

from app.models.campaign import CampaignInDB, CampaignStatus, OptimizationMode
from app.models.creative_test import CreativeTestInDB, TestStatus, TestType, TestMetric, TestVariant, WinnerSelectionMethod
from app.models.creative import CreativeInDB

logger = structlog.get_logger(__name__)

async def handle_new_creative(creative: CreativeInDB, client_id: str, db: AsyncIOMotorDatabase):
    """
    This function is called when a new creative is uploaded.
    It will automatically create a campaign and a creative test.
    """
    logger.info("Handling new creative", creative_id=creative.creative_id, client_id=client_id)

    # 1. Generate IDs
    campaign_id = f"auto-campaign-{uuid.uuid4().hex[:8]}"
    test_id = f"auto-test-{uuid.uuid4().hex[:8]}"

    # 2. Create a new campaign
    new_campaign = CampaignInDB(
        client_id=client_id,
        campaign_id=campaign_id,
        name=f"Auto Campaign for {creative.name}",
        platform=creative.platform,
        platform_campaign_id=f"p-{campaign_id}", # Placeholder
        daily_budget=50.0, # Default budget
        status=CampaignStatus.DRAFT,
        optimization_mode=OptimizationMode.EXPLORE,
        creative_ids=[creative.creative_id],
        sku_id="default-sku" # Placeholder, this might need more logic
    )

    await db.campaigns.insert_one(new_campaign.dict(by_alias=True))
    logger.info("Auto-created campaign", campaign_id=campaign_id, client_id=client_id)

    # 3. Create a new creative test
    variant = TestVariant(
        creative_id=creative.creative_id,
        variant_name="Variant A",
        is_control=False, # Not a control since it's the first one
        traffic_allocation=100.0
    )

    new_test = CreativeTestInDB(
        client_id=client_id,
        test_id=test_id,
        name=f"Auto Test for {creative.name}",
        campaign_id=campaign_id,
        test_type=TestType.AB_TEST,
        primary_metric=TestMetric.ROAS,
        variants=[variant],
        status=TestStatus.DRAFT,
        winner_selection=WinnerSelectionMethod.STATISTICAL_SIGNIFICANCE,
        auto_promote_winner=True,
        auto_pause_losers=True,
    )

    await db.creative_tests.insert_one(new_test.dict(by_alias=True))
    logger.info("Auto-created creative test", test_id=test_id, client_id=client_id)

    # 4. Link creative to campaign and test
    await db.creatives.update_one(
        {"_id": creative.id},
        {
            "$set": {
                "campaign_ids": [campaign_id],
                "test_id": test_id,
                "is_test_variant": True,
                "variant_name": "Variant A",
                "updated_at": datetime.utcnow()
            }
        }
    )
    logger.info("Linked creative to new campaign and test", creative_id=creative.creative_id)