"""Tests for Layer 7: Platform Strategy

This layer adapts the base strategy for each platform's unique logic and culture.
"""

import pytest
from app.strategy_engine.analysis.layer7_platform_strategy import (
    PlatformStrategyAdapter,
    PlatformStrategy
)


@pytest.mark.asyncio
async def test_platform_adaptation():
    """Should adapt strategy per platform logic."""

    base_strategy = {
        "brand_positioning": "authentic, minimalist, premium",
        "target_audience": "conscious consumers",
        "key_message": "quality over quantity"
    }

    adapter = PlatformStrategyAdapter()
    adapted = await adapter.adapt(base_strategy, platform="tiktok")

    # Assertions
    assert isinstance(adapted, PlatformStrategy)
    assert adapted.platform == "tiktok"
    assert adapted.content_strategy == "culture_participation"
    assert adapted != base_strategy  # Platform-specific adaptation


@pytest.mark.asyncio
async def test_adapt_for_meta():
    """Should adapt strategy for Meta (Facebook/Instagram)."""

    base_strategy = {
        "positioning": "innovative tech product",
        "audience": "early adopters"
    }

    adapter = PlatformStrategyAdapter()
    meta_strategy = await adapter.adapt_for_meta(base_strategy)

    # Meta-specific assertions
    assert meta_strategy.platform == "meta"
    assert "social_proof" in meta_strategy.targeting_approach.lower() or "community" in meta_strategy.content_strategy.lower()
    assert len(meta_strategy.creative_guidelines) > 0


@pytest.mark.asyncio
async def test_adapt_for_google():
    """Should adapt strategy for Google Ads."""

    base_strategy = {
        "offering": "B2B SaaS solution",
        "value_prop": "increase efficiency"
    }

    adapter = PlatformStrategyAdapter()
    google_strategy = await adapter.adapt_for_google(base_strategy)

    # Google-specific assertions
    assert google_strategy.platform == "google"
    assert "intent" in google_strategy.targeting_approach.lower() or "search" in google_strategy.targeting_approach.lower()
    assert google_strategy.content_strategy in ["problem_solution", "direct_response", "educational"]


@pytest.mark.asyncio
async def test_adapt_for_tiktok():
    """Should adapt strategy for TikTok."""

    base_strategy = {
        "brand": "fashion retailer",
        "tone": "youthful and trendy"
    }

    adapter = PlatformStrategyAdapter()
    tiktok_strategy = await adapter.adapt_for_tiktok(base_strategy)

    # TikTok-specific assertions
    assert tiktok_strategy.platform == "tiktok"
    assert tiktok_strategy.content_strategy == "culture_participation"
    assert "authentic" in tiktok_strategy.creative_guidelines.get("style", "").lower() or "trend" in str(tiktok_strategy.creative_guidelines.values()).lower()


@pytest.mark.asyncio
async def test_adapt_for_linkedin():
    """Should adapt strategy for LinkedIn."""

    base_strategy = {
        "offering": "executive coaching",
        "audience": "senior leaders"
    }

    adapter = PlatformStrategyAdapter()
    linkedin_strategy = await adapter.adapt_for_linkedin(base_strategy)

    # LinkedIn-specific assertions
    assert linkedin_strategy.platform == "linkedin"
    assert "professional" in linkedin_strategy.content_strategy.lower() or "thought_leadership" in linkedin_strategy.content_strategy.lower()
    assert "credibility" in str(linkedin_strategy.creative_guidelines.values()).lower() or "authority" in str(linkedin_strategy.creative_guidelines.values()).lower()


@pytest.mark.asyncio
async def test_all_platforms_different():
    """Should produce different strategies for each platform."""

    base_strategy = {"product": "fitness app"}

    adapter = PlatformStrategyAdapter()

    meta_strat = await adapter.adapt_for_meta(base_strategy)
    google_strat = await adapter.adapt_for_google(base_strategy)
    tiktok_strat = await adapter.adapt_for_tiktok(base_strategy)
    linkedin_strat = await adapter.adapt_for_linkedin(base_strategy)

    # All should be different
    strategies = [meta_strat, google_strat, tiktok_strat, linkedin_strat]
    content_strategies = [s.content_strategy for s in strategies]

    # At least 3 should be unique (some overlap is okay)
    assert len(set(content_strategies)) >= 3
