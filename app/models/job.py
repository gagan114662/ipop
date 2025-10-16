# app/models/job.py - MongoDB Document Models
from enum import Enum
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Job(BaseModel):
    """Job document model for MongoDB"""

    # Primary key
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Job metadata
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
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
    output_files: Optional[Dict[str, str]] = None
    zip_filepath: Optional[str] = None

    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0

    # Performance metrics
    processing_time: Optional[float] = None

    # AI outfill options
    use_ai_outfill: bool = False
    outfill_strength: float = 0.8

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.total_platforms == 0:
            return 0.0
        return (self.completed_platforms / self.total_platforms) * 100

    def is_completed(self) -> bool:
        """Check if job is in a final state"""
        return self.status in [JobStatus.COMPLETE, JobStatus.FAILED, JobStatus.CANCELLED]

    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.status == JobStatus.FAILED and self.retry_count < 3

    def to_mongo(self) -> dict:
        """Convert to MongoDB document"""
        data = self.dict()
        # Convert datetime objects to ISO format
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value
        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "Job":
        """Create Job from MongoDB document"""
        if data and '_id' in data:
            data.pop('_id')  # Remove MongoDB's _id field
        return cls(**data)
