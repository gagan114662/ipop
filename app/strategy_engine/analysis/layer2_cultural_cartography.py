"""Layer 2: Cultural Cartography

This layer analyzes cultural trends and shifts:
- Macro cultural trends
- Value shifts (old → new)
- Emerging communities
- Uses data from Reddit, TikTok, Google Trends

Mock implementation for now with placeholder data sources.
"""

import logging
from typing import List
from app.strategy_engine.analysis.models import CulturalLandscape, CulturalTrend, ValueShift
from app.strategy_engine.data_sources.reddit_analyzer import RedditAnalyzer
from app.strategy_engine.data_sources.tiktok_analyzer import TikTokAnalyzer
from app.strategy_engine.data_sources.google_trends import GoogleTrendsAnalyzer

logger = logging.getLogger(__name__)


class CulturalCartography:
    """Analyzes cultural landscape and value shifts."""

    def __init__(self):
        """Initialize the cultural cartography analyzer."""
        self.logger = logger
        self.reddit = RedditAnalyzer()
        self.tiktok = TikTokAnalyzer()
        self.google_trends = GoogleTrendsAnalyzer()

    async def analyze(self, category: str) -> CulturalLandscape:
        """
        Analyze cultural landscape for a category.

        Args:
            category: Category to analyze (e.g., "luxury watches")

        Returns:
            CulturalLandscape with macro trends, value shifts, emerging communities
        """
        self.logger.info(f"Analyzing cultural landscape for: {category}")

        # Get trends from all sources
        reddit_trends = await self._get_reddit_trends(category)
        tiktok_trends = await self._get_tiktok_trends(category)
        google_trends_data = await self._get_google_trends(category)

        # Combine and deduplicate trends
        all_trends_data = reddit_trends + tiktok_trends + google_trends_data
        macro_trends = self._consolidate_trends(all_trends_data)

        # Detect value shifts
        value_shifts = await self.detect_value_shifts(category)

        # Identify emerging communities
        emerging_communities = await self.identify_emerging_communities(category)

        self.logger.info(
            f"Cultural analysis complete: {len(macro_trends)} trends, "
            f"{len(value_shifts)} value shifts, {len(emerging_communities)} communities"
        )

        return CulturalLandscape(
            macro_trends=macro_trends,
            value_shifts=value_shifts,
            emerging_communities=emerging_communities
        )

    async def _get_reddit_trends(self, category: str) -> List[dict]:
        """Get trends from Reddit."""
        try:
            return await self.reddit.get_trends(category)
        except Exception as e:
            self.logger.warning(f"Reddit trends fetch failed: {e}")
            return []

    async def _get_tiktok_trends(self, category: str) -> List[dict]:
        """Get trends from TikTok."""
        try:
            return await self.tiktok.get_trends(category)
        except Exception as e:
            self.logger.warning(f"TikTok trends fetch failed: {e}")
            return []

    async def _get_google_trends(self, category: str) -> List[dict]:
        """Get trends from Google Trends."""
        try:
            return await self.google_trends.get_trends(category)
        except Exception as e:
            self.logger.warning(f"Google Trends fetch failed: {e}")
            return []

    def _consolidate_trends(self, trends_data: List[dict]) -> List[CulturalTrend]:
        """
        Consolidate trends from multiple sources.

        Deduplicates similar trends and combines evidence.
        """
        # Simple implementation: convert all to CulturalTrend objects
        # In production, would use NLP to detect similar trends and merge them
        consolidated = []
        seen_names = set()

        for trend_dict in trends_data:
            name = trend_dict.get("name", "")
            if name and name not in seen_names:
                consolidated.append(
                    CulturalTrend(
                        trend_name=name,
                        description=trend_dict.get("description", ""),
                        evidence=trend_dict.get("evidence", []),
                        strength=trend_dict.get("strength", 0.5)
                    )
                )
                seen_names.add(name)

        # Sort by strength
        consolidated.sort(key=lambda t: t.strength, reverse=True)

        return consolidated[:10]  # Top 10 trends

    async def detect_value_shifts(self, category: str) -> List[ValueShift]:
        """
        Detect value shifts in the category.

        Args:
            category: Category to analyze

        Returns:
            List of ValueShift objects
        """
        self.logger.info(f"Detecting value shifts for: {category}")

        # Get value shifts from Reddit (our primary source for cultural discourse)
        reddit_shifts = await self.reddit.get_value_shifts(category)

        # Add category-specific shifts based on keyword analysis
        category_shifts = self._get_category_specific_shifts(category)

        # Combine all shifts
        all_shifts_data = reddit_shifts + category_shifts

        # Convert to ValueShift objects
        shifts = []
        for shift_dict in all_shifts_data:
            shifts.append(
                ValueShift(
                    old_value=shift_dict.get("old_value", ""),
                    new_value=shift_dict.get("new_value", ""),
                    evidence=shift_dict.get("evidence", []),
                    strength=shift_dict.get("strength", 0.5)
                )
            )

        # Sort by strength
        shifts.sort(key=lambda s: s.strength, reverse=True)

        self.logger.info(f"Found {len(shifts)} value shifts")
        return shifts

    def _get_category_specific_shifts(self, category: str) -> List[dict]:
        """Get value shifts specific to category based on keywords."""
        shifts = []

        category_lower = category.lower()

        if "luxury" in category_lower:
            shifts.append({
                "old_value": "Conspicuous consumption",
                "new_value": "Conscious luxury",
                "evidence": ["Quiet luxury trend", "Logo fatigue"],
                "strength": 0.75
            })
            shifts.append({
                "old_value": "Possession",
                "new_value": "Experience",
                "evidence": ["Experience economy growth", "Minimalism movement"],
                "strength": 0.70
            })

        if "sustain" in category_lower or "eco" in category_lower:
            shifts.append({
                "old_value": "Convenience first",
                "new_value": "Environmental responsibility",
                "evidence": ["Zero waste movement", "Climate activism"],
                "strength": 0.80
            })

        if "fashion" in category_lower:
            shifts.append({
                "old_value": "Fast fashion trends",
                "new_value": "Timeless personal style",
                "evidence": ["Capsule wardrobe trend", "Slow fashion movement"],
                "strength": 0.72
            })

        if "watch" in category_lower:
            shifts.append({
                "old_value": "Smartphone time-telling",
                "new_value": "Watches as intentional objects",
                "evidence": ["Watch collecting growth", "Appreciation for craftsmanship"],
                "strength": 0.65
            })

        # Universal shifts (apply to all categories)
        shifts.append({
            "old_value": "Brand loyalty through advertising",
            "new_value": "Brand loyalty through values alignment",
            "evidence": ["Gen Z brand expectations", "Purpose-driven purchasing"],
            "strength": 0.78
        })

        return shifts

    async def identify_emerging_communities(self, category: str) -> List[str]:
        """
        Identify emerging communities related to category.

        Args:
            category: Category to analyze

        Returns:
            List of community descriptions
        """
        self.logger.info(f"Identifying emerging communities for: {category}")

        # Get communities from Reddit
        communities = await self.reddit.get_emerging_communities(category)

        # Add category-specific communities
        category_lower = category.lower()

        if "sustain" in category_lower:
            communities.extend([
                "Zero waste practitioners",
                "Climate action advocates"
            ])

        if "luxury" in category_lower:
            communities.extend([
                "Quiet luxury enthusiasts",
                "Heritage brand collectors"
            ])

        # Remove duplicates
        communities = list(set(communities))

        self.logger.info(f"Found {len(communities)} emerging communities")
        return communities[:5]  # Top 5 communities
