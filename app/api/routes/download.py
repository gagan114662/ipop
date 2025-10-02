from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import os
import logging
import zipfile
import tempfile
from pathlib import Path as PathLib

from app.config.database import get_db
from app.services.job_service import JobService
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/download/{job_id}/platform/{platform_id}")
async def download_platform_file(
    job_id: UUID = Path(..., description="Job ID"),
    platform_id: str = Path(..., description="Platform ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Download resized file for specific platform
    
    - **job_id**: UUID of the completed job
    - **platform_id**: ID of the platform to download
    
    Returns the resized file for the specified platform
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
        
        if job.status != "COMPLETE":
            raise AppException(
                status_code=400,
                error_code="JOB_NOT_COMPLETE",
                message="Job is not complete yet"
            )
        
        # Check if platform file exists
        if not job.output_files or platform_id not in job.output_files:
            raise AppException(
                status_code=404,
                error_code="PLATFORM_FILE_NOT_FOUND",
                message=f"No output file found for platform {platform_id}"
            )
        
        file_path = job.output_files[platform_id]
        
        if not os.path.exists(file_path):
            raise AppException(
                status_code=404,
                error_code="FILE_NOT_FOUND",
                message="Output file no longer exists on disk"
            )
        
        # Get platform info for filename
        from app.utils.platform_configs import get_platform_by_id
        platform_config = get_platform_by_id(platform_id)
        platform_name = platform_config.display_name if platform_config else platform_id
        
        # Generate download filename
        original_name = PathLib(job.original_filename).stem
        file_ext = PathLib(file_path).suffix
        download_filename = f"{original_name}_{platform_name.replace(' ', '_')}{file_ext}"
        
        return FileResponse(
            path=file_path,
            filename=download_filename,
            media_type='application/octet-stream'
        )
        
    except AppException:
        raise
    except Exception as e:
        logger.error(f"Download failed for job {job_id}, platform {platform_id}: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="DOWNLOAD_FAILED",
            message="Failed to download file"
        )


@router.get("/download/{job_id}/all")
async def download_all_files(
    job_id: UUID = Path(..., description="Job ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Download all resized files as ZIP archive
    
    - **job_id**: UUID of the completed job
    
    Returns ZIP file containing all resized files
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
        
        if job.status != "COMPLETE":
            raise AppException(
                status_code=400,
                error_code="JOB_NOT_COMPLETE",
                message="Job is not complete yet"
            )
        
        # Check if ZIP already exists
        if job.zip_filepath and os.path.exists(job.zip_filepath):
            return FileResponse(
                path=job.zip_filepath,
                filename=f"resized_creatives_{job_id}.zip",
                media_type='application/zip'
            )
        
        # Create ZIP file if it doesn't exist
        if not job.output_files:
            raise AppException(
                status_code=404,
                error_code="NO_OUTPUT_FILES",
                message="No output files available for download"
            )
        
        zip_path = await _create_zip_file(job, job_id)
        
        # Update job with ZIP path
        await job_service.update_zip_path(job_id, zip_path)
        
        return FileResponse(
            path=zip_path,
            filename=f"resized_creatives_{job_id}.zip",
            media_type='application/zip'
        )
        
    except AppException:
        raise
    except Exception as e:
        logger.error(f"ZIP download failed for job {job_id}: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="ZIP_DOWNLOAD_FAILED",
            message="Failed to create ZIP download"
        )


async def _create_zip_file(job, job_id: UUID) -> str:
    """Create ZIP file containing all output files"""
    
    from app.config.settings import settings
    from app.utils.platform_configs import get_platform_by_id
    
    # Create ZIP file path
    zip_dir = PathLib(settings.OUTPUT_DIR) / "zips"
    zip_dir.mkdir(exist_ok=True)
    zip_path = zip_dir / f"{job_id}.zip"
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            original_name = PathLib(job.original_filename).stem
            
            for platform_id, file_path in job.output_files.items():
                if not os.path.exists(file_path):
                    logger.warning(f"Skipping missing file: {file_path}")
                    continue
                
                # Get platform info for organized filename
                platform_config = get_platform_by_id(platform_id)
                platform_name = platform_config.display_name if platform_config else platform_id
                
                file_ext = PathLib(file_path).suffix
                zip_filename = f"{platform_name.replace(' ', '_')}/{original_name}_{platform_name.replace(' ', '_')}{file_ext}"
                
                zip_file.write(file_path, zip_filename)
        
        logger.info(f"Created ZIP file: {zip_path}")
        return str(zip_path)
        
    except Exception as e:
        # Clean up partial ZIP file
        if zip_path.exists():
            zip_path.unlink()
        raise e


@router.get("/download/{job_id}/info")
async def get_download_info(
    job_id: UUID = Path(..., description="Job ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get download information for a job
    
    - **job_id**: UUID of the job
    
    Returns available downloads and file information
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
        
        download_info = {
            "job_id": str(job_id),
            "status": job.status,
            "original_filename": job.original_filename,
            "platforms": [],
            "zip_available": False,
            "total_size": 0
        }
        
        if job.status == "COMPLETE" and job.output_files:
            from app.utils.platform_configs import get_platform_by_id
            
            total_size = 0
            
            for platform_id, file_path in job.output_files.items():
                platform_config = get_platform_by_id(platform_id)
                
                file_size = 0
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                
                download_info["platforms"].append({
                    "platform_id": platform_id,
                    "platform_name": platform_config.display_name if platform_config else platform_id,
                    "file_size": file_size,
                    "download_url": f"/api/v1/download/{job_id}/platform/{platform_id}",
                    "available": os.path.exists(file_path)
                })
            
            download_info["total_size"] = total_size
            download_info["zip_available"] = len(job.output_files) > 1
            
            if download_info["zip_available"]:
                download_info["zip_download_url"] = f"/api/v1/download/{job_id}/all"
        
        return download_info
        
    except AppException:
        raise
    except Exception as e:
        logger.error(f"Failed to get download info for job {job_id}: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="DOWNLOAD_INFO_FAILED",
            message="Failed to retrieve download information"
        )
