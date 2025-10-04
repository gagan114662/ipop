from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ContentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    BOTH = "both"


@dataclass
class PlatformSpec:
    """Platform specification for content resizing"""
    id: str
    name: str
    display_name: str
    dimensions: Tuple[int, int]  # (width, height)
    content_type: ContentType
    max_duration: Optional[int] = None  # seconds for video
    format_preference: List[str] = None  # preferred file formats
    quality: int = 85  # compression quality
    icon_url: Optional[str] = None
    
    def __post_init__(self):
        if self.format_preference is None:
            if self.content_type == ContentType.VIDEO:
                self.format_preference = ["mp4"]
            else:
                self.format_preference = ["jpg", "png"]


# Platform configurations
PLATFORM_CONFIGS: Dict[str, PlatformSpec] = {
    "tiktok_short": PlatformSpec(
        id="tiktok_short",
        name="tiktok",
        display_name="TikTok Short",
        dimensions=(1080, 1920),
        content_type=ContentType.VIDEO,
        max_duration=60,
        format_preference=["mp4"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
    ),
    
    "instagram_reel": PlatformSpec(
        id="instagram_reel",
        name="instagram",
        display_name="Instagram Reel",
        dimensions=(1080, 1920),
        content_type=ContentType.BOTH,
        max_duration=90,
        format_preference=["mp4", "jpg"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    
    "instagram_feed": PlatformSpec(
        id="instagram_feed",
        name="instagram",
        display_name="Instagram Feed",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    
    "instagram_story": PlatformSpec(
        id="instagram_story",
        name="instagram",
        display_name="Instagram Story",
        dimensions=(1080, 1920),
        content_type=ContentType.BOTH,
        max_duration=15,
        format_preference=["mp4", "jpg"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    
    "facebook_story": PlatformSpec(
        id="facebook_story",
        name="facebook",
        display_name="Facebook Story",
        dimensions=(1080, 1920),
        content_type=ContentType.BOTH,
        max_duration=20,
        format_preference=["mp4", "jpg"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
    ),
    
    "facebook_feed": PlatformSpec(
        id="facebook_feed",
        name="facebook",
        display_name="Facebook Feed",
        dimensions=(1200, 630),
        content_type=ContentType.BOTH,
        max_duration=240,
        format_preference=["mp4", "jpg"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
    ),
    
    "youtube_short": PlatformSpec(
        id="youtube_short",
        name="youtube",
        display_name="YouTube Short",
        dimensions=(1080, 1920),
        content_type=ContentType.VIDEO,
        max_duration=60,
        format_preference=["mp4"],
        quality=92,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    
    "youtube_bumper": PlatformSpec(
        id="youtube_bumper",
        name="youtube",
        display_name="YouTube Bumper",
        dimensions=(1920, 1080),
        content_type=ContentType.VIDEO,
        max_duration=6,
        format_preference=["mp4"],
        quality=95,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    
    "twitter_post": PlatformSpec(
        id="twitter_post",
        name="twitter",
        display_name="Twitter/X Post",
        dimensions=(1200, 675),
        content_type=ContentType.BOTH,
        max_duration=140,
        format_preference=["mp4", "jpg"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
    ),
    
    "linkedin_post": PlatformSpec(
        id="linkedin_post",
        name="linkedin",
        display_name="LinkedIn Post",
        dimensions=(1200, 627),
        content_type=ContentType.BOTH,
        max_duration=600,
        format_preference=["mp4", "jpg"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg"
    ),
    
    "google_display_medium": PlatformSpec(
        id="google_display_medium",
        name="google_ads",
        display_name="Google Display (Medium Rectangle)",
        dimensions=(300, 250),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    
    "google_display_banner": PlatformSpec(
        id="google_display_banner",
        name="google_ads",
        display_name="Google Display (Banner)",
        dimensions=(728, 90),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    )
}


def get_compatible_platforms(content_type: str) -> List[PlatformSpec]:
    """Get platforms compatible with content type"""
    compatible = []
    
    for platform in PLATFORM_CONFIGS.values():
        if (platform.content_type == ContentType.BOTH or 
            platform.content_type.value == content_type):
            compatible.append(platform)
    
    return compatible


def get_platform_by_id(platform_id: str) -> Optional[PlatformSpec]:
    """Get platform configuration by ID"""
    return PLATFORM_CONFIGS.get(platform_id)


def validate_platform_ids(platform_ids: List[str], content_type: str) -> List[str]:
    """Validate and filter platform IDs based on content type"""
    valid_platforms = []
    compatible_platforms = get_compatible_platforms(content_type)
    compatible_ids = {p.id for p in compatible_platforms}
    
    for platform_id in platform_ids:
        if platform_id in compatible_ids:
            valid_platforms.append(platform_id)
    
    return valid_platforms