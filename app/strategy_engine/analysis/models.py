"""Data models for strategic analysis.

Contains Pydantic models for:
- Category analysis results
- Cultural trends
- Framework tensions
- Semiotic maps
- Behavioral dynamics
- Jobs analysis
- Platform strategies
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class MaturityStage(BaseModel):
    """Category maturity stage."""

    stage: str = Field(..., description="early_innovation, growth, mature, commoditized")
    strategic_implication: str = Field(..., description="What this means for brand strategy")


class CategoryAnalysis(BaseModel):
    """Category archaeology analysis results."""

    stated_category: str = Field(..., description="How brand describes itself")
    functional_category: Optional[str] = Field(None, description="True functional job category")
    emotional_category: Optional[str] = Field(None, description="Emotional job served")
    social_category: Optional[str] = Field(None, description="Social job served")
    maturity: Optional[MaturityStage] = Field(None, description="Category maturity stage")
    strategic_implication: Optional[str] = Field(None, description="Strategic implications of category analysis")
    real_competitors: List[str] = Field(default_factory=list, description="True competitors based on function")


class CulturalTrend(BaseModel):
    """Cultural trend or value shift."""

    trend_name: str
    description: str
    evidence: List[str] = Field(default_factory=list)
    strength: float = Field(..., ge=0, le=1, description="Trend strength 0-1")


class ValueShift(BaseModel):
    """Cultural value shift from old to new."""

    old_value: str = Field(..., description="Previous cultural value")
    new_value: str = Field(..., description="Emerging cultural value")
    evidence: List[str] = Field(default_factory=list)
    strength: float = Field(..., ge=0, le=1, description="Shift strength 0-1")


class CulturalLandscape(BaseModel):
    """Complete cultural analysis."""

    macro_trends: List[CulturalTrend] = Field(default_factory=list)
    value_shifts: List[ValueShift] = Field(default_factory=list)
    emerging_communities: List[str] = Field(default_factory=list)


class Tension(BaseModel):
    """Strategic tension or contradiction."""

    tension_type: str = Field(..., description="product_user, space_time, ux_product")
    contradiction: str
    human_truth: str = Field(..., description="The underlying human truth revealed")
    strategic_implication: str = Field(..., description="What this means for strategy")


class VisualCode(BaseModel):
    """Visual semiotic code."""

    code_name: str
    frequency: float = Field(..., ge=0, le=1)
    examples: List[str] = Field(default_factory=list)


class CognitiveBias(BaseModel):
    """Cognitive bias identified in purchase behavior."""

    bias_name: str = Field(..., description="Name of cognitive bias (e.g., anchoring, social_proof)")
    description: str = Field(..., description="How this bias manifests")
    strength: float = Field(..., ge=0, le=1, description="Strength of bias 0-1")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting this bias")


class DecisionDriver(BaseModel):
    """Factor driving customer decision-making."""

    driver_name: str = Field(..., description="Name of decision driver")
    category: str = Field(..., description="emotional, rational, or social")
    importance: float = Field(..., ge=0, le=1, description="Importance score 0-1")
    description: str = Field(..., description="How this driver influences decisions")


class BehavioralLever(BaseModel):
    """Lever to influence customer behavior."""

    lever_name: str = Field(..., description="Name of behavioral lever")
    bias_targeted: str = Field(..., description="Which bias this lever targets")
    tactic: str = Field(..., description="Specific tactic to apply")
    expected_impact: str = Field(..., description="Expected impact on behavior")


class BehavioralDynamics(BaseModel):
    """Complete behavioral economics analysis (formerly BehavioralDynamic)."""

    dominant_biases: List[str] = Field(default_factory=list, description="Top cognitive biases at play")
    decision_speed: str = Field(..., description="fast, slow, or mixed")
    primary_drivers: List[DecisionDriver] = Field(default_factory=list)
    leverage_points: List[BehavioralLever] = Field(default_factory=list)
    decision_architecture: Dict[str, Any] = Field(default_factory=dict, description="System 1 vs System 2")


# Keep old name for backward compatibility
BehavioralDynamic = BehavioralDynamics


class Job(BaseModel):
    """Job-to-be-done."""

    job_type: str = Field(..., description="functional, emotional, social")
    description: str
    alternatives: List[str] = Field(default_factory=list)
    importance: float = Field(default=0.5, ge=0, le=1)


class Alternative(BaseModel):
    """Alternative solution customers consider for the job."""

    name: str = Field(..., description="Name of alternative solution")
    category: str = Field(..., description="direct_competitor, indirect_competitor, substitute, non-consumption")
    description: str = Field(..., description="How this alternative addresses the job")
    switching_cost: float = Field(default=0.5, ge=0, le=1, description="Difficulty of switching to this alternative")


class JobsAnalysis(BaseModel):
    """Complete Jobs-to-be-Done analysis."""

    primary_job: Job = Field(..., description="The most important job customer is hiring product for")
    functional_job: Job = Field(..., description="Practical, tangible job")
    emotional_job: Job = Field(..., description="How customer wants to feel")
    social_job: Job = Field(..., description="How customer wants to be perceived")
    alternatives: List[Alternative] = Field(default_factory=list, description="Alternative solutions considered")
    job_hierarchy: Dict[str, float] = Field(default_factory=dict, description="Ranking of job importance")


class PlatformStrategy(BaseModel):
    """Platform-specific strategy adaptation."""

    platform: str
    content_strategy: str
    targeting_approach: str
    creative_guidelines: Dict[str, str] = Field(default_factory=dict)


class BrandStrategy(BaseModel):
    """Complete strategic analysis output."""

    category_analysis: Optional[CategoryAnalysis] = None
    cultural_trends: List[CulturalTrend] = Field(default_factory=list)
    framework_tensions: List[Tension] = Field(default_factory=list)
    visual_codes: List[VisualCode] = Field(default_factory=list)
    behavioral_dynamics: Optional[BehavioralDynamic] = None
    jobs: List[Job] = Field(default_factory=list)
    platform_strategies: Dict[str, PlatformStrategy] = Field(default_factory=dict)
