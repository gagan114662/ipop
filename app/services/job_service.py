from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
import logging
from typing import Optional, Dict, Any

from app.models.job import Job, JobStatus
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_job(self, job_id: UUID) -> Optional[Job]:
        """Retrieve a job by ID"""
        try:
            stmt = select(Job).where(Job.id == job_id)
            result = await self.db.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            raise

    async def create_job(self, job_data) -> Job:
        """Create a new job"""
        try:
            new_job = Job(
                original_filename=job_data.original_filename,
                original_filepath=job_data.original_filepath,
                file_size=job_data.file_size,
                file_type=job_data.file_type,
                mime_type=job_data.mime_type,
                selected_platforms=job_data.selected_platforms,
                total_platforms=len(job_data.selected_platforms),
            )
            self.db.add(new_job)
            await self.db.commit()
            await self.db.refresh(new_job)
            logger.info(f"Created job {new_job.id} with {len(job_data.selected_platforms)} platforms")
            return new_job
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            await self.db.rollback()
            raise

    async def update_job_status(self, job_id: UUID, status: str):
        """Update job status"""
        try:
            job = await self.get_job(job_id)
            if job:
                job.status = status
                if status == JobStatus.COMPLETE:
                    job.completed_at = datetime.utcnow()
                elif status == JobStatus.FAILED:
                    job.completed_at = datetime.utcnow()
                await self.db.commit()
                logger.info(f"Updated job {job_id} status to {status}")
            else:
                logger.warning(f"Job {job_id} not found for status update")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {e}")
            await self.db.rollback()
            raise

    async def update_job_progress(self, job_id: UUID, completed_platforms: int, output_files: dict):
        """Update job progress and output files"""
        try:
            job = await self.get_job(job_id)
            if job:
                job.completed_platforms = completed_platforms
                job.output_files = output_files.copy()  # Create a copy to avoid reference issues
                await self.db.commit()
                logger.debug(f"Updated job {job_id} progress: {completed_platforms}/{job.total_platforms} platforms")
            else:
                logger.warning(f"Job {job_id} not found for progress update")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} progress: {e}")
            await self.db.rollback()
            raise

    async def complete_job(self, job_id: UUID, output_files: dict, processing_time: float, metadata: Optional[Dict[str, Any]] = None):
        """Mark job as complete with optional metadata"""
        try:
            job = await self.get_job(job_id)
            if job:
                job.status = JobStatus.COMPLETE
                job.completed_at = datetime.utcnow()
                job.output_files = output_files.copy()
                job.processing_time = processing_time
                job.completed_platforms = len(output_files)
                
                # Store metadata if provided (you might need to add a metadata JSON field to your Job model)
                if metadata:
                    # If you have a metadata field in your Job model, uncomment this:
                    # job.metadata = metadata
                    logger.info(f"Job {job_id} completed with metadata: {metadata}")
                
                await self.db.commit()
                await self.db.refresh(job)
                logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s with {len(output_files)} outputs")
                return job
            else:
                logger.error(f"Job {job_id} not found for completion")
                raise AppException(
                    status_code=404,
                    error_code="JOB_NOT_FOUND",
                    message=f"Job {job_id} not found"
                )
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
            await self.db.rollback()
            raise

    async def fail_job(self, job_id: UUID, error_message: str):
        """Mark job as failed"""
        try:
            job = await self.get_job(job_id)
            if job:
                job.status = JobStatus.FAILED
                job.error_message = error_message
                job.completed_at = datetime.utcnow()
                await self.db.commit()
                logger.error(f"Job {job_id} failed: {error_message}")
            else:
                logger.warning(f"Job {job_id} not found for failure update")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} failure status: {e}")
            await self.db.rollback()
            raise

    async def update_zip_path(self, job_id: UUID, zip_path: str):
        """Update the path to the generated ZIP file"""
        try:
            job = await self.get_job(job_id)
            if job:
                job.zip_filepath = zip_path
                await self.db.commit()
                logger.info(f"Updated ZIP path for job {job_id}: {zip_path}")
            else:
                logger.warning(f"Job {job_id} not found for ZIP path update")
        except Exception as e:
            logger.error(f"Failed to update ZIP path for job {job_id}: {e}")
            await self.db.rollback()
            raise

    async def cancel_job(self, job_id: UUID) -> bool:
        """Cancel a job"""
        try:
            job = await self.get_job(job_id)
            if job and not job.is_completed():
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.utcnow()
                await self.db.commit()
                logger.info(f"Job {job_id} cancelled successfully")
                return True
            else:
                logger.warning(f"Cannot cancel job {job_id} - already completed or not found")
                return False
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            await self.db.rollback()
            raise

    async def retry_job(self, job_id: UUID) -> Job:
        """Reset a failed job for retry"""
        try:
            job = await self.get_job(job_id)
            if job and job.can_retry():
                job.status = JobStatus.PENDING
                job.retry_count += 1
                job.error_message = None
                job.completed_platforms = 0
                job.output_files = None
                job.zip_filepath = None
                job.completed_at = None
                job.processing_time = None
                await self.db.commit()
                await self.db.refresh(job)
                logger.info(f"Job {job_id} reset for retry (attempt {job.retry_count})")
                return job
            else:
                error_msg = "Cannot retry this job - not failed or exceeded retry limit"
                logger.error(f"Retry failed for job {job_id}: {error_msg}")
                raise AppException(
                    status_code=400,
                    error_code="RETRY_NOT_ALLOWED",
                    message=error_msg
                )
        except AppException:
            raise
        except Exception as e:
            logger.error(f"Failed to retry job {job_id}: {e}")
            await self.db.rollback()
            raise

    # Additional utility methods
    async def get_job_statistics(self, job_id: UUID) -> Dict[str, Any]:
        """Get detailed statistics for a job"""
        try:
            job = await self.get_job(job_id)
            if not job:
                raise AppException(
                    status_code=404,
                    error_code="JOB_NOT_FOUND",
                    message=f"Job {job_id} not found"
                )
            
            stats = {
                "job_id": str(job.id),
                "status": job.status,
                "created_at": job.created_at,
                "completed_at": job.completed_at,
                "processing_time": job.processing_time,
                "total_platforms": job.total_platforms,
                "completed_platforms": job.completed_platforms,
                "success_rate": (job.completed_platforms / job.total_platforms * 100) if job.total_platforms > 0 else 0,
                "file_info": {
                    "original_filename": job.original_filename,
                    "file_size": job.file_size,
                    "file_type": job.file_type,
                    "mime_type": job.mime_type
                },
                "platforms": job.selected_platforms,
                "output_files": job.output_files or {},
                "zip_available": bool(job.zip_filepath),
                "error_message": job.error_message,
                "retry_count": job.retry_count
            }
            return stats
        except AppException:
            raise
        except Exception as e:
            logger.error(f"Failed to get job statistics for {job_id}: {e}")
            raise
