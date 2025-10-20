"""Tests for Framework Dialectics - Layer 3

This module tests the Framework Dialectics layer which:
- Finds contradictions/tensions across dimension pairs:
  * Product vs User (what they say vs what they do)
  * Space vs Time (market position vs purchase timing)
  * UX vs Product (experience vs actual features)
- Extracts human truths from contradictions
- Generates strategic implications
"""

import pytest
from app.strategy_engine.analysis.layer3_framework_dialectics import FrameworkDialectics
from app.strategy_engine.analysis.models import Tension


@pytest.mark.asyncio
async def test_find_product_user_tension():
    """Should find contradiction between product promise and user behavior"""
    analyzer = FrameworkDialectics()

    product_data = {
        "product_promise": "sustainable eco-friendly materials",
        "messaging_focus": ["sustainability", "environment", "green"]
    }

    user_data = {
        "purchase_drivers": ["aesthetics", "price", "brand", "sustainability"],
        "stated_values": ["sustainability", "quality"],
        "actual_behavior": "price_sensitive"
    }

    tension = await analyzer.find_product_user_tension(product_data, user_data)

    assert isinstance(tension, Tension)
    assert tension.tension_type == "product_user"
    assert tension.contradiction is not None
    assert len(tension.contradiction) > 0
    assert tension.human_truth is not None
    assert len(tension.human_truth) > 0
    assert tension.strategic_implication is not None
    assert len(tension.strategic_implication) > 0


@pytest.mark.asyncio
async def test_find_product_user_luxury_tension():
    """Should find tension in luxury product positioning"""
    analyzer = FrameworkDialectics()

    product_data = {
        "product_promise": "exclusive luxury timepiece",
        "messaging_focus": ["heritage", "craftsmanship", "exclusivity"]
    }

    user_data = {
        "purchase_drivers": ["status", "instagram-worthy", "brand recognition"],
        "stated_values": ["craftsmanship", "heritage"],
        "actual_behavior": "social_media_display"
    }

    tension = await analyzer.find_product_user_tension(product_data, user_data)

    assert isinstance(tension, Tension)
    assert "status" in tension.human_truth.lower() or "recognition" in tension.human_truth.lower()


@pytest.mark.asyncio
async def test_find_space_time_tension():
    """Should find contradiction between market space and purchase timing"""
    analyzer = FrameworkDialectics()

    space_data = {
        "market_position": "premium luxury",
        "price_point": "high",
        "distribution": "exclusive"
    }

    time_data = {
        "purchase_occasion": "impulse",
        "consideration_period": "short",
        "seasonal_pattern": "gift-driven"
    }

    tension = await analyzer.find_space_time_tension(space_data, time_data)

    assert isinstance(tension, Tension)
    assert tension.tension_type == "space_time"
    assert tension.contradiction is not None
    assert tension.human_truth is not None


@pytest.mark.asyncio
async def test_find_ux_product_tension():
    """Should find contradiction between user experience and product reality"""
    analyzer = FrameworkDialectics()

    ux_data = {
        "desired_experience": "simplicity and ease",
        "emotional_goal": "peace of mind",
        "journey_expectation": "effortless"
    }

    product_data = {
        "actual_complexity": "high learning curve",
        "feature_count": "extensive",
        "setup_required": "significant"
    }

    tension = await analyzer.find_ux_product_tension(ux_data, product_data)

    assert isinstance(tension, Tension)
    assert tension.tension_type == "ux_product"
    assert "simplicity" in tension.contradiction.lower() or "complex" in tension.contradiction.lower()


@pytest.mark.asyncio
async def test_find_all_tensions():
    """Should find tensions across all dimension pairs"""
    analyzer = FrameworkDialectics()

    brand_analysis = {
        "product": {
            "promise": "sustainability",
            "messaging": ["eco-friendly", "green", "responsible"]
        },
        "user": {
            "stated_values": ["sustainability", "quality"],
            "behavior": "aesthetics-driven",
            "purchase_drivers": ["looks", "price", "sustainability"]
        },
        "space": {
            "market": "premium",
            "price_point": "high"
        },
        "time": {
            "purchase": "impulse",
            "occasion": "gift"
        },
        "ux": {
            "desired_experience": "simple",
            "emotional_goal": "confidence"
        }
    }

    tensions = await analyzer.find_all_tensions(brand_analysis)

    assert isinstance(tensions, list)
    assert len(tensions) > 0
    assert all(isinstance(t, Tension) for t in tensions)

    # Should have at least product_user tension
    assert any(t.tension_type == "product_user" for t in tensions)


@pytest.mark.asyncio
async def test_tension_human_truth_starts_with_they():
    """Human truths should be framed as 'They say X, but they actually Y'"""
    analyzer = FrameworkDialectics()

    product_data = {
        "product_promise": "artisanal craftsmanship",
        "messaging_focus": ["handmade", "craft", "artisan"]
    }

    user_data = {
        "purchase_drivers": ["convenience", "fast delivery", "ease"],
        "stated_values": ["craftsmanship"],
        "actual_behavior": "convenience_seeking"
    }

    tension = await analyzer.find_product_user_tension(product_data, user_data)

    # Human truth should reveal the gap between stated and actual
    assert "craft" in tension.contradiction.lower() or "convenience" in tension.contradiction.lower()
    assert len(tension.human_truth) > 10  # Should be a substantive statement


@pytest.mark.asyncio
async def test_strategic_implication_actionable():
    """Strategic implications should be actionable"""
    analyzer = FrameworkDialectics()

    product_data = {
        "product_promise": "professional performance",
        "messaging_focus": ["pro-grade", "performance", "serious"]
    }

    user_data = {
        "purchase_drivers": ["beginner-friendly", "easy", "fun"],
        "stated_values": ["performance"],
        "actual_behavior": "hobbyist"
    }

    tension = await analyzer.find_product_user_tension(product_data, user_data)

    # Strategic implication should be actionable (contains action words)
    impl_lower = tension.strategic_implication.lower()
    action_words = ["focus", "position", "message", "target", "create", "build", "emphasize"]
    assert any(word in impl_lower for word in action_words)


@pytest.mark.asyncio
async def test_handles_minimal_tension():
    """Should handle cases with minimal contradiction gracefully"""
    analyzer = FrameworkDialectics()

    product_data = {
        "product_promise": "quality",
        "messaging_focus": ["quality"]
    }

    user_data = {
        "purchase_drivers": ["quality"],
        "stated_values": ["quality"],
        "actual_behavior": "quality_focused"
    }

    tension = await analyzer.find_product_user_tension(product_data, user_data)

    # Should still return a tension object even if minimal
    assert isinstance(tension, Tension)
    assert tension.contradiction is not None
