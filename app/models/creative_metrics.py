"""
Creative performance metrics model for time-series tracking.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.client import PyObjectId
from app.models.campaign import Platform


class CreativeMetricsBase(BaseModel):
    """Base schema for creative metrics."""
    creative_id: str
    campaign_id: str
    platform: Platform

    # Core metrics
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    revenue: float = 0.0

    # Calculated rates
    ctr: float = Field(0.0, description="Click-through rate (%)")
    cpc: float = Field(0.0, description="Cost per click")
    cpm: float = Field(0.0, description="Cost per mille (1000 impressions)")
    cpa: float = Field(0.0, description="Cost per acquisition")
    cvr: float = Field(0.0, description="Conversion rate (%)")
    roas: float = Field(0.0, description="Return on ad spend")

    # Social engagement (Meta, TikTok, LinkedIn)
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saves: int = 0
    engagement_rate: float = Field(0.0, description="Engagement rate (%)")

    # Video metrics (if applicable)
    video_views: int = 0
    video_views_25: int = 0
    video_views_50: int = 0
    video_views_75: int = 0
    video_views_100: int = 0
    avg_watch_time: float = Field(0.0, description="Average watch time in seconds")

    # Quality metrics
    relevance_score: Optional[float] = Field(None, description="Platform quality score")
    frequency: Optional[float] = Field(None, description="Avg times shown to same user")

    # Time period
    date: datetime = Field(..., description="Metrics date (YYYY-MM-DD)")
    aggregation_period: str = Field("daily", description="daily, weekly, monthly")

    # Platform-specific data
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreativeMetricsInDB(CreativeMetricsBase):
    """Creative metrics as stored in database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: str

    # Tracking
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    data_source: str = Field("platform_api", description="platform_api, manual, estimated")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreativeMetricsResponse(BaseModel):
    """Creative metrics response schema."""
    creative_id: str
    campaign_id: str
    platform: Platform

    impressions: int
    clicks: int
    conversions: int
    spend: float
    revenue: float

    ctr: float
    cpc: float
    cpm: float
    cpa: float
    cvr: float
    roas: float

    likes: int
    shares: int
    comments: int
    engagement_rate: float

    video_views: int
    video_views_100: int
    avg_watch_time: float

    relevance_score: Optional[float]
    frequency: Optional[float]

    date: datetime
    aggregation_period: str

    class Config:
        from_attributes = True


class CreativeMetricsTimeseries(BaseModel):
    """Time-series metrics for a creative."""
    creative_id: str
    campaign_id: str
    start_date: datetime
    end_date: datetime
    data_points: list[CreativeMetricsResponse]
    total_points: int


class CreativeMetricsSummary(BaseModel):
    """Aggregated summary of creative performance."""
    creative_id: str
    campaign_id: str
    period_start: datetime
    period_end: datetime
    days_active: int

    # Totals
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_spend: float
    total_revenue: float

    # Averages
    avg_ctr: float
    avg_cpc: float
    avg_cpa: float
    avg_roas: float
    avg_engagement_rate: float

    # Trends
    ctr_trend: str = Field(..., description="increasing, decreasing, stable")
    roas_trend: str = Field(..., description="increasing, decreasing, stable")
    spend_trend: str = Field(..., description="increasing, decreasing, stable")

    # Performance indicators
    best_day: Optional[datetime] = Field(None, description="Best performing day")
    worst_day: Optional[datetime] = Field(None, description="Worst performing day")
    best_roas: float = 0.0
    worst_roas: float = 0.0

    # Health indicators
    is_fatigued: bool = Field(False, description="Showing signs of creative fatigue")
    fatigue_score: float = Field(0.0, description="0-100, higher = more fatigued")
    recommendation: Optional[str] = None


class CreativeMetricsAggregation(BaseModel):
    """Aggregated metrics across multiple creatives."""
    campaign_id: str
    period_start: datetime
    period_end: datetime
    creative_count: int

    # Totals
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_spend: float
    total_revenue: float

    # Overall performance
    overall_ctr: float
    overall_roas: float
    overall_cpa: float

    # Creative breakdown
    top_creative_by_roas: Optional[str] = None
    top_creative_by_ctr: Optional[str] = None
    top_creative_by_engagement: Optional[str] = None

    # Distribution
    active_creatives: int
    paused_creatives: int
    testing_creatives: int
