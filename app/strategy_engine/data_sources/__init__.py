"""Data Sources Module.

Integrations with external data sources:
- Brand web scraping (static + browser automation)
- Design platform scraping (Pinterest, Behance, Dribbble)
- Reddit discourse analysis
- TikTok trend detection
- Google Trends
- Cultural intelligence
"""

from . import models
from .brand_scraper import BrandScraper
from .browser_scraper import BrowserScraper
from .pinterest_scraper import PinterestScraper
from .behance_scraper import BehanceScraper
from .dribbble_scraper import DribbbleScraper

__all__ = [
    "models",
    "BrandScraper",
    "BrowserScraper",
    "PinterestScraper",
    "BehanceScraper",
    "DribbbleScraper"
]
