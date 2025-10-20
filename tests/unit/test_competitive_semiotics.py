"""Tests for Competitive Semiotics - Layer 4

This module tests the Competitive Semiotics analysis layer which:
- Extracts visual codes from competitor creative assets
- Extracts verbal codes from brand messaging
- Maps the competitive semiotic landscape
- Identifies positioning white space opportunities
"""

import pytest
from pathlib import Path
from app.strategy_engine.analysis.layer4_competitive_semiotics import CompetitiveSemiotics
from app.strategy_engine.analysis.models import VisualCode


# Test asset paths
SANGI_ASSETS_PATH = Path("/Users/gagan/Desktop/Sangi_Advertising_Concepts")
INSTAGRAM_IMAGES_PATH = SANGI_ASSETS_PATH / "instagram_full"
PINTEREST_IMAGES_PATH = SANGI_ASSETS_PATH / "pinterest_boards"


@pytest.mark.asyncio
async def test_extract_visual_codes_from_images():
    """Should extract visual codes from competitor images"""
    analyzer = CompetitiveSemiotics()

    # Use real Sangi advertising images
    sample_images = list(INSTAGRAM_IMAGES_PATH.glob("*.jpg"))[:5]

    result = await analyzer.extract_visual_codes(
        images=[str(img) for img in sample_images],
        brand_name="Sangi Advertising"
    )

    assert isinstance(result, list)
    assert all(isinstance(code, VisualCode) for code in result)
    assert len(result) > 0

    # Should extract meaningful codes
    for code in result:
        assert code.code_name  # Not empty
        assert 0 <= code.frequency <= 1
        assert len(code.examples) > 0


@pytest.mark.asyncio
async def test_visual_codes_identify_dominant_patterns():
    """Should identify dominant visual patterns across images"""
    analyzer = CompetitiveSemiotics()

    sample_images = list(INSTAGRAM_IMAGES_PATH.glob("*.jpg"))[:10]

    codes = await analyzer.extract_visual_codes(
        images=[str(img) for img in sample_images],
        brand_name="Sangi Advertising"
    )

    # Should have dominant codes (frequency > 0.5)
    dominant_codes = [c for c in codes if c.frequency > 0.5]
    assert len(dominant_codes) > 0

    # Dominant codes should appear in multiple examples
    for code in dominant_codes:
        assert len(code.examples) >= 2


@pytest.mark.asyncio
async def test_extract_verbal_codes_from_copy():
    """Should extract verbal/messaging codes from brand copy"""
    analyzer = CompetitiveSemiotics()

    brand_copy = [
        "Premium quality handcrafted jewelry",
        "Timeless elegance for modern women",
        "Sustainable luxury you can feel good about",
        "Artisan craftsmanship meets contemporary design",
        "Elevate your everyday with premium materials"
    ]

    result = await analyzer.extract_verbal_codes(
        copy=brand_copy,
        brand_name="Test Brand"
    )

    assert isinstance(result, dict)
    assert "dominant_themes" in result
    assert "tone" in result
    assert "messaging_patterns" in result

    # Should identify themes
    assert len(result["dominant_themes"]) > 0
    assert any("premium" in theme.lower() or "quality" in theme.lower()
               for theme in result["dominant_themes"])


@pytest.mark.asyncio
async def test_build_semiotic_map():
    """Should build a competitive semiotic map"""
    analyzer = CompetitiveSemiotics()

    competitors_data = {
        "Competitor A": {
            "visual_codes": ["minimalist", "monochrome", "geometric"],
            "verbal_codes": ["luxury", "timeless", "exclusive"]
        },
        "Competitor B": {
            "visual_codes": ["colorful", "playful", "organic"],
            "verbal_codes": ["fun", "accessible", "vibrant"]
        },
        "Competitor C": {
            "visual_codes": ["minimalist", "warm_tones", "natural"],
            "verbal_codes": ["sustainable", "ethical", "conscious"]
        }
    }

    semiotic_map = await analyzer.build_semiotic_map(competitors_data)

    assert semiotic_map is not None
    assert "visual_territory" in semiotic_map
    assert "verbal_territory" in semiotic_map
    assert "competitor_positions" in semiotic_map

    # Should map all competitors
    assert len(semiotic_map["competitor_positions"]) == 3


@pytest.mark.asyncio
async def test_identify_white_space():
    """Should identify unclaimed positioning territory"""
    analyzer = CompetitiveSemiotics()

    competitors_data = {
        "Competitor A": {
            "visual_codes": ["minimalist", "monochrome"],
            "verbal_codes": ["luxury", "exclusive"]
        },
        "Competitor B": {
            "visual_codes": ["colorful", "playful"],
            "verbal_codes": ["fun", "accessible"]
        }
    }

    white_space = await analyzer.identify_white_space(competitors_data)

    assert isinstance(white_space, list)
    assert len(white_space) > 0

    # Each opportunity should have description and rationale
    for opportunity in white_space:
        assert "visual_opportunity" in opportunity
        assert "verbal_opportunity" in opportunity
        assert "strategic_rationale" in opportunity
        assert "differentiation_score" in opportunity
        assert 0 <= opportunity["differentiation_score"] <= 1


@pytest.mark.asyncio
async def test_analyze_competitor_positioning():
    """Should analyze how competitors are positioned semiotically"""
    analyzer = CompetitiveSemiotics()

    competitor_name = "Test Competitor"
    visual_codes = ["minimalist", "monochrome", "geometric", "clean_lines"]
    verbal_codes = ["luxury", "timeless", "exclusive", "premium"]

    positioning = await analyzer.analyze_positioning(
        competitor_name=competitor_name,
        visual_codes=visual_codes,
        verbal_codes=verbal_codes
    )

    assert positioning is not None
    assert "visual_identity" in positioning
    assert "verbal_identity" in positioning
    assert "overall_positioning" in positioning

    # Should categorize positioning
    assert positioning["overall_positioning"] in [
        "luxury_minimalist",
        "playful_accessible",
        "sustainable_conscious",
        "premium_traditional",
        "modern_innovative",
        "other"
    ]


@pytest.mark.asyncio
async def test_compare_brand_to_competitors():
    """Should compare brand positioning against competitors"""
    analyzer = CompetitiveSemiotics()

    brand_data = {
        "visual_codes": ["warm_tones", "natural", "organic"],
        "verbal_codes": ["sustainable", "ethical", "conscious"]
    }

    competitors_data = {
        "Competitor A": {
            "visual_codes": ["minimalist", "monochrome"],
            "verbal_codes": ["luxury", "exclusive"]
        },
        "Competitor B": {
            "visual_codes": ["colorful", "playful"],
            "verbal_codes": ["fun", "accessible"]
        }
    }

    comparison = await analyzer.compare_brand_to_market(
        brand_data=brand_data,
        competitors_data=competitors_data
    )

    assert comparison is not None
    assert "similarity_scores" in comparison
    assert "differentiation_areas" in comparison
    assert "competitive_advantage" in comparison

    # Should have similarity score for each competitor
    assert len(comparison["similarity_scores"]) == 2

    # Scores should be between 0 and 1
    for competitor, score in comparison["similarity_scores"].items():
        assert 0 <= score <= 1


@pytest.mark.asyncio
async def test_mock_implementation_without_real_images():
    """Should work with mock data when real images unavailable"""
    analyzer = CompetitiveSemiotics()

    # Mock: analyze without actual image processing
    mock_images = ["image1.jpg", "image2.jpg", "image3.jpg"]

    result = await analyzer.extract_visual_codes(
        images=mock_images,
        brand_name="Mock Brand",
        use_mock=True  # Flag to use mock analysis
    )

    assert isinstance(result, list)
    assert len(result) > 0

    # Mock should still return valid structure
    for code in result:
        assert hasattr(code, 'code_name')
        assert hasattr(code, 'frequency')


@pytest.mark.asyncio
async def test_semiotic_analysis_generates_insights():
    """Should generate actionable semiotic insights"""
    analyzer = CompetitiveSemiotics()

    competitors_data = {
        "Competitor A": {
            "visual_codes": ["minimalist", "monochrome", "geometric"],
            "verbal_codes": ["luxury", "timeless", "exclusive"]
        },
        "Competitor B": {
            "visual_codes": ["minimalist", "warm_tones", "natural"],
            "verbal_codes": ["sustainable", "ethical", "conscious"]
        },
        "Competitor C": {
            "visual_codes": ["minimalist", "monochrome", "clean_lines"],
            "verbal_codes": ["luxury", "premium", "sophisticated"]
        }
    }

    insights = await analyzer.generate_insights(competitors_data)

    assert insights is not None
    assert "crowded_territories" in insights
    assert "empty_territories" in insights
    assert "recommended_positioning" in insights

    # Should identify that "minimalist" is crowded
    assert any("minimalist" in territory.lower()
               for territory in insights["crowded_territories"])

    # Should recommend differentiation
    assert len(insights["recommended_positioning"]) > 0


@pytest.mark.asyncio
async def test_visual_code_extraction_consistency():
    """Should extract consistent codes from similar images"""
    analyzer = CompetitiveSemiotics()

    # Get first 3 images
    sample_images_1 = list(INSTAGRAM_IMAGES_PATH.glob("*.jpg"))[:3]
    codes_1 = await analyzer.extract_visual_codes(
        images=[str(img) for img in sample_images_1],
        brand_name="Sangi Advertising"
    )

    # Get overlapping set (images 2-4)
    sample_images_2 = list(INSTAGRAM_IMAGES_PATH.glob("*.jpg"))[1:4]
    codes_2 = await analyzer.extract_visual_codes(
        images=[str(img) for img in sample_images_2],
        brand_name="Sangi Advertising"
    )

    # Should have some overlapping codes
    codes_1_names = {c.code_name for c in codes_1}
    codes_2_names = {c.code_name for c in codes_2}

    overlap = codes_1_names.intersection(codes_2_names)
    assert len(overlap) > 0  # At least some consistency
