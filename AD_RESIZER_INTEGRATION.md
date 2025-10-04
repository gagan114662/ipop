# Ad Resizer Integration

Integration of the Creative Resizing Service into the IPOP Media Buying Platform.

## Overview

The Ad Resizer service automatically resizes creative assets (images and videos) for different social media platforms and display ad formats. It uses AI-powered outfill technology to intelligently fill missing areas when changing aspect ratios.

## Features

✅ **Multi-Platform Support**
- Social Media: Instagram, Facebook, Twitter, LinkedIn, TikTok
- Video: YouTube (Standard & Shorts), Instagram Reels
- Display Ads: Google Display Network (Multiple sizes)

✅ **AI-Powered Outfill**
- Uses FLUX.1-Fill-dev model for intelligent background extension
- Maintains subject focus while changing aspect ratios
- Natural-looking results

✅ **Async Processing**
- Background job queue using Celery
- Real-time status tracking
- Multiple concurrent resize operations

## Integration Points

### API Endpoints

#### 1. Resize Existing Creative
```bash
POST /api/v1/ad-resizer/creatives/{creative_id}/resize

# Parameters:
- creative_id: ID of existing creative
- platforms: List of target platforms
- use_ai_outfill: Boolean (enable AI background extension)
```

#### 2. Upload and Resize
```bash
POST /api/v1/ad-resizer/creatives/upload-and-resize

# Form Data:
- file: Image or video file
- creative_name: Name for the creative
- creative_type: "image" or "video"
- platform: Target advertising platform
- platforms: List of resize targets
- use_ai_outfill: Boolean
```

#### 3. Check Resize Job Status
```bash
GET /api/v1/ad-resizer/resize-jobs/{job_id}
```

#### 4. Get Platform Sizes
```bash
GET /api/v1/ad-resizer/platform-sizes
```

#### 5. Get Resized Versions
```bash
GET /api/v1/ad-resizer/creatives/{creative_id}/resized-versions
```

## Supported Platforms

### Social Media - Images
- **Instagram Feed**: 1080x1080 (1:1)
- **Instagram Story**: 1080x1920 (9:16)
- **Instagram Reel**: 1080x1920 (9:16)
- **Facebook Feed**: 1200x630 (1.91:1)
- **Facebook Story**: 1080x1920 (9:16)
- **Twitter Post**: 1200x675 (16:9)
- **LinkedIn Feed**: 1200x627 (1.91:1)

### Video Formats
- **TikTok Short**: 1080x1920 (9:16)
- **YouTube Short**: 1080x1920 (9:16)
- **YouTube Standard**: 1920x1080 (16:9)

### Display Ads
- **Google Display Banner**: 728x90
- **Google Square**: 250x250 (1:1)
- **Google Skyscraper**: 160x600

## Usage Examples

### Example 1: Resize Existing Creative

```python
import httpx

async def resize_creative():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/ad-resizer/creatives/my_creative_001/resize",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "platforms": ["instagram_feed", "facebook_story", "tiktok_short"],
                "use_ai_outfill": True
            }
        )

        job_info = response.json()
        print(f"Job ID: {job_info['job_id']}")
        print(f"Status: {job_info['status']}")
```

### Example 2: Upload and Resize

```bash
curl -X POST \
  'http://localhost:8000/api/v1/ad-resizer/creatives/upload-and-resize' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -F 'file=@my_image.jpg' \
  -F 'creative_name=Summer Sale Banner' \
  -F 'creative_type=image' \
  -F 'platform=meta' \
  -F 'platforms=["instagram_feed","facebook_feed","google_display_banner"]' \
  -F 'use_ai_outfill=true'
```

### Example 3: Check Job Status

```python
async def check_status(job_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/ad-resizer/resize-jobs/{job_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        status = response.json()
        print(f"Status: {status['status']}")
        print(f"Platforms: {status['platforms']}")
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              IPOP Media Buying Platform             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐      ┌──────────────────┐       │
│  │   Creative   │      │   Ad Resizer     │       │
│  │     API      │─────▶│   Integration    │       │
│  └──────────────┘      └──────────────────┘       │
│                                │                    │
│                                ▼                    │
│                       ┌─────────────────┐          │
│                       │  Resize Jobs    │          │
│                       │   (MongoDB)     │          │
│                       └─────────────────┘          │
│                                │                    │
│                                ▼                    │
│                       ┌─────────────────┐          │
│                       │ Celery Worker   │          │
│                       │   (Background)  │          │
│                       └─────────────────┘          │
│                                │                    │
│                                ▼                    │
│                    ┌──────────────────────┐        │
│                    │  Image/Video Resize  │        │
│                    │  + AI Outfill (FLUX) │        │
│                    └──────────────────────┘        │
└─────────────────────────────────────────────────────┘
```

## Database Schema

### Resize Jobs Collection

```python
{
    "_id": ObjectId("..."),
    "client_id": "client_123",
    "creative_id": "creative_001",
    "job_id": "resize_creative_001",
    "platforms": ["instagram_feed", "facebook_story"],
    "use_ai_outfill": true,
    "status": "completed",  # queued, processing, completed, failed
    "created_at": ISODate("2025-01-01T00:00:00Z"),
    "completed_at": ISODate("2025-01-01T00:05:00Z"),
    "output_files": {
        "instagram_feed": "/path/to/instagram_version.jpg",
        "facebook_story": "/path/to/facebook_version.jpg"
    }
}
```

## Future Enhancements

### Phase 2
- [ ] Integrate actual Celery workers for background processing
- [ ] Add webhook callbacks for job completion
- [ ] Implement file storage (S3/GCS)
- [ ] Add video format conversion
- [ ] Batch processing for multiple creatives

### Phase 3
- [ ] AI-powered copy generation for each platform
- [ ] Automatic brand asset overlay
- [ ] Performance prediction for each platform
- [ ] Smart cropping based on detected subjects
- [ ] Platform-specific optimizations

## Dependencies

The resizer service requires:
- **PostgreSQL**: Job tracking and metadata
- **Redis**: Task queue and caching
- **Celery**: Background job processing
- **Pillow**: Image processing
- **OpenCV**: Video processing
- **moviepy**: Video manipulation
- **FLUX.1-Fill-dev**: AI outfill model (optional)

## Installation

Additional dependencies for full resizer functionality:

```bash
pip install -r requirements-resizer.txt
```

## Configuration

Add to `.env`:

```bash
# Ad Resizer Settings
RESIZER_UPLOAD_DIR=/workspace/uploads
RESIZER_OUTPUT_DIR=/workspace/outputs
RESIZER_USE_AI_OUTFILL=true
RESIZER_CELERY_BROKER=redis://localhost:6379/0
RESIZER_CELERY_BACKEND=redis://localhost:6379/0

# AI Model Settings (Optional)
HF_TOKEN=your_huggingface_token
HF_HOME=/workspace/hf_cache
FLUX_MODEL_PATH=/workspace/flux_model
```

## Testing

Test the integration:

```bash
python test_ad_resizer.py
```

## License

Same as main IPOP platform.
