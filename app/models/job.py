from sqlalchemy import Column, String, DateTime, Integer, Text, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum

from app.config.database import Base
from sqlalchemy import Boolean, Float


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Job(Base):
    """Job model for tracking resize operations"""
    
    __tablename__ = "jobs"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Job metadata
    status = Column(String(20), default=JobStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    original_filepath = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)  # 'image' or 'video'
    mime_type = Column(String(100), nullable=False)
    
    # Processing details
    selected_platforms = Column(JSON, nullable=False)  # List of platform IDs
    total_platforms = Column(Integer, nullable=False)
    completed_platforms = Column(Integer, default=0)
    
    # Results
    output_files = Column(JSON, nullable=True)  # Dict of platform_id: file_path
    zip_filepath = Column(String(500), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Performance metrics
    processing_time = Column(Float, nullable=True)

    use_ai_outfill = Column(Boolean, default=False) 
    outfill_strength = Column(Float, default=0.8)    
    
    def __repr__(self):
        return f""
    
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