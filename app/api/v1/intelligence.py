"""
Intelligence and optimization API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.intelligence.decision_engine import DecisionEngine
from app.models.intelligence import (
    IntelligenceDecisionResponse,
    DecisionHistory,
    OptimizationRecommendation
)
from app.models.campaign import BudgetAdjustment

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/optimize/campaigns/{campaign_id}", response_model=IntelligenceDecisionResponse)
async def optimize_campaign(
    campaign_id: str,
    apply: bool = Query(False, description="Apply the optimization immediately"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Run intelligence optimization for a specific campaign.
    
    This endpoint analyzes campaign performance and makes budget optimization decisions
    based on the EXPLORE/EXPLOIT framework.
    """
    client_id = current_user["client_id"]
    
    # Verify campaign exists
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Run optimization
    engine = DecisionEngine(db)
    decision = await engine.optimize_campaign(campaign_id, client_id)
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to make optimization decision. Insufficient data."
        )
    
    # Apply decision if requested
    if apply:
        await _apply_decision(decision, db)
    
    return IntelligenceDecisionResponse(**decision.dict())


@router.post("/optimize/skus/{sku_id}", response_model=list[IntelligenceDecisionResponse])
async def optimize_sku_campaigns(
    sku_id: str,
    apply: bool = Query(False, description="Apply the optimizations immediately"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Run intelligence optimization for all campaigns under a SKU.
    """
    client_id = current_user["client_id"]
    
    # Verify SKU exists
    sku = await db.skus.find_one({
        "client_id": client_id,
        "sku_id": sku_id
    })
    
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU not found"
        )
    
    # Run optimization for all campaigns
    engine = DecisionEngine(db)
    decisions = await engine.optimize_all_campaigns(client_id, sku_id)
    
    # Apply decisions if requested
    if apply:
        for decision in decisions:
            await _apply_decision(decision, db)
    
    return [IntelligenceDecisionResponse(**d.dict()) for d in decisions]


@router.post("/optimize/all", response_model=list[IntelligenceDecisionResponse])
async def optimize_all_campaigns(
    apply: bool = Query(False, description="Apply the optimizations immediately"),
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Run intelligence optimization for all active campaigns.
    
    This is typically run hourly by the scheduler.
    """
    client_id = current_user["client_id"]
    
    # Run optimization for all campaigns
    engine = DecisionEngine(db)
    decisions = await engine.optimize_all_campaigns(client_id)
    
    logger.info(
        "bulk_optimization_completed",
        client_id=client_id,
        decisions_count=len(decisions)
    )
    
    # Apply decisions if requested
    if apply:
        for decision in decisions:
            await _apply_decision(decision, db)
    
    return [IntelligenceDecisionResponse(**d.dict()) for d in decisions]


@router.get("/recommendations/{campaign_id}", response_model=OptimizationRecommendation)
async def get_recommendations(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get optimization recommendations for a campaign without applying them.
    
    This is useful for previewing what the intelligence engine would recommend.
    """
    client_id = current_user["client_id"]
    
    # Verify campaign exists
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Get recommendations
    engine = DecisionEngine(db)
    recommendation = await engine.get_recommendations(campaign_id, client_id)
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to generate recommendation. Insufficient data."
        )
    
    return recommendation


@router.get("/history/{campaign_id}", response_model=DecisionHistory)
async def get_decision_history(
    campaign_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of decisions to return"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get historical intelligence decisions for a campaign.
    """
    client_id = current_user["client_id"]
    
    # Verify campaign exists
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": campaign_id
    })
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Get decision history
    cursor = db.intelligence_decisions.find({
        "client_id": client_id,
        "campaign_id": campaign_id
    }).sort("timestamp", -1).limit(limit)
    
    decisions = await cursor.to_list(length=limit)
    
    # Calculate success metrics
    total_decisions = len(decisions)
    successful_decisions = sum(1 for d in decisions if d.get("success_score", 0) >= 0.7)
    avg_success = sum(d.get("success_score", 0) for d in decisions if d.get("success_score")) / total_decisions if total_decisions > 0 else 0
    last_decision = decisions[0].get("timestamp") if decisions else None
    
    return DecisionHistory(
        campaign_id=campaign_id,
        decisions=[IntelligenceDecisionResponse(**d) for d in decisions],
        total_decisions=total_decisions,
        successful_decisions=successful_decisions,
        average_success_score=round(avg_success, 3),
        last_decision=last_decision
    )


async def _apply_decision(decision, db: AsyncIOMotorDatabase):
    """
    Apply an intelligence decision to a campaign.
    
    This updates the campaign budget and marks the decision as applied.
    If platform credentials are configured, it also pushes changes to the actual platform.
    """
    from datetime import datetime
    from app.models.intelligence import DecisionType
    from app.models.campaign import Platform
    from app.platforms.manager import PlatformManager
    
    platform_manager = PlatformManager()
    
    # Get campaign details
    campaign = await db.campaigns.find_one({
        "client_id": decision.client_id,
        "campaign_id": decision.campaign_id
    })
    
    if not campaign:
        logger.error("campaign_not_found", campaign_id=decision.campaign_id)
        return
    
    platform = Platform(campaign["platform"])
    platform_push_success = False
    
    # Try to push to platform if configured
    if platform_manager.is_platform_configured(platform):
        try:
            if decision.decision_type == DecisionType.BUDGET_INCREASE or \
               decision.decision_type == DecisionType.BUDGET_DECREASE:
                platform_push_success = await platform_manager.update_budget(
                    platform=platform,
                    campaign=campaign,
                    new_budget=decision.new_budget
                )
            
            elif decision.decision_type == DecisionType.PAUSE_CAMPAIGN:
                platform_push_success = await platform_manager.pause_campaign(
                    platform=platform,
                    campaign=campaign
                )
            
            elif decision.decision_type == DecisionType.ACTIVATE_CAMPAIGN:
                platform_push_success = await platform_manager.activate_campaign(
                    platform=platform,
                    campaign=campaign
                )
            
        except Exception as e:
            logger.error(
                "platform_push_failed",
                campaign_id=decision.campaign_id,
                error=str(e)
            )
    else:
        logger.info(
            "platform_not_configured_local_only",
            platform=platform.value,
            campaign_id=decision.campaign_id
        )
    
    # Always update local database
    if decision.decision_type == DecisionType.BUDGET_INCREASE or decision.decision_type == DecisionType.BUDGET_DECREASE:
        # Update campaign budget
        await db.campaigns.update_one(
            {
                "client_id": decision.client_id,
                "campaign_id": decision.campaign_id
            },
            {
                "$set": {
                    "daily_budget": decision.new_budget,
                    "updated_at": datetime.utcnow(),
                    "last_optimization": datetime.utcnow()
                },
                "$inc": {
                    "optimization_count": 1
                }
            }
        )
    
    elif decision.decision_type == DecisionType.PAUSE_CAMPAIGN:
        # Pause the campaign
        await db.campaigns.update_one(
            {
                "client_id": decision.client_id,
                "campaign_id": decision.campaign_id
            },
            {
                "$set": {
                    "status": "paused",
                    "updated_at": datetime.utcnow(),
                    "last_optimization": datetime.utcnow()
                },
                "$inc": {
                    "optimization_count": 1
                }
            }
        )
    
    elif decision.decision_type == DecisionType.ACTIVATE_CAMPAIGN:
        # Activate the campaign
        await db.campaigns.update_one(
            {
                "client_id": decision.client_id,
                "campaign_id": decision.campaign_id
            },
            {
                "$set": {
                    "status": "active",
                    "updated_at": datetime.utcnow(),
                    "last_optimization": datetime.utcnow()
                },
                "$inc": {
                    "optimization_count": 1
                }
            }
        )
    
    # Mark decision as applied
    await db.intelligence_decisions.update_one(
        {"_id": decision.id},
        {
            "$set": {
                "applied": True,
                "applied_at": datetime.utcnow(),
                "platform_push_success": platform_push_success
            }
        }
    )
    
    logger.info(
        "decision_applied",
        campaign_id=decision.campaign_id,
        decision_type=decision.decision_type.value,
        new_budget=decision.new_budget,
        platform_pushed=platform_push_success
    )
