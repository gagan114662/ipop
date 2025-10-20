"""Tests for Cultural Cartography - Layer 2

This module tests the Cultural Cartography analysis layer which:
- Analyzes cultural trends and macro movements
- Detects value shifts (old value -> new value)
- Identifies emerging communities
- Uses mock data sources for Reddit, TikTok, Google Trends
"""

import pytest
from app.strategy_engine.analysis.layer2_cultural_cartography import CulturalCartography
from app.strategy_engine.analysis.models import CulturalLandscape, CulturalTrend, ValueShift


@pytest.mark.asyncio
async def test_analyze_cultural_landscape():
    """Should analyze cultural trends and values"""
    analyzer = CulturalCartography()

    result = await analyzer.analyze(category="luxury watches")

    assert isinstance(result, CulturalLandscape)
    assert len(result.macro_trends) > 0
    assert len(result.value_shifts) > 0
    assert len(result.emerging_communities) >= 0  # Can be empty


@pytest.mark.asyncio
async def test_analyze_sustainability_category():
    """Should detect sustainability trends"""
    analyzer = CulturalCartography()

    result = await analyzer.analyze(category="sustainable fashion")

    assert isinstance(result, CulturalLandscape)
    # Should have sustainability-related trends
    assert any(
        "sustain" in trend.trend_name.lower() or
        "eco" in trend.trend_name.lower() or
        "conscious" in trend.trend_name.lower()
        for trend in result.macro_trends
    )


@pytest.mark.asyncio
async def test_detect_value_shifts():
    """Should identify value shifts in category"""
    analyzer = CulturalCartography()

    shifts = await analyzer.detect_value_shifts(category="sustainability")

    assert isinstance(shifts, list)
    assert all(isinstance(s, ValueShift) for s in shifts)
    assert all(hasattr(s, 'old_value') for s in shifts)
    assert all(hasattr(s, 'new_value') for s in shifts)
    assert all(s.old_value != s.new_value for s in shifts)


@pytest.mark.asyncio
async def test_value_shifts_have_evidence():
    """Value shifts should have supporting evidence"""
    analyzer = CulturalCartography()

    shifts = await analyzer.detect_value_shifts(category="luxury")

    assert len(shifts) > 0
    for shift in shifts:
        assert len(shift.evidence) > 0
        assert shift.strength >= 0 and shift.strength <= 1


@pytest.mark.asyncio
async def test_identify_emerging_communities():
    """Should identify emerging communities"""
    analyzer = CulturalCartography()

    communities = await analyzer.identify_emerging_communities(category="watches")

    assert isinstance(communities, list)
    # Communities can be empty for some categories, so just check type


@pytest.mark.asyncio
async def test_mock_data_sources():
    """Should work with mock data when APIs unavailable"""
    analyzer = CulturalCartography()

    # Should not fail even without real API connections
    trends = await analyzer._get_reddit_trends("watches")
    assert isinstance(trends, list)

    tiktok_trends = await analyzer._get_tiktok_trends("fashion")
    assert isinstance(tiktok_trends, list)

    google_trends = await analyzer._get_google_trends("sustainability")
    assert isinstance(google_trends, list)


@pytest.mark.asyncio
async def test_macro_trends_have_strength():
    """Macro trends should have strength scores"""
    analyzer = CulturalCartography()

    result = await analyzer.analyze(category="fashion")

    assert len(result.macro_trends) > 0
    for trend in result.macro_trends:
        assert isinstance(trend, CulturalTrend)
        assert trend.strength >= 0 and trend.strength <= 1
        assert len(trend.description) > 0


@pytest.mark.asyncio
async def test_analyze_tech_category():
    """Should analyze tech category trends"""
    analyzer = CulturalCartography()

    result = await analyzer.analyze(category="smart watches")

    assert isinstance(result, CulturalLandscape)
    # Tech category should have trends
    assert len(result.macro_trends) > 0


@pytest.mark.asyncio
async def test_value_shifts_reflect_zeitgeist():
    """Value shifts should reflect cultural zeitgeist"""
    analyzer = CulturalCartography()

    shifts = await analyzer.detect_value_shifts(category="luxury")

    assert len(shifts) > 0
    # At least one shift should be about modern values
    shift_themes = [s.new_value.lower() for s in shifts]
    assert any(
        "conscious" in theme or
        "sustainable" in theme or
        "authentic" in theme or
        "experience" in theme
        for theme in shift_themes
    )
