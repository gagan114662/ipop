"""
SKU (Stock Keeping Unit) model for product-level campaign management.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum

from app.models.client import PyObjectId


class SKUStatus(str, Enum):
    """SKU status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class BudgetAllocation(BaseModel):
    """Budget allocation across platforms."""
    google_ads: float = 0.0
    meta: float = 0.0
    tiktok: float = 0.0
    linkedin: float = 0.0
    
    @property
    def total(self) -> float:
        """Calculate total budget."""
        return self.google_ads + self.meta + self.tiktok + self.linkedin


class SKUBase(BaseModel):
    """Base SKU schema."""
    sku_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    target_roas: Optional[float] = Field(None, gt=0)
    daily_budget: float = Field(..., gt=0)
    monthly_budget: float = Field(..., gt=0)
    budget_allocation: BudgetAllocation = BudgetAllocation()
    status: SKUStatus = SKUStatus.ACTIVE
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SKUCreate(SKUBase):
    """Schema for creating a new SKU."""
    pass


class SKUUpdate(BaseModel):
    """Schema for updating a SKU."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    target_roas: Optional[float] = Field(None, gt=0)
    daily_budget: Optional[float] = Field(None, gt=0)
    monthly_budget: Optional[float] = Field(None, gt=0)
    budget_allocation: Optional[BudgetAllocation] = None
    status: Optional[SKUStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class SKUInDB(SKUBase):
    """SKU model as stored in database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    total_spend: float = 0.0
    total_revenue: float = 0.0
    total_impressions: int = 0
    total_clicks: int = 0
    total_conversions: int = 0
    current_roas: Optional[float] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SKUResponse(BaseModel):
    """SKU response schema."""
    sku_id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    target_roas: Optional[float]
    daily_budget: float
    monthly_budget: float
    budget_allocation: BudgetAllocation
    status: SKUStatus
    created_at: datetime
    updated_at: datetime
    total_spend: float
    total_revenue: float
    total_impressions: int
    total_clicks: int
    total_conversions: int
    current_roas: Optional[float]
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class SKUList(BaseModel):
    """Paginated SKU list response."""
    items: List[SKUResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
