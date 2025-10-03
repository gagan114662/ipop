"""
Intelligence decision model for tracking optimization decisions and audit trail.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.client import PyObjectId
from app.models.campaign import Platform, OptimizationMode


class DecisionType(str, Enum):
    """Type of intelligence decision."""
    BUDGET_INCREASE = "budget_increase"
    BUDGET_DECREASE = "budget_decrease"
    PAUSE_CAMPAIGN = "pause_campaign"
    ACTIVATE_CAMPAIGN = "activate_campaign"
    MODE_SWITCH = "mode_switch"  # EXPLORE <-> EXPLOIT
    NO_ACTION = "no_action"


from enum import Enum


class DecisionBase(BaseModel):
    """Base decision schema."""
    campaign_id: str
    decision_type: DecisionType
    mode: OptimizationMode
    confidence_score: float = Field(..., ge=0, le=1)
    reasoning: str
    old_budget: Optional[float] = None
    new_budget: Optional[float] = None
    budget_change_percent: Optional[float] = None
    expected_impact: Optional[str] = None
    metrics_snapshot: Dict[str, Any] = Field(default_factory=dict)


class IntelligenceDecisionCreate(DecisionBase):
    """Schema for creating an intelligence decision."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IntelligenceDecisionInDB(DecisionBase):
    """Intelligence decision as stored in database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: str
    sku_id: str
    platform: Platform
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    applied: bool = False  # Whether the decision was actually applied
    applied_at: Optional[datetime] = None
    actual_impact: Optional[Dict[str, Any]] = None
    success_score: Optional[float] = None  # 0-1, evaluated after some time
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class IntelligenceDecisionResponse(BaseModel):
    """Intelligence decision response schema."""
    campaign_id: str
    sku_id: str
    platform: Platform
    decision_type: DecisionType
    mode: OptimizationMode
    confidence_score: float
    reasoning: str
    old_budget: Optional[float]
    new_budget: Optional[float]
    budget_change_percent: Optional[float]
    expected_impact: Optional[str]
    timestamp: datetime
    applied: bool
    applied_at: Optional[datetime]
    success_score: Optional[float]
    
    class Config:
        from_attributes = True


class DecisionHistory(BaseModel):
    """Historical decisions for a campaign."""
    campaign_id: str
    decisions: List[IntelligenceDecisionResponse]
    total_decisions: int
    successful_decisions: int
    average_success_score: float
    last_decision: Optional[datetime]


class OptimizationRecommendation(BaseModel):
    """Real-time optimization recommendation."""
    campaign_id: str
    current_mode: OptimizationMode
    recommended_action: DecisionType
    recommended_budget: Optional[float]
    confidence: float
    reasoning: str
    priority: str  # "high", "medium", "low"
    estimated_impact: str
