"""
Creative A/B testing model for managing creative experiments.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.client import PyObjectId


class TestStatus(str, Enum):
    """Test status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestType(str, Enum):
    """Type of creative test."""
    AB_TEST = "ab_test"  # 2 variants
    MVT = "multivariate"  # Multiple variants
    CHAMPION_CHALLENGER = "champion_challenger"  # Existing vs new
    SEQUENTIAL = "sequential"  # Test variants one at a time


class TestMetric(str, Enum):
    """Primary metric to optimize for."""
    CTR = "ctr"
    ROAS = "roas"
    CPA = "cpa"
    CONVERSIONS = "conversions"
    ENGAGEMENT_RATE = "engagement_rate"
    VIDEO_COMPLETION = "video_completion"


class WinnerSelectionMethod(str, Enum):
    """How to select the winner."""
    STATISTICAL_SIGNIFICANCE = "statistical_significance"  # P-value based
    PERFORMANCE_THRESHOLD = "performance_threshold"  # Beats threshold
    BEST_AFTER_DURATION = "best_after_duration"  # Best when time expires
    BAYESIAN = "bayesian"  # Bayesian inference


class TestVariant(BaseModel):
    """A single variant in the test."""
    creative_id: str
    variant_name: str = Field(..., description="e.g., 'Control', 'Variant A', 'Variant B'")
    is_control: bool = False
    traffic_allocation: float = Field(..., ge=0, le=100, description="% of traffic")

    # Performance
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    revenue: float = 0.0

    # Calculated
    ctr: float = 0.0
    roas: float = 0.0
    cpa: float = 0.0
    cvr: float = 0.0

    # Statistical
    confidence_level: float = Field(0.0, description="0-100, confidence in results")
    is_significant: bool = False


class TestResult(BaseModel):
    """Results of the A/B test."""
    winner_creative_id: Optional[str] = None
    winner_variant_name: Optional[str] = None
    confidence_level: float = Field(0.0, description="0-100")
    improvement_vs_control: float = Field(0.0, description="% improvement")

    # Statistical metrics
    p_value: Optional[float] = None
    sample_size: int = 0
    statistical_power: Optional[float] = None

    # Performance comparison
    control_performance: Dict[str, float] = Field(default_factory=dict)
    winner_performance: Dict[str, float] = Field(default_factory=dict)

    # Recommendations
    recommendation: str = Field(..., description="Action to take based on results")
    next_steps: List[str] = Field(default_factory=list)


class CreativeTestBase(BaseModel):
    """Base schema for creative tests."""
    test_id: str = Field(..., min_length=1, max_length=200)
    name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = Field(None, max_length=1000)

    # Test configuration
    campaign_id: str
    test_type: TestType = TestType.AB_TEST
    primary_metric: TestMetric = TestMetric.ROAS

    # Variants
    variants: List[TestVariant] = Field(..., min_items=2)

    # Test settings
    min_sample_size: int = Field(1000, description="Minimum impressions per variant")
    confidence_threshold: float = Field(95.0, ge=90, le=99.9, description="Required confidence %")
    winner_selection: WinnerSelectionMethod = WinnerSelectionMethod.STATISTICAL_SIGNIFICANCE

    # Duration
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_duration_days: int = Field(14, description="Auto-conclude after N days")

    # Status
    status: TestStatus = TestStatus.DRAFT

    # Actions
    auto_promote_winner: bool = Field(True, description="Auto-activate winner")
    auto_pause_losers: bool = Field(True, description="Auto-pause losing variants")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreativeTestCreate(CreativeTestBase):
    """Schema for creating a new test."""
    pass


class CreativeTestUpdate(BaseModel):
    """Schema for updating a test."""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    status: Optional[TestStatus] = None
    end_date: Optional[datetime] = None
    variants: Optional[List[TestVariant]] = None
    auto_promote_winner: Optional[bool] = None
    auto_pause_losers: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class CreativeTestInDB(CreativeTestBase):
    """Creative test as stored in database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: str

    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    current_leader: Optional[str] = Field(None, description="Current best performing creative_id")
    result: Optional[TestResult] = None

    # Lifecycle
    is_concluded: bool = False
    conclusion_reason: Optional[str] = Field(None, description="Why test ended")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreativeTestResponse(BaseModel):
    """Creative test response schema."""
    id: str
    test_id: str
    name: str
    description: Optional[str]

    campaign_id: str
    test_type: TestType
    primary_metric: TestMetric

    variants: List[TestVariant]
    status: TestStatus

    min_sample_size: int
    confidence_threshold: float
    winner_selection: WinnerSelectionMethod

    start_date: Optional[datetime]
    end_date: Optional[datetime]
    max_duration_days: int

    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    current_leader: Optional[str]
    result: Optional[TestResult]

    is_concluded: bool
    conclusion_reason: Optional[str]

    auto_promote_winner: bool
    auto_pause_losers: bool

    class Config:
        from_attributes = True


class CreativeTestList(BaseModel):
    """List of creative tests with pagination."""
    tests: List[CreativeTestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CreativeTestAnalysis(BaseModel):
    """Detailed analysis of a running test."""
    test_id: str
    campaign_id: str
    status: TestStatus

    # Progress
    days_running: int
    progress_pct: float = Field(..., description="0-100, progress toward min sample size")

    # Current standings
    variants_analysis: List[Dict[str, Any]]
    current_leader: Optional[str]
    leader_confidence: float

    # Statistical analysis
    has_statistical_significance: bool
    can_conclude: bool = Field(..., description="Met criteria to conclude")
    recommendation: str

    # Time estimates
    estimated_days_remaining: Optional[int] = None
    min_sample_reached: bool

    timestamp: datetime = Field(default_factory=datetime.utcnow)
