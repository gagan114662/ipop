"""
Creative A/B Testing API endpoints.

This module provides endpoints for creating and managing creative tests,
analyzing test performance, and declaring winners.
"""
from datetime import datetime, timedelta
from typing import Optional, List
import structlog
from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.security import get_current_user
from app.models.creative_test import (
    CreativeTestCreate,
    CreativeTestUpdate,
    CreativeTestResponse,
    CreativeTestList,
    CreativeTestAnalysis,
    CreativeTestInDB,
    TestStatus,
    TestType,
    TestMetric,
    TestVariant,
    TestResult,
)
from app.models.creative import CreativeInDB

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Creative Testing"])


@router.post("/", response_model=CreativeTestResponse)
async def create_creative_test(
    test_data: CreativeTestCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Create a new creative A/B test.

    Validates:
    - All creative IDs exist and belong to the client
    - Traffic allocation sums to 100%
    - At least 2 variants
    - Exactly one control variant
    - Campaign exists and belongs to client
    """
    client_id = current_user["client_id"]

    logger.info(
        "creating_creative_test",
        client_id=client_id,
        test_id=test_data.test_id,
        campaign_id=test_data.campaign_id,
        variant_count=len(test_data.variants),
    )

    # Validate test_id uniqueness
    existing = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_data.test_id,
    })
    if existing:
        raise HTTPException(400, f"Test ID '{test_data.test_id}' already exists")

    # Validate campaign exists
    campaign = await db.campaigns.find_one({
        "client_id": client_id,
        "campaign_id": test_data.campaign_id,
    })
    if not campaign:
        raise HTTPException(404, f"Campaign '{test_data.campaign_id}' not found")

    # Validate all creative IDs exist and belong to client
    creative_ids = [v.creative_id for v in test_data.variants]
    creatives = await db.creatives.find({
        "client_id": client_id,
        "creative_id": {"$in": creative_ids}
    }).to_list(length=100)

    found_ids = {c["creative_id"] for c in creatives}
    missing = set(creative_ids) - found_ids
    if missing:
        raise HTTPException(404, f"Creatives not found: {missing}")

    # Validate traffic allocation and control variants
    if len(test_data.variants) > 1:
        # Validate traffic allocation sums to 100%
        total_traffic = sum(v.traffic_allocation for v in test_data.variants)
        if abs(total_traffic - 100.0) > 0.01:
            raise HTTPException(
                400,
                f"Traffic allocation must sum to 100%, got {total_traffic}%"
            )

        # Validate exactly one control
        control_count = sum(1 for v in test_data.variants if v.is_control)
        if control_count != 1:
            raise HTTPException(
                400,
                f"Exactly one control variant required, got {control_count}"
            )

    # Create test document
    test_doc = {
        **test_data.model_dump(),
        "client_id": client_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "started_at": None,
        "completed_at": None,
        "current_leader": None,
        "result": None,
        "is_concluded": False,
        "conclusion_reason": None,
    }

    result = await db.creative_tests.insert_one(test_doc)
    test_doc["_id"] = result.inserted_id

    logger.info(
        "creative_test_created",
        client_id=client_id,
        test_id=test_data.test_id,
        test_type=test_data.test_type,
    )

    # Convert to response model
    return _test_doc_to_response(test_doc)


@router.get("/", response_model=CreativeTestList)
async def list_creative_tests(
    campaign_id: Optional[str] = None,
    status: Optional[TestStatus] = None,
    is_concluded: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    List creative tests with optional filtering.

    Filters:
    - campaign_id: Tests for specific campaign
    - status: Test status (draft, running, paused, completed, cancelled)
    - is_concluded: Whether test has been concluded
    """
    client_id = current_user["client_id"]

    # Build query
    query = {"client_id": client_id}
    if campaign_id:
        query["campaign_id"] = campaign_id
    if status:
        query["status"] = status
    if is_concluded is not None:
        query["is_concluded"] = is_concluded

    # Get total count
    total = await db.creative_tests.count_documents(query)

    # Get paginated results
    skip = (page - 1) * page_size
    cursor = db.creative_tests.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    tests = await cursor.to_list(length=page_size)

    # Convert to response models
    test_responses = [_test_doc_to_response(test) for test in tests]

    total_pages = (total + page_size - 1) // page_size

    return CreativeTestList(
        tests=test_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{test_id}", response_model=CreativeTestResponse)
async def get_creative_test(
    test_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get detailed information about a specific creative test."""
    client_id = current_user["client_id"]

    test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    if not test:
        raise HTTPException(404, f"Test '{test_id}' not found")

    return _test_doc_to_response(test)


@router.post("/{test_id}/start", response_model=CreativeTestResponse)
async def start_creative_test(
    test_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Start a creative test.

    Actions:
    - Changes status from DRAFT to RUNNING
    - Sets started_at timestamp
    - Calculates end_date based on max_duration_days
    - Updates all variant creatives to TESTING status
    """
    client_id = current_user["client_id"]

    test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    if not test:
        raise HTTPException(404, f"Test '{test_id}' not found")

    if test["status"] != TestStatus.DRAFT:
        raise HTTPException(400, f"Test must be in DRAFT status to start, currently {test['status']}")

    if test["is_concluded"]:
        raise HTTPException(400, "Cannot start a concluded test")

    # Calculate end date
    now = datetime.utcnow()
    end_date = now + timedelta(days=test["max_duration_days"])

    # Update test status
    update_result = await db.creative_tests.update_one(
        {"client_id": client_id, "test_id": test_id},
        {
            "$set": {
                "status": TestStatus.RUNNING,
                "started_at": now,
                "start_date": now,
                "end_date": end_date,
                "updated_at": now,
            }
        }
    )

    if update_result.modified_count == 0:
        raise HTTPException(500, "Failed to start test")

    # Update all variant creatives to TESTING status
    creative_ids = [v["creative_id"] for v in test["variants"]]
    await db.creatives.update_many(
        {
            "client_id": client_id,
            "creative_id": {"$in": creative_ids}
        },
        {
            "$set": {
                "status": "testing",
                "updated_at": now,
            }
        }
    )

    logger.info(
        "creative_test_started",
        client_id=client_id,
        test_id=test_id,
        end_date=end_date.isoformat(),
        creative_count=len(creative_ids),
    )

    # Fetch updated test
    updated_test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    return _test_doc_to_response(updated_test)


@router.post("/{test_id}/pause", response_model=CreativeTestResponse)
async def pause_creative_test(
    test_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Pause a running creative test.

    Does not conclude the test - can be resumed later.
    """
    client_id = current_user["client_id"]

    test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    if not test:
        raise HTTPException(404, f"Test '{test_id}' not found")

    if test["status"] != TestStatus.RUNNING:
        raise HTTPException(400, f"Test must be RUNNING to pause, currently {test['status']}")

    # Update test status
    now = datetime.utcnow()
    await db.creative_tests.update_one(
        {"client_id": client_id, "test_id": test_id},
        {
            "$set": {
                "status": TestStatus.PAUSED,
                "updated_at": now,
            }
        }
    )

    logger.info("creative_test_paused", client_id=client_id, test_id=test_id)

    # Fetch updated test
    updated_test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    return _test_doc_to_response(updated_test)


@router.post("/{test_id}/resume", response_model=CreativeTestResponse)
async def resume_creative_test(
    test_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Resume a paused creative test."""
    client_id = current_user["client_id"]

    test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    if not test:
        raise HTTPException(404, f"Test '{test_id}' not found")

    if test["status"] != TestStatus.PAUSED:
        raise HTTPException(400, f"Test must be PAUSED to resume, currently {test['status']}")

    if test["is_concluded"]:
        raise HTTPException(400, "Cannot resume a concluded test")

    # Update test status
    now = datetime.utcnow()
    await db.creative_tests.update_one(
        {"client_id": client_id, "test_id": test_id},
        {
            "$set": {
                "status": TestStatus.RUNNING,
                "updated_at": now,
            }
        }
    )

    logger.info("creative_test_resumed", client_id=client_id, test_id=test_id)

    # Fetch updated test
    updated_test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    return _test_doc_to_response(updated_test)


@router.post("/{test_id}/conclude", response_model=CreativeTestResponse)
async def conclude_creative_test(
    test_id: str,
    force: bool = Query(False, description="Force conclude even if criteria not met"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Conclude a creative test and declare winner.

    Actions:
    - Analyzes variant performance
    - Calculates statistical significance
    - Declares winner based on winner_selection method
    - Auto-promotes winner if enabled
    - Auto-pauses losers if enabled
    - Sets status to COMPLETED
    """
    client_id = current_user["client_id"]

    test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    if not test:
        raise HTTPException(404, f"Test '{test_id}' not found")

    if test["is_concluded"]:
        raise HTTPException(400, "Test already concluded")

    if test["status"] not in [TestStatus.RUNNING, TestStatus.PAUSED]:
        raise HTTPException(400, f"Test must be RUNNING or PAUSED to conclude, currently {test['status']}")

    # Get analysis
    analysis = await _analyze_test(test_id, client_id, db)

    # Check if can conclude
    if not force and not analysis["can_conclude"]:
        raise HTTPException(
            400,
            f"Test does not meet criteria to conclude. Reason: {analysis['recommendation']}. "
            f"Use force=true to conclude anyway."
        )

    # Determine winner
    winner_creative_id = analysis["current_leader"]
    winner_variant = None
    control_variant = None

    for variant in test["variants"]:
        if variant["creative_id"] == winner_creative_id:
            winner_variant = variant
        if variant["is_control"]:
            control_variant = variant

    # Calculate improvement vs control
    improvement = 0.0
    if winner_variant and control_variant:
        metric = test["primary_metric"]
        control_value = _get_variant_metric_value(control_variant, metric)
        winner_value = _get_variant_metric_value(winner_variant, metric)

        if control_value > 0:
            improvement = ((winner_value - control_value) / control_value) * 100

    # Create result
    result = TestResult(
        winner_creative_id=winner_creative_id,
        winner_variant_name=winner_variant["variant_name"] if winner_variant else None,
        confidence_level=analysis["leader_confidence"],
        improvement_vs_control=improvement,
        p_value=0.05 if analysis["has_statistical_significance"] else 0.10,  # Simplified
        sample_size=sum(v["impressions"] for v in test["variants"]),
        statistical_power=0.8 if analysis["has_statistical_significance"] else 0.6,
        control_performance={
            "ctr": control_variant["ctr"],
            "roas": control_variant["roas"],
            "conversions": control_variant["conversions"],
        } if control_variant else {},
        winner_performance={
            "ctr": winner_variant["ctr"],
            "roas": winner_variant["roas"],
            "conversions": winner_variant["conversions"],
        } if winner_variant else {},
        recommendation=f"Promote '{winner_variant['variant_name']}' as winner with {improvement:.1f}% improvement" if winner_variant else "No clear winner",
        next_steps=[
            f"Activate creative '{winner_creative_id}' in campaign" if test["auto_promote_winner"] else f"Consider activating creative '{winner_creative_id}'",
            "Run follow-up test with new variants",
            "Monitor performance for 7 days",
        ] if winner_creative_id else ["Extend test duration", "Add more variants"],
    )

    # Update test
    now = datetime.utcnow()
    conclusion_reason = "Automatic - criteria met" if not force else "Manual - forced by user"

    await db.creative_tests.update_one(
        {"client_id": client_id, "test_id": test_id},
        {
            "$set": {
                "status": TestStatus.COMPLETED,
                "is_concluded": True,
                "conclusion_reason": conclusion_reason,
                "completed_at": now,
                "updated_at": now,
                "result": result.model_dump(),
                "current_leader": winner_creative_id,
            }
        }
    )

    # Auto-promote winner
    if test["auto_promote_winner"] and winner_creative_id:
        await db.creatives.update_one(
            {"client_id": client_id, "creative_id": winner_creative_id},
            {"$set": {"status": "active", "updated_at": now}}
        )

        # Set as primary creative in campaign
        await db.campaigns.update_one(
            {"client_id": client_id, "campaign_id": test["campaign_id"]},
            {"$set": {"primary_creative_id": winner_creative_id, "updated_at": now}}
        )

        logger.info(
            "test_winner_promoted",
            client_id=client_id,
            test_id=test_id,
            winner_creative_id=winner_creative_id,
        )

    # Auto-pause losers
    if test["auto_pause_losers"] and winner_creative_id:
        loser_ids = [v["creative_id"] for v in test["variants"] if v["creative_id"] != winner_creative_id]
        await db.creatives.update_many(
            {"client_id": client_id, "creative_id": {"$in": loser_ids}},
            {"$set": {"status": "paused", "updated_at": now}}
        )

        logger.info(
            "test_losers_paused",
            client_id=client_id,
            test_id=test_id,
            loser_count=len(loser_ids),
        )

    logger.info(
        "creative_test_concluded",
        client_id=client_id,
        test_id=test_id,
        winner_creative_id=winner_creative_id,
        improvement=improvement,
    )

    # Fetch updated test
    updated_test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    return _test_doc_to_response(updated_test)


@router.get("/{test_id}/analysis", response_model=CreativeTestAnalysis)
async def analyze_creative_test(
    test_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get real-time analysis of a creative test.

    Provides:
    - Current leader and confidence level
    - Statistical significance
    - Progress toward min sample size
    - Whether test can be concluded
    - Estimated time remaining
    - Performance comparison of all variants
    """
    client_id = current_user["client_id"]

    analysis = await _analyze_test(test_id, client_id, db)

    return CreativeTestAnalysis(**analysis)


# Helper functions

def _test_doc_to_response(test_doc: dict) -> CreativeTestResponse:
    """Convert database document to response model."""
    return CreativeTestResponse(
        id=str(test_doc["_id"]),
        test_id=test_doc["test_id"],
        name=test_doc["name"],
        description=test_doc.get("description"),
        campaign_id=test_doc["campaign_id"],
        test_type=test_doc["test_type"],
        primary_metric=test_doc["primary_metric"],
        variants=test_doc["variants"],
        status=test_doc["status"],
        min_sample_size=test_doc["min_sample_size"],
        confidence_threshold=test_doc["confidence_threshold"],
        winner_selection=test_doc["winner_selection"],
        start_date=test_doc.get("start_date"),
        end_date=test_doc.get("end_date"),
        max_duration_days=test_doc["max_duration_days"],
        created_at=test_doc["created_at"],
        started_at=test_doc.get("started_at"),
        completed_at=test_doc.get("completed_at"),
        current_leader=test_doc.get("current_leader"),
        result=TestResult(**test_doc["result"]) if test_doc.get("result") else None,
        is_concluded=test_doc["is_concluded"],
        conclusion_reason=test_doc.get("conclusion_reason"),
        auto_promote_winner=test_doc["auto_promote_winner"],
        auto_pause_losers=test_doc["auto_pause_losers"],
    )


async def _analyze_test(
    test_id: str,
    client_id: str,
    db: AsyncIOMotorDatabase,
) -> dict:
    """
    Analyze a creative test and return analysis results.

    This is a simplified implementation. In production, you'd use proper
    statistical libraries like scipy.stats for t-tests, chi-square tests, etc.
    """
    test = await db.creative_tests.find_one({
        "client_id": client_id,
        "test_id": test_id,
    })

    if not test:
        raise HTTPException(404, f"Test '{test_id}' not found")

    # Calculate days running
    if test.get("started_at"):
        days_running = (datetime.utcnow() - test["started_at"]).days
    else:
        days_running = 0

    # Get creative metrics for all variants
    creative_ids = [v["creative_id"] for v in test["variants"]]

    # Fetch latest metrics from creative_metrics collection
    # For now, we'll use the metrics stored in the variants themselves
    # In production, you'd aggregate from creative_metrics collection

    variants_analysis = []
    total_impressions = sum(v["impressions"] for v in test["variants"])

    for variant in test["variants"]:
        variant_dict = {
            "creative_id": variant["creative_id"],
            "variant_name": variant["variant_name"],
            "is_control": variant["is_control"],
            "impressions": variant["impressions"],
            "clicks": variant["clicks"],
            "conversions": variant["conversions"],
            "spend": variant["spend"],
            "revenue": variant["revenue"],
            "ctr": variant["ctr"],
            "roas": variant["roas"],
            "cpa": variant["cpa"],
            "confidence_level": variant["confidence_level"],
            "is_significant": variant["is_significant"],
        }
        variants_analysis.append(variant_dict)

    # Determine current leader based on primary metric
    metric = test["primary_metric"]
    best_variant = max(test["variants"], key=lambda v: _get_variant_metric_value(v, metric))
    current_leader = best_variant["creative_id"]
    leader_confidence = best_variant["confidence_level"]

    # Check if minimum sample size reached
    min_sample_reached = all(
        v["impressions"] >= test["min_sample_size"]
        for v in test["variants"]
    )

    # Check statistical significance (simplified)
    # In production, use proper statistical tests
    has_statistical_significance = (
        min_sample_reached and
        leader_confidence >= test["confidence_threshold"]
    )

    # Calculate progress
    progress_pct = min(100.0, (total_impressions / (test["min_sample_size"] * len(test["variants"]))) * 100)

    # Determine if can conclude
    can_conclude = False
    recommendation = ""

    if test["status"] == TestStatus.DRAFT:
        recommendation = "Test not started - start test to begin collecting data"
    elif not min_sample_reached:
        recommendation = f"Continue test - need {test['min_sample_size']} impressions per variant (currently at {min([v['impressions'] for v in test['variants']])})"
    elif not has_statistical_significance:
        recommendation = f"Continue test - confidence level {leader_confidence:.1f}% below threshold {test['confidence_threshold']}%"
    else:
        can_conclude = True
        recommendation = f"Test can be concluded - {best_variant['variant_name']} is statistically significant winner"

    # Also allow concluding if max duration reached
    if test.get("end_date") and datetime.utcnow() >= test["end_date"]:
        can_conclude = True
        recommendation = f"Test duration complete - {best_variant['variant_name']} is current best performer"

    # Estimate days remaining
    estimated_days_remaining = None
    if test.get("end_date"):
        remaining = test["end_date"] - datetime.utcnow()
        estimated_days_remaining = max(0, remaining.days)

    return {
        "test_id": test_id,
        "campaign_id": test["campaign_id"],
        "status": test["status"],
        "days_running": days_running,
        "progress_pct": progress_pct,
        "variants_analysis": variants_analysis,
        "current_leader": current_leader,
        "leader_confidence": leader_confidence,
        "has_statistical_significance": has_statistical_significance,
        "can_conclude": can_conclude,
        "recommendation": recommendation,
        "estimated_days_remaining": estimated_days_remaining,
        "min_sample_reached": min_sample_reached,
        "timestamp": datetime.utcnow(),
    }


def _get_variant_metric_value(variant: dict, metric: TestMetric) -> float:
    """Get the value of a specific metric for a variant."""
    metric_map = {
        TestMetric.CTR: "ctr",
        TestMetric.ROAS: "roas",
        TestMetric.CPA: "cpa",
        TestMetric.CONVERSIONS: "conversions",
        TestMetric.ENGAGEMENT_RATE: "ctr",  # Simplified - would need separate engagement tracking
        TestMetric.VIDEO_COMPLETION: "ctr",  # Simplified - would need video metrics
    }

    field = metric_map.get(metric, "roas")
    return variant.get(field, 0.0)
