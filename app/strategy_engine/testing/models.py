"""Data models for testing and learning systems.

Contains models for:
- Hypotheses
- Test designs
- Bayesian learning
- Meta-learning patterns
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Variant(BaseModel):
    """Test variant configuration."""

    variant_id: str
    variant_type: str = Field(..., description="control, product_hero, lifestyle, insight_driven")
    creative_brief: str
    expected_lift: Optional[float] = None


class Hypothesis(BaseModel):
    """Testable hypothesis from insight."""

    belief_statement: str
    variants: List[Variant] = Field(default_factory=list)
    success_metric: str = Field(..., description="conversion_rate, roas, ctr, etc.")
    minimum_sample_size: int


class TestPlan(BaseModel):
    """Complete A/B test plan."""

    hypothesis: Hypothesis
    control: Variant
    variants: List[Variant] = Field(default_factory=list)
    sample_size_per_variant: int
    minimum_significance: float = Field(default=0.95, ge=0, le=1)
    budget_allocation: Dict[str, float] = Field(default_factory=dict)


class TestResult(BaseModel):
    """Test results."""

    test_id: str
    winner: str
    lift: float
    significance: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)


class UpdatedBelief(BaseModel):
    """Bayesian updated belief."""

    prior_confidence: float
    posterior_confidence: float
    evidence_strength: float
    recommendation: str
