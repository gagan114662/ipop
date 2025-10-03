"""
Admin API endpoints for system management and monitoring.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.tasks.metrics_ingestion import MetricsIngestionService
from app.tasks.scheduler import get_scheduler
from app.platforms.manager import PlatformManager

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/ingest-metrics", response_model=Dict[str, Any])
async def manual_metrics_ingestion(
    campaign_id: str = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Manually trigger metrics ingestion.
    
    If campaign_id is provided, ingests metrics for that campaign only.
    Otherwise, ingests metrics for all active campaigns.
    """
    ingestion_service = MetricsIngestionService(db)
    
    if campaign_id:
        # Ingest single campaign
        client_id = current_user["client_id"]
        success = await ingestion_service.ingest_campaign_metrics(campaign_id, client_id)
        
        return {
            "status": "success" if success else "failed",
            "campaign_id": campaign_id,
            "message": "Metrics ingested successfully" if success else "Failed to ingest metrics"
        }
    else:
        # Ingest all campaigns
        summary = await ingestion_service.ingest_all_metrics()
        return summary


@router.get("/scheduler/status")
async def get_scheduler_status(
    current_user: dict = Depends(get_current_user)
):
    """Get status of automated scheduler."""
    scheduler = get_scheduler()
    
    return {
        "is_running": scheduler.is_running(),
        "jobs": scheduler.get_jobs()
    }


@router.post("/scheduler/start")
async def start_scheduler(
    current_user: dict = Depends(get_current_user)
):
    """Start the automated scheduler."""
    scheduler = get_scheduler()
    
    if scheduler.is_running():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduler is already running"
        )
    
    scheduler.start()
    
    return {
        "status": "started",
        "message": "Automated scheduler started successfully"
    }


@router.post("/scheduler/stop")
async def stop_scheduler(
    current_user: dict = Depends(get_current_user)
):
    """Stop the automated scheduler."""
    scheduler = get_scheduler()
    
    if not scheduler.is_running():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduler is not running"
        )
    
    scheduler.stop()
    
    return {
        "status": "stopped",
        "message": "Automated scheduler stopped successfully"
    }


@router.get("/platforms/status")
async def get_platforms_status(
    current_user: dict = Depends(get_current_user)
):
    """Get status of all platform integrations."""
    platform_manager = PlatformManager()
    
    from app.models.campaign import Platform
    
    status_list = []
    for platform in Platform:
        is_configured = platform_manager.is_platform_configured(platform)
        status_list.append({
            "platform": platform.value,
            "configured": is_configured,
            "status": "ready" if is_configured else "not_configured"
        })
    
    return {
        "platforms": status_list,
        "total_configured": len(platform_manager.get_configured_platforms())
    }


@router.get("/system/health")
async def system_health_check(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Comprehensive system health check."""
    health = {
        "status": "healthy",
        "timestamp": str(logger.info("health_check")),
        "components": {}
    }
    
    # Check database
    try:
        await db.command("ping")
        health["components"]["database"] = "healthy"
    except Exception as e:
        health["components"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check scheduler
    scheduler = get_scheduler()
    health["components"]["scheduler"] = "running" if scheduler.is_running() else "stopped"
    
    # Check platforms
    platform_manager = PlatformManager()
    configured_count = len(platform_manager.get_configured_platforms())
    health["components"]["platforms"] = f"{configured_count}/4 configured"
    
    return health
