"""
Automated Scheduler - Hourly metrics ingestion and optimization.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import structlog

from app.core.database import Database
from app.tasks.metrics_ingestion import MetricsIngestionService
from app.intelligence.decision_engine import DecisionEngine
from app.platforms.manager import PlatformManager

logger = structlog.get_logger(__name__)


class AutomatedScheduler:
    """
    Scheduler for automated tasks:
    - Hourly metrics ingestion from platforms
    - Hourly optimization decisions
    - Budget application to platforms
    """
    
    def __init__(self):
        """Initialize scheduler."""
        self.scheduler = AsyncIOScheduler()
        self._is_running = False
    
    def start(self):
        """Start the scheduler."""
        if self._is_running:
            logger.warning("scheduler_already_running")
            return
        
        # Schedule hourly metrics ingestion (at minute 0 of every hour)
        self.scheduler.add_job(
            self._ingest_metrics_job,
            trigger=CronTrigger(minute=0),
            id="metrics_ingestion",
            name="Hourly Metrics Ingestion",
            replace_existing=True
        )
        
        # Schedule hourly optimization (at minute 15 of every hour)
        self.scheduler.add_job(
            self._optimization_job,
            trigger=CronTrigger(minute=15),
            id="optimization",
            name="Hourly Optimization",
            replace_existing=True
        )
        
        # Schedule benchmark updates (daily at 2 AM)
        self.scheduler.add_job(
            self._benchmark_update_job,
            trigger=CronTrigger(hour=2, minute=0),
            id="benchmark_update",
            name="Daily Benchmark Update",
            replace_existing=True
        )
        
        self.scheduler.start()
        self._is_running = True
        
        logger.info(
            "scheduler_started",
            jobs=["metrics_ingestion", "optimization", "benchmark_update"]
        )
    
    def stop(self):
        """Stop the scheduler."""
        if not self._is_running:
            return
        
        self.scheduler.shutdown()
        self._is_running = False
        logger.info("scheduler_stopped")
    
    async def _ingest_metrics_job(self):
        """Job: Ingest metrics from all platforms."""
        job_start = datetime.utcnow()
        logger.info("scheduled_metrics_ingestion_started", timestamp=job_start)
        
        try:
            db = Database.get_database()
            ingestion_service = MetricsIngestionService(db)
            
            summary = await ingestion_service.ingest_all_metrics()
            
            logger.info(
                "scheduled_metrics_ingestion_completed",
                successful=summary["successful"],
                failed=summary["failed"],
                skipped=summary["skipped"],
                duration=summary["duration_seconds"]
            )
            
        except Exception as e:
            logger.critical(
                "scheduled_metrics_ingestion_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
                timestamp=datetime.utcnow()
            )
            # Don't raise - allow scheduler to continue with other jobs
            
            # TODO: Send alert to monitoring system
            # await self._send_alert("metrics_ingestion_failed", str(e))
    
    async def _optimization_job(self):
        """Job: Run optimization for all active campaigns."""
        job_start = datetime.utcnow()
        logger.info("scheduled_optimization_started", timestamp=job_start)
        
        try:
            db = Database.get_database()
            decision_engine = DecisionEngine(db)
            platform_manager = PlatformManager()
            
            # Get all clients
            clients_cursor = db.clients.find({"is_active": True})
            clients = await clients_cursor.to_list(length=10000)
            
            total_decisions = 0
            total_applied = 0
            total_failed = 0
            
            for client in clients:
                try:
                    client_id = client["client_id"]
                    
                    # Run optimization for all campaigns
                    decisions = await decision_engine.optimize_all_campaigns(client_id)
                    total_decisions += len(decisions)
                    
                    # Apply decisions if auto-optimization is enabled
                    if client.get("settings", {}).get("auto_optimization_enabled", True):
                        for decision in decisions:
                            try:
                                applied = await self._apply_decision_to_platform(
                                    decision,
                                    platform_manager,
                                    db
                                )
                                if applied:
                                    total_applied += 1
                                else:
                                    total_failed += 1
                            except Exception as e:
                                total_failed += 1
                                logger.error(
                                    "decision_application_failed",
                                    campaign_id=decision.campaign_id,
                                    client_id=client_id,
                                    error=str(e)
                                )
                except Exception as e:
                    logger.error(
                        "client_optimization_failed",
                        client_id=client.get("client_id"),
                        error=str(e)
                    )
                    # Continue with next client
                    continue
            
            logger.info(
                "scheduled_optimization_completed",
                total_decisions=total_decisions,
                applied=total_applied,
                failed=total_failed,
                duration=(datetime.utcnow() - job_start).total_seconds()
            )
            
        except Exception as e:
            logger.critical(
                "scheduled_optimization_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
                timestamp=datetime.utcnow()
            )
            # Don't raise - allow scheduler to continue
            
            # TODO: Send alert to monitoring system
            # await self._send_alert("optimization_failed", str(e))
    
    async def _apply_decision_to_platform(
        self,
        decision,
        platform_manager: PlatformManager,
        db
    ) -> bool:
        """Apply an intelligence decision to the actual platform."""
        from app.models.intelligence import DecisionType
        from app.models.campaign import Platform
        
        try:
            # Get campaign
            campaign = await db.campaigns.find_one({
                "campaign_id": decision.campaign_id,
                "client_id": decision.client_id
            })
            
            if not campaign:
                logger.error("campaign_not_found_for_decision", campaign_id=decision.campaign_id)
                return False
            
            platform = Platform(campaign["platform"])
            
            # Check if platform is configured
            if not platform_manager.is_platform_configured(platform):
                logger.warning(
                    "platform_not_configured_for_decision",
                    platform=platform.value,
                    campaign_id=decision.campaign_id
                )
                # Still mark as applied locally even if we can't push to platform
                await self._mark_decision_applied(decision, db, success=False)
                return False
            
            # Apply decision based on type
            if decision.decision_type == DecisionType.BUDGET_INCREASE or \
               decision.decision_type == DecisionType.BUDGET_DECREASE:
                
                success = await platform_manager.update_budget(
                    platform=platform,
                    campaign=campaign,
                    new_budget=decision.new_budget
                )
                
                if success:
                    # Update local database
                    await db.campaigns.update_one(
                        {"campaign_id": decision.campaign_id, "client_id": decision.client_id},
                        {
                            "$set": {
                                "daily_budget": decision.new_budget,
                                "updated_at": datetime.utcnow(),
                                "last_optimization": datetime.utcnow()
                            },
                            "$inc": {"optimization_count": 1}
                        }
                    )
                    
                    await self._mark_decision_applied(decision, db, success=True)
                    return True
            
            elif decision.decision_type == DecisionType.PAUSE_CAMPAIGN:
                success = await platform_manager.pause_campaign(platform, campaign)
                
                if success:
                    await db.campaigns.update_one(
                        {"campaign_id": decision.campaign_id, "client_id": decision.client_id},
                        {
                            "$set": {
                                "status": "paused",
                                "updated_at": datetime.utcnow(),
                                "last_optimization": datetime.utcnow()
                            },
                            "$inc": {"optimization_count": 1}
                        }
                    )
                    
                    await self._mark_decision_applied(decision, db, success=True)
                    return True
            
            elif decision.decision_type == DecisionType.ACTIVATE_CAMPAIGN:
                success = await platform_manager.activate_campaign(platform, campaign)
                
                if success:
                    await db.campaigns.update_one(
                        {"campaign_id": decision.campaign_id, "client_id": decision.client_id},
                        {
                            "$set": {
                                "status": "active",
                                "updated_at": datetime.utcnow(),
                                "last_optimization": datetime.utcnow()
                            },
                            "$inc": {"optimization_count": 1}
                        }
                    )
                    
                    await self._mark_decision_applied(decision, db, success=True)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(
                "apply_decision_to_platform_failed",
                campaign_id=decision.campaign_id,
                error=str(e)
            )
            await self._mark_decision_applied(decision, db, success=False)
            return False
    
    async def _mark_decision_applied(self, decision, db, success: bool):
        """Mark decision as applied in database."""
        await db.intelligence_decisions.update_one(
            {"_id": decision.id},
            {
                "$set": {
                    "applied": True,
                    "applied_at": datetime.utcnow(),
                    "success_score": 1.0 if success else 0.0
                }
            }
        )
    
    async def _benchmark_update_job(self):
        """Job: Update system benchmarks."""
        job_start = datetime.utcnow()
        logger.info("scheduled_benchmark_update_started", timestamp=job_start)
        
        try:
            db = Database.get_database()
            ingestion_service = MetricsIngestionService(db)
            
            await ingestion_service._update_system_benchmarks()
            
            logger.info(
                "scheduled_benchmark_update_completed",
                duration=(datetime.utcnow() - job_start).total_seconds()
            )
            
        except Exception as e:
            logger.critical(
                "scheduled_benchmark_update_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
                timestamp=datetime.utcnow()
            )
            # Don't raise - allow scheduler to continue
            
            # TODO: Send alert to monitoring system
            # await self._send_alert("benchmark_update_failed", str(e))
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running
    
    def get_jobs(self) -> list:
        """Get list of scheduled jobs."""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in self.scheduler.get_jobs()
        ]


# Global scheduler instance
_scheduler = None


def get_scheduler() -> AutomatedScheduler:
    """Get global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AutomatedScheduler()
    return _scheduler
