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
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    original_filename: str
    original_filepath: str
    file_size: int
    file_type: str
    mime_type: str

    selected_platforms: List[str]
    total_platforms: int
    completed_platforms: int = 0

    output_files: Optional[Dict[str, str]] = None
    zip_filepath: Optional[str] = None

    error_message: Optional[str] = None
    retry_count: int = 0
    processing_time: Optional[float] = None

    # ❌ REMOVED: from_attributes = True
    # Reason: We are using MongoDB (dict/Pydantic), not SQLAlchemy ORM


class JobStatusResponse(BaseModel):
    """Schema for job status endpoint"""
    job_id: UUID
    status: JobStatus
    progress_percentage: float
    completed_platforms: int
    total_platforms: int
    platform_status: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    zip_available: bool