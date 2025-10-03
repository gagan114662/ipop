"""
Main decision engine that orchestrates all intelligence components.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import structlog

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.intelligence.explore_exploit import ExploreExploitEngine
from app.models.campaign import CampaignInDB, OptimizationMode
from app.models.intelligence import (
    IntelligenceDecisionCreate,
    IntelligenceDecisionInDB,
    OptimizationRecommendation,
    DecisionType
)
from app.models.metrics import PerformanceMetricsInDB

logger = structlog.get_logger(__name__)


class DecisionEngine:
    """
    Main orchestrator for intelligent campaign optimization decisions.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.explore_exploit = ExploreExploitEngine()
    
    async def optimize_campaign(
        self,
        campaign_id: str,
        client_id: str
    ) -> Optional[IntelligenceDecisionInDB]:
        """
        Run optimization for a single campaign.
        
        Args:
            campaign_id: Campaign identifier
            client_id: Client identifier (for multi-tenant isolation)
        
        Returns:
            Intelligence decision or None if no action needed
        """
        # Fetch campaign
        campaign_doc = await self.db.campaigns.find_one({
            "campaign_id": campaign_id,
            "client_id": client_id
        })
        
        if not campaign_doc:
            logger.warning("campaign_not_found", campaign_id=campaign_id)
            return None
        
        campaign = CampaignInDB(**campaign_doc)
        
        # Get recent performance metrics
        metrics = await self._get_recent_metrics(campaign_id, client_id)
        
        if not metrics:
            logger.info("no_metrics_available", campaign_id=campaign_id)
            return None
        
        # Calculate totals
        total_impressions = sum(m.get("impressions", 0) for m in metrics)
        total_conversions = sum(m.get("conversions", 0) for m in metrics)
        total_spend = sum(m.get("spend", 0) for m in metrics)
        total_revenue = sum(m.get("revenue", 0) for m in metrics)
        
        # Calculate current ROAS
        current_roas = total_revenue / total_spend if total_spend > 0 else 0
        
        # Determine campaign age
        campaign_age = datetime.utcnow() - campaign.created_at
        campaign_age_days = campaign_age.days
        
        # Determine optimization mode
        mode = self.explore_exploit.determine_mode(
            campaign=campaign,
            total_impressions=total_impressions,
            campaign_age_days=campaign_age_days
        )
        
        # Get benchmark ROAS if available
        benchmark_roas = await self._get_benchmark_roas(
            campaign.platform,
            campaign.metadata.get("industry")
        )
        
        # Calculate budget adjustment
        new_budget, decision_type, reasoning = self.explore_exploit.calculate_budget_adjustment(
            campaign=campaign,
            current_roas=current_roas,
            target_roas=campaign.target_roas,
            mode=mode,
            benchmark_roas=benchmark_roas
        )
        
        # Calculate confidence score
        confidence = self.explore_exploit.calculate_confidence_score(
            impressions=total_impressions,
            conversions=total_conversions,
            campaign_age_days=campaign_age_days,
            mode=mode
        )
        
        # Calculate budget change percentage
        budget_change_pct = ((new_budget - campaign.daily_budget) / campaign.daily_budget * 100) if campaign.daily_budget > 0 else 0
        
        # Create decision
        decision = IntelligenceDecisionInDB(
            client_id=client_id,
            campaign_id=campaign_id,
            sku_id=campaign.sku_id,
            platform=campaign.platform,
            decision_type=decision_type,
            mode=mode,
            confidence_score=confidence,
            reasoning=reasoning,
            old_budget=campaign.daily_budget,
            new_budget=new_budget,
            budget_change_percent=round(budget_change_pct, 2),
            expected_impact=self._estimate_impact(decision_type, budget_change_pct),
            metrics_snapshot={
                "impressions": total_impressions,
                "conversions": total_conversions,
                "spend": total_spend,
                "revenue": total_revenue,
                "roas": current_roas
            },
            timestamp=datetime.utcnow()
        )
        
        # Save decision to database
        result = await self.db.intelligence_decisions.insert_one(
            decision.dict(by_alias=True, exclude={"id"})
        )
        decision.id = result.inserted_id
        
        logger.info(
            "optimization_decision_created",
            campaign_id=campaign_id,
            decision_type=decision_type.value,
            mode=mode.value,
            confidence=confidence,
            old_budget=campaign.daily_budget,
            new_budget=new_budget
        )
        
        return decision
    
    async def optimize_all_campaigns(
        self,
        client_id: str,
        sku_id: Optional[str] = None
    ) -> List[IntelligenceDecisionInDB]:
        """
        Run optimization for all active campaigns.
        
        Args:
            client_id: Client identifier
            sku_id: Optional SKU filter
        
        Returns:
            List of decisions made
        """
        # Build query
        query = {
            "client_id": client_id,
            "status": "active"
        }
        if sku_id:
            query["sku_id"] = sku_id
        
        # Get all active campaigns
        campaigns_cursor = self.db.campaigns.find(query)
        campaigns = await campaigns_cursor.to_list(length=1000)
        
        logger.info(
            "optimizing_campaigns",
            client_id=client_id,
            campaign_count=len(campaigns),
            sku_id=sku_id
        )
        
        # Optimize each campaign
        decisions = []
        for campaign_doc in campaigns:
            try:
                decision = await self.optimize_campaign(
                    campaign_id=campaign_doc["campaign_id"],
                    client_id=client_id
                )
                if decision:
                    decisions.append(decision)
            except Exception as e:
                logger.error(
                    "campaign_optimization_failed",
                    campaign_id=campaign_doc["campaign_id"],
                    error=str(e)
                )
        
        return decisions
    
    async def get_recommendations(
        self,
        campaign_id: str,
        client_id: str
    ) -> Optional[OptimizationRecommendation]:
        """
        Get real-time optimization recommendations without applying them.
        
        Args:
            campaign_id: Campaign identifier
            client_id: Client identifier
        
        Returns:
            Optimization recommendation
        """
        # Run optimization logic
        decision = await self.optimize_campaign(campaign_id, client_id)
        
        if not decision:
            return None
        
        # Convert to recommendation (don't apply)
        priority = "high" if decision.confidence_score > 0.7 else "medium" if decision.confidence_score > 0.4 else "low"
        
        recommendation = OptimizationRecommendation(
            campaign_id=campaign_id,
            current_mode=decision.mode,
            recommended_action=decision.decision_type,
            recommended_budget=decision.new_budget,
            confidence=decision.confidence_score,
            reasoning=decision.reasoning,
            priority=priority,
            estimated_impact=decision.expected_impact or "Unknown"
        )
        
        return recommendation
    
    async def _get_recent_metrics(
        self,
        campaign_id: str,
        client_id: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get recent performance metrics for a campaign.
        
        Args:
            campaign_id: Campaign identifier
            client_id: Client identifier
            hours: Number of hours to look back
        
        Returns:
            List of metrics documents
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        metrics_cursor = self.db.performance_metrics.find({
            "campaign_id": campaign_id,
            "client_id": client_id,
            "timestamp": {"$gte": since}
        }).sort("timestamp", -1)
        
        return await metrics_cursor.to_list(length=100)
    
    async def _get_benchmark_roas(
        self,
        platform: str,
        industry: Optional[str] = None
    ) -> Optional[float]:
        """
        Get benchmark ROAS for platform and industry.
        
        Args:
            platform: Platform name
            industry: Industry category
        
        Returns:
            Benchmark ROAS or None
        """
        query = {"platform": platform}
        if industry:
            query["industry"] = industry
        
        # Get most recent benchmark
        benchmark = await self.db.system_benchmarks.find_one(
            query,
            sort=[("timestamp", -1)]
        )
        
        if benchmark:
            return benchmark.get("avg_roas", 0)
        
        return None
    
    def _estimate_impact(self, decision_type: DecisionType, budget_change_pct: float) -> str:
        """
        Estimate the impact of a decision.
        
        Args:
            decision_type: Type of decision
            budget_change_pct: Budget change percentage
        
        Returns:
            Impact estimate string
        """
        if decision_type == DecisionType.BUDGET_INCREASE:
            if abs(budget_change_pct) > 15:
                return f"Significant increase in impressions and potential conversions (+{budget_change_pct:.1f}% budget)"
            else:
                return f"Moderate increase in campaign reach (+{budget_change_pct:.1f}% budget)"
        
        elif decision_type == DecisionType.BUDGET_DECREASE:
            if abs(budget_change_pct) > 15:
                return f"Significant cost reduction with minimal impact ({budget_change_pct:.1f}% budget)"
            else:
                return f"Minor cost optimization ({budget_change_pct:.1f}% budget)"
        
        elif decision_type == DecisionType.PAUSE_CAMPAIGN:
            return "Stop spending on underperforming campaign"
        
        elif decision_type == DecisionType.ACTIVATE_CAMPAIGN:
            return "Resume campaign spending"
        
        else:
            return "Maintain current performance"
