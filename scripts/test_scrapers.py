#!/usr/bin/env python3
"""Test all scrapers with real websites."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.strategy_engine.data_sources.brand_scraper import BrandScraper
from app.strategy_engine.data_sources.pinterest_scraper import PinterestScraper


async def test_brand_scraper():
    """Test brand scraper with real websites."""

    websites = [
        'https://sangeeta.work',
        'https://studio-mcgee.com/'
    ]

    scraper = BrandScraper(timeout=30)

    for url in websites:
        print(f"\n{'='*80}")
        print(f"Testing: {url}")
        print('='*80)

        try:
            result = await scraper.scrape_brand(url)

            print(f"\n✓ SUCCESS")
            print(f"  Name: {result['name']}")
            print(f"  Category: {result['category']}")
            print(f"  Description: {result['description'][:200]}...")
            print(f"  Features: {len(result['features'])} found")
            print(f"  Images: {len(result['images'])} found")
            print(f"  Content length: {len(result['content'])} chars")

            if result.get('metadata'):
                print(f"  Meta title: {result['metadata'].get('title', 'N/A')}")

        except Exception as e:
            print(f"\n✗ FAILED: {e}")


async def test_pinterest_scraper():
    """Test Pinterest scraper with search."""

    print(f"\n{'='*80}")
    print("Testing: Pinterest search - flowers")
    print('='*80)

    # Note: Pinterest requires authentication for some operations
    # This test will verify the scraper can handle the site
    print("\nNote: Pinterest search requires authentication.")
    print("Testing with profile scraping instead...")

    async with PinterestScraper() as scraper:
        try:
            # Test with a known public profile
            result = await scraper.scrape_profile('pinterest')

            print(f"\n✓ SUCCESS")
            print(f"  Username: {result['username']}")
            print(f"  Display name: {result['display_name']}")
            print(f"  Followers: {result['follower_count']}")
            print(f"  Boards: {len(result['boards'])} found")

        except Exception as e:
            print(f"\n✗ FAILED: {e}")


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("SCRAPER ROBUSTNESS TEST")
    print("="*80)

    # Test brand scraper
    await test_brand_scraper()

    # Test Pinterest scraper
    await test_pinterest_scraper()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)


if __name__ == '__main__':
    asyncio.run(main())
