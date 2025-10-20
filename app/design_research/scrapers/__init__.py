"""Scrapers Module.

Integrations for visual research platforms:
- Behance project scraper
- Pinterest board scraper
- Dribbble shots scraper
- Instagram Ad Library scraper
- Generic brand website scraper (e-commerce)
"""

from app.design_research.scrapers.brand_website_scraper import BrandWebsiteScraper

__all__ = ['BrandWebsiteScraper']
