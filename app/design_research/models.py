"""Data models for design research.

Contains models for:
- Visual research results
- Aesthetic analysis
- Taste models
- Design patterns
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DesignProject(BaseModel):
    """Scraped design project."""

    platform: str = Field(..., description="behance, pinterest, dribbble, instagram")
    project_id: str
    title: str
    creator: str
    image_urls: List[str] = Field(default_factory=list)
    appreciations: int = Field(default=0)
    views: int = Field(default=0)
    tags: List[str] = Field(default_factory=list)
    scraped_at: datetime


class AestheticAnalysis(BaseModel):
    """Vision model analysis of image."""

    image_url: str
    composition: str
    color_theory: str
    typography: Optional[str] = None
    mood: str
    overall_score: float = Field(..., ge=0, le=10)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class ColorPalette(BaseModel):
    """Extracted color palette."""

    palette_name: str
    hex_colors: List[str] = Field(default_factory=list)
    frequency: float = Field(..., ge=0, le=1)
    mood: str


class DesignPattern(BaseModel):
    """Identified design pattern."""

    pattern_name: str
    description: str
    frequency: float = Field(..., ge=0, le=1)
    platforms: List[str] = Field(default_factory=list)
    example_urls: List[str] = Field(default_factory=list)


class HumanRating(BaseModel):
    """Human rating of a design."""

    image_url: str
    composition_score: float = Field(..., ge=0, le=10)
    color_score: float = Field(..., ge=0, le=10)
    originality_score: float = Field(..., ge=0, le=10)
    brand_fit_score: float = Field(..., ge=0, le=10)
    overall_score: float = Field(..., ge=0, le=10)
    notes: Optional[str] = None
    rated_at: datetime


class TasteModel(BaseModel):
    """Trained taste preference model."""

    model_id: str
    version: str
    trained_on: int = Field(..., description="Number of rated images")
    accuracy: float = Field(..., ge=0, le=1)
    preferences: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime


class VisualDNA(BaseModel):
    """Brand visual DNA extracted from research."""

    dominant_colors: List[str] = Field(default_factory=list)
    composition_style: str
    typography_approach: str
    mood_descriptors: List[str] = Field(default_factory=list)
    cultural_codes: List[str] = Field(default_factory=list)
    avoid_patterns: List[str] = Field(default_factory=list)
