"""Mock TikTok analyzer for viral trends and aesthetics.

In production, this would connect to TikTok API and analyze trending content.
For now, returns mock data based on category keywords.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class TikTokAnalyzer:
    """Analyzes TikTok trends and viral aesthetics (mock implementation)."""

    def __init__(self):
        """Initialize the TikTok analyzer."""
        self.logger = logger

    async def get_trends(self, category: str) -> List[Dict]:
        """
        Get viral trends from TikTok.

        Args:
            category: Category to analyze (e.g., "watches", "fashion")

        Returns:
            List of trend dictionaries with name, description, evidence
        """
        self.logger.info(f"Fetching TikTok trends for category: {category}")

        trends = []

        if "watch" in category.lower():
            trends = [
                {
                    "name": "Watch Collecting POV",
                    "description": "First-person watch unboxing and collection showcases",
                    "evidence": ["#watchtok hashtag 2M+ views", "Luxury watch POV videos"],
                    "strength": 0.70
                }
            ]
        elif "fashion" in category.lower() or "sustain" in category.lower():
            trends = [
                {
                    "name": "Thrift Flip Culture",
                    "description": "Transforming thrifted items into unique pieces",
                    "evidence": ["#ThriftFlip 500M+ views", "Upcycling tutorials"],
                    "strength": 0.85
                },
                {
                    "name": "Outfit Repeating",
                    "description": "Celebrating wearing the same items multiple times",
                    "evidence": ["#OutfitRepeater trend", "Capsule wardrobe content"],
                    "strength": 0.65
                }
            ]
        else:
            trends = [
                {
                    "name": "Authentic Living",
                    "description": "Raw, unfiltered lifestyle content",
                    "evidence": ["De-influencing trend", "Reality-based content growth"],
                    "strength": 0.75
                }
            ]

        self.logger.info(f"Found {len(trends)} TikTok trends")
        return trends

    async def get_aesthetic_trends(self, category: str) -> List[Dict]:
        """
        Get aesthetic and visual trends from TikTok.

        Args:
            category: Category to analyze

        Returns:
            List of aesthetic trend dictionaries
        """
        aesthetics = [
            {
                "name": "Old Money Aesthetic",
                "description": "Quiet luxury, timeless, understated elegance",
                "strength": 0.80
            },
            {
                "name": "Dopamine Dressing",
                "description": "Bold colors and patterns for mood boost",
                "strength": 0.70
            }
        ]

        return aesthetics
