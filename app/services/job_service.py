from app.database import database
from app.models.job import Job, JobStatus
from app.utils.exceptions import AppException
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self):
        self.collection = database.get_collection("jobs")

    async def get_job(self, job_id: UUID) -> Optional[Job]:
        """Retrieve a job by ID"""
        try:
            doc = await self.collection.find_one({"id": str(job_id)})
            return Job(**doc) if doc else None
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
            job_dict = new_job.model_dump(by_alias=True, mode="json")
            await self.collection.insert_one(job_dict)
            logger.info(f"Created job {new_job.id} with {len(job_data.selected_platforms)} platforms")
            return new_job
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise

    async def update_job_status(self, job_id: UUID, status: str):
        """Update job status"""
        try:
            update_data = {"status": status, "updated_at": datetime.now(timezone.utc)}
            if status in (JobStatus.COMPLETE, JobStatus.FAILED):
                update_data["completed_at"] = datetime.now(timezone.utc)

            result = await self.collection.update_one(
                {"id": str(job_id)},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                logger.warning(f"Job {job_id} not found for status update")
            else:
                logger.info(f"Updated job {job_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {e}")
            raise

    async def update_job_progress(self, job_id: UUID, completed_platforms: int, output_files: dict):
        """Update job progress and output files"""
        try:
            result = await self.collection.update_one(
                {"id": str(job_id)},
                {"$set": {
                    "completed_platforms": completed_platforms,
                    "output_files": output_files.copy(),
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            if result.matched_count == 0:
                logger.warning(f"Job {job_id} not found for progress update")
            else:
                logger.debug(f"Updated job {job_id} progress: {completed_platforms}/{completed_platforms + (len(output_files) - completed_platforms)} platforms")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} progress: {e}")
            raise

    async def complete_job(
        self,
        job_id: UUID,
        output_files: dict,
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Mark job as complete with optional metadata"""
        try:
            update_data = {
                "status": JobStatus.COMPLETE,
                "completed_at": datetime.now(timezone.utc),
                "output_files": output_files.copy(),
                "processing_time": processing_time,
                "completed_platforms": len(output_files),
                "updated_at": datetime.now(timezone.utc)
            }
            if metadata:
                update_data["metadata"] = metadata
                logger.info(f"Job {job_id} completed with metadata: {metadata}")

            result = await self.collection.update_one(
                {"id": str(job_id)},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                logger.error(f"Job {job_id} not found for completion")
                raise AppException(
                    status_code=404,
                    error_code="JOB_NOT_FOUND",
                    message=f"Job {job_id} not found"
                )

            job = await self.get_job(job_id)
            logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s with {len(output_files)} outputs")
            return job
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
            raise

    async def fail_job(self, job_id: UUID, error_message: str):
        """Mark job as failed"""
        try:
            result = await self.collection.update_one(
                {"id": str(job_id)},
                {"$set": {
                    "status": JobStatus.FAILED,
                    "error_message": error_message,
                    "completed_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            if result.matched_count == 0:
                logger.warning(f"Job {job_id} not found for failure update")
            else:
                logger.error(f"Job {job_id} failed: {error_message}")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} failure status: {e}")
            raise

    async def update_zip_path(self, job_id: UUID, zip_path: str):
        """Update the path to the generated ZIP file"""
        try:
            result = await self.collection.update_one(
                {"id": str(job_id)},
                {"$set": {
                    "zip_filepath": zip_path,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            if result.matched_count == 0:
                logger.warning(f"Job {job_id} not found for ZIP path update")
            else:
                logger.info(f"Updated ZIP path for job {job_id}: {zip_path}")
        except Exception as e:
            logger.error(f"Failed to update ZIP path for job {job_id}: {e}")
            raise

    async def cancel_job(self, job_id: UUID) -> bool:
        """Cancel a job"""
        try:
            result = await self.collection.update_one(
                {
                    "id": str(job_id),
                    "status": {"$nin": [JobStatus.COMPLETE, JobStatus.FAILED, JobStatus.CANCELLED]}
                },
                {"$set": {
                    "status": JobStatus.CANCELLED,
                    "completed_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            if result.modified_count > 0:
                logger.info(f"Job {job_id} cancelled successfully")
                return True
            else:
                logger.warning(f"Cannot cancel job {job_id} - already completed or not found")
                return False
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            raise

    async def retry_job(self, job_id: UUID) -> Job:
        """Reset a failed job for retry"""
        try:
            job = await self.get_job(job_id)
            if not job or not job.can_retry():
                error_msg = "Cannot retry this job - not failed or exceeded retry limit"
                logger.error(f"Retry failed for job {job_id}: {error_msg}")
                raise AppException(
                    status_code=400,
                    error_code="RETRY_NOT_ALLOWED",
                    message=error_msg
                )

            update_data = {
                "status": JobStatus.PENDING,
                "retry_count": job.retry_count + 1,
                "error_message": None,
                "completed_platforms": 0,
                "output_files": None,
                "zip_filepath": None,
                "completed_at": None,
                "processing_time": None,
                "updated_at": datetime.now(timezone.utc)
            }

            await self.collection.update_one(
                {"id": str(job_id)},
                {"$set": update_data}
            )

            updated_job = await self.get_job(job_id)
            logger.info(f"Job {job_id} reset for retry (attempt {updated_job.retry_count})")
            return updated_job
        except AppException:
            raise
        except Exception as e:
            logger.error(f"Failed to retry job {job_id}: {e}")
            raise

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