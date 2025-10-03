"""
Enhanced input validation for API models.
"""
from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import datetime


class EnhancedValidationMixin:
    """Mixin for enhanced validation across models."""
    
    @validator('daily_budget', 'target_roas', 'monthly_budget', check_fields=False)
    def validate_positive_number(cls, v, field):
        """Ensure numeric values are positive."""
        if v is not None and v <= 0:
            raise ValueError(f'{field.name} must be positive')
        return v
    
    @validator('daily_budget', check_fields=False)
    def validate_minimum_budget(cls, v):
        """Ensure budget meets minimum requirements."""
        if v is not None and v < 100:
            raise ValueError('Minimum daily budget is $100')
        return v
    
    @validator('target_roas', check_fields=False)
    def validate_roas_range(cls, v):
        """Ensure ROAS is in reasonable range."""
        if v is not None:
            if v < 0.1:
                raise ValueError('ROAS must be at least 0.1')
            if v > 100:
                raise ValueError('ROAS cannot exceed 100')
        return v


class DateRangeValidationMixin:
    """Mixin for date range validation."""
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Ensure end_date is after start_date."""
        start_date = values.get('start_date')
        if start_date and v:
            if v < start_date:
                raise ValueError('end_date must be after start_date')
            
            # Prevent extremely long date ranges
            delta = v - start_date
            if delta.days > 365:
                raise ValueError('Date range cannot exceed 365 days')
        
        return v


class StringValidationMixin:
    """Mixin for string validation."""
    
    @validator('email', check_fields=False)
    def validate_email_format(cls, v):
        """Validate email format."""
        if v:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
        return v.lower() if v else v
    
    @validator('campaign_id', 'sku_id', 'client_id', check_fields=False)
    def validate_id_format(cls, v, field):
        """Validate ID formats."""
        if v:
            # Ensure IDs are not empty strings
            if not v.strip():
                raise ValueError(f'{field.name} cannot be empty')
            
            # Ensure reasonable length
            if len(v) > 100:
                raise ValueError(f'{field.name} must be 100 characters or less')
            
            # Remove leading/trailing whitespace
            v = v.strip()
        
        return v
    
    @validator('name', 'company_name', check_fields=False)
    def validate_name_length(cls, v, field):
        """Validate name fields."""
        if v:
            if not v.strip():
                raise ValueError(f'{field.name} cannot be empty')
            
            if len(v) > 200:
                raise ValueError(f'{field.name} must be 200 characters or less')
            
            v = v.strip()
        
        return v


class MetadataValidationMixin:
    """Mixin for metadata validation."""
    
    @validator('metadata', check_fields=False)
    def validate_metadata_size(cls, v):
        """Ensure metadata is not too large."""
        if v:
            import json
            metadata_str = json.dumps(v)
            if len(metadata_str) > 10000:  # 10KB limit
                raise ValueError('Metadata size exceeds 10KB limit')
        return v


# Example usage in existing models:

class BudgetUpdateRequest(BaseModel, EnhancedValidationMixin):
    """Budget update request with validation."""
    daily_budget: float = Field(..., gt=100, description="Daily budget in USD (minimum $100)")
    reason: Optional[str] = Field(None, max_length=500)


class DateRangeRequest(BaseModel, DateRangeValidationMixin):
    """Date range request with validation."""
    start_date: datetime
    end_date: datetime


class CampaignCreateRequest(BaseModel, EnhancedValidationMixin, StringValidationMixin, MetadataValidationMixin):
    """Campaign creation with full validation."""
    campaign_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    daily_budget: float = Field(..., gt=100)
    target_roas: Optional[float] = Field(None, gt=0.1, lt=100)
    metadata: Optional[dict] = None
