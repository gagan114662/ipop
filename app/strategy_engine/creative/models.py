"""Data models for creative brief generation.

Contains models for:
- Creative briefs
- Platform adaptations
- Brand consistency
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class CreativeBrief(BaseModel):
    """Creative brief for campaign creation."""

    single_minded_message: str = Field(..., description="Core message to communicate")
    tone: str = Field(..., description="Brand tone of voice")
    mandatories: List[str] = Field(default_factory=list, description="Must-have elements")
    avoid: List[str] = Field(default_factory=list, description="Things to avoid")
    platform: str = Field(..., description="Target platform")
    target_audience: Optional[str] = None
    context: Dict[str, str] = Field(default_factory=dict)


class BrandGuidelines(BaseModel):
    """Brand consistency guidelines."""

    visual_dos: List[str] = Field(default_factory=list)
    visual_donts: List[str] = Field(default_factory=list)
    verbal_dos: List[str] = Field(default_factory=list)
    verbal_donts: List[str] = Field(default_factory=list)
    core_values: List[str] = Field(default_factory=list)
