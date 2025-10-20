"""Layer 5: Behavioral Economics

This layer identifies which cognitive biases and behavioral patterns are at play
in customer purchase decisions. It analyzes:
- Cognitive biases driving behavior
- Decision architecture (System 1 vs System 2)
- Behavioral levers for influence
- Decision drivers (emotional, rational, social)

Mock implementation for now - will integrate real behavioral analysis later.
"""

import logging
from typing import List, Dict, Any
from app.strategy_engine.analysis.models import (
    BehavioralDynamics,
    CognitiveBias,
    DecisionDriver,
    BehavioralLever
)

logger = logging.getLogger(__name__)


class BehavioralEconomics:
    """Analyzes behavioral economics patterns in customer decision-making."""

    def __init__(self):
        """Initialize the behavioral economics analyzer."""
        self.logger = logger

    async def identify_biases(self, purchase_data: Dict[str, Any]) -> BehavioralDynamics:
        """
        Identify which cognitive biases are active in purchase behavior.

        Args:
            purchase_data: Dictionary containing purchase behavior metrics

        Returns:
            BehavioralDynamics with identified biases and decision patterns
        """
        self.logger.info("Analyzing behavioral patterns from purchase data")

        # Extract decision speed
        decision_speed = self._determine_decision_speed(purchase_data)

        # Detect cognitive biases
        biases = await self.detect_cognitive_biases(purchase_data)
        dominant_bias_names = [b.bias_name for b in biases[:3]]  # Top 3

        # Analyze decision drivers
        drivers = await self.analyze_decision_drivers(purchase_data)

        # Suggest behavioral levers
        levers = await self.suggest_levers(dominant_bias_names)

        # Map decision architecture
        architecture = await self.map_decision_architecture(purchase_data)

        return BehavioralDynamics(
            dominant_biases=dominant_bias_names,
            decision_speed=decision_speed,
            primary_drivers=drivers,
            leverage_points=levers,
            decision_architecture=architecture
        )

    async def detect_cognitive_biases(self, patterns: Dict[str, Any]) -> List[CognitiveBias]:
        """
        Detect specific cognitive biases from behavioral patterns.

        Args:
            patterns: Dictionary of behavioral metrics and patterns

        Returns:
            List of detected cognitive biases with strength scores
        """
        self.logger.info("Detecting cognitive biases from behavioral patterns")

        detected_biases = []

        # Social Proof Detection
        if patterns.get("review_dependency") == "high" or patterns.get("peer_influence_score", 0) > 0.6:
            detected_biases.append(CognitiveBias(
                bias_name="social_proof",
                description="Customers rely heavily on what others think/do",
                strength=min(patterns.get("peer_influence_score", 0.7), 1.0),
                evidence=["High review dependency", "Strong peer influence"]
            ))

        # Anchoring Detection
        if patterns.get("first_seen_price_stickiness", 0) > 0.7:
            detected_biases.append(CognitiveBias(
                bias_name="anchoring",
                description="First price seen anchors subsequent price perceptions",
                strength=patterns.get("first_seen_price_stickiness", 0.8),
                evidence=["High price stickiness to first exposure"]
            ))

        # Scarcity/FOMO Detection
        if patterns.get("last_minute_purchases", 0) > 0.5 or patterns.get("impulse_purchase_rate", 0) > 0.4:
            detected_biases.append(CognitiveBias(
                bias_name="scarcity",
                description="Fear of missing out drives rushed decisions",
                strength=max(patterns.get("last_minute_purchases", 0.5), patterns.get("impulse_purchase_rate", 0.5)),
                evidence=["High impulse purchase rate", "Last-minute buying patterns"]
            ))

        # Authority Bias Detection
        if patterns.get("authority_bias", 0) > 0.6 or patterns.get("brand_loyalty") == "high":
            detected_biases.append(CognitiveBias(
                bias_name="authority",
                description="Trust in established brands or expert recommendations",
                strength=patterns.get("authority_bias", 0.7),
                evidence=["High brand loyalty", "Expert influence"]
            ))

        # Default Bias Detection
        if patterns.get("default_option_selection", 0) > 0.6:
            detected_biases.append(CognitiveBias(
                bias_name="default_bias",
                description="Strong tendency to select default or recommended options",
                strength=patterns.get("default_option_selection", 0.7),
                evidence=["High default option selection rate"]
            ))

        # Bandwagon Effect
        if patterns.get("social_validation_seeking", 0) > 0.7:
            detected_biases.append(CognitiveBias(
                bias_name="bandwagon_effect",
                description="Following what's popular or trending",
                strength=patterns.get("social_validation_seeking", 0.8),
                evidence=["High social validation seeking"]
            ))

        # Sort by strength
        detected_biases.sort(key=lambda x: x.strength, reverse=True)

        # If no specific biases detected, return defaults
        if not detected_biases:
            detected_biases = self._default_biases()

        return detected_biases

    async def analyze_decision_drivers(self, behavior_data: Dict[str, Any]) -> List[DecisionDriver]:
        """
        Analyze what drives customer decision-making.

        Args:
            behavior_data: Dictionary containing behavioral and decision data

        Returns:
            List of decision drivers categorized by type
        """
        self.logger.info("Analyzing decision drivers")

        drivers = []

        # Emotional Drivers
        emotional_triggers = behavior_data.get("emotional_triggers", [])
        if emotional_triggers or behavior_data.get("impulse_purchase_rate", 0) > 0.4:
            drivers.append(DecisionDriver(
                driver_name="emotional_resonance",
                category="emotional",
                importance=0.7,
                description="Emotional connection and feeling-driven purchases"
            ))

        # Rational Drivers
        rational_factors = behavior_data.get("rational_factors", [])
        if rational_factors or behavior_data.get("comparison_shopping_rate", 0) > 0.5:
            drivers.append(DecisionDriver(
                driver_name="rational_evaluation",
                category="rational",
                importance=0.6,
                description="Logical comparison and feature analysis"
            ))

        # Social Drivers
        social_factors = behavior_data.get("social_factors", [])
        if social_factors or behavior_data.get("peer_influence_score", 0) > 0.6:
            drivers.append(DecisionDriver(
                driver_name="social_validation",
                category="social",
                importance=0.8,
                description="Peer approval and social signaling"
            ))

        # If no drivers found, provide defaults
        if not drivers:
            drivers = self._default_drivers()

        return drivers

    async def suggest_levers(self, biases: List[str]) -> List[BehavioralLever]:
        """
        Suggest behavioral levers to influence behavior based on identified biases.

        Args:
            biases: List of identified cognitive bias names

        Returns:
            List of actionable behavioral levers
        """
        self.logger.info(f"Suggesting behavioral levers for biases: {biases}")

        levers = []

        for bias in biases:
            if bias == "social_proof" or bias == "bandwagon_effect":
                levers.append(BehavioralLever(
                    lever_name="social_proof_amplification",
                    bias_targeted=bias,
                    tactic="Display customer counts, reviews, testimonials prominently",
                    expected_impact="15-25% lift in conversion rate"
                ))

            elif bias == "anchoring":
                levers.append(BehavioralLever(
                    lever_name="strategic_anchoring",
                    bias_targeted=bias,
                    tactic="Show premium option first to anchor high, then present target option",
                    expected_impact="10-20% increase in AOV"
                ))

            elif bias == "scarcity":
                levers.append(BehavioralLever(
                    lever_name="scarcity_messaging",
                    bias_targeted=bias,
                    tactic="Limited time offers, low stock indicators, countdown timers",
                    expected_impact="20-35% urgency-driven conversions"
                ))

            elif bias == "authority":
                levers.append(BehavioralLever(
                    lever_name="authority_endorsement",
                    bias_targeted=bias,
                    tactic="Expert endorsements, certifications, brand heritage messaging",
                    expected_impact="10-15% trust-driven lift"
                ))

            elif bias == "default_bias":
                levers.append(BehavioralLever(
                    lever_name="strategic_defaults",
                    bias_targeted=bias,
                    tactic="Set desired option as default, use recommended tags",
                    expected_impact="30-40% increased selection of default"
                ))

        return levers

    async def map_decision_architecture(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map the decision architecture (System 1 fast thinking vs System 2 slow thinking).

        Args:
            behavior_data: Behavioral metrics

        Returns:
            Dictionary describing decision architecture
        """
        self.logger.info("Mapping decision architecture")

        impulse_rate = behavior_data.get("impulse_purchase_rate", 0.3)
        consideration_time = behavior_data.get("average_consideration_time", "1_day")
        comparison_rate = behavior_data.get("comparison_shopping_rate", 0.5)

        # Parse consideration time
        if "minute" in consideration_time or "hour" in consideration_time:
            time_score = 0.8  # Fast decision
        elif "day" in consideration_time:
            time_score = 0.5  # Medium decision
        else:
            time_score = 0.2  # Slow decision

        # Calculate System 1 dominance (fast, intuitive)
        system1_dominance = (impulse_rate + time_score + (1 - comparison_rate)) / 3

        # Determine dominant mode
        if system1_dominance > 0.6:
            dominant_mode = "impulse_driven"
            decision_speed = "fast"
        elif system1_dominance < 0.4:
            dominant_mode = "deliberative"
            decision_speed = "slow"
        else:
            dominant_mode = "mixed"
            decision_speed = "mixed"

        return {
            "system1_dominance": system1_dominance,
            "system2_dominance": 1 - system1_dominance,
            "dominant_mode": dominant_mode,
            "decision_speed": decision_speed
        }

    def _determine_decision_speed(self, purchase_data: Dict[str, Any]) -> str:
        """Determine if decisions are fast or slow."""
        consideration_time = purchase_data.get("average_consideration_time", "1_day")
        impulse_rate = purchase_data.get("impulse_purchase_rate", 0.3)

        if "minute" in consideration_time or "hour" in consideration_time or impulse_rate > 0.5:
            return "fast"
        elif "week" in consideration_time or "month" in consideration_time:
            return "slow"
        else:
            return "mixed"

    def _default_biases(self) -> List[CognitiveBias]:
        """Return default biases when none detected."""
        return [
            CognitiveBias(
                bias_name="social_proof",
                description="General tendency to look to others for validation",
                strength=0.6,
                evidence=["Default behavioral pattern"]
            ),
            CognitiveBias(
                bias_name="anchoring",
                description="First price seen influences perception",
                strength=0.5,
                evidence=["Common cognitive bias"]
            )
        ]

    def _default_drivers(self) -> List[DecisionDriver]:
        """Return default drivers when none detected."""
        return [
            DecisionDriver(
                driver_name="value_perception",
                category="rational",
                importance=0.7,
                description="Perceived value for money"
            ),
            DecisionDriver(
                driver_name="emotional_appeal",
                category="emotional",
                importance=0.6,
                description="Emotional connection to brand"
            )
        ]
