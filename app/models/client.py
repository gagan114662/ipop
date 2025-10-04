"""
Client model for multi-tenant architecture.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Pydantic v2 core schema."""
        from pydantic_core import core_schema

        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ], serialization=core_schema.plain_serializer_function_ser_schema(
            lambda x: str(x)
        ))

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class ClientSettings(BaseModel):
    """Client-specific configuration settings."""
    default_timezone: str = "UTC"
    default_currency: str = "USD"
    regions: List[str] = ["NA", "EU"]
    notification_email: Optional[EmailStr] = None
    auto_optimization_enabled: bool = True
    min_campaign_budget: float = 100.0
    max_daily_budget_change_percent: float = 20.0


class ClientBase(BaseModel):
    """Base client schema for creation/update."""
    company_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    is_active: bool = True
    settings: Optional[ClientSettings] = ClientSettings()


class ClientCreate(ClientBase):
    """Schema for creating a new client."""
    password: str = Field(..., min_length=8)


class ClientUpdate(BaseModel):
    """Schema for updating a client."""
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    settings: Optional[ClientSettings] = None


class ClientInDB(ClientBase):
    """Client model as stored in database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: str  # UUID for external references
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ClientResponse(BaseModel):
    """Client response schema (public facing)."""
    client_id: str
    company_name: str
    email: EmailStr
    is_active: bool
    settings: ClientSettings
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str


class LoginRequest(BaseModel):
    """Login credentials."""
    email: EmailStr
    password: str
