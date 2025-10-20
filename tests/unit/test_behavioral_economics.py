"""Tests for Layer 5: Behavioral Economics

This layer identifies which cognitive biases and behavioral patterns are at play
in customer purchase decisions.
"""

import pytest
from app.strategy_engine.analysis.layer5_behavioral_economics import (
    BehavioralEconomics,
    BehavioralDynamics,
    CognitiveBias,
    DecisionDriver
)


@pytest.mark.asyncio
async def test_identify_active_biases():
    """Should identify which cognitive biases are at play in purchase behavior."""

    # Sample purchase behavior data
    purchase_data = {
        "average_consideration_time": "2_hours",  # Fast decision
        "review_dependency": "high",  # Social proof seeking
        "price_sensitivity": "medium",
        "brand_loyalty": "low",
        "impulse_purchase_rate": 0.45,
        "peer_influence_score": 0.78
    }

    analyzer = BehavioralEconomics()
    dynamics = await analyzer.identify_biases(purchase_data)

    # Assertions
    assert isinstance(dynamics, BehavioralDynamics)
    assert len(dynamics.dominant_biases) > 0
    assert "social_proof" in dynamics.dominant_biases or "bandwagon_effect" in dynamics.dominant_biases
    assert dynamics.decision_speed in ["fast", "slow", "mixed"]


@pytest.mark.asyncio
async def test_analyze_decision_drivers():
    """Should analyze what drives customer decision-making."""

    behavior_data = {
        "emotional_triggers": ["fear_of_missing_out", "desire_for_status"],
        "rational_factors": ["price_comparison", "feature_checklist"],
        "social_factors": ["influencer_recommendations", "peer_reviews"]
    }

    analyzer = BehavioralEconomics()
    drivers = await analyzer.analyze_decision_drivers(behavior_data)

    # Assertions
    assert len(drivers) > 0
    assert all(isinstance(d, DecisionDriver) for d in drivers)
    assert any(d.category == "emotional" for d in drivers)
    assert any(d.category == "rational" for d in drivers)
    assert any(d.category == "social" for d in drivers)


@pytest.mark.asyncio
async def test_suggest_behavioral_levers():
    """Should suggest levers to influence behavior based on identified biases."""

    biases = ["anchoring", "scarcity", "social_proof"]

    analyzer = BehavioralEconomics()
    levers = await analyzer.suggest_levers(biases)

    # Assertions
    assert len(levers) > 0
    assert "anchoring" in str(levers).lower() or "price_anchor" in str(levers).lower()
    assert "scarcity" in str(levers).lower() or "limited_time" in str(levers).lower()


@pytest.mark.asyncio
async def test_cognitive_bias_detection():
    """Should detect specific cognitive biases from behavioral patterns."""

    patterns = {
        "first_seen_price_stickiness": 0.82,  # Anchoring
        "last_minute_purchases": 0.65,  # Scarcity/FOMO
        "review_count_correlation": 0.89,  # Social proof
        "premium_option_preference": 0.45  # Decoy effect potential
    }

    analyzer = BehavioralEconomics()
    biases = await analyzer.detect_cognitive_biases(patterns)

    # Assertions
    assert len(biases) > 0
    assert any(b.bias_name == "anchoring" for b in biases)
    assert any(b.strength > 0.5 for b in biases)


@pytest.mark.asyncio
async def test_behavioral_dynamics_complete():
    """Should generate complete behavioral dynamics analysis."""

    purchase_data = {
        "average_consideration_time": "1_day",
        "review_dependency": "high",
        "price_sensitivity": "low",
        "brand_loyalty": "high",
        "impulse_purchase_rate": 0.15,
        "peer_influence_score": 0.45,
        "rational_vs_emotional": "60_40"  # 60% rational, 40% emotional
    }

    analyzer = BehavioralEconomics()
    dynamics = await analyzer.identify_biases(purchase_data)

    # Comprehensive assertions
    assert dynamics.dominant_biases is not None
    assert len(dynamics.dominant_biases) > 0
    assert dynamics.decision_speed in ["fast", "slow", "mixed"]
    assert hasattr(dynamics, "primary_drivers")
    assert hasattr(dynamics, "leverage_points")


@pytest.mark.asyncio
async def test_bias_strength_scoring():
    """Should score the strength of each identified bias."""

    patterns = {
        "social_validation_seeking": 0.95,  # Very strong
        "price_anchoring": 0.35,  # Weak
        "authority_bias": 0.72  # Strong
    }

    analyzer = BehavioralEconomics()
    biases = await analyzer.detect_cognitive_biases(patterns)

    # Check strength scoring
    social_proof_bias = next((b for b in biases if "social" in b.bias_name.lower()), None)
    if social_proof_bias:
        assert social_proof_bias.strength > 0.7


@pytest.mark.asyncio
async def test_decision_architecture_mapping():
    """Should map the decision architecture (fast vs slow thinking)."""

    behavior_data = {
        "impulse_purchase_rate": 0.65,
        "average_consideration_time": "15_minutes",
        "comparison_shopping_rate": 0.25,
        "deliberation_indicators": ["feature_comparison", "review_reading"]
    }

    analyzer = BehavioralEconomics()
    architecture = await analyzer.map_decision_architecture(behavior_data)

    # Assertions
    assert architecture["system1_dominance"] > 0.5  # Fast thinking dominant
    assert architecture["decision_speed"] == "fast"
    assert "impulse" in architecture["dominant_mode"].lower()
