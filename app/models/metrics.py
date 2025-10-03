"""
Performance metrics model for tracking campaign performance over time.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.client import PyObjectId
from app.models.campaign import Platform


class MetricsBase(BaseModel):
    """Base metrics schema."""
    impressions: int = Field(..., ge=0)
    clicks: int = Field(..., ge=0)
    conversions: int = Field(..., ge=0)
    spend: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    ctr: float = Field(0.0, ge=0)  # Click-through rate
    cpc: float = Field(0.0, ge=0)  # Cost per click
    cpa: float = Field(0.0, ge=0)  # Cost per acquisition
    cvr: float = Field(0.0, ge=0)  # Conversion rate
    roas: float = Field(0.0, ge=0)  # Return on ad spend


class PerformanceMetricsCreate(MetricsBase):
    """Schema for creating performance metrics."""
    campaign_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PerformanceMetricsInDB(MetricsBase):
    """Performance metrics as stored in database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: str
    campaign_id: str
    sku_id: str
    platform: Platform
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    hour_of_day: int  # 0-23 for time pattern analysis
    day_of_week: int  # 0-6 for weekly pattern analysis
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response schema."""
    campaign_id: str
    sku_id: str
    platform: Platform
    timestamp: datetime
    impressions: int
    clicks: int
    conversions: int
    spend: float
    revenue: float
    ctr: float
    cpc: float
    cpa: float
    cvr: float
    roas: float
    
    class Config:
        from_attributes = True


class MetricsSummary(BaseModel):
    """Aggregated metrics summary."""
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_spend: float
    total_revenue: float
    avg_ctr: float
    avg_cpc: float
    avg_cpa: float
    avg_cvr: float
    avg_roas: float
    period_start: datetime
    period_end: datetime


class CampaignBurnRate(BaseModel):
    """Campaign budget burn rate analysis."""
    campaign_id: str
    daily_budget: float
    current_spend_today: float
    burn_rate_percent: float  # % of daily budget spent
    projected_end_time: Optional[datetime]  # When budget will be exhausted
    hours_remaining: Optional[float]
    status: str  # "on_track", "under_spending", "over_spending"
    recommendation: Optional[str]


class SKUBurnRate(BaseModel):
    """SKU-level budget burn rate."""
    sku_id: str
    daily_budget: float
    current_spend_today: float
    burn_rate_percent: float
    campaigns: List[CampaignBurnRate]
    status: str
