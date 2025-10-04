"""
Ad Resizer Integration API

Integrates the creative resizing service with the main IPOP platform.
Allows automatic resizing of creative assets for different platforms.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from typing import List, Optional
import structlog
from motor.motor_asyncio import AsyncIOMotorDatabase
from pathlib import Path
import aiofiles
import json

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.creative import CreativeInDB

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Ad Resizer"])


PLATFORM_SIZES = {
    # Social Media - Image
    "instagram_feed": {"width": 1080, "height": 1080, "aspect": "1:1"},
    "instagram_story": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "instagram_reel": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "facebook_feed": {"width": 1200, "height": 630, "aspect": "1.91:1"},
    "facebook_story": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "twitter_post": {"width": 1200, "height": 675, "aspect": "16:9"},
    "linkedin_feed": {"width": 1200, "height": 627, "aspect": "1.91:1"},

    # Video Formats
    "tiktok_short": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "youtube_short": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "youtube_standard": {"width": 1920, "height": 1080, "aspect": "16:9"},

    # Display Ads
    "google_display_banner": {"width": 728, "height": 90, "aspect": "728:90"},
    "google_square": {"width": 250, "height": 250, "aspect": "1:1"},
    "google_skyscraper": {"width": 160, "height": 600, "aspect": "160:600"}
}


@router.post("/creatives/{creative_id}/resize")
async def resize_creative(
    creative_id: str,
    platforms: List[str] = Form(...),
    use_ai_outfill: bool = Form(False),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Resize an existing creative for multiple platforms.

    Args:
        creative_id: ID of the creative to resize
        platforms: List of target platforms (e.g., instagram_feed, facebook_story)
        use_ai_outfill: Whether to use AI to fill missing areas

    Returns:
        Job information with resize task ID
    """
    client_id = current_user["client_id"]

    # Get creative from database
    creative = await db.creatives.find_one({
        "client_id": client_id,
        "creative_id": creative_id
    })

    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Creative {creative_id} not found"
        )

    # Validate platforms
    invalid_platforms = [p for p in platforms if p not in PLATFORM_SIZES]
    if invalid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platforms: {invalid_platforms}"
        )

    # Get file path from creative
    file_path = creative.get("image_url") or creative.get("video_url")
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creative has no associated media file"
        )

    logger.info(
        "creative_resize_requested",
        creative_id=creative_id,
        platforms=platforms,
        use_ai_outfill=use_ai_outfill
    )

    # TODO: Integrate with actual resize service (Celery task)
    # For now, return mock response
    resize_info = {
        "job_id": f"resize_{creative_id}",
        "creative_id": creative_id,
        "original_file": file_path,
        "platforms": platforms,
        "use_ai_outfill": use_ai_outfill,
        "status": "queued",
        "message": "Resize job queued successfully"
    }

    # Store resize job in database
    await db.resize_jobs.insert_one({
        "client_id": client_id,
        "creative_id": creative_id,
        "job_id": resize_info["job_id"],
        "platforms": platforms,
        "use_ai_outfill": use_ai_outfill,
        "status": "queued"
    })

    return resize_info


@router.post("/creatives/upload-and-resize")
async def upload_and_resize(
    file: UploadFile = File(...),
    platforms: List[str] = Form(...),
    creative_name: str = Form(...),
    creative_type: str = Form(...),
    platform: str = Form("meta"),
    use_ai_outfill: bool = Form(False),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Upload a new creative and immediately resize it for multiple platforms.

    This combines creative creation with automatic resizing.
    """
    client_id = current_user["client_id"]

    # Validate platforms
    invalid_platforms = [p for p in platforms if p not in PLATFORM_SIZES]
    if invalid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platforms: {invalid_platforms}"
        )

    # Save uploaded file
    upload_dir = Path("uploads") / client_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    # Create creative in database
    creative_id = f"creative_{file.filename.split('.')[0]}"
    creative_data = {
        "client_id": client_id,
        "creative_id": creative_id,
        "name": creative_name,
        "creative_type": creative_type,
        "platform": platform,
        "status": "active",
        "image_url": str(file_path) if creative_type == "image" else None,
        "video_url": str(file_path) if creative_type == "video" else None
    }

    await db.creatives.insert_one(creative_data)

    logger.info(
        "creative_uploaded_for_resize",
        creative_id=creative_id,
        filename=file.filename,
        platforms=platforms
    )

    # Queue resize job
    resize_info = {
        "job_id": f"resize_{creative_id}",
        "creative_id": creative_id,
        "original_file": str(file_path),
        "platforms": platforms,
        "use_ai_outfill": use_ai_outfill,
        "status": "queued"
    }

    await db.resize_jobs.insert_one({
        "client_id": client_id,
        "creative_id": creative_id,
        "job_id": resize_info["job_id"],
        "platforms": platforms,
        "use_ai_outfill": use_ai_outfill,
        "status": "queued"
    })

    return {
        "creative": creative_data,
        "resize_job": resize_info,
        "message": "Creative uploaded and resize job queued"
    }


@router.get("/resize-jobs/{job_id}")
async def get_resize_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get the status of a resize job."""
    client_id = current_user["client_id"]

    job = await db.resize_jobs.find_one({
        "client_id": client_id,
        "job_id": job_id
    })

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resize job {job_id} not found"
        )

    # Remove MongoDB _id from response
    job.pop("_id", None)
    return job


@router.get("/platform-sizes")
async def get_platform_sizes():
    """Get all supported platform sizes and dimensions."""
    return {
        "platforms": PLATFORM_SIZES,
        "total_platforms": len(PLATFORM_SIZES)
    }


@router.get("/creatives/{creative_id}/resized-versions")
async def get_resized_versions(
    creative_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all resized versions of a creative."""
    client_id = current_user["client_id"]

    # Find all resize jobs for this creative
    cursor = db.resize_jobs.find({
        "client_id": client_id,
        "creative_id": creative_id
    })

    jobs = await cursor.to_list(length=100)

    # Remove MongoDB _id from each job
    for job in jobs:
        job.pop("_id", None)

    return {
        "creative_id": creative_id,
        "resize_jobs": jobs,
        "total_jobs": len(jobs)
    }
