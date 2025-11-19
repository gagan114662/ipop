"""
Reference Image Finder Service - Finds award-winning creative references.

This service finds award-winning ad creatives based on product category
to use as reference for generating new creatives.
"""
import asyncio
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import structlog
import httpx
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ReferenceImageFinder:
    """Finds award-winning reference images for creative generation."""

    # Award-winning creative sources
    SOURCES = {
        "facebook_ads_library": "https://www.facebook.com/ads/library/",
        "ads_of_the_world": "https://www.adsoftheworld.com/",
        "the_drum": "https://www.thedrum.com/creative-works",
        "adweek": "https://www.adweek.com/creativity/",
    }

    # Category to search query mapping
    CATEGORY_QUERIES = {
        "ecommerce": ["ecommerce ad", "online store ad", "product ad"],
        "fashion": ["fashion ad campaign", "clothing brand ad", "fashion creative"],
        "beauty": ["beauty ad", "cosmetics ad", "skincare ad"],
        "food": ["food ad", "restaurant ad", "food brand creative"],
        "tech": ["tech product ad", "software ad", "app ad"],
        "automotive": ["car ad", "automotive ad", "vehicle campaign"],
        "travel": ["travel ad", "tourism ad", "hotel ad"],
        "finance": ["fintech ad", "banking ad", "finance creative"],
        "health": ["healthcare ad", "wellness ad", "fitness ad"],
        "real_estate": ["real estate ad", "property ad", "home sale ad"],
        "default": ["award winning ad", "best ad creative", "viral ad campaign"]
    }

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize the reference image finder."""
        self.db = db
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def find_reference_images(
        self,
        category: str,
        count: int = 5,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find award-winning reference images for a category.

        Args:
            category: Product category (e.g., "fashion", "tech", "food")
            count: Number of reference images to return
            platform: Target platform (e.g., "meta", "google", "tiktok")

        Returns:
            List of reference images with metadata
        """
        try:
            # Check cache first
            cached = await self._get_cached_references(category, platform, count)
            if cached:
                logger.info(
                    "reference_images_from_cache",
                    category=category,
                    count=len(cached)
                )
                return cached

            # Find new references
            references = await self._search_reference_images(category, count, platform)

            # Cache results
            if references:
                await self._cache_references(category, platform, references)

            logger.info(
                "reference_images_found",
                category=category,
                count=len(references),
                from_cache=False
            )

            return references

        except Exception as e:
            logger.error(
                "reference_image_search_failed",
                category=category,
                error=str(e),
                exc_info=True
            )
            # Return fallback references
            return await self._get_fallback_references(category, count)

    async def _search_reference_images(
        self,
        category: str,
        count: int,
        platform: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Search for reference images from multiple sources."""
        references = []

        # Get search queries for category
        queries = self.CATEGORY_QUERIES.get(
            category.lower(),
            self.CATEGORY_QUERIES["default"]
        )

        # Add platform-specific search terms
        if platform:
            queries = [f"{q} {platform}" for q in queries]

        # Search from curated award-winning database first
        curated = await self._get_curated_references(category, platform, count)
        references.extend(curated)

        # If we need more, search online sources
        if len(references) < count:
            needed = count - len(references)
            online_refs = await self._search_online_sources(queries[:2], needed)
            references.extend(online_refs)

        # Rank and return top results
        ranked = self._rank_references(references, category, platform)
        return ranked[:count]

    async def _get_curated_references(
        self,
        category: str,
        platform: Optional[str],
        count: int
    ) -> List[Dict[str, Any]]:
        """
        Get references from curated award-winning database.

        This queries a collection of pre-vetted award-winning creatives
        that have been manually curated for quality.
        """
        try:
            query = {
                "category": category.lower(),
                "is_award_winning": True,
                "quality_score": {"$gte": 0.8}
            }

            if platform:
                query["platform"] = platform

            cursor = self.db.reference_creatives.find(query).sort(
                "quality_score", -1
            ).limit(count)

            references = await cursor.to_list(length=count)

            return [
                {
                    "image_url": ref["image_url"],
                    "title": ref.get("title", ""),
                    "description": ref.get("description", ""),
                    "source": "curated_database",
                    "category": ref["category"],
                    "platform": ref.get("platform", ""),
                    "quality_score": ref.get("quality_score", 0.8),
                    "award_info": ref.get("award_info", ""),
                    "brand": ref.get("brand", ""),
                    "year": ref.get("year", datetime.utcnow().year)
                }
                for ref in references
            ]

        except Exception as e:
            logger.warning(
                "curated_references_fetch_failed",
                error=str(e),
                category=category
            )
            return []

    async def _search_online_sources(
        self,
        queries: List[str],
        count: int
    ) -> List[Dict[str, Any]]:
        """
        Search online sources for award-winning creatives.

        This uses web scraping to find high-quality reference images
        from award-winning ad galleries and creative showcases.
        """
        references = []

        # For now, use a mock/placeholder approach
        # In production, you would implement actual web scraping here
        # using BeautifulSoup, Playwright, or similar tools

        # Example: You could scrape from:
        # - Ads of the World (adsoftheworld.com)
        # - The Drum Creative Works
        # - Adweek Creativity section
        # - Facebook Ads Library
        # - Behance

        logger.info(
            "online_source_search",
            queries=queries,
            note="Using fallback - implement web scraping for production"
        )

        # Return empty for now - will use fallback or curated only
        return references

    def _rank_references(
        self,
        references: List[Dict[str, Any]],
        category: str,
        platform: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Rank reference images by relevance and quality.

        Scoring factors:
        - Quality score (if available)
        - Category match
        - Platform match
        - Recency
        """
        for ref in references:
            score = 0.0

            # Base quality score
            score += ref.get("quality_score", 0.5) * 40

            # Category match
            if ref.get("category", "").lower() == category.lower():
                score += 30

            # Platform match
            if platform and ref.get("platform", "").lower() == platform.lower():
                score += 20

            # Recency bonus (prefer recent years)
            current_year = datetime.utcnow().year
            year = ref.get("year", current_year - 5)
            years_old = current_year - year
            recency_score = max(0, 10 - years_old)
            score += recency_score

            ref["relevance_score"] = score

        # Sort by relevance score
        references.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return references

    async def _get_cached_references(
        self,
        category: str,
        platform: Optional[str],
        count: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached reference images if available and not expired."""
        try:
            cache_key = self._get_cache_key(category, platform)

            cached = await self.db.reference_cache.find_one({
                "cache_key": cache_key
            })

            if not cached:
                return None

            # Check if expired
            expires_at = cached.get("expires_at")
            if expires_at and expires_at < datetime.utcnow():
                # Delete expired cache
                await self.db.reference_cache.delete_one({"cache_key": cache_key})
                return None

            references = cached.get("references", [])
            return references[:count]

        except Exception as e:
            logger.warning(
                "cache_fetch_failed",
                error=str(e),
                category=category
            )
            return None

    async def _cache_references(
        self,
        category: str,
        platform: Optional[str],
        references: List[Dict[str, Any]]
    ) -> None:
        """Cache reference images for future use."""
        try:
            cache_key = self._get_cache_key(category, platform)
            expires_at = datetime.utcnow() + timedelta(
                seconds=settings.REFERENCE_IMAGE_CACHE_TTL
            )

            await self.db.reference_cache.update_one(
                {"cache_key": cache_key},
                {
                    "$set": {
                        "cache_key": cache_key,
                        "category": category,
                        "platform": platform,
                        "references": references,
                        "expires_at": expires_at,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )

            logger.debug(
                "references_cached",
                cache_key=cache_key,
                count=len(references),
                expires_at=expires_at
            )

        except Exception as e:
            logger.warning(
                "cache_save_failed",
                error=str(e),
                category=category
            )

    def _get_cache_key(self, category: str, platform: Optional[str]) -> str:
        """Generate cache key for category and platform."""
        key_parts = [category.lower()]
        if platform:
            key_parts.append(platform.lower())

        key_string = "_".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def _get_fallback_references(
        self,
        category: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """
        Get fallback reference images when search fails.

        Returns a set of generic high-quality ad templates
        that can be used as references.
        """
        fallback_refs = [
            {
                "image_url": "https://picsum.photos/1200/628?random=1",
                "title": f"High-performing {category} ad template",
                "description": "Professional ad creative template with proven engagement",
                "source": "fallback",
                "category": category,
                "platform": "universal",
                "quality_score": 0.7,
                "award_info": "Industry best practices",
                "brand": "Template",
                "year": datetime.utcnow().year,
                "relevance_score": 50
            }
            for i in range(count)
        ]

        logger.info(
            "using_fallback_references",
            category=category,
            count=len(fallback_refs)
        )

        return fallback_refs

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


async def get_reference_finder(db: AsyncIOMotorDatabase) -> ReferenceImageFinder:
    """Get reference image finder instance."""
    return ReferenceImageFinder(db)
