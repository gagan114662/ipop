from fastapi import APIRouter, Depends, Path, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from uuid import UUID
import logging

from app.config.database import get_db
from app.schemas.job import JobResponse, JobStatusResponse
from app.services.job_service import JobService
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str = Path(..., description="Job ID to retrieve"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get job details by ID
    
    - **job_id**: UUID of the job to retrieve
    
    Returns complete job information including status and results
    """
    try:
        job_service = JobService(db)
        job = await job_service.get_job(job_id)
        
        if not job:
            raise AppException(
                status_code=404,
                error_code="JOB_NOT_FOUND",
                message=f"Job {job_id} not found"
            )
        
        return JobResponse.from_orm(job)
        
    except AppException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="JOB_FETCH_FAILED",
            message="Failed to retrieve job information"
        )


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str = Path(..., description="Job ID to check status"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get job status and progress
    
    - **job_id**: UUID of the job to check
    
    Returns current status, progress, and platform completion details
    """
    try:
        job_service = JobService(db)
        job = await job_service.get_job(job_id)
        
        if not job:
            raise AppException(
                status_code=404,
                error_code="JOB_NOT_FOUND",
                message=f"Job {job_id} not found"
            )
        
        # Build platform status details
        platform_status = []
        
        from app.utils.platform_configs import get_platform_by_id
        
        for platform_id in job.selected_platforms:
            platform_config = get_platform_by_id(platform_id)
            if not platform_config:
                continue
            
            # Determine platform status
            if job.output_files and platform_id in job.output_files:
                status = "COMPLETE"
                download_url = f"/api/v1/download/{job_id}/platform/{platform_id}"
            elif job.status == "FAILED":
                status = "FAILED"
                download_url = None
            elif job.status == "PROCESSING":
                # Check if this specific platform is being processed
                # This would need Redis integration for real-time status
                status = "PROCESSING"
                download_url = None
            else:
                status = "PENDING"
                download_url = None
            
            platform_status.append({
                "platform_id": platform_id,
                "platform_name": platform_config.display_name,
                "status": status,
                "download_url": download_url
            })
        
        return JobStatusResponse(
            job_id=job.id,
            status=job.status,
            progress_percentage=job.progress_percentage,
            completed_platforms=job.completed_platforms,
            total_platforms=job.total_platforms,
            platform_status=platform_status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            zip_available=bool(job.zip_filepath and job.status == "COMPLETE")
        )
        
    except AppException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status {job_id}: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="STATUS_FETCH_FAILED",
            message="Failed to retrieve job status"
        )


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str = Path(..., description="Job ID to cancel"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Cancel a pending or processing job
    
    - **job_id**: UUID of the job to cancel
    
    Returns success message if cancellation was successful
    """
    try:
        job_service = JobService(db)
        job = await job_service.get_job(job_id)
        
        if not job:
            raise AppException(
                status_code=404,
                error_code="JOB_NOT_FOUND",
                message=f"Job {job_id} not found"
            )
        
        if job.is_completed():
            raise AppException(
                status_code=400,
                error_code="JOB_ALREADY_COMPLETED",
                message="Cannot cancel completed job"
            )
        
        # Cancel the job
        success = await job_service.cancel_job(job_id)
        
        if not success:
            raise AppException(
                status_code=500,
                error_code="CANCELLATION_FAILED",
                message="Failed to cancel job"
            )
        
        logger.info(f"Job {job_id} cancelled successfully")
        
        return {
            "message": "Job cancelled successfully",
            "job_id": str(job_id),
            "status": "CANCELLED"
        }
        
    except AppException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="CANCELLATION_ERROR",
            message="Error occurred while cancelling job"
        )


@router.post("/jobs/{job_id}/retry")
async def retry_job(
    job_id: str = Path(..., description="Job ID to retry"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Retry a failed job
    
    - **job_id**: UUID of the job to retry
    
    Returns updated job information after retry initiation
    """
    try:
        job_service = JobService(db)
        job = await job_service.get_job(job_id)
        
        if not job:
            raise AppException(
                status_code=404,
                error_code="JOB_NOT_FOUND",
                message=f"Job {job_id} not found"
            )
        
        if not job.can_retry():
            raise AppException(
                status_code=400,
                error_code="RETRY_NOT_ALLOWED",
                message="Job cannot be retried (not failed or exceeded retry limit)"
            )
        
        # Reset job for retry
        updated_job = await job_service.retry_job(job_id)
        
        # Restart background processing
        from app.workers.resize_worker import start_resize_job
        await start_resize_job(job_id)
        
        logger.info(f"Job {job_id} retry initiated")
        
        return JobResponse.from_orm(updated_job)
        
    except AppException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry job {job_id}: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="RETRY_FAILED",
            message="Failed to retry job"
        )