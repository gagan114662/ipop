from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.job import JobStatus


class JobCreate(BaseModel):
    """Schema for creating a new job"""
    original_filename: str
    original_filepath: str
    file_size: int
    file_type: str  # 'image' or 'video'
    mime_type: str
    selected_platforms: List[str]


class JobResponse(BaseModel):
    """Schema for returning job details"""
    id: UUID
    status: JobStatus
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

    original_filename: str
    original_filepath: str
    file_size: int
    file_type: str
    mime_type: str

    selected_platforms: List[str]
    total_platforms: int
    completed_platforms: int

    output_files: Optional[Dict[str, str]] = None
    zip_filepath: Optional[str] = None

    error_message: Optional[str] = None
    retry_count: int
    processing_time: Optional[float] = None

    class Config:
        from_attributes = True  # Enables ORM mode (was orm_mode in Pydantic v1)


class JobStatusResponse(BaseModel):
    """Schema for job status endpoint"""
    job_id: UUID
    status: JobStatus
    progress_percentage: float
    completed_platforms: int
    total_platforms: int
    platform_status: List[Dict[str, Any]]  # Simplified; you can make a nested model if needed
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    zip_available: bool