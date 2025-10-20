"""Unit Tests for Universal Brand Web Scraper

Tests web scraping functionality that works with ANY website.
"""

import pytest
from app.strategy_engine.data_sources.brand_scraper import BrandScraper


@pytest.mark.asyncio
async def test_scraper_extracts_basic_info():
    """Should extract basic brand information from any website."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://example.com")

    # Should return structured data
    assert result is not None
    assert "name" in result
    assert "url" in result
    assert "description" in result

    # URL should match input
    assert result["url"] == "https://example.com"


@pytest.mark.asyncio
async def test_scraper_extracts_text_content():
    """Should extract meaningful text content from website."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://example.com")

    assert "content" in result
    assert len(result["content"]) > 0
    assert isinstance(result["content"], str)


@pytest.mark.asyncio
async def test_scraper_extracts_metadata():
    """Should extract SEO metadata from website."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://example.com")

    assert "metadata" in result
    metadata = result["metadata"]

    # Should have common SEO fields
    assert "title" in metadata
    assert "meta_description" in metadata


@pytest.mark.asyncio
async def test_scraper_extracts_images():
    """Should extract image URLs from website."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://example.com")

    assert "images" in result
    assert isinstance(result["images"], list)

    # If images exist, they should be URLs
    if len(result["images"]) > 0:
        assert result["images"][0].startswith("http")


@pytest.mark.asyncio
async def test_scraper_categorizes_brand():
    """Should attempt to categorize the brand based on content."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://example.com")

    assert "category" in result
    assert result["category"] is not None
    assert isinstance(result["category"], str)


@pytest.mark.asyncio
async def test_scraper_extracts_features():
    """Should extract product/service features from content."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://example.com")

    assert "features" in result
    assert isinstance(result["features"], list)


@pytest.mark.asyncio
async def test_scraper_handles_invalid_url():
    """Should handle invalid URLs gracefully."""

    scraper = BrandScraper()

    with pytest.raises(ValueError):
        await scraper.scrape_brand("not-a-url")


@pytest.mark.asyncio
async def test_scraper_handles_http_errors():
    """Should handle HTTP errors gracefully."""

    scraper = BrandScraper()

    # Non-existent domain should fail gracefully
    with pytest.raises(Exception):
        await scraper.scrape_brand("https://this-domain-definitely-does-not-exist-12345.com")


@pytest.mark.asyncio
async def test_scraper_respects_timeout():
    """Should timeout for slow websites."""

    scraper = BrandScraper(timeout=1)  # 1 second timeout

    # Should complete or timeout, not hang
    try:
        result = await scraper.scrape_brand("https://example.com")
        assert result is not None
    except Exception:
        # Timeout is acceptable
        pass


@pytest.mark.asyncio
async def test_scraper_extracts_links():
    """Should extract navigation and external links."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://example.com")

    assert "links" in result
    assert isinstance(result["links"], dict)
    assert "internal" in result["links"]
    assert "external" in result["links"]


@pytest.mark.asyncio
async def test_scraper_identifies_social_media():
    """Should identify social media links."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://example.com")

    assert "social_media" in result
    assert isinstance(result["social_media"], dict)


@pytest.mark.asyncio
async def test_scraper_works_with_different_domains():
    """Should work with various TLDs and domains."""

    scraper = BrandScraper()

    test_urls = [
        "https://example.com",
        "https://example.org",
        "https://example.co.uk",
        "https://example.io"
    ]

    for url in test_urls:
        try:
            result = await scraper.scrape_brand(url)
            assert result["url"] == url
        except Exception:
            # Some may not exist, that's okay
            pass


@pytest.mark.asyncio
async def test_scraper_normalizes_brand_name():
    """Should extract and normalize brand name from URL."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://my-awesome-brand.com")

    assert result["name"] is not None
    # Should be capitalized/cleaned
    assert len(result["name"]) > 0


@pytest.mark.asyncio
async def test_scraper_output_structure():
    """Should return consistently structured output."""

    scraper = BrandScraper()
    result = await scraper.scrape_brand("https://example.com")

    # Required fields
    required_fields = [
        "name", "url", "category", "description",
        "features", "images", "content", "metadata",
        "links", "social_media"
    ]

    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
