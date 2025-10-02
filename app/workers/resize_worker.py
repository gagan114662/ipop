# import asyncio
# import logging
# from uuid import UUID
# from pathlib import Path
# import time
# import os
# import subprocess
# import json
# from PIL import Image, ImageOps
# # from moviepy.editor import VideoFileClip
# # from moviepy import VideoFileClip
# # from moviepy.video.io.VideoFileClip import VideoFileClip

# from moviepy.editor import VideoFileClip

# from app.config.database import AsyncSessionLocal
# from app.services.job_service import JobService
# from app.services.redis_service import RedisService
# from app.utils.platform_configs import get_platform_by_id
# from app.utils.exceptions import AppException
# from app.config.settings import settings

# logger = logging.getLogger(__name__)


# class ResizeWorker:
#     """Background worker for processing resize jobs"""
    
#     def __init__(self):
#         self.redis_service = RedisService()
#         self.running = False
    
#     async def start(self):
#         """Start the worker"""
#         await self.redis_service.connect()
#         self.running = True
#         logger.info("Resize worker started")
        
#         while self.running:
#             try:
#                 # Get next job from queue
#                 job_data = await self.redis_service.get_job()
                
#                 if job_data:
#                     job_id = UUID(job_data['job_id'])
#                     await self.process_job(job_id)
#                 else:
#                     # No jobs available, wait briefly
#                     await asyncio.sleep(1)
                    
#             except Exception as e:
#                 logger.error(f"Worker error: {e}", exc_info=True)
#                 await asyncio.sleep(5)  # Wait before retrying
    
#     async def stop(self):
#         """Stop the worker"""
#         self.running = False
#         await self.redis_service.disconnect()
#         logger.info("Resize worker stopped")
    
#     async def process_job(self, job_id: UUID):
#         """Process a single resize job"""
#         async with AsyncSessionLocal() as db:
#             try:
#                 job_service = JobService(db)
#                 job = await job_service.get_job(job_id)
                
#                 if not job:
#                     logger.error(f"Job {job_id} not found")
#                     return
                
#                 if job.status != "PENDING":
#                     logger.warning(f"Job {job_id} status is {job.status}, skipping")
#                     return
                
#                 logger.info(f"Processing job {job_id}")
                
#                 # Update status to processing
#                 await job_service.update_job_status(job_id, "PROCESSING")
                
#                 start_time = time.time()
#                 output_files = {}
                
#                 # Process each platform
#                 for platform_id in job.selected_platforms:
#                     try:
#                         await self._process_platform(job, platform_id, output_files, job_service)
                        
#                         # Update progress
#                         completed = len(output_files)
#                         await job_service.update_job_progress(job_id, completed, output_files)
                        
#                     except Exception as e:
#                         logger.error(f"Failed to process platform {platform_id} for job {job_id}: {e}")
#                         # Continue with other platforms
                
#                 # Complete the job
#                 processing_time = time.time() - start_time
                
#                 if output_files:
#                     await job_service.complete_job(job_id, output_files, processing_time)
#                     logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s")
#                 else:
#                     await job_service.fail_job(job_id, "No platforms processed successfully")
#                     logger.error(f"Job {job_id} failed - no successful outputs")
                
#             except Exception as e:
#                 logger.error(f"Job {job_id} processing failed: {e}", exc_info=True)
                
#                 try:
#                     async with AsyncSessionLocal() as db:
#                         job_service = JobService(db)
#                         await job_service.fail_job(job_id, str(e))
#                 except Exception as update_error:
#                     logger.error(f"Failed to update job {job_id} status: {update_error}")
    
#     async def _process_platform(self, job, platform_id: str, output_files: dict, job_service: JobService):
#         """Process resizing for a specific platform"""
        
#         platform_config = get_platform_by_id(platform_id)
#         if not platform_config:
#             raise AppException(
#                 status_code=400,
#                 error_code="INVALID_PLATFORM",
#                 message=f"Platform {platform_id} not found"
#             )
        
#         # Create output directory
#         output_dir = Path(settings.OUTPUT_DIR) / str(job.id) / platform_id
#         output_dir.mkdir(parents=True, exist_ok=True)
        
#         # Generate output filename
#         input_path = Path(job.original_filepath)
#         file_ext = platform_config.format_preference[0]
#         output_filename = f"{input_path.stem}_{platform_id}.{file_ext}"
#         output_path = output_dir / output_filename
        
#         # Process based on content type
#         if job.file_type == "image":
#             await self._resize_image(job.original_filepath, output_path, platform_config)
#         else:  # video
#             await self._resize_video(job.original_filepath, output_path, platform_config)
        
#         # Verify output file was created
#         if not output_path.exists():
#             raise Exception(f"Output file was not created: {output_path}")
        
#         output_files[platform_id] = str(output_path)
#         logger.info(f"Successfully processed {platform_id} for job {job.id}")
    
#     async def _resize_image(self, input_path: str, output_path: Path, platform_config):
#         """Resize image for platform specifications"""
        
#         try:
#             with Image.open(input_path) as img:
#                 # Convert to RGB if necessary
#                 if img.mode not in ('RGB', 'RGBA'):
#                     img = img.convert('RGB')
                
#                 # Calculate resize dimensions maintaining aspect ratio
#                 target_width, target_height = platform_config.dimensions
#                 original_width, original_height = img.size
                
#                 # Calculate scaling to fit target dimensions
#                 width_ratio = target_width / original_width
#                 height_ratio = target_height / original_height
                
#                 # Use the smaller ratio to ensure image fits within bounds
#                 scale_ratio = min(width_ratio, height_ratio)
                
#                 # Calculate new dimensions
#                 new_width = int(original_width * scale_ratio)
#                 new_height = int(original_height * scale_ratio)
                
#                 # Resize image
#                 resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
#                 # Create canvas with target dimensions and center the image
#                 canvas = Image.new('RGB', (target_width, target_height), (255, 255, 255))
                
#                 # Calculate position to center the image
#                 x_offset = (target_width - new_width) // 2
#                 y_offset = (target_height - new_height) // 2
                
#                 # Paste resized image onto canvas
#                 if resized_img.mode == 'RGBA':
#                     canvas.paste(resized_img, (x_offset, y_offset), resized_img)
#                 else:
#                     canvas.paste(resized_img, (x_offset, y_offset))
                
#                 # Save with platform-specific quality
#                 save_kwargs = {
#                     'quality': platform_config.quality,
#                     'optimize': True
#                 }
                
#                 if output_path.suffix.lower() == '.png':
#                     canvas.save(output_path, 'PNG', **save_kwargs)
#                 else:
#                     canvas.save(output_path, 'JPEG', **save_kwargs)
                
#                 logger.info(f"Image resized from {original_width}x{original_height} to {target_width}x{target_height}")
                
#         except Exception as e:
#             logger.error(f"Image resize failed: {e}")
#             raise
    
#     async def _resize_video(self, input_path: str, output_path: Path, platform_config):
#         """Resize video for platform specifications"""
        
#         try:
#             # Load video
#             with VideoFileClip(input_path) as video:
#                 original_width, original_height = video.size
#                 original_duration = video.duration
                
#                 target_width, target_height = platform_config.dimensions
                
#                 # Trim video if it exceeds max duration
#                 if platform_config.max_duration and original_duration > platform_config.max_duration:
#                     video = video.subclip(0, platform_config.max_duration)
#                     logger.info(f"Video trimmed from {original_duration:.1f}s to {platform_config.max_duration}s")
                
#                 # Calculate resize dimensions maintaining aspect ratio
#                 width_ratio = target_width / original_width
#                 height_ratio = target_height / original_height
                
#                 # Use the smaller ratio to ensure video fits within bounds
#                 scale_ratio = min(width_ratio, height_ratio)
                
#                 # Calculate new dimensions
#                 new_width = int(original_width * scale_ratio)
#                 new_height = int(original_height * scale_ratio)
                
#                 # Ensure dimensions are even (required for some codecs)
#                 new_width = new_width - (new_width % 2)
#                 new_height = new_height - (new_height % 2)
                
#                 # Resize video
#                 resized_video = video.resize((new_width, new_height))
                
#                 # Add padding if needed to match exact target dimensions
#                 if new_width != target_width or new_height != target_height:
#                     # Calculate padding
#                     pad_x = (target_width - new_width) // 2
#                     pad_y = (target_height - new_height) // 2
                    
#                     resized_video = resized_video.margin(
#                         left=pad_x, 
#                         right=target_width - new_width - pad_x,
#                         top=pad_y, 
#                         bottom=target_height - new_height - pad_y,
#                         color=(0, 0, 0)
#                     )
                
#                 # Set codec parameters based on quality
#                 codec_params = {
#                     'codec': 'libx264',
#                     'audio_codec': 'aac',
#                     'temp_audiofile': f"{output_path}_temp_audio.m4a",
#                     'remove_temp': True
#                 }
                
#                 # Adjust bitrate based on quality setting
#                 if platform_config.quality >= 90:
#                     codec_params['bitrate'] = '8000k'
#                 elif platform_config.quality >= 85:
#                     codec_params['bitrate'] = '5000k'
#                 else:
#                     codec_params['bitrate'] = '3000k'
                
#                 # Write video file
#                 resized_video.write_videofile(
#                     str(output_path),
#                     **codec_params,
#                     verbose=False,
#                     logger=None
#                 )
                
#                 logger.info(f"Video resized from {original_width}x{original_height} to {target_width}x{target_height}")
                
#         except Exception as e:
#             logger.error(f"Video resize failed: {e}")
#             raise


# # Global worker instance
# worker = ResizeWorker()


# async def start_resize_job(job_id: UUID):
#     """Add job to processing queue"""
#     redis_service = RedisService()
#     await redis_service.connect()
    
#     try:
#         await redis_service.add_job({
#             'job_id': str(job_id),
#             'timestamp': time.time()
#         })
#         logger.info(f"Job {job_id} added to processing queue")
#     finally:
#         await redis_service.disconnect()


# async def start_worker():
#     """Start the background worker"""
#     await worker.start()


# async def stop_worker():
#     """Stop the background worker"""
#     await worker.stop()





import asyncio
import logging
from uuid import UUID
from pathlib import Path
import time
import os
import subprocess
import json
from PIL import Image, ImageOps, ImageFile
import tempfile
import shutil
from moviepy.editor import VideoFileClip
import ffmpeg

from app.config.database import AsyncSessionLocal
from app.services.job_service import JobService
from app.services.redis_service import RedisService
from app.utils.platform_configs import get_platform_by_id
from app.utils.exceptions import AppException
from app.config.settings import settings

# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

logger = logging.getLogger(__name__)


class ResizeWorker:
    """Background worker for processing resize jobs"""
    
    def __init__(self):
        self.redis_service = RedisService()
        self.running = False
        self.temp_dir = None
    
    async def start(self):
        """Start the worker"""
        await self.redis_service.connect()
        self.running = True
        # Create temporary directory for processing
        self.temp_dir = Path(tempfile.mkdtemp(prefix="resize_worker_"))
        logger.info(f"Resize worker started with temp dir: {self.temp_dir}")
        
        while self.running:
            try:
                # Get next job from queue
                job_data = await self.redis_service.get_job()
                
                if job_data:
                    job_id = UUID(job_data['job_id'])
                    await self.process_job(job_id)
                else:
                    # No jobs available, wait briefly
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                await asyncio.sleep(5)  # Wait before retrying
    
    async def stop(self):
        """Stop the worker"""
        self.running = False
        await self.redis_service.disconnect()
        # Clean up temporary directory
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        logger.info("Resize worker stopped")
    
    async def process_job(self, job_id: UUID):
        """Process a single resize job"""
        async with AsyncSessionLocal() as db:
            try:
                job_service = JobService(db)
                job = await job_service.get_job(job_id)
                
                if not job:
                    logger.error(f"Job {job_id} not found")
                    return
                
                if job.status != "PENDING":
                    logger.warning(f"Job {job_id} status is {job.status}, skipping")
                    return
                
                logger.info(f"Processing job {job_id} with {len(job.selected_platforms)} platforms")
                
                # Validate input file exists
                if not os.path.exists(job.original_filepath):
                    await job_service.fail_job(job_id, f"Input file not found: {job.original_filepath}")
                    return
                
                # Update status to processing
                await job_service.update_job_status(job_id, "PROCESSING")
                
                start_time = time.time()
                output_files = {}
                platform_errors = {}
                
                # Process each platform
                for i, platform_id in enumerate(job.selected_platforms):
                    try:
                        logger.info(f"Processing platform {platform_id} ({i+1}/{len(job.selected_platforms)})")
                        await self._process_platform(job, platform_id, output_files, job_service)
                        
                        # Update progress after each successful platform
                        completed = len(output_files)
                        await job_service.update_job_progress(job_id, completed, output_files)
                        logger.info(f"Successfully processed {platform_id} for job {job_id}")
                        
                    except Exception as e:
                        error_msg = f"Failed to process platform {platform_id}: {str(e)}"
                        logger.error(error_msg, exc_info=True)
                        platform_errors[platform_id] = error_msg
                        # Continue with other platforms
                
                # Complete the job
                processing_time = time.time() - start_time
                
                if output_files:
                    # Include platform errors in job metadata if any
                    job_metadata = {"platform_errors": platform_errors} if platform_errors else None
                    await job_service.complete_job(job_id, output_files, processing_time, job_metadata)
                    logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s with {len(output_files)} outputs")
                    
                    if platform_errors:
                        logger.warning(f"Job {job_id} had errors for platforms: {list(platform_errors.keys())}")
                else:
                    error_summary = "; ".join(platform_errors.values()) if platform_errors else "No platforms processed successfully"
                    await job_service.fail_job(job_id, error_summary)
                    logger.error(f"Job {job_id} failed - no successful outputs")
                
            except Exception as e:
                logger.error(f"Job {job_id} processing failed: {e}", exc_info=True)
                
                try:
                    async with AsyncSessionLocal() as db:
                        job_service = JobService(db)
                        await job_service.fail_job(job_id, str(e))
                except Exception as update_error:
                    logger.error(f"Failed to update job {job_id} status: {update_error}")
    
    async def _process_platform(self, job, platform_id: str, output_files: dict, job_service: JobService):
        """Process resizing for a specific platform"""
        
        platform_config = get_platform_by_id(platform_id)
        if not platform_config:
            raise AppException(
                status_code=400,
                error_code="INVALID_PLATFORM",
                message=f"Platform {platform_id} not found"
            )
        
        # Validate platform compatibility
        if job.file_type == "image" and platform_config.content_type.value == "video":
            raise ValueError(f"Platform {platform_id} only supports video content")
        elif job.file_type == "video" and platform_config.content_type.value == "image":
            raise ValueError(f"Platform {platform_id} only supports image content")
        
        # Create output directory structure
        output_dir = Path(settings.OUTPUT_DIR) / str(job.id)
        platform_dir = output_dir / platform_id
        platform_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine output file extension based on content type and platform preference
        input_path = Path(job.original_filepath)
        output_extension = self._get_output_extension(job.file_type, platform_config)
        output_filename = f"{input_path.stem}_{platform_id}.{output_extension}"
        output_path = platform_dir / output_filename
        
        logger.info(f"Processing {job.file_type} for {platform_id}: {input_path} -> {output_path}")
        
        # Process based on content type
        if job.file_type == "image":
            await self._resize_image(job.original_filepath, output_path, platform_config)
        else:  # video
            await self._resize_video(job.original_filepath, output_path, platform_config)
        
        # Verify output file was created and has reasonable size
        if not output_path.exists():
            raise Exception(f"Output file was not created: {output_path}")
        
        file_size = output_path.stat().st_size
        if file_size == 0:
            raise Exception(f"Output file is empty: {output_path}")
        
        output_files[platform_id] = str(output_path)
        logger.info(f"Successfully processed {platform_id} -> {output_path} ({file_size} bytes)")
    
    def _get_output_extension(self, content_type: str, platform_config) -> str:
        """Determine the appropriate output file extension"""
        if content_type == "image":
            # For images, prefer JPG unless PNG is specifically required
            if "png" in platform_config.format_preference:
                return "png"
            else:
                return "jpg"
        else:  # video
            # For videos, prefer MP4
            if "mp4" in platform_config.format_preference:
                return "mp4"
            elif platform_config.format_preference:
                return platform_config.format_preference[0]
            else:
                return "mp4"
    
    async def _resize_image(self, input_path: str, output_path: Path, platform_config):
        """Resize image for platform specifications with improved error handling"""
        
        try:
            # Use temp file for processing to avoid corruption
            temp_output = self.temp_dir / f"temp_{output_path.name}"
            
            with Image.open(input_path) as img:
                # Handle different color modes
                original_mode = img.mode
                if original_mode in ('RGBA', 'LA'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if original_mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                    else:
                        background.paste(img)
                    img = background
                elif original_mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Get target dimensions
                target_width, target_height = platform_config.dimensions
                original_width, original_height = img.size
                
                logger.debug(f"Resizing image from {original_width}x{original_height} to {target_width}x{target_height}")
                
                # Calculate scaling to fit target dimensions while maintaining aspect ratio
                width_ratio = target_width / original_width
                height_ratio = target_height / original_height
                scale_ratio = min(width_ratio, height_ratio)
                
                # Calculate new dimensions
                new_width = max(1, int(original_width * scale_ratio))
                new_height = max(1, int(original_height * scale_ratio))
                
                # Resize image with high-quality resampling
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create canvas with target dimensions
                if output_path.suffix.lower() == '.png':
                    canvas = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 255))
                else:
                    canvas = Image.new('RGB', (target_width, target_height), (255, 255, 255))
                
                # Center the resized image on canvas
                x_offset = (target_width - new_width) // 2
                y_offset = (target_height - new_height) // 2
                
                if resized_img.mode == 'RGBA' and canvas.mode == 'RGBA':
                    canvas.paste(resized_img, (x_offset, y_offset), resized_img)
                else:
                    canvas.paste(resized_img, (x_offset, y_offset))
                
                # Save with appropriate format and quality
                save_kwargs = {
                    'optimize': True,
                    'quality': platform_config.quality
                }
                
                if output_path.suffix.lower() == '.png':
                    # For PNG, use compression level instead of quality
                    save_kwargs.pop('quality')
                    save_kwargs['compress_level'] = 6
                    canvas.save(temp_output, 'PNG', **save_kwargs)
                else:
                    # For JPEG
                    if canvas.mode != 'RGB':
                        canvas = canvas.convert('RGB')
                    canvas.save(temp_output, 'JPEG', **save_kwargs)
                
                # Move temp file to final location
                shutil.move(str(temp_output), str(output_path))
                
                logger.info(f"Image resized: {original_width}x{original_height} -> {target_width}x{target_height}")
                
        except Exception as e:
            logger.error(f"Image resize failed for {input_path}: {e}")
            # Clean up temp file if it exists
            temp_output = self.temp_dir / f"temp_{output_path.name}"
            if temp_output.exists():
                temp_output.unlink()
            raise
    
    async def _resize_video(self, input_path: str, output_path: Path, platform_config):
        """Resize video for platform specifications with improved stability"""
        
        temp_output = None
        video_clip = None
        
        try:
            # Create temporary output file
            temp_output = self.temp_dir / f"temp_{output_path.name}"
            
            # Load video with proper error handling
            try:
                video_clip = VideoFileClip(input_path)
            except Exception as e:
                logger.error(f"Failed to load video {input_path}: {e}")
                # Try with ffmpeg probe first
                try:
                    probe = ffmpeg.probe(input_path)
                    logger.info(f"Video info: {probe}")
                    video_clip = VideoFileClip(input_path)
                except Exception as probe_error:
                    raise Exception(f"Cannot process video file: {probe_error}")
            
            original_width, original_height = video_clip.size
            original_duration = video_clip.duration
            target_width, target_height = platform_config.dimensions
            
            logger.info(f"Processing video: {original_width}x{original_height}, {original_duration:.1f}s")
            
            # Trim video if it exceeds max duration
            if platform_config.max_duration and original_duration > platform_config.max_duration:
                video_clip = video_clip.subclip(0, platform_config.max_duration)
                logger.info(f"Video trimmed to {platform_config.max_duration}s")
            
            # Calculate resize dimensions maintaining aspect ratio
            width_ratio = target_width / original_width
            height_ratio = target_height / original_height
            scale_ratio = min(width_ratio, height_ratio)
            
            # Calculate new dimensions (ensure even numbers for codec compatibility)
            new_width = max(2, int(original_width * scale_ratio) & ~1)  # Make even
            new_height = max(2, int(original_height * scale_ratio) & ~1)  # Make even
            
            # Resize video
            resized_video = video_clip.resize((new_width, new_height))
            
            # Add padding if needed to match exact target dimensions
            if new_width != target_width or new_height != target_height:
                # Ensure target dimensions are even
                target_width = target_width & ~1
                target_height = target_height & ~1
                
                # Calculate padding (ensure even padding)
                pad_x = ((target_width - new_width) // 2) & ~1
                pad_y = ((target_height - new_height) // 2) & ~1
                
                resized_video = resized_video.margin(
                    left=pad_x,
                    right=target_width - new_width - pad_x,
                    top=pad_y,
                    bottom=target_height - new_height - pad_y,
                    color=(0, 0, 0)
                )
            
            # Enhanced codec parameters
            codec_params = {
                'codec': 'libx264',
                'audio_codec': 'aac',
                'temp_audiofile': str(self.temp_dir / f"temp_audio_{output_path.stem}.m4a"),
                'remove_temp': True,
                'verbose': False,
                'logger': None,
                'fps': min(30, video_clip.fps) if video_clip.fps else 30,  # Limit FPS for efficiency
            }
            
            # Adjust quality settings based on platform requirements
            if platform_config.quality >= 95:
                codec_params.update({
                    'bitrate': '8000k',
                    'ffmpeg_params': ['-crf', '18', '-preset', 'medium']
                })
            elif platform_config.quality >= 90:
                codec_params.update({
                    'bitrate': '5000k',
                    'ffmpeg_params': ['-crf', '20', '-preset', 'medium']
                })
            elif platform_config.quality >= 85:
                codec_params.update({
                    'bitrate': '3000k',
                    'ffmpeg_params': ['-crf', '23', '-preset', 'fast']
                })
            else:
                codec_params.update({
                    'bitrate': '2000k',
                    'ffmpeg_params': ['-crf', '25', '-preset', 'fast']
                })
            
            # Write video file
            resized_video.write_videofile(str(temp_output), **codec_params)
            
            # Move temp file to final location
            shutil.move(str(temp_output), str(output_path))
            
            logger.info(f"Video processed: {original_width}x{original_height} -> {target_width}x{target_height}")
            
        except Exception as e:
            logger.error(f"Video resize failed for {input_path}: {e}")
            # Clean up temp files
            if temp_output and temp_output.exists():
                temp_output.unlink()
            raise
        finally:
            # Always close video clip to free resources
            if video_clip:
                try:
                    video_clip.close()
                except:
                    pass


# Global worker instance
worker = ResizeWorker()


async def start_resize_job(job_id: UUID):
    """Add job to processing queue"""
    redis_service = RedisService()
    await redis_service.connect()
    
    try:
        await redis_service.add_job({
            'job_id': str(job_id),
            'timestamp': time.time()
        })
        logger.info(f"Job {job_id} added to processing queue")
    finally:
        await redis_service.disconnect()


async def start_worker():
    """Start the background worker"""
    await worker.start()


async def stop_worker():
    """Stop the background worker"""
    await worker.stop()


