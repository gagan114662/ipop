"""
Creative Optimizer - Fatigue Detection and Auto-Pause.

Monitors creative performance and automatically:
- Detects creative fatigue (declining CTR, engagement)
- Pauses underperforming creatives
- Recommends creative refreshes
- Rotates creatives based on strategy
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import structlog
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.creative import CreativeStatus

logger = structlog.get_logger(__name__)


class CreativeOptimizer:
    """Optimizer for creative performance management."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize creative optimizer."""
        self.db = db

    async def detect_creative_fatigue(
        self,
        client_id: str,
        creative_id: str,
        days: int = 14
    ) -> Dict[str, Any]:
        """
        Detect if a creative is experiencing fatigue.

        Fatigue indicators:
        1. CTR declining over time (comparing first half vs second half)
        2. Engagement rate declining
        3. Frequency increasing (showing too often to same users)
        4. Relevance score declining (if available)

        Args:
            client_id: Client ID
            creative_id: Creative ID
            days: Days to analyze (default 14)

        Returns:
            Dict with fatigue analysis
        """
        try:
            # Get creative
            creative = await self.db.creatives.find_one({
                "client_id": client_id,
                "creative_id": creative_id
            })

            if not creative:
                raise ValueError(f"Creative {creative_id} not found")

            # Get time-series metrics
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            metrics = await self.db.creative_metrics.find({
                "client_id": client_id,
                "creative_id": creative_id,
                "date": {"$gte": start_date, "$lte": end_date}
            }).sort("date", 1).to_list(length=days)

            if len(metrics) < 7:
                return {
                    "is_fatigued": False,
                    "fatigue_score": 0,
                    "confidence": "low",
                    "reason": f"Insufficient data (need 7+ days, have {len(metrics)})",
                    "recommendation": "Continue gathering data"
                }

            # Split into first half and second half
            midpoint = len(metrics) // 2
            first_half = metrics[:midpoint]
            second_half = metrics[midpoint:]

            # Calculate average CTR for each half
            first_half_ctr = sum(m["ctr"] for m in first_half) / len(first_half) if first_half else 0
            second_half_ctr = sum(m["ctr"] for m in second_half) / len(second_half) if second_half else 0

            # Calculate average engagement rate
            first_half_engagement = sum(m.get("engagement_rate", 0) for m in first_half) / len(first_half) if first_half else 0
            second_half_engagement = sum(m.get("engagement_rate", 0) for m in second_half) / len(second_half) if second_half else 0

            # Calculate average frequency
            first_half_frequency = sum(m.get("frequency", 0) for m in first_half) / len(first_half) if first_half else 0
            second_half_frequency = sum(m.get("frequency", 0) for m in second_half) / len(second_half) if second_half else 0

            # Calculate trends
            ctr_decline_pct = 0
            if first_half_ctr > 0:
                ctr_decline_pct = ((second_half_ctr - first_half_ctr) / first_half_ctr) * 100

            engagement_decline_pct = 0
            if first_half_engagement > 0:
                engagement_decline_pct = ((second_half_engagement - first_half_engagement) / first_half_engagement) * 100

            frequency_increase_pct = 0
            if first_half_frequency > 0:
                frequency_increase_pct = ((second_half_frequency - first_half_frequency) / first_half_frequency) * 100

            # Calculate fatigue score (0-100)
            fatigue_score = 0

            # CTR declining is a strong signal (0-40 points)
            if ctr_decline_pct < -20:
                fatigue_score += 40
            elif ctr_decline_pct < -10:
                fatigue_score += 25
            elif ctr_decline_pct < -5:
                fatigue_score += 10

            # Engagement declining (0-30 points)
            if engagement_decline_pct < -20:
                fatigue_score += 30
            elif engagement_decline_pct < -10:
                fatigue_score += 20
            elif engagement_decline_pct < -5:
                fatigue_score += 10

            # Frequency increasing (0-30 points)
            if frequency_increase_pct > 50:
                fatigue_score += 30
            elif frequency_increase_pct > 30:
                fatigue_score += 20
            elif frequency_increase_pct > 15:
                fatigue_score += 10

            # Determine if fatigued (threshold: 50)
            is_fatigued = fatigue_score >= 50

            # Determine confidence
            if len(metrics) >= 14:
                confidence = "high"
            elif len(metrics) >= 10:
                confidence = "medium"
            else:
                confidence = "low"

            # Generate recommendation
            if is_fatigued:
                if fatigue_score >= 75:
                    recommendation = "⚠️ High fatigue - pause creative and create new variant"
                else:
                    recommendation = "⚠️ Moderate fatigue - consider rotating to different creative"
            else:
                if ctr_decline_pct < 0:
                    recommendation = "✓ Slight decline detected - monitor closely"
                else:
                    recommendation = "✓ Creative performing well - continue"

            # Build reason
            reasons = []
            if ctr_decline_pct < -5:
                reasons.append(f"CTR declined {abs(ctr_decline_pct):.1f}%")
            if engagement_decline_pct < -5:
                reasons.append(f"Engagement declined {abs(engagement_decline_pct):.1f}%")
            if frequency_increase_pct > 15:
                reasons.append(f"Frequency increased {frequency_increase_pct:.1f}%")

            reason = ", ".join(reasons) if reasons else "No significant fatigue signals"

            result = {
                "is_fatigued": is_fatigued,
                "fatigue_score": round(fatigue_score, 1),
                "confidence": confidence,
                "reason": reason,
                "recommendation": recommendation,

                # Detailed metrics
                "ctr_trend": {
                    "first_half_avg": round(first_half_ctr, 2),
                    "second_half_avg": round(second_half_ctr, 2),
                    "change_pct": round(ctr_decline_pct, 2),
                },
                "engagement_trend": {
                    "first_half_avg": round(first_half_engagement, 2),
                    "second_half_avg": round(second_half_engagement, 2),
                    "change_pct": round(engagement_decline_pct, 2),
                },
                "frequency_trend": {
                    "first_half_avg": round(first_half_frequency, 2),
                    "second_half_avg": round(second_half_frequency, 2),
                    "change_pct": round(frequency_increase_pct, 2),
                },

                "days_analyzed": len(metrics),
                "timestamp": datetime.utcnow(),
            }

            logger.info(
                "creative_fatigue_analyzed",
                client_id=client_id,
                creative_id=creative_id,
                is_fatigued=is_fatigued,
                fatigue_score=fatigue_score,
            )

            return result

        except Exception as e:
            logger.error(
                "creative_fatigue_detection_failed",
                creative_id=creative_id,
                error=str(e)
            )
            raise

    async def auto_pause_underperformers(
        self,
        client_id: str,
        campaign_id: Optional[str] = None,
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Automatically pause creatives that are underperforming.

        Pauses creatives that:
        1. Are below min_ctr threshold
        2. Are below min_roas threshold
        3. Have high fatigue score (>70)

        Args:
            client_id: Client ID
            campaign_id: Optional campaign to limit to
            dry_run: If True, only return what would be paused

        Returns:
            List of paused (or would-be-paused) creatives
        """
        try:
            # Build query
            query = {
                "client_id": client_id,
                "status": CreativeStatus.ACTIVE,
            }

            if campaign_id:
                query["campaign_ids"] = campaign_id

            # Get all active creatives
            creatives = await self.db.creatives.find(query).to_list(length=1000)

            paused = []

            for creative in creatives:
                should_pause = False
                reason = []

                creative_id = creative["creative_id"]
                current_perf = creative.get("current_performance", {})

                # Check min_ctr threshold
                min_ctr = creative.get("min_ctr")
                if min_ctr and current_perf.get("ctr", 0) < min_ctr:
                    should_pause = True
                    reason.append(f"CTR {current_perf.get('ctr', 0):.2f}% below threshold {min_ctr}%")

                # Check min_roas threshold
                min_roas = creative.get("min_roas")
                if min_roas and current_perf.get("roas", 0) < min_roas:
                    should_pause = True
                    reason.append(f"ROAS {current_perf.get('roas', 0):.2f} below threshold {min_roas}")

                # Check fatigue
                fatigue = await self.detect_creative_fatigue(
                    client_id=client_id,
                    creative_id=creative_id,
                    days=settings.CREATIVE_HISTORY_DAYS
                )

                if fatigue.get("fatigue_score", 0) >= 70:
                    should_pause = True
                    reason.append(f"High fatigue score ({fatigue['fatigue_score']:.1f})")

                if should_pause:
                    pause_info = {
                        "creative_id": creative_id,
                        "creative_name": creative["name"],
                        "reason": ", ".join(reason),
                        "current_ctr": current_perf.get("ctr", 0),
                        "current_roas": current_perf.get("roas", 0),
                        "fatigue_score": fatigue.get("fatigue_score", 0),
                        "timestamp": datetime.utcnow(),
                    }

                    if not dry_run:
                        # Actually pause the creative
                        await self.db.creatives.update_one(
                            {"client_id": client_id, "creative_id": creative_id},
                            {
                                "$set": {
                                    "status": CreativeStatus.PAUSED,
                                    "paused_at": datetime.utcnow(),
                                    "updated_at": datetime.utcnow(),
                                }
                            }
                        )

                        logger.info(
                            "creative_auto_paused",
                            client_id=client_id,
                            creative_id=creative_id,
                            reason=", ".join(reason)
                        )

                        pause_info["paused"] = True
                    else:
                        pause_info["paused"] = False

                    paused.append(pause_info)

            logger.info(
                "auto_pause_completed",
                client_id=client_id,
                campaign_id=campaign_id,
                paused_count=len(paused),
                dry_run=dry_run
            )

            return paused

        except Exception as e:
            logger.error(
                "auto_pause_failed",
                client_id=client_id,
                error=str(e)
            )
            raise

    async def recommend_creative_rotation(
        self,
        client_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """
        Recommend which creative should be active based on rotation strategy.

        Strategies:
        1. Even: Equal rotation (round-robin)
        2. Optimized: More traffic to better performers
        3. Explore/Exploit: Balance learning vs winning (Thompson Sampling)

        Args:
            client_id: Client ID
            campaign_id: Campaign ID

        Returns:
            Dict with rotation recommendation
        """
        try:
            # Get campaign
            campaign = await self.db.campaigns.find_one({
                "client_id": client_id,
                "campaign_id": campaign_id
            })

            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")

            creative_ids = campaign.get("creative_ids", [])
            strategy = campaign.get("creative_rotation_strategy", "optimized")
            current_primary = campaign.get("primary_creative_id")

            if not creative_ids:
                return {
                    "recommendation": None,
                    "reason": "No creatives linked to campaign",
                    "strategy": strategy
                }

            # Get all linked creatives
            creatives = await self.db.creatives.find({
                "client_id": client_id,
                "creative_id": {"$in": creative_ids},
                "status": {"$in": [CreativeStatus.ACTIVE, CreativeStatus.TESTING]}
            }).to_list(length=100)

            if not creatives:
                return {
                    "recommendation": None,
                    "reason": "No active creatives available",
                    "strategy": strategy
                }

            if strategy == "even":
                # Round-robin: rotate to next creative
                if current_primary:
                    try:
                        current_idx = creative_ids.index(current_primary)
                        next_idx = (current_idx + 1) % len(creative_ids)
                        next_creative = creative_ids[next_idx]
                    except ValueError:
                        next_creative = creative_ids[0]
                else:
                    next_creative = creative_ids[0]

                return {
                    "recommendation": next_creative,
                    "reason": "Round-robin rotation (even strategy)",
                    "strategy": strategy,
                    "all_creatives": creative_ids
                }

            elif strategy == "optimized":
                # Select best performer by ROAS
                best_creative = max(
                    creatives,
                    key=lambda c: c.get("current_performance", {}).get("roas", 0)
                )

                return {
                    "recommendation": best_creative["creative_id"],
                    "reason": f"Best ROAS: {best_creative.get('current_performance', {}).get('roas', 0):.2f}",
                    "strategy": strategy,
                    "performance": {
                        c["creative_id"]: c.get("current_performance", {}).get("roas", 0)
                        for c in creatives
                    }
                }

            elif strategy == "explore_exploit":
                # Thompson Sampling for multi-armed bandit
                # Simplified: 80% to best performer, 20% explore others
                import random

                if random.random() < 0.8:
                    # Exploit: choose best
                    best_creative = max(
                        creatives,
                        key=lambda c: c.get("current_performance", {}).get("roas", 0)
                    )
                    recommendation = best_creative["creative_id"]
                    reason = f"Exploit best performer (ROAS: {best_creative.get('current_performance', {}).get('roas', 0):.2f})"
                else:
                    # Explore: choose randomly
                    explore_creative = random.choice(creatives)
                    recommendation = explore_creative["creative_id"]
                    reason = "Explore alternative creative"

                return {
                    "recommendation": recommendation,
                    "reason": reason,
                    "strategy": strategy,
                }

            else:
                # Unknown strategy - default to optimized
                best_creative = max(
                    creatives,
                    key=lambda c: c.get("current_performance", {}).get("roas", 0)
                )

                return {
                    "recommendation": best_creative["creative_id"],
                    "reason": f"Unknown strategy '{strategy}' - defaulting to optimized",
                    "strategy": "optimized",
                }

        except Exception as e:
            logger.error(
                "creative_rotation_recommendation_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise

    async def optimize_all_campaigns(
        self,
        client_id: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Run optimizer across all campaigns for a client.

        Actions:
        1. Detect and pause fatigued creatives
        2. Auto-pause underperformers
        3. Rotate creatives based on strategy

        Args:
            client_id: Client ID
            dry_run: If True, only report what would be done

        Returns:
            Dict with optimization results
        """
        try:
            # Get all active campaigns
            campaigns = await self.db.campaigns.find({
                "client_id": client_id,
                "status": "active"
            }).to_list(length=1000)

            results = {
                "campaigns_analyzed": len(campaigns),
                "creatives_paused": [],
                "rotations_recommended": [],
                "timestamp": datetime.utcnow(),
                "dry_run": dry_run,
            }

            # Auto-pause underperformers across all campaigns
            paused = await self.auto_pause_underperformers(
                client_id=client_id,
                dry_run=dry_run
            )
            results["creatives_paused"] = paused

            # Recommend rotations for each campaign
            for campaign in campaigns:
                campaign_id = campaign["campaign_id"]
                rotation = await self.recommend_creative_rotation(
                    client_id=client_id,
                    campaign_id=campaign_id
                )

                if rotation.get("recommendation"):
                    results["rotations_recommended"].append({
                        "campaign_id": campaign_id,
                        "campaign_name": campaign["name"],
                        "recommended_creative": rotation["recommendation"],
                        "reason": rotation["reason"],
                        "strategy": rotation["strategy"],
                    })

            logger.info(
                "campaign_optimization_completed",
                client_id=client_id,
                campaigns_analyzed=len(campaigns),
                creatives_paused=len(paused),
                rotations_recommended=len(results["rotations_recommended"]),
                dry_run=dry_run
            )

            return results

        except Exception as e:
            logger.error(
                "campaign_optimization_failed",
                client_id=client_id,
                error=str(e)
            )
            raise
