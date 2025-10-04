"""
Creative model for managing ad creative assets across platforms.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId

from app.models.client import PyObjectId
from app.models.campaign import Platform


class CreativeType(str, Enum):
    """Type of creative asset."""
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    COLLECTION = "collection"
    TEXT = "text"
    DYNAMIC = "dynamic"


class CreativeStatus(str, Enum):
    """Creative status."""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    DRAFT = "draft"
    TESTING = "testing"


class CallToAction(str, Enum):
    """Call-to-action button types."""
    SHOP_NOW = "shop_now"
    LEARN_MORE = "learn_more"
    SIGN_UP = "sign_up"
    DOWNLOAD = "download"
    GET_QUOTE = "get_quote"
    CONTACT_US = "contact_us"
    APPLY_NOW = "apply_now"
    BOOK_NOW = "book_now"
    SEE_MORE = "see_more"
    SUBSCRIBE = "subscribe"
    NO_BUTTON = "no_button"


class CreativeMedia(BaseModel):
    """Media asset information."""
    media_url: str = Field(..., description="URL to image or video")
    media_type: str = Field(..., description="image/jpeg, video/mp4, etc.")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail for videos")
    width: Optional[int] = Field(None, description="Width in pixels")
    height: Optional[int] = Field(None, description="Height in pixels")
    duration: Optional[int] = Field(None, description="Duration in seconds (for videos)")
    file_size: Optional[int] = Field(None, description="File size in bytes")


class CreativeBase(BaseModel):
    """Base creative schema."""
    creative_id: str = Field(..., min_length=1, max_length=200)
    name: str = Field(..., min_length=1, max_length=300)
    creative_type: CreativeType
    platform: Platform
    platform_creative_id: Optional[str] = Field(None, description="ID in the platform")

    # Creative content
    headline: Optional[str] = Field(None, max_length=200)
    primary_text: Optional[str] = Field(None, max_length=2000, description="Main ad copy")
    description: Optional[str] = Field(None, max_length=500)
    call_to_action: CallToAction = CallToAction.SHOP_NOW

    # Media assets
    media_assets: List[CreativeMedia] = Field(default_factory=list)

    # URLs
    destination_url: Optional[HttpUrl] = Field(None, description="Landing page URL")
    display_url: Optional[str] = Field(None, description="Display URL shown in ad")

    # Status and settings
    status: CreativeStatus = CreativeStatus.DRAFT

    # Performance thresholds
    min_ctr: Optional[float] = Field(None, gt=0, description="Minimum CTR threshold")
    min_roas: Optional[float] = Field(None, gt=0, description="Minimum ROAS threshold")

    # Tags and categorization
    tags: List[str] = Field(default_factory=list)

    # Platform-specific data
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreativeCreate(CreativeBase):
    """Schema for creating a new creative."""
    campaign_id: Optional[str] = Field(None, description="Associate with campaign")


class CreativeUpdate(BaseModel):
    """Schema for updating a creative."""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    headline: Optional[str] = Field(None, max_length=200)
    primary_text: Optional[str] = Field(None, max_length=2000)
    description: Optional[str] = Field(None, max_length=500)
    call_to_action: Optional[CallToAction] = None
    destination_url: Optional[HttpUrl] = None
    display_url: Optional[str] = None
    status: Optional[CreativeStatus] = None
    min_ctr: Optional[float] = Field(None, gt=0)
    min_roas: Optional[float] = Field(None, gt=0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class CreativePerformance(BaseModel):
    """Current creative performance metrics."""
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    revenue: float = 0.0

    # Calculated metrics
    ctr: float = Field(0.0, description="Click-through rate (%)")
    cpc: float = Field(0.0, description="Cost per click")
    cpa: float = Field(0.0, description="Cost per acquisition")
    cvr: float = Field(0.0, description="Conversion rate (%)")
    roas: float = Field(0.0, description="Return on ad spend")

    # Engagement (social platforms)
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0

    # Time tracking
    days_active: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class CreativeInDB(CreativeBase):
    """Creative model as stored in database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: str
    campaign_ids: List[str] = Field(default_factory=list, description="Associated campaigns")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    first_seen_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None

    # Performance tracking
    current_performance: CreativePerformance = CreativePerformance()
    total_impressions: int = 0
    total_spend: float = 0.0

    # Testing
    is_test_variant: bool = False
    test_id: Optional[str] = None
    variant_name: Optional[str] = Field(None, description="e.g., 'Variant A', 'Control'")

    # Lifecycle
    paused_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreativeResponse(BaseModel):
    """Creative response schema."""
    id: str
    creative_id: str
    name: str
    creative_type: CreativeType
    platform: Platform
    platform_creative_id: Optional[str]

    headline: Optional[str]
    primary_text: Optional[str]
    description: Optional[str]
    call_to_action: CallToAction

    media_assets: List[CreativeMedia]
    destination_url: Optional[str]
    display_url: Optional[str]

    status: CreativeStatus
    campaign_ids: List[str]

    current_performance: CreativePerformance
    total_impressions: int
    total_spend: float

    is_test_variant: bool
    test_id: Optional[str]

    tags: List[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreativeList(BaseModel):
    """List of creatives with pagination."""
    creatives: List[CreativeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CreativeComparison(BaseModel):
    """Compare multiple creatives."""
    creative_id: str
    name: str
    creative_type: CreativeType
    performance: CreativePerformance
    rank: int
    performance_score: float = Field(..., description="0-100 score based on ROAS, CTR, etc.")


class CreativeComparisonResponse(BaseModel):
    """Response for creative comparison."""
    campaign_id: str
    campaign_name: str
    creatives: List[CreativeComparison]
    best_performer: str
    recommendation: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
