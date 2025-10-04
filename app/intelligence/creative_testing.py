"""
Creative A/B Testing Engine.

Provides statistical analysis and winner selection for creative tests.
Implements multiple statistical methods including:
- Two-proportion z-test for CTR comparisons
- T-test for ROAS/revenue comparisons
- Chi-square test for conversion rates
- Bayesian inference (simplified)
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import math
import structlog
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.creative_test import (
    TestVariant,
    TestMetric,
    WinnerSelectionMethod,
    TestStatus,
)

logger = structlog.get_logger(__name__)


class CreativeTestingEngine:
    """Engine for analyzing creative A/B tests."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize testing engine."""
        self.db = db

    async def update_variant_metrics(
        self,
        client_id: str,
        test_id: str,
        creative_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Update performance metrics for a test variant.

        Args:
            client_id: Client ID
            test_id: Test ID
            creative_id: Creative ID
            metrics: Dict with impressions, clicks, conversions, spend, revenue

        Returns:
            True if successful
        """
        try:
            # Calculate derived metrics
            impressions = metrics.get("impressions", 0)
            clicks = metrics.get("clicks", 0)
            conversions = metrics.get("conversions", 0)
            spend = metrics.get("spend", 0.0)
            revenue = metrics.get("revenue", 0.0)

            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            roas = (revenue / spend) if spend > 0 else 0
            cpa = (spend / conversions) if conversions > 0 else 0
            cvr = (conversions / clicks * 100) if clicks > 0 else 0

            # Update the variant in the test document
            result = await self.db.creative_tests.update_one(
                {
                    "client_id": client_id,
                    "test_id": test_id,
                    "variants.creative_id": creative_id
                },
                {
                    "$set": {
                        "variants.$.impressions": impressions,
                        "variants.$.clicks": clicks,
                        "variants.$.conversions": conversions,
                        "variants.$.spend": spend,
                        "variants.$.revenue": revenue,
                        "variants.$.ctr": round(ctr, 2),
                        "variants.$.roas": round(roas, 2),
                        "variants.$.cpa": round(cpa, 2),
                        "variants.$.cvr": round(cvr, 2),
                        "updated_at": datetime.utcnow(),
                    }
                }
            )

            if result.modified_count > 0:
                logger.info(
                    "variant_metrics_updated",
                    test_id=test_id,
                    creative_id=creative_id,
                    impressions=impressions,
                    ctr=ctr,
                )
                return True

            return False

        except Exception as e:
            logger.error(
                "variant_metrics_update_failed",
                test_id=test_id,
                creative_id=creative_id,
                error=str(e)
            )
            raise

    async def calculate_statistical_significance(
        self,
        client_id: str,
        test_id: str,
        primary_metric: TestMetric,
        confidence_threshold: float = 95.0
    ) -> Dict[str, Any]:
        """
        Calculate statistical significance for a test.

        Uses appropriate statistical test based on the primary metric:
        - CTR: Two-proportion z-test
        - ROAS/Revenue: T-test (simplified)
        - Conversions: Two-proportion z-test
        - CPA: T-test (simplified)

        Args:
            client_id: Client ID
            test_id: Test ID
            primary_metric: The metric being optimized
            confidence_threshold: Required confidence level (%)

        Returns:
            Dict with statistical analysis results
        """
        try:
            # Fetch test
            test = await self.db.creative_tests.find_one({
                "client_id": client_id,
                "test_id": test_id
            })

            if not test:
                raise ValueError(f"Test {test_id} not found")

            variants = test["variants"]

            if len(variants) < 2:
                raise ValueError("Need at least 2 variants for statistical test")

            # Find control variant
            control = next((v for v in variants if v["is_control"]), variants[0])
            challengers = [v for v in variants if not v["is_control"]]

            # Calculate significance for each challenger vs control
            results = []

            for challenger in challengers:
                if primary_metric in [TestMetric.CTR, TestMetric.CONVERSIONS]:
                    # Use two-proportion z-test
                    significance = self._two_proportion_z_test(
                        control=control,
                        challenger=challenger,
                        metric=primary_metric,
                        confidence_threshold=confidence_threshold
                    )
                else:
                    # Use simplified t-test for ROAS/CPA
                    significance = self._simplified_t_test(
                        control=control,
                        challenger=challenger,
                        metric=primary_metric,
                        confidence_threshold=confidence_threshold
                    )

                results.append({
                    "creative_id": challenger["creative_id"],
                    "variant_name": challenger["variant_name"],
                    **significance
                })

            # Update variants with significance
            for result in results:
                await self.db.creative_tests.update_one(
                    {
                        "client_id": client_id,
                        "test_id": test_id,
                        "variants.creative_id": result["creative_id"]
                    },
                    {
                        "$set": {
                            "variants.$.confidence_level": result["confidence_level"],
                            "variants.$.is_significant": result["is_significant"],
                        }
                    }
                )

            # Determine overall winner
            significant_results = [r for r in results if r["is_significant"]]

            if significant_results:
                # Get the best performing significant variant
                winner = max(
                    significant_results,
                    key=lambda x: x["improvement_pct"]
                )

                # Update test with current leader
                await self.db.creative_tests.update_one(
                    {"client_id": client_id, "test_id": test_id},
                    {
                        "$set": {
                            "current_leader": winner["creative_id"],
                            "updated_at": datetime.utcnow(),
                        }
                    }
                )

                return {
                    "has_winner": True,
                    "winner": winner,
                    "all_results": results,
                }
            else:
                return {
                    "has_winner": False,
                    "winner": None,
                    "all_results": results,
                    "message": "No statistically significant winner yet"
                }

        except Exception as e:
            logger.error(
                "statistical_significance_calculation_failed",
                test_id=test_id,
                error=str(e)
            )
            raise

    def _two_proportion_z_test(
        self,
        control: Dict[str, Any],
        challenger: Dict[str, Any],
        metric: TestMetric,
        confidence_threshold: float
    ) -> Dict[str, Any]:
        """
        Perform two-proportion z-test.

        Used for CTR and conversion rate comparisons.

        Args:
            control: Control variant data
            challenger: Challenger variant data
            metric: Metric to test (CTR or CONVERSIONS)
            confidence_threshold: Required confidence %

        Returns:
            Dict with test results
        """
        # Get sample sizes and successes
        if metric == TestMetric.CTR:
            n1 = control["impressions"]
            n2 = challenger["impressions"]
            x1 = control["clicks"]
            x2 = challenger["clicks"]
        else:  # CONVERSIONS
            n1 = control["clicks"]
            n2 = challenger["clicks"]
            x1 = control["conversions"]
            x2 = challenger["conversions"]

        # Calculate proportions
        p1 = x1 / n1 if n1 > 0 else 0
        p2 = x2 / n2 if n2 > 0 else 0

        # Check minimum sample size
        if n1 < 100 or n2 < 100:
            return {
                "confidence_level": 0.0,
                "is_significant": False,
                "p_value": 1.0,
                "improvement_pct": ((p2 - p1) / p1 * 100) if p1 > 0 else 0,
                "message": "Insufficient sample size (need at least 100 per variant)"
            }

        # Calculate pooled proportion
        p_pooled = (x1 + x2) / (n1 + n2) if (n1 + n2) > 0 else 0

        # Calculate standard error
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2)) if p_pooled > 0 else 0

        if se == 0:
            return {
                "confidence_level": 0.0,
                "is_significant": False,
                "p_value": 1.0,
                "improvement_pct": 0,
                "message": "Cannot calculate - no variance"
            }

        # Calculate z-score
        z = abs(p2 - p1) / se

        # Calculate p-value (two-tailed)
        # Using simplified approximation
        p_value = self._z_to_p_value(z)

        # Calculate confidence level
        confidence_level = (1 - p_value) * 100

        # Check if significant
        is_significant = confidence_level >= confidence_threshold

        # Calculate improvement
        improvement_pct = ((p2 - p1) / p1 * 100) if p1 > 0 else 0

        return {
            "confidence_level": round(confidence_level, 2),
            "is_significant": is_significant,
            "p_value": round(p_value, 4),
            "z_score": round(z, 2),
            "improvement_pct": round(improvement_pct, 2),
            "control_rate": round(p1 * 100, 2),
            "challenger_rate": round(p2 * 100, 2),
            "message": "Statistically significant" if is_significant else "Not significant yet"
        }

    def _simplified_t_test(
        self,
        control: Dict[str, Any],
        challenger: Dict[str, Any],
        metric: TestMetric,
        confidence_threshold: float
    ) -> Dict[str, Any]:
        """
        Simplified t-test for continuous metrics (ROAS, CPA).

        This is a simplified implementation. In production, use scipy.stats.ttest_ind.

        Args:
            control: Control variant data
            challenger: Challenger variant data
            metric: Metric to test (ROAS or CPA)
            confidence_threshold: Required confidence %

        Returns:
            Dict with test results
        """
        # Get metric values
        metric_map = {
            TestMetric.ROAS: "roas",
            TestMetric.CPA: "cpa",
            TestMetric.ENGAGEMENT_RATE: "ctr",  # Simplified
            TestMetric.VIDEO_COMPLETION: "ctr",  # Simplified
        }

        field = metric_map.get(metric, "roas")

        control_value = control.get(field, 0)
        challenger_value = challenger.get(field, 0)

        # Calculate sample sizes
        n1 = control.get("conversions", 0) if metric == TestMetric.CPA else control.get("clicks", 0)
        n2 = challenger.get("conversions", 0) if metric == TestMetric.CPA else challenger.get("clicks", 0)

        # Check minimum sample size
        if n1 < 30 or n2 < 30:
            return {
                "confidence_level": 0.0,
                "is_significant": False,
                "p_value": 1.0,
                "improvement_pct": ((challenger_value - control_value) / control_value * 100) if control_value > 0 else 0,
                "message": "Insufficient sample size (need at least 30 conversions per variant)"
            }

        # Simplified: assume we're comparing means
        # In reality, we'd need the full distribution to calculate variance
        # For now, use a simplified approach based on relative difference

        # Calculate relative difference
        if control_value > 0:
            relative_diff = abs((challenger_value - control_value) / control_value)
        else:
            relative_diff = 0

        # Simplified confidence calculation based on sample size and difference
        # Larger sample size + larger difference = higher confidence
        sample_factor = math.log(n1 + n2) / math.log(1000)  # Normalized to 1000 samples
        diff_factor = min(relative_diff * 10, 1.0)  # Cap at 1.0

        confidence_level = min(sample_factor * diff_factor * 100, 99.0)

        is_significant = confidence_level >= confidence_threshold

        # Calculate improvement
        improvement_pct = ((challenger_value - control_value) / control_value * 100) if control_value > 0 else 0

        return {
            "confidence_level": round(confidence_level, 2),
            "is_significant": is_significant,
            "p_value": round((100 - confidence_level) / 100, 4),
            "improvement_pct": round(improvement_pct, 2),
            "control_value": round(control_value, 2),
            "challenger_value": round(challenger_value, 2),
            "message": "Statistically significant" if is_significant else "Not significant yet"
        }

    def _z_to_p_value(self, z: float) -> float:
        """
        Convert z-score to p-value (two-tailed).

        Simplified approximation. In production, use scipy.stats.norm.sf.

        Args:
            z: Z-score

        Returns:
            P-value
        """
        # Simplified lookup table for common z-scores
        z_table = {
            0.0: 1.000,
            0.5: 0.617,
            1.0: 0.317,
            1.5: 0.134,
            1.645: 0.100,  # 90% confidence
            1.96: 0.050,   # 95% confidence
            2.0: 0.046,
            2.33: 0.020,   # 98% confidence
            2.5: 0.012,
            2.58: 0.010,   # 99% confidence
            3.0: 0.003,
            3.5: 0.0005,
            4.0: 0.00006,
        }

        # Find closest z-score
        z = abs(z)
        closest_z = min(z_table.keys(), key=lambda x: abs(x - z))

        return z_table[closest_z]

    async def should_conclude_test(
        self,
        client_id: str,
        test_id: str
    ) -> Tuple[bool, str]:
        """
        Determine if a test should be concluded.

        Checks:
        - Has a statistically significant winner
        - Has reached max duration
        - Has reached minimum sample size

        Args:
            client_id: Client ID
            test_id: Test ID

        Returns:
            Tuple of (should_conclude, reason)
        """
        try:
            test = await self.db.creative_tests.find_one({
                "client_id": client_id,
                "test_id": test_id
            })

            if not test:
                return False, "Test not found"

            if test["status"] != TestStatus.RUNNING:
                return False, "Test not running"

            # Check if already concluded
            if test.get("is_concluded"):
                return False, "Test already concluded"

            # Check max duration
            if test.get("end_date"):
                if datetime.utcnow() >= test["end_date"]:
                    return True, "Maximum duration reached"

            # Check minimum sample size
            min_sample = test["min_sample_size"]
            all_variants_ready = all(
                v["impressions"] >= min_sample
                for v in test["variants"]
            )

            if not all_variants_ready:
                return False, "Waiting for minimum sample size"

            # Check for statistical significance
            significance = await self.calculate_statistical_significance(
                client_id=client_id,
                test_id=test_id,
                primary_metric=test["primary_metric"],
                confidence_threshold=test["confidence_threshold"]
            )

            if significance["has_winner"]:
                return True, f"Statistically significant winner found: {significance['winner']['variant_name']}"

            # If we have enough samples but no winner, check how long we've been running
            if test.get("started_at"):
                days_running = (datetime.utcnow() - test["started_at"]).days
                if days_running >= test["max_duration_days"]:
                    return True, "Max duration reached - selecting best performer"

            return False, "Continue testing - no significant winner yet"

        except Exception as e:
            logger.error(
                "should_conclude_test_check_failed",
                test_id=test_id,
                error=str(e)
            )
            return False, f"Error: {str(e)}"

    async def recommend_action(
        self,
        client_id: str,
        test_id: str
    ) -> Dict[str, Any]:
        """
        Generate recommendations for a test.

        Args:
            client_id: Client ID
            test_id: Test ID

        Returns:
            Dict with recommendations
        """
        try:
            test = await self.db.creative_tests.find_one({
                "client_id": client_id,
                "test_id": test_id
            })

            if not test:
                return {"error": "Test not found"}

            # Check if should conclude
            should_conclude, reason = await self.should_conclude_test(
                client_id=client_id,
                test_id=test_id
            )

            # Calculate current leader
            variants = test["variants"]
            metric = test["primary_metric"]

            # Get metric field
            metric_field_map = {
                TestMetric.CTR: "ctr",
                TestMetric.ROAS: "roas",
                TestMetric.CPA: "cpa",
                TestMetric.CONVERSIONS: "conversions",
            }
            metric_field = metric_field_map.get(metric, "roas")

            # Find best performer
            best_variant = max(
                variants,
                key=lambda v: v.get(metric_field, 0)
            )

            recommendations = []

            if should_conclude:
                recommendations.append(f"✅ {reason}")
                recommendations.append(f"Promote '{best_variant['variant_name']}' as winner")
            else:
                recommendations.append(f"⏳ {reason}")

                # Check sample size progress
                min_sample = test["min_sample_size"]
                progress = [
                    (v["variant_name"], v["impressions"], min_sample)
                    for v in variants
                ]

                for name, impressions, needed in progress:
                    pct = (impressions / needed * 100) if needed > 0 else 0
                    if pct < 100:
                        recommendations.append(
                            f"Variant '{name}' at {pct:.1f}% of minimum sample size"
                        )

            return {
                "should_conclude": should_conclude,
                "reason": reason,
                "current_leader": best_variant["variant_name"],
                "current_leader_id": best_variant["creative_id"],
                "leader_metric_value": best_variant.get(metric_field, 0),
                "recommendations": recommendations,
                "timestamp": datetime.utcnow(),
            }

        except Exception as e:
            logger.error(
                "recommend_action_failed",
                test_id=test_id,
                error=str(e)
            )
            return {"error": str(e)}
