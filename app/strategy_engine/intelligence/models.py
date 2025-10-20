"""Data models for intelligence and insight mining.

Contains models for:
- Contradictions
- Strategic insights
- Insight scoring
- Pattern recognition
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Contradiction(BaseModel):
    """Gap between stated preference and actual behavior."""

    tension: str
    stated_preference: str
    actual_behavior: str
    human_truth: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)


class Insight(BaseModel):
    """Strategic insight derived from contradiction."""

    observation: str
    tension: str
    human_truth: str
    strategic_implication: str
    source_contradiction: Optional[Contradiction] = None


class InsightScore(BaseModel):
    """Multi-dimensional scoring of an insight."""

    market_opportunity: float = Field(..., ge=0, le=10)
    conversion_potential: float = Field(..., ge=0, le=10)
    competitive_advantage: float = Field(..., ge=0, le=10)
    total: float = Field(..., ge=0, le=10)
    reasoning: str


class Pattern(BaseModel):
    """Cross-client pattern identified."""

    pattern_name: str
    description: str
    validated_in_count: int = Field(..., ge=0)
    avg_lift: float = Field(..., ge=0)
    categories: List[str] = Field(default_factory=list)
