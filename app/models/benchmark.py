"""
System-wide benchmarks model for cross-client learning (anonymized).
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.client import PyObjectId
from app.models.campaign import Platform


class BenchmarkBase(BaseModel):
    """Base benchmark schema."""
    platform: Platform
    industry: Optional[str] = None
    region: str  # NA, EU, etc.
    avg_ctr: float = 0.0
    avg_cpc: float = 0.0
    avg_cpa: float = 0.0
    avg_cvr: float = 0.0
    avg_roas: float = 0.0
    median_roas: float = 0.0
    p75_roas: float = 0.0  # 75th percentile
    p90_roas: float = 0.0  # 90th percentile
    sample_size: int = 0  # Number of campaigns in benchmark
    confidence_level: float = 0.0  # 0-1


class SystemBenchmarkCreate(BenchmarkBase):
    """Schema for creating system benchmarks."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemBenchmarkInDB(BenchmarkBase):
    """System benchmark as stored in database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    month: str  # YYYY-MM for monthly aggregation
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SystemBenchmarkResponse(BaseModel):
    """System benchmark response schema."""
    platform: Platform
    industry: Optional[str]
    region: str
    avg_ctr: float
    avg_cpc: float
    avg_cpa: float
    avg_cvr: float
    avg_roas: float
    median_roas: float
    p75_roas: float
    p90_roas: float
    sample_size: int
    confidence_level: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PerformanceComparison(BaseModel):
    """Compare campaign performance to benchmarks."""
    campaign_id: str
    platform: Platform
    campaign_roas: float
    benchmark_avg_roas: float
    benchmark_median_roas: float
    performance_percentile: Optional[float]  # Where campaign ranks (0-100)
    status: str  # "above_average", "average", "below_average"
    gap_to_p75: Optional[float]  # How far from 75th percentile
    recommendations: list[str]
