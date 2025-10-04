from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
import mimetypes
import os
from pathlib import Path

from app.config.database import get_db
from app.config.settings import settings
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate, JobResponse
from app.services.file_service import FileService
from app.services.job_service import JobService
from app.utils.platform_configs import validate_platform_ids, get_compatible_platforms
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=JobResponse)
async def upload_file(
    file: UploadFile = File(...),
    platforms: str = Form(...),  # JSON string of platform IDs
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file and create a resize job
    
    - **file**: Image or video file (max 500MB)
    - **platforms**: JSON array of platform IDs to resize for
    
    Returns job information with tracking ID
    """
    try:
        # Parse platforms
        import json
        try:
            platform_list = json.loads(platforms)
            if not isinstance(platform_list, list) or not platform_list:
                raise ValueError("Platforms must be a non-empty list")
        except (json.JSONDecodeError, ValueError) as e:
            raise AppException(
                status_code=400,
                error_code="INVALID_PLATFORMS",
                message="Invalid platforms format"
            )
        
        # Validate file
        await _validate_upload_file(file)
        
        # Determine content type
        content_type = _get_content_type(file.content_type)
        
        # Validate platforms for content type
        valid_platforms = validate_platform_ids(platform_list, content_type)
        if not valid_platforms:
            raise AppException(
                status_code=400,
                error_code="NO_COMPATIBLE_PLATFORMS",
                message=f"No platforms compatible with {content_type} content"
            )
        
        # Save uploaded file
        file_service = FileService()
        file_path = await file_service.save_upload(file)
        
        # Create job
        job_service = JobService(db)
        job_data = JobCreate(
            original_filename=file.filename,
            original_filepath=str(file_path),
            file_size=file.size,
            file_type=content_type,
            mime_type=file.content_type,
            selected_platforms=valid_platforms,
        )
        
        job = await job_service.create_job(job_data)
        
        # Start background processing
        from app.workers.resize_worker import start_resize_job
        await start_resize_job(job.id)
        
        logger.info(f"Created job {job.id} for file {file.filename}")
        
        return JobResponse.from_orm(job)
        
    except AppException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="UPLOAD_FAILED",
            message="File upload failed"
        )


@router.get("/platforms")
async def get_platforms():
    """
    Get available platforms with their specifications
    
    Returns list of all available platforms with dimensions and supported content types
    """
    try:
        from app.utils.platform_configs import PLATFORM_CONFIGS
        
        platforms = []
        for platform in PLATFORM_CONFIGS.values():
            platforms.append({
                "id": platform.id,
                "name": platform.name,
                "display_name": platform.display_name,
                "dimensions": {
                    "width": platform.dimensions[0],
                    "height": platform.dimensions[1]
                },
                "content_type": platform.content_type.value,
                "max_duration": platform.max_duration,
                "format": f"{platform.dimensions[0]}x{platform.dimensions[1]}",
                "icon_url": platform.icon_url
            })
        
        return {
            "platforms": platforms,
            "total": len(platforms)
        }
        
    except Exception as e:
        logger.error(f"Failed to get platforms: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="PLATFORMS_FETCH_FAILED",
            message="Failed to fetch platform configurations"
        )


@router.get("/platforms/compatible/{content_type}")
async def get_compatible_platforms_endpoint(content_type: str):
    """
    Get platforms compatible with specific content type
    
    - **content_type**: 'image' or 'video'
    
    Returns filtered list of compatible platforms
    """
    try:
        if content_type not in ["image", "video"]:
            raise AppException(
                status_code=400,
                error_code="INVALID_CONTENT_TYPE",
                message="Content type must be 'image' or 'video'"
            )
        
        compatible = get_compatible_platforms(content_type)
        
        platforms = []
        for platform in compatible:
            platforms.append({
                "id": platform.id,
                "name": platform.name,
                "display_name": platform.display_name,
                "dimensions": {
                    "width": platform.dimensions[0],
                    "height": platform.dimensions[1]
                },
                "content_type": platform.content_type.value,
                "max_duration": platform.max_duration,
                "format": f"{platform.dimensions[0]}x{platform.dimensions[1]}",
                "icon_url": platform.icon_url
            })
        
        return {
            "platforms": platforms,
            "content_type": content_type,
            "total": len(platforms)
        }
        
    except AppException:
        raise
    except Exception as e:
        logger.error(f"Failed to get compatible platforms: {e}", exc_info=True)
        raise AppException(
            status_code=500,
            error_code="COMPATIBLE_PLATFORMS_FAILED",
            message="Failed to fetch compatible platforms"
        )


async def _validate_upload_file(file: UploadFile):
    """Validate uploaded file"""
    
    # Check file size
    if file.size > settings.MAX_FILE_SIZE:
        raise AppException(
            status_code=413,
            error_code="FILE_TOO_LARGE",
            message=f"File size exceeds {settings.MAX_FILE_SIZE / 1024 / 1024:.0f}MB limit"
        )
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    
    allowed_extensions = (
        settings.ALLOWED_IMAGE_EXTENSIONS + 
        settings.ALLOWED_VIDEO_EXTENSIONS
    )
    
    if file_ext not in allowed_extensions:
        raise AppException(
            status_code=400,
            error_code="UNSUPPORTED_FILE_TYPE",
            message=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate MIME type
    if not file.content_type:
        raise AppException(
            status_code=400,
            error_code="MISSING_CONTENT_TYPE",
            message="File content type not specified"
        )
    
    expected_mime_prefixes = ["image/", "video/"]
    if not any(file.content_type.startswith(prefix) for prefix in expected_mime_prefixes):
        raise AppException(
            status_code=400,
            error_code="INVALID_CONTENT_TYPE",
            message="File must be an image or video"
        )


def _get_content_type(mime_type: str) -> str:
    """Determine content type from MIME type"""
    if mime_type.startswith("image/"):
        return "image"
    elif mime_type.startswith("video/"):
        return "video"
    else:
        raise AppException(
            status_code=400,
            error_code="UNKNOWN_CONTENT_TYPE",
            message="Cannot determine content type"
        )