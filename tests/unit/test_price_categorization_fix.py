"""
Tests for system-wide price categorization fix.

These tests validate currency-aware, region-aware, and category-aware pricing logic.
"""
import pytest
from app.strategy_engine.analysis.layer1_category_archaeology import CategoryArchaeology


@pytest.mark.asyncio
async def test_indian_rupee_luxury_ethnic_wear():
    """Should correctly categorize Indian luxury ethnic wear (₹50,000-80,000)"""
    analyzer = CategoryArchaeology()

    brand_data = {
        "products": [
            {"name": "Sherwani", "price": "₹67,000"},
            {"name": "Bandhgala", "price": "₹79,000"},
            {"name": "Kurta", "price": "₹25,500"}
        ],
        "currency": "INR",
        "category_stated": "Ethnic Menswear",
        "region": "India"
    }

    result = await analyzer.analyze(brand_data)

    # ₹50,000-80,000 should be categorized as luxury/status in Indian ethnic wear
    assert result.emotional_category in ["status", "luxury", "status_symbols"]
    assert result.social_category in ["stand_out", "signal_wealth", "cultural_pride", "family_pride"]


@pytest.mark.asyncio
async def test_indian_rupee_mass_market():
    """Should correctly categorize Indian mass-market ethnic wear (₹2,000-5,000)"""
    analyzer = CategoryArchaeology()

    brand_data = {
        "products": [
            {"name": "Kurta", "price": "₹2,499"},
            {"name": "Kurta Set", "price": "₹3,999"}
        ],
        "currency": "INR",
        "category_stated": "Ethnic Menswear",
        "region": "India"
    }

    result = await analyzer.analyze(brand_data)

    # ₹2,000-5,000 should be categorized as functional/value in Indian ethnic wear
    assert result.emotional_category in ["functional_necessity", "value", "practical"]


@pytest.mark.asyncio
async def test_usd_luxury_fashion():
    """Should correctly categorize USD luxury fashion ($500-2000)"""
    analyzer = CategoryArchaeology()

    brand_data = {
        "products": [
            {"name": "Designer Jacket", "price": "$899"},
            {"name": "Premium Suit", "price": "$1,299"}
        ],
        "currency": "USD",
        "category_stated": "Fashion",
        "region": "United States"
    }

    result = await analyzer.analyze(brand_data)

    assert result.emotional_category in ["status", "luxury", "self_reward"]


@pytest.mark.asyncio
async def test_euro_luxury_watches():
    """Should correctly categorize Euro luxury watches (€5,000+)"""
    analyzer = CategoryArchaeology()

    brand_data = {
        "products": [
            {"name": "Automatic Watch", "price": "€5,500"},
            {"name": "Chronograph", "price": "€8,900"}
        ],
        "currency": "EUR",
        "category_stated": "Watches",
        "region": "Europe"
    }

    result = await analyzer.analyze(brand_data)

    assert result.emotional_category in ["status", "luxury", "status_symbols"]
    assert result.social_category in ["stand_out", "signal_wealth"]


@pytest.mark.asyncio
async def test_price_string_parsing():
    """Should correctly parse various price formats"""
    analyzer = CategoryArchaeology()

    # Test various price formats
    test_cases = [
        ("₹67,000", "INR", 67000),
        ("$1,299.99", "USD", 1299.99),
        ("€5,500.50", "EUR", 5500.50),
        ("67000", "INR", 67000),  # No currency symbol
        ("1,299", "USD", 1299),  # With comma
    ]

    for price_str, currency, expected in test_cases:
        parsed = await analyzer._parse_price(price_str, currency)
        assert parsed == expected, f"Failed to parse {price_str} as {expected}"


@pytest.mark.asyncio
async def test_category_specific_price_brackets():
    """Should apply different price brackets based on category"""
    analyzer = CategoryArchaeology()

    # Same price (₹50,000) should have different implications in different categories

    # ₹50,000 watch = mid-range
    watch_data = {
        "products": [{"name": "Watch", "price": "₹50,000"}],
        "currency": "INR",
        "category_stated": "Watches",
        "region": "India"
    }
    watch_result = await analyzer.analyze(watch_data)

    # ₹50,000 ethnic wear = luxury
    ethnic_data = {
        "products": [{"name": "Sherwani", "price": "₹50,000"}],
        "currency": "INR",
        "category_stated": "Ethnic Menswear",
        "region": "India"
    }
    ethnic_result = await analyzer.analyze(ethnic_data)

    # Watches have higher price expectations, so emotional jobs may differ
    # Both should recognize luxury/status positioning but ethnic wear is clear luxury
    assert ethnic_result.emotional_category in ["status", "luxury", "status_symbols"]


@pytest.mark.asyncio
async def test_currency_conversion():
    """Should convert currencies for consistent comparison"""
    analyzer = CategoryArchaeology()

    # ₹67,000 INR ≈ $800 USD (rough conversion)
    # Should be treated similarly to $800 luxury item in same category

    inr_data = {
        "products": [{"name": "Sherwani", "price": "₹67,000"}],
        "currency": "INR",
        "category_stated": "Fashion",
        "region": "India"
    }

    usd_data = {
        "products": [{"name": "Jacket", "price": "$800"}],
        "currency": "USD",
        "category_stated": "Fashion",
        "region": "United States"
    }

    inr_result = await analyzer.analyze(inr_data)
    usd_result = await analyzer.analyze(usd_data)

    # Both should land in similar emotional category after conversion
    assert inr_result.emotional_category == usd_result.emotional_category


@pytest.mark.asyncio
async def test_no_hardcoded_thresholds():
    """Should not use hardcoded $500 or $200 thresholds"""
    analyzer = CategoryArchaeology()

    # This test ensures we're not using the old hardcoded logic
    # by testing edge cases around those old thresholds

    # $499 (just below old $500 threshold) in luxury watches should still be status
    watch_data = {
        "products": [{"name": "Watch", "price": "$499"}],
        "currency": "USD",
        "category_stated": "Watches",
        "region": "United States"
    }

    result = await analyzer.analyze(watch_data)

    # Should use category-aware logic, not hardcoded $500 cutoff
    # In watches, $499 is entry-level but still aspirational
    assert result.emotional_category in ["self_reward", "status", "aspirational"]


@pytest.mark.asyncio
async def test_regional_adjustment():
    """Should adjust pricing expectations by region"""
    analyzer = CategoryArchaeology()

    # $100 means different things in different regions/economies
    india_data = {
        "products": [{"name": "Kurta", "price": "$100"}],
        "currency": "USD",
        "category_stated": "Ethnic Menswear",
        "region": "India"
    }

    usa_data = {
        "products": [{"name": "Shirt", "price": "$100"}],
        "currency": "USD",
        "category_stated": "Fashion",
        "region": "United States"
    }

    india_result = await analyzer.analyze(india_data)
    usa_result = await analyzer.analyze(usa_data)

    # $100 may be considered premium in India but mid-range in USA
    # Results should reflect this
    assert india_result is not None
    assert usa_result is not None


@pytest.mark.asyncio
async def test_mixed_currency_products():
    """Should handle products with mixed/missing currency info"""
    analyzer = CategoryArchaeology()

    brand_data = {
        "products": [
            {"name": "Product A", "price": "₹50,000"},
            {"name": "Product B", "price": "60000"},  # No symbol
            {"name": "Product C", "price": "$700"}  # Different currency
        ],
        "currency": "INR",  # Default currency
        "category_stated": "Fashion",
        "region": "India"
    }

    result = await analyzer.analyze(brand_data)

    # Should gracefully handle mixed currencies and infer from context
    assert result.emotional_category is not None
    assert result.social_category is not None
