"""Data models for external data sources.

Contains models for:
- Reddit discourse
- TikTok trends
- Google Trends
- Cultural intelligence
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RedditDiscourse(BaseModel):
    """Reddit discourse analysis."""

    subreddit: str
    trending_topics: List[str] = Field(default_factory=list)
    emerging_values: List[str] = Field(default_factory=list)
    sentiment: float = Field(..., ge=-1, le=1)
    sample_posts: List[str] = Field(default_factory=list)


class TikTokTrend(BaseModel):
    """TikTok trend data."""

    trend_name: str
    hashtag: str
    view_count: int
    viral_themes: List[str] = Field(default_factory=list)
    aesthetic_codes: List[str] = Field(default_factory=list)


class GoogleTrendData(BaseModel):
    """Google Trends data."""

    keyword: str
    interest_over_time: Dict[str, float] = Field(default_factory=dict)
    related_queries: List[str] = Field(default_factory=list)
    regional_interest: Dict[str, float] = Field(default_factory=dict)


class CulturalSignal(BaseModel):
    """Aggregated cultural signal."""

    signal_name: str
    strength: float = Field(..., ge=0, le=1)
    sources: List[str] = Field(default_factory=list)
    first_detected: datetime
    trend_direction: str = Field(..., description="rising, stable, declining")
