# app/models/job.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4, UUID
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Job(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # File information
    original_filename: str
    original_filepath: str
    file_size: int
    file_type: str  # 'image' or 'video'
    mime_type: str

    # Processing details
    selected_platforms: List[str]
    total_platforms: int
    completed_platforms: int = 0

    # Results
    output_files: Optional[Dict[str, str]] = None  # platform_id → file_path
    zip_filepath: Optional[str] = None

    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0

    # Performance & AI
    processing_time: Optional[float] = None
    use_ai_outfill: bool = False
    outfill_strength: float = 0.8

    class Config:
        # Allow MongoDB BSON types like UUID, datetime
        arbitrary_types_allowed = True

    @property
    def progress_percentage(self) -> float:
        if self.total_platforms == 0:
            return 0.0
        return (self.completed_platforms / self.total_platforms) * 100

    def is_completed(self) -> bool:
        return self.status in {JobStatus.COMPLETE, JobStatus.FAILED, JobStatus.CANCELLED}

    def can_retry(self) -> bool:
        return self.status == JobStatus.FAILED and self.retry_count < 3