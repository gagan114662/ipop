"""Tests for Category Archaeology - Layer 1

This module tests the Category Archaeology analysis layer which:
- Identifies true functional, emotional, and social categories
- Determines category maturity stage
- Identifies real (non-obvious) competitors
"""

import pytest
from app.strategy_engine.analysis.layer1_category_archaeology import CategoryArchaeology
from app.strategy_engine.analysis.models import CategoryAnalysis, MaturityStage


@pytest.mark.asyncio
async def test_analyze_brand_category():
    """Should analyze brand and determine real categories"""
    analyzer = CategoryArchaeology()

    brand_data = {
        "products": [
            {
                "name": "Heritage Watch",
                "description": "Swiss automatic movement, leather strap, precision timekeeping"
            },
            {
                "name": "Sport Chrono",
                "description": "Premium materials, statement piece"
            }
        ],
        "category_stated": "Watches",
        "price_range": (299, 899),
        "brand_messaging": "Timeless elegance meets modern craftsmanship"
    }

    result = await analyzer.analyze(brand_data)

    assert isinstance(result, CategoryAnalysis)
    assert result.stated_category == "Watches"
    assert result.functional_category is not None
    assert result.emotional_category is not None
    assert result.social_category is not None
    assert result.maturity is not None
    assert result.strategic_implication is not None


@pytest.mark.asyncio
async def test_determine_maturity_commoditized():
    """Should identify commoditized market"""
    analyzer = CategoryArchaeology()

    market_data = {
        "competitor_count": 500,
        "price_variance": 0.10,
        "innovation_rate": "low",
        "market_growth": 0.02
    }

    result = await analyzer.determine_maturity(market_data)

    assert isinstance(result, MaturityStage)
    assert result.stage == "commoditized"
    assert "meaning" in result.strategic_implication.lower() or "culture" in result.strategic_implication.lower()


@pytest.mark.asyncio
async def test_determine_maturity_early_innovation():
    """Should identify early innovation stage"""
    analyzer = CategoryArchaeology()

    market_data = {
        "competitor_count": 15,
        "price_variance": 0.45,
        "innovation_rate": "high",
        "market_growth": 0.35
    }

    result = await analyzer.determine_maturity(market_data)

    assert isinstance(result, MaturityStage)
    assert result.stage == "early_innovation"
    assert len(result.strategic_implication) > 0


@pytest.mark.asyncio
async def test_identify_real_competitors_status_symbols():
    """Should find non-obvious competitors for status symbols"""
    analyzer = CategoryArchaeology()

    category_data = {
        "stated_category": "Watches",
        "emotional_job": "status_symbols",
        "social_job": "identity_markers"
    }

    competitors = await analyzer.identify_real_competitors(category_data)

    assert isinstance(competitors, list)
    assert len(competitors) > 0
    # Should include non-watch categories that serve same job
    assert any(
        "jewelry" in c.lower() or
        "fashion" in c.lower() or
        "luxury" in c.lower() or
        "car" in c.lower()
        for c in competitors
    )


@pytest.mark.asyncio
async def test_identify_real_competitors_functional():
    """Should find competitors based on functional job"""
    analyzer = CategoryArchaeology()

    category_data = {
        "stated_category": "Watches",
        "functional_category": "time_management",
        "emotional_job": None,
        "social_job": None
    }

    competitors = await analyzer.identify_real_competitors(category_data)

    assert isinstance(competitors, list)
    assert len(competitors) > 0
    # For functional time management, should include digital alternatives
    assert any(
        "phone" in c.lower() or
        "smart" in c.lower() or
        "app" in c.lower() or
        "digital" in c.lower()
        for c in competitors
    )


@pytest.mark.asyncio
async def test_analyze_with_sustainability_brand():
    """Should correctly analyze sustainability-focused brand"""
    analyzer = CategoryArchaeology()

    brand_data = {
        "products": [
            {
                "name": "Eco Watch",
                "description": "Made from recycled ocean plastic, carbon neutral shipping, sustainable materials"
            }
        ],
        "category_stated": "Sustainable Watches",
        "price_range": (150, 350),
        "brand_messaging": "Save the planet, one watch at a time"
    }

    result = await analyzer.analyze(brand_data)

    assert isinstance(result, CategoryAnalysis)
    assert result.stated_category == "Sustainable Watches"
    # Emotional category should reflect virtue signaling or identity
    assert result.emotional_category is not None
    assert len(result.real_competitors) > 0


@pytest.mark.asyncio
async def test_determine_maturity_growth_stage():
    """Should identify growth stage market"""
    analyzer = CategoryArchaeology()

    market_data = {
        "competitor_count": 85,
        "price_variance": 0.28,
        "innovation_rate": "medium",
        "market_growth": 0.18
    }

    result = await analyzer.determine_maturity(market_data)

    assert isinstance(result, MaturityStage)
    assert result.stage == "growth"
    assert len(result.strategic_implication) > 0


@pytest.mark.asyncio
async def test_analyze_handles_minimal_data():
    """Should handle minimal brand data gracefully"""
    analyzer = CategoryArchaeology()

    brand_data = {
        "products": [{"name": "Product X", "description": "A product"}],
        "category_stated": "General",
        "price_range": (50, 100),
        "brand_messaging": "Quality products"
    }

    result = await analyzer.analyze(brand_data)

    assert isinstance(result, CategoryAnalysis)
    assert result.stated_category == "General"
    # Should still provide analysis even with minimal data
    assert result.functional_category is not None or result.emotional_category is not None
