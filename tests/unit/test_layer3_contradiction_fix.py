"""
Tests for Layer 3 empty contradiction strings fix.

Validates robust data extraction and meaningful fallback values.
"""
import pytest
from app.strategy_engine.analysis.layer3_framework_dialectics import FrameworkDialectics


@pytest.mark.asyncio
async def test_product_user_tension_with_complete_data():
    """Should generate meaningful tension with complete data"""
    analyzer = FrameworkDialectics()

    product_data = {
        "product_promise": "luxury craftsmanship",
        "messaging_focus": ["premium quality", "exclusive designs"]
    }

    user_data = {
        "purchase_drivers": ["status", "social proof", "quality"],
        "stated_values": ["sustainability", "quality"],
        "actual_behavior": "buys for social status"
    }

    tension = await analyzer.find_product_user_tension(product_data, user_data)

    assert tension.contradiction != ""
    assert "luxury craftsmanship" in tension.contradiction or "status" in tension.contradiction
    assert tension.human_truth != ""
    assert tension.strategic_implication != ""


@pytest.mark.asyncio
async def test_product_user_tension_with_missing_data():
    """Should generate meaningful tension even with missing data"""
    analyzer = FrameworkDialectics()

    product_data = {
        "product_promise": "",
        "messaging_focus": []
    }

    user_data = {
        "purchase_drivers": [],
        "stated_values": [],
        "actual_behavior": ""
    }

    tension = await analyzer.find_product_user_tension(product_data, user_data)

    # Should have fallback values, not empty strings
    assert tension.contradiction != ""
    assert "Brand emphasizes ''" not in tension.contradiction
    assert tension.human_truth != ""
    assert tension.strategic_implication != ""


@pytest.mark.asyncio
async def test_space_time_tension_with_complete_data():
    """Should generate meaningful space-time tension"""
    analyzer = FrameworkDialectics()

    space_data = {
        "market_position": "premium",
        "price_point": "high-end"
    }

    time_data = {
        "purchase_occasion": "wedding",
        "consideration_period": "2-3 weeks"
    }

    tension = await analyzer.find_space_time_tension(space_data, time_data)

    assert tension.contradiction != ""
    assert "premium" in tension.contradiction.lower()
    assert tension.human_truth != ""
    assert tension.strategic_implication != ""


@pytest.mark.asyncio
async def test_space_time_tension_with_missing_data():
    """Should handle missing space-time data gracefully"""
    analyzer = FrameworkDialectics()

    space_data = {
        "market_position": "",
        "price_point": ""
    }

    time_data = {
        "purchase_occasion": "",
        "consideration_period": ""
    }

    tension = await analyzer.find_space_time_tension(space_data, time_data)

    # Should have meaningful fallback
    assert tension.contradiction != ""
    assert tension.contradiction != "Market position () matches purchase timing ()"
    assert tension.human_truth != ""
    assert tension.strategic_implication != ""


@pytest.mark.asyncio
async def test_ux_product_tension_with_complete_data():
    """Should generate meaningful UX-product tension"""
    analyzer = FrameworkDialectics()

    ux_data = {
        "desired_experience": "simple and elegant",
        "emotional_goal": "feel confident"
    }

    product_data = {
        "actual_complexity": "high",
        "feature_count": "extensive"
    }

    tension = await analyzer.find_ux_product_tension(ux_data, product_data)

    assert tension.contradiction != ""
    assert "simple" in tension.contradiction.lower()
    assert tension.human_truth != ""
    assert tension.strategic_implication != ""


@pytest.mark.asyncio
async def test_real_brand_data_extraction():
    """Should extract tensions from real brand data structure"""
    analyzer = FrameworkDialectics()

    # Simulate real brand data from scraped website
    brand_data = {
        "products": [
            {"name": "Sherwani", "price": "₹67,000", "description": "Handcrafted embroidery luxury"},
            {"name": "Bandhgala", "price": "₹79,000", "description": "Premium designer wear"}
        ],
        "brand_messaging": "Modern Craftsmanship Meets Tradition",
        "category_stated": "Ethnic Menswear",
        "currency": "INR",
        "region": "India"
    }

    # Layer 3 should be able to extract data from this structure
    # and create meaningful tensions

    # Extract product promise from brand_messaging
    product_data = analyzer._extract_product_data(brand_data)
    assert product_data["product_promise"] != ""

    # Extract user data from category and price signals
    user_data = analyzer._extract_user_data(brand_data)
    assert len(user_data["purchase_drivers"]) > 0

    # Extract space data from price and category
    space_data = analyzer._extract_space_data(brand_data)
    assert space_data["market_position"] != ""

    # Extract time data from category (weddings = high-stakes, time-constrained)
    time_data = analyzer._extract_time_data(brand_data)
    assert time_data["purchase_occasion"] != ""


@pytest.mark.asyncio
async def test_no_empty_contradiction_strings():
    """Anti-regression test: ensure no empty contradiction strings"""
    analyzer = FrameworkDialectics()

    # Various edge cases that previously caused empty strings
    test_cases = [
        ({}, {}),  # Completely empty
        ({"product_promise": ""}, {"purchase_drivers": []}),
        ({"product_promise": None}, {"purchase_drivers": None}),
    ]

    for product_data, user_data in test_cases:
        tension = await analyzer.find_product_user_tension(product_data, user_data)

        # None of these should produce empty strings or strings like "Brand emphasizes ''"
        assert "Brand emphasizes ''" not in tension.contradiction
        assert "Brand emphasizes 'None'" not in tension.contradiction
        assert len(tension.contradiction) > 20  # Meaningful length
        assert len(tension.human_truth) > 20
        assert len(tension.strategic_implication) > 20
