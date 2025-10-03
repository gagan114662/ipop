"""
Campaign model for platform-specific advertising campaigns.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum

from app.models.client import PyObjectId


class Platform(str, Enum):
    """Supported advertising platforms."""
    GOOGLE_ADS = "google_ads"
    META = "meta"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    DRAFT = "draft"


class OptimizationMode(str, Enum):
    """Campaign optimization mode."""
    EXPLORE = "explore"  # Bold changes, learning phase
    EXPLOIT = "exploit"  # Small optimizations, proven performance


class CampaignBase(BaseModel):
    """Base campaign schema."""
    campaign_id: str = Field(..., min_length=1, max_length=200)
    name: str = Field(..., min_length=1, max_length=300)
    platform: Platform
    platform_campaign_id: str  # ID in the actual platform (Google Ads, Meta, etc.)
    daily_budget: float = Field(..., gt=0)
    target_cpa: Optional[float] = Field(None, gt=0)
    target_roas: Optional[float] = Field(None, gt=0)
    status: CampaignStatus = CampaignStatus.ACTIVE
    optimization_mode: OptimizationMode = OptimizationMode.EXPLORE
    integrator: Optional[str] = None  # revealbot, adroll, etc.
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CampaignCreate(CampaignBase):
    """Schema for creating a new campaign."""
    sku_id: str


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    daily_budget: Optional[float] = Field(None, gt=0)
    target_cpa: Optional[float] = Field(None, gt=0)
    target_roas: Optional[float] = Field(None, gt=0)
    status: Optional[CampaignStatus] = None
    optimization_mode: Optional[OptimizationMode] = None
    integrator: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CampaignMetrics(BaseModel):
    """Current campaign performance metrics."""
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    revenue: float = 0.0
    ctr: float = 0.0  # Click-through rate
    cpc: float = 0.0  # Cost per click
    cpa: float = 0.0  # Cost per acquisition
    roas: float = 0.0  # Return on ad spend
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class CampaignInDB(CampaignBase):
    """Campaign model as stored in database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: str
    sku_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    campaign_age_days: int = 0
    current_metrics: CampaignMetrics = CampaignMetrics()
    last_optimization: Optional[datetime] = None
    optimization_count: int = 0
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CampaignResponse(BaseModel):
    """Campaign response schema."""
    campaign_id: str
    name: str
    platform: Platform
    platform_campaign_id: str
    sku_id: str
    daily_budget: float
    target_cpa: Optional[float]
    target_roas: Optional[float]
    status: CampaignStatus
    optimization_mode: OptimizationMode
    integrator: Optional[str]
    created_at: datetime
    updated_at: datetime
    campaign_age_days: int
    current_metrics: CampaignMetrics
    last_optimization: Optional[datetime]
    optimization_count: int
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class CampaignList(BaseModel):
    """Paginated campaign list response."""
    items: List[CampaignResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class BudgetAdjustment(BaseModel):
    """Budget adjustment decision."""
    campaign_id: str
    old_budget: float
    new_budget: float
    change_percent: float
    reason: str
    mode: OptimizationMode
