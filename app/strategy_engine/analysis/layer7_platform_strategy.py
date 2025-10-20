"""Layer 7: Platform Strategy

This layer adapts the base strategy for each platform's unique logic and culture.

Each platform has different:
- User behavior patterns
- Content consumption modes
- Advertising mechanics
- Cultural norms

Mock implementation for now - will integrate real platform intelligence later.

TODO: Externalize platform-specific rules to configuration files or database
for easier updates without code changes (Open/Closed Principle).
"""

import logging
from typing import Dict, Any
from app.strategy_engine.analysis.models import PlatformStrategy

logger = logging.getLogger(__name__)


class PlatformStrategyAdapter:
    """Adapts base strategy for platform-specific execution."""

    def __init__(self):
        """Initialize the platform strategy adapter."""
        self.logger = logger

    async def adapt(
        self,
        base_strategy: Dict[str, Any],
        platform: str
    ) -> PlatformStrategy:
        """
        Adapt strategy for specific platform.

        Args:
            base_strategy: Core brand strategy
            platform: Platform name (meta, google, tiktok, linkedin)

        Returns:
            Platform-specific strategy
        """
        self.logger.info(f"Adapting strategy for {platform}")

        platform_map = {
            "meta": self.adapt_for_meta,
            "google": self.adapt_for_google,
            "tiktok": self.adapt_for_tiktok,
            "linkedin": self.adapt_for_linkedin
        }

        adapter_func = platform_map.get(platform.lower())
        if not adapter_func:
            raise ValueError(f"Unknown platform: {platform}")

        return await adapter_func(base_strategy)

    async def adapt_for_meta(self, base_strategy: Dict[str, Any]) -> PlatformStrategy:
        """
        Adapt strategy for Meta (Facebook/Instagram).

        Meta logic:
        - Social proof and community matter
        - Visual storytelling
        - Interest-based targeting
        - Feed interruption pattern
        """
        self.logger.info("Adapting for Meta platform")

        return PlatformStrategy(
            platform="meta",
            content_strategy="social_storytelling",
            targeting_approach="interest_and_behavior_targeting",
            creative_guidelines={
                "format": "Carousel ads and Stories for engagement",
                "visual_style": "Authentic, user-generated feel",
                "copy_length": "Hook in first 3 words, concise body",
                "cta": "Social proof (reviews, user counts) prominently",
                "testing": "Test multiple creative variations (A/B/C/D)"
            }
        )

    async def adapt_for_google(self, base_strategy: Dict[str, Any]) -> PlatformStrategy:
        """
        Adapt strategy for Google Ads.

        Google logic:
        - Intent-driven (search behavior)
        - Problem-solution matching
        - Quality Score mechanics
        - Direct response focus
        """
        self.logger.info("Adapting for Google platform")

        return PlatformStrategy(
            platform="google",
            content_strategy="problem_solution",
            targeting_approach="search_intent_matching",
            creative_guidelines={
                "format": "Responsive Search Ads with extensions",
                "headline_structure": "Problem + Solution + Benefit",
                "keywords": "Match customer language exactly",
                "landing_page": "Message match from ad to landing page",
                "bidding": "Focus on high-intent keywords, use RLSA"
            }
        )

    async def adapt_for_tiktok(self, base_strategy: Dict[str, Any]) -> PlatformStrategy:
        """
        Adapt strategy for TikTok.

        TikTok logic:
        - Culture participation, not interruption
        - Trend-jacking and sound usage
        - Authentic, not polished
        - For You Page algorithm
        """
        self.logger.info("Adapting for TikTok platform")

        return PlatformStrategy(
            platform="tiktok",
            content_strategy="culture_participation",
            targeting_approach="interest_and_engagement_based",
            creative_guidelines={
                "format": "Vertical video 9:16, hook in first 2 seconds",
                "style": "Native, authentic, NOT like an ad",
                "trends": "Participate in trending sounds and challenges",
                "pacing": "Fast cuts, high energy, entertainment value",
                "cta": "Soft sell, invite to learn more vs hard pitch"
            }
        )

    async def adapt_for_linkedin(self, base_strategy: Dict[str, Any]) -> PlatformStrategy:
        """
        Adapt strategy for LinkedIn.

        LinkedIn logic:
        - Professional context
        - Thought leadership and credibility
        - B2B decision-makers
        - Career and business utility
        """
        self.logger.info("Adapting for LinkedIn platform")

        return PlatformStrategy(
            platform="linkedin",
            content_strategy="thought_leadership",
            targeting_approach="professional_criteria_targeting",
            creative_guidelines={
                "format": "Single image or document ads, professional quality",
                "tone": "Professional but approachable, expertise without jargon",
                "messaging": "Business outcomes and ROI focus",
                "credibility": "Use company logos, credentials, case studies",
                "targeting": "Job title, seniority, company size, industry"
            }
        )
