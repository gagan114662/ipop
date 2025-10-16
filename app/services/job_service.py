# app/services/job_service.py - MongoDB Version
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import logging
from typing import Optional, Dict, Any

from app.models.job import Job, JobStatus
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.jobs

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by ID"""
        try:
            doc = await self.collection.find_one({"id": job_id})
            if doc:
                return Job.from_mongo(doc)
            return None
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
                use_ai_outfill=getattr(job_data, 'use_ai_outfill', False),
                outfill_strength=getattr(job_data, 'outfill_strength', 0.8)
            )

            await self.collection.insert_one(new_job.to_mongo())
            logger.info(f"Created job {new_job.id} with {len(job_data.selected_platforms)} platforms")
            return new_job
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise

    async def update_job_status(self, job_id: str, status: str):
        """Update job status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }

            if status == JobStatus.COMPLETE or status == JobStatus.FAILED:
                update_data["completed_at"] = datetime.utcnow()

            result = await self.collection.update_one(
                {"id": job_id},
                {"$set": update_data}
            )

            if result.matched_count > 0:
                logger.info(f"Updated job {job_id} status to {status}")
            else:
                logger.warning(f"Job {job_id} not found for status update")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {e}")
            raise

    async def update_job_progress(self, job_id: str, completed_platforms: int, output_files: dict):
        """Update job progress and output files"""
        try:
            result = await self.collection.update_one(
                {"id": job_id},
                {
                    "$set": {
                        "completed_platforms": completed_platforms,
                        "output_files": output_files,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            if result.matched_count > 0:
                logger.debug(f"Updated job {job_id} progress: {completed_platforms} platforms")
            else:
                logger.warning(f"Job {job_id} not found for progress update")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} progress: {e}")
            raise

    async def complete_job(self, job_id: str, output_files: dict, processing_time: float, metadata: Optional[Dict[str, Any]] = None):
        """Mark job as complete with optional metadata"""
        try:
            update_data = {
                "status": JobStatus.COMPLETE.value,
                "completed_at": datetime.utcnow(),
                "output_files": output_files,
                "processing_time": processing_time,
                "completed_platforms": len(output_files),
                "updated_at": datetime.utcnow()
            }

            if metadata:
                update_data["metadata"] = metadata
                logger.info(f"Job {job_id} completed with metadata: {metadata}")

            result = await self.collection.update_one(
                {"id": job_id},
                {"$set": update_data}
            )

            if result.matched_count > 0:
                logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s with {len(output_files)} outputs")
                return await self.get_job(job_id)
            else:
                logger.error(f"Job {job_id} not found for completion")
                raise AppException(
                    status_code=404,
                    error_code="JOB_NOT_FOUND",
                    message=f"Job {job_id} not found"
                )
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
            raise

    async def fail_job(self, job_id: str, error_message: str):
        """Mark job as failed"""
        try:
            result = await self.collection.update_one(
                {"id": job_id},
                {
                    "$set": {
                        "status": JobStatus.FAILED.value,
                        "error_message": error_message,
                        "completed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            if result.matched_count > 0:
                logger.error(f"Job {job_id} failed: {error_message}")
            else:
                logger.warning(f"Job {job_id} not found for failure update")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} failure status: {e}")
            raise

    async def update_zip_path(self, job_id: str, zip_path: str):
        """Update the path to the generated ZIP file"""
        try:
            result = await self.collection.update_one(
                {"id": job_id},
                {
                    "$set": {
                        "zip_filepath": zip_path,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            if result.matched_count > 0:
                logger.info(f"Updated ZIP path for job {job_id}: {zip_path}")
            else:
                logger.warning(f"Job {job_id} not found for ZIP path update")
        except Exception as e:
            logger.error(f"Failed to update ZIP path for job {job_id}: {e}")
            raise

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        try:
            job = await self.get_job(job_id)
            if job and not job.is_completed():
                result = await self.collection.update_one(
                    {"id": job_id},
                    {
                        "$set": {
                            "status": JobStatus.CANCELLED.value,
                            "completed_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                logger.info(f"Job {job_id} cancelled successfully")
                return True
            else:
                logger.warning(f"Cannot cancel job {job_id} - already completed or not found")
                return False
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            raise

    async def retry_job(self, job_id: str) -> Job:
        """Reset a failed job for retry"""
        try:
            job = await self.get_job(job_id)
            if job and job.can_retry():
                result = await self.collection.update_one(
                    {"id": job_id},
                    {
                        "$set": {
                            "status": JobStatus.PENDING.value,
                            "error_message": None,
                            "completed_platforms": 0,
                            "output_files": None,
                            "zip_filepath": None,
                            "completed_at": None,
                            "processing_time": None,
                            "updated_at": datetime.utcnow()
                        },
                        "$inc": {"retry_count": 1}
                    }
                )
                updated_job = await self.get_job(job_id)
                logger.info(f"Job {job_id} reset for retry (attempt {updated_job.retry_count})")
                return updated_job
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
            raise

    async def get_job_statistics(self, job_id: str) -> Dict[str, Any]:
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
                "job_id": job.id,
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
