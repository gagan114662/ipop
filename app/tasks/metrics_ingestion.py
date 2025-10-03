"""
Metrics Ingestion Service - Fetch performance data from all platforms hourly.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import structlog
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.platforms.manager import PlatformManager
from app.models.campaign import Platform

logger = structlog.get_logger(__name__)


class MetricsIngestionService:
    """
    Service to fetch and store performance metrics from advertising platforms.
    
    This service:
    1. Fetches metrics from all configured platforms
    2. Stores them in the performance_metrics collection
    3. Updates campaign current_metrics
    4. Aggregates SKU-level metrics
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize metrics ingestion service."""
        self.db = db
        self.platform_manager = PlatformManager()
    
    async def ingest_all_metrics(self) -> Dict[str, Any]:
        """
        Ingest metrics for all active campaigns across all clients.
        
        Returns:
            Summary of ingestion results
        """
        logger.info("metrics_ingestion_started")
        
        start_time = datetime.utcnow()
        
        # Get all active campaigns
        campaigns = await self.db.campaigns.find({
            "status": "active"
        }).to_list(length=10000)
        
        total_campaigns = len(campaigns)
        successful = 0
        failed = 0
        skipped = 0
        
        for campaign in campaigns:
            try:
                platform = Platform(campaign["platform"])
                
                # Check if platform is configured
                if not self.platform_manager.is_platform_configured(platform):
                    skipped += 1
                    logger.debug(
                        "platform_not_configured_skipping",
                        campaign_id=campaign["campaign_id"],
                        platform=platform.value
                    )
                    continue
                
                # Fetch metrics from platform
                metrics = await self.platform_manager.fetch_metrics(
                    platform=platform,
                    campaign=campaign,
                    start_date=datetime.utcnow() - timedelta(hours=1),
                    end_date=datetime.utcnow()
                )
                
                if metrics:
                    # Store metrics
                    await self._store_metrics(campaign, metrics)
                    
                    # Update campaign current metrics
                    await self._update_campaign_metrics(campaign["campaign_id"], metrics)
                    
                    successful += 1
                else:
                    failed += 1
                    logger.warning(
                        "metrics_fetch_returned_none",
                        campaign_id=campaign["campaign_id"]
                    )
                    
            except Exception as e:
                failed += 1
                logger.error(
                    "metrics_ingestion_failed_for_campaign",
                    campaign_id=campaign.get("campaign_id"),
                    error=str(e)
                )
        
        # Update SKU aggregates
        await self._update_sku_aggregates()
        
        # Update system benchmarks
        await self._update_system_benchmarks()
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        summary = {
            "total_campaigns": total_campaigns,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "duration_seconds": duration,
            "timestamp": datetime.utcnow()
        }
        
        logger.info(
            "metrics_ingestion_completed",
            **summary
        )
        
        return summary
    
    async def ingest_campaign_metrics(
        self,
        campaign_id: str,
        client_id: str
    ) -> bool:
        """
        Ingest metrics for a specific campaign.
        
        Args:
            campaign_id: Campaign identifier
            client_id: Client identifier
        
        Returns:
            True if successful
        """
        try:
            # Get campaign
            campaign = await self.db.campaigns.find_one({
                "campaign_id": campaign_id,
                "client_id": client_id
            })
            
            if not campaign:
                logger.error("campaign_not_found", campaign_id=campaign_id)
                return False
            
            platform = Platform(campaign["platform"])
            
            # Check if platform is configured
            if not self.platform_manager.is_platform_configured(platform):
                logger.warning(
                    "platform_not_configured",
                    campaign_id=campaign_id,
                    platform=platform.value
                )
                return False
            
            # Fetch metrics
            metrics = await self.platform_manager.fetch_metrics(
                platform=platform,
                campaign=campaign,
                start_date=datetime.utcnow() - timedelta(hours=1),
                end_date=datetime.utcnow()
            )
            
            if not metrics:
                return False
            
            # Store metrics
            await self._store_metrics(campaign, metrics)
            
            # Update campaign current metrics
            await self._update_campaign_metrics(campaign_id, metrics)
            
            logger.info(
                "campaign_metrics_ingested",
                campaign_id=campaign_id
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "campaign_metrics_ingestion_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            return False
    
    async def _store_metrics(
        self,
        campaign: Dict[str, Any],
        metrics: Dict[str, Any]
    ):
        """Store metrics in performance_metrics collection."""
        timestamp = datetime.utcnow()
        
        metrics_doc = {
            "client_id": campaign["client_id"],
            "campaign_id": campaign["campaign_id"],
            "sku_id": campaign["sku_id"],
            "platform": campaign["platform"],
            "timestamp": timestamp,
            "hour_of_day": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "impressions": metrics.get("impressions", 0),
            "clicks": metrics.get("clicks", 0),
            "conversions": metrics.get("conversions", 0),
            "spend": metrics.get("spend", 0.0),
            "revenue": metrics.get("revenue", 0.0),
            "ctr": metrics.get("ctr", 0.0),
            "cpc": metrics.get("cpc", 0.0),
            "cpa": metrics.get("cpa", 0.0),
            "cvr": metrics.get("cvr", 0.0),
            "roas": metrics.get("roas", 0.0)
        }
        
        await self.db.performance_metrics.insert_one(metrics_doc)
    
    async def _update_campaign_metrics(
        self,
        campaign_id: str,
        metrics: Dict[str, Any]
    ):
        """Update campaign's current_metrics field."""
        await self.db.campaigns.update_one(
            {"campaign_id": campaign_id},
            {
                "$set": {
                    "current_metrics": {
                        "impressions": metrics.get("impressions", 0),
                        "clicks": metrics.get("clicks", 0),
                        "conversions": metrics.get("conversions", 0),
                        "spend": metrics.get("spend", 0.0),
                        "revenue": metrics.get("revenue", 0.0),
                        "ctr": metrics.get("ctr", 0.0),
                        "cpc": metrics.get("cpc", 0.0),
                        "cpa": metrics.get("cpa", 0.0),
                        "roas": metrics.get("roas", 0.0),
                        "last_updated": datetime.utcnow()
                    },
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    async def _update_sku_aggregates(self):
        """Update SKU-level aggregated metrics."""
        # Aggregate by SKU
        pipeline = [
            {
                "$match": {
                    "status": "active"
                }
            },
            {
                "$group": {
                    "_id": {
                        "client_id": "$client_id",
                        "sku_id": "$sku_id"
                    },
                    "total_spend": {"$sum": "$current_metrics.spend"},
                    "total_revenue": {"$sum": "$current_metrics.revenue"},
                    "total_impressions": {"$sum": "$current_metrics.impressions"},
                    "total_clicks": {"$sum": "$current_metrics.clicks"},
                    "total_conversions": {"$sum": "$current_metrics.conversions"}
                }
            }
        ]
        
        cursor = self.db.campaigns.aggregate(pipeline)
        aggregates = await cursor.to_list(length=10000)
        
        # Update each SKU
        for agg in aggregates:
            client_id = agg["_id"]["client_id"]
            sku_id = agg["_id"]["sku_id"]
            
            total_spend = agg["total_spend"]
            total_revenue = agg["total_revenue"]
            current_roas = (total_revenue / total_spend) if total_spend > 0 else 0
            
            await self.db.skus.update_one(
                {
                    "client_id": client_id,
                    "sku_id": sku_id
                },
                {
                    "$set": {
                        "total_spend": total_spend,
                        "total_revenue": total_revenue,
                        "total_impressions": agg["total_impressions"],
                        "total_clicks": agg["total_clicks"],
                        "total_conversions": agg["total_conversions"],
                        "current_roas": round(current_roas, 2),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
    
    async def _update_system_benchmarks(self):
        """Update anonymized system-wide benchmarks."""
        # Aggregate metrics by platform and region
        pipeline = [
            {
                "$match": {
                    "timestamp": {
                        "$gte": datetime.utcnow() - timedelta(days=30)
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "platform": "$platform"
                    },
                    "avg_ctr": {"$avg": "$ctr"},
                    "avg_cpc": {"$avg": "$cpc"},
                    "avg_cpa": {"$avg": "$cpa"},
                    "avg_cvr": {"$avg": "$cvr"},
                    "avg_roas": {"$avg": "$roas"},
                    "sample_size": {"$sum": 1}
                }
            }
        ]
        
        cursor = self.db.performance_metrics.aggregate(pipeline)
        benchmarks = await cursor.to_list(length=100)
        
        # Store benchmarks
        for benchmark in benchmarks:
            if benchmark["sample_size"] < 10:
                continue  # Skip if not enough data
            
            # Calculate percentiles (simplified - use actual data for production)
            avg_roas = benchmark["avg_roas"]
            
            benchmark_doc = {
                "platform": benchmark["_id"]["platform"],
                "industry": None,  # Can be enhanced with industry data
                "region": "Global",
                "avg_ctr": round(benchmark["avg_ctr"], 2),
                "avg_cpc": round(benchmark["avg_cpc"], 2),
                "avg_cpa": round(benchmark["avg_cpa"], 2),
                "avg_cvr": round(benchmark["avg_cvr"], 2),
                "avg_roas": round(avg_roas, 2),
                "median_roas": round(avg_roas, 2),
                "p75_roas": round(avg_roas * 1.2, 2),
                "p90_roas": round(avg_roas * 1.5, 2),
                "sample_size": benchmark["sample_size"],
                "confidence_level": min(benchmark["sample_size"] / 1000, 0.95),
                "timestamp": datetime.utcnow(),
                "month": datetime.utcnow().strftime("%Y-%m"),
                "metadata": {}
            }
            
            # Upsert benchmark
            await self.db.system_benchmarks.update_one(
                {
                    "platform": benchmark_doc["platform"],
                    "month": benchmark_doc["month"]
                },
                {"$set": benchmark_doc},
                upsert=True
            )
