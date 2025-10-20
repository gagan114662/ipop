"""Mock Google Trends analyzer for search trend analysis.

In production, this would connect to Google Trends API.
For now, returns mock data based on category keywords.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class GoogleTrendsAnalyzer:
    """Analyzes Google search trends (mock implementation)."""

    def __init__(self):
        """Initialize the Google Trends analyzer."""
        self.logger = logger

    async def get_trends(self, category: str) -> List[Dict]:
        """
        Get search trends from Google.

        Args:
            category: Category to analyze (e.g., "watches", "fashion")

        Returns:
            List of trend dictionaries with name, description, evidence
        """
        self.logger.info(f"Fetching Google Trends for category: {category}")

        trends = []

        if "watch" in category.lower():
            trends = [
                {
                    "name": "Micro-brand watches",
                    "description": "Increasing search interest in independent watch brands",
                    "evidence": ["Search volume up 45% YoY", "Regional interest: US, UK"],
                    "strength": 0.65
                }
            ]
        elif "sustain" in category.lower():
            trends = [
                {
                    "name": "Sustainable products",
                    "description": "Rising searches for eco-friendly alternatives",
                    "evidence": ["Search volume up 60% YoY", "Related: carbon neutral, eco-friendly"],
                    "strength": 0.80
                }
            ]
        else:
            trends = [
                {
                    "name": "Authentic brands",
                    "description": "Growing search for brand transparency and values",
                    "evidence": ["Search volume steady growth", "Related: ethical, transparent"],
                    "strength": 0.70
                }
            ]

        self.logger.info(f"Found {len(trends)} Google Trends")
        return trends

    async def get_rising_queries(self, category: str) -> List[str]:
        """
        Get rising search queries related to category.

        Args:
            category: Category to analyze

        Returns:
            List of rising query strings
        """
        queries = [
            f"{category} sustainability",
            f"best {category} brands",
            f"{category} reviews",
            f"ethical {category}"
        ]

        return queries
