# # app/utils/platform_configs.py
# from dataclasses import dataclass
# from typing import Dict, List, Optional, Tuple
# from enum import Enum


# class ContentType(str, Enum):
#     IMAGE = "image"
#     VIDEO = "video"
#     BOTH = "both"


# @dataclass
# class PlatformSpec:
#     """Platform specification for content resizing"""
#     id: str
#     name: str
#     display_name: str
#     dimensions: Tuple[int, int]  # (width, height)
#     content_type: ContentType
#     max_duration: Optional[int] = None  # seconds for video
#     format_preference: List[str] = None  # preferred file formats
#     quality: int = 85  # compression quality
#     icon_url: Optional[str] = None

#     def __post_init__(self):
#         if self.format_preference is None:
#             if self.content_type == ContentType.VIDEO:
#                 self.format_preference = ["mp4"]
#             else:
#                 self.format_preference = ["jpg", "png"]


# # Platform configurations
# PLATFORM_CONFIGS: Dict[str, PlatformSpec] = {
#     "tiktok_short": PlatformSpec(
#         id="tiktok_short",
#         name="tiktok",
#         display_name="TikTok Short",
#         dimensions=(1080, 1920),
#         content_type=ContentType.VIDEO,
#         max_duration=60,
#         format_preference=["mp4"],
#         quality=90,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
#     ),
#     "instagram_reel": PlatformSpec(
#         id="instagram_reel",
#         name="instagram",
#         display_name="Instagram Reel",
#         dimensions=(1080, 1920),
#         content_type=ContentType.BOTH,
#         max_duration=90,
#         format_preference=["mp4", "jpg"],
#         quality=88,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_feed": PlatformSpec(
#         id="instagram_feed",
#         name="instagram",
#         display_name="Instagram Feed",
#         dimensions=(1080, 1080),
#         content_type=ContentType.IMAGE,
#         format_preference=["jpg"],
#         quality=85,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_story": PlatformSpec(
#         id="instagram_story",
#         name="instagram",
#         display_name="Instagram Story",
#         dimensions=(1080, 1920),
#         content_type=ContentType.BOTH,
#         max_duration=15,
#         format_preference=["mp4", "jpg"],
#         quality=88,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),

#         "instagram_feed_image": PlatformSpec(
#         id="instagram_feed_image",
#         name="instagram",
#         display_name="Instagram Feed (1:1)",
#         dimensions=(1440, 1440),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_profile_feed_image": PlatformSpec(
#         id="instagram_profile_feed_image",
#         name="instagram",
#         display_name="Instagram Profile Feed (1.91:1 → 4:5)",
#         dimensions=(1080, 1080),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_story_image": PlatformSpec(
#         id="instagram_story_image",
#         name="instagram",
#         display_name="Instagram Story (9:16)",
#         dimensions=(1080, 1920),
#         content_type=ContentType.IMAGE,
#         quality=90,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_reel_image": PlatformSpec(
#         id="instagram_reel_image",
#         name="instagram",
#         display_name="Instagram Reel Cover (9:16)",
#         dimensions=(1080, 1920),
#         content_type=ContentType.IMAGE,
#         quality=90,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_carousel_feed_image": PlatformSpec(
#         id="instagram_carousel_feed_image",
#         name="instagram",
#         display_name="Instagram Carousel Feed (1:1)",
#         dimensions=(1080, 1080),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_carousel_story_image": PlatformSpec(
#         id="instagram_carousel_story_image",
#         name="instagram",
#         display_name="Instagram Carousel Story (9:16)",
#         dimensions=(1080, 1920),
#         content_type=ContentType.IMAGE,
#         quality=90,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_collection_feed_image": PlatformSpec(
#         id="instagram_collection_feed_image",
#         name="instagram",
#         display_name="Instagram Collection Feed (1:1)",
#         dimensions=(1080, 1080),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_collection_reel_image": PlatformSpec(
#         id="instagram_collection_reel_image",
#         name="instagram",
#         display_name="Instagram Collection Reel Cover (9:16)",
#         dimensions=(500, 888),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_explore_image": PlatformSpec(
#         id="instagram_explore_image",
#         name="instagram",
#         display_name="Instagram Explore (9:16)",
#         dimensions=(1080, 1920),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),




#     "facebook_story": PlatformSpec(
#         id="facebook_story",
#         name="facebook",
#         display_name="Facebook Story",
#         dimensions=(1080, 1920),
#         content_type=ContentType.BOTH,
#         max_duration=20,
#         format_preference=["mp4", "jpg"],
#         quality=85,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
#     ),
#     "facebook_feed": PlatformSpec(
#         id="facebook_feed",
#         name="facebook",
#         display_name="Facebook Feed",
#         dimensions=(1200, 630),
#         content_type=ContentType.BOTH,
#         max_duration=240,
#         format_preference=["mp4", "jpg"],
#         quality=85,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
#     ),
#     "youtube_short": PlatformSpec(
#         id="youtube_short",
#         name="youtube",
#         display_name="YouTube Short",
#         dimensions=(1080, 1920),
#         content_type=ContentType.VIDEO,
#         max_duration=60,
#         format_preference=["mp4"],
#         quality=92,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
#     ),
#     "youtube_bumper": PlatformSpec(
#         id="youtube_bumper",
#         name="youtube",
#         display_name="YouTube Bumper",
#         dimensions=(1920, 1080),
#         content_type=ContentType.VIDEO,
#         max_duration=6,
#         format_preference=["mp4"],
#         quality=95,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
#     ),
#     "twitter_post": PlatformSpec(
#         id="twitter_post",
#         name="twitter",
#         display_name="Twitter/X Post",
#         dimensions=(1200, 675),
#         content_type=ContentType.BOTH,
#         max_duration=140,
#         format_preference=["mp4", "jpg"],
#         quality=85,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
#     ),
#     "linkedin_post": PlatformSpec(
#         id="linkedin_post",
#         name="linkedin",
#         display_name="LinkedIn Post",
#         dimensions=(1200, 627),
#         content_type=ContentType.BOTH,
#         max_duration=600,
#         format_preference=["mp4", "jpg"],
#         quality=88,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg"
#     ),
#     "google_display_medium": PlatformSpec(
#         id="google_display_medium",
#         name="google_ads",
#         display_name="Google Display (Medium Rectangle)",
#         dimensions=(300, 250),
#         content_type=ContentType.IMAGE,
#         format_preference=["jpg", "png"],
#         quality=80,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
#     ),
#     "google_display_banner": PlatformSpec(
#         id="google_display_banner",
#         name="google_ads",
#         display_name="Google Display (Banner)",
#         dimensions=(728, 90),
#         content_type=ContentType.IMAGE,
#         format_preference=["jpg", "png"],
#         quality=80,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
#     )
# }


# def get_compatible_platforms(content_type: str) -> List[PlatformSpec]:
#     """Get platforms compatible with content type"""
#     compatible = []
#     for platform in PLATFORM_CONFIGS.values():
#         if (platform.content_type == ContentType.BOTH or 
#             platform.content_type.value == content_type):
#             compatible.append(platform)
#     return compatible


# def get_platform_by_id(platform_id: str) -> Optional[PlatformSpec]:
#     """Get platform configuration by ID"""
#     return PLATFORM_CONFIGS.get(platform_id)




# def validate_platform_ids(platform_ids: List[str], content_type: str) -> List[str]:
#     """Validate and filter platform IDs based on content type"""
#     from app.utils.platform_configs import PLATFORM_CONFIGS, ContentType

#     # 🔹 Auto-expand Instagram to all its image-based platform IDs
#     if "instagram" in platform_ids:
#         instagram_image_ids = [
#             pid for pid, p in PLATFORM_CONFIGS.items()
#             if p.name == "instagram" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
#         ]
#         platform_ids = instagram_image_ids

#     valid_platforms = []
#     compatible_platforms = get_compatible_platforms(content_type)
#     compatible_ids = {p.id for p in compatible_platforms}
#     for platform_id in platform_ids:
#         if platform_id in compatible_ids:
#             valid_platforms.append(platform_id)
#     return valid_platforms


# app/utils/platform_configs.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import cv2
from PIL import Image
import numpy as np
from pathlib import Path
from ultralytics import YOLO  # YOLOv8 lightweight detector


# =============================
# ENUM + DATA CLASS
# =============================

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


# =============================
# PLATFORM CONFIGURATIONS
# =============================

PLATFORM_CONFIGS: Dict[str, PlatformSpec] = {
    # --- Instagram Image Variants ---
    "instagram_feed_image": PlatformSpec(
        id="instagram_feed_image",
        name="instagram",
        display_name="Instagram Feed (1:1)",
        dimensions=(1440, 1440),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_profile_feed_image": PlatformSpec(
        id="instagram_profile_feed_image",
        name="instagram",
        display_name="Instagram Profile Feed (1.91:1 → 4:5)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_story_image": PlatformSpec(
        id="instagram_story_image",
        name="instagram",
        display_name="Instagram Story (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        quality=90,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_reel_image": PlatformSpec(
        id="instagram_reel_image",
        name="instagram",
        display_name="Instagram Reel Cover (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        quality=90,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_carousel_feed_image": PlatformSpec(
        id="instagram_carousel_feed_image",
        name="instagram",
        display_name="Instagram Carousel Feed (1:1)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_carousel_story_image": PlatformSpec(
        id="instagram_carousel_story_image",
        name="instagram",
        display_name="Instagram Carousel Story (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        quality=90,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_collection_feed_image": PlatformSpec(
        id="instagram_collection_feed_image",
        name="instagram",
        display_name="Instagram Collection Feed (1:1)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_collection_reel_image": PlatformSpec(
        id="instagram_collection_reel_image",
        name="instagram",
        display_name="Instagram Collection Reel Cover (9:16)",
        dimensions=(500, 888),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_explore_image": PlatformSpec(
        id="instagram_explore_image",
        name="instagram",
        display_name="Instagram Explore (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
        # --- Google Ads Display Image Variants ---
    "google_display_250x250": PlatformSpec(
        id="google_display_250x250",
        name="google_ads",
        display_name="Google Ads (250x250 – Square)",
        dimensions=(250, 250),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_200x200": PlatformSpec(
        id="google_display_200x200",
        name="google_ads",
        display_name="Google Ads (200x200 – Small Square)",
        dimensions=(200, 200),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_468x60": PlatformSpec(
        id="google_display_468x60",
        name="google_ads",
        display_name="Google Ads (468x60 – Banner)",
        dimensions=(468, 60),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_728x90": PlatformSpec(
        id="google_display_728x90",
        name="google_ads",
        display_name="Google Ads (728x90 – Leaderboard)",
        dimensions=(728, 90),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_300x250": PlatformSpec(
        id="google_display_300x250",
        name="google_ads",
        display_name="Google Ads (300x250 – Medium Rectangle)",
        dimensions=(300, 250),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_336x280": PlatformSpec(
        id="google_display_336x280",
        name="google_ads",
        display_name="Google Ads (336x280 – Large Rectangle)",
        dimensions=(336, 280),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_120x600": PlatformSpec(
        id="google_display_120x600",
        name="google_ads",
        display_name="Google Ads (120x600 – Skyscraper)",
        dimensions=(120, 600),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_160x600": PlatformSpec(
        id="google_display_160x600",
        name="google_ads",
        display_name="Google Ads (160x600 – Wide Skyscraper)",
        dimensions=(160, 600),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_300x600": PlatformSpec(
        id="google_display_300x600",
        name="google_ads",
        display_name="Google Ads (300x600 – Half Page)",
        dimensions=(300, 600),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_970x90": PlatformSpec(
        id="google_display_970x90",
        name="google_ads",
        display_name="Google Ads (970x90 – Large Leaderboard)",
        dimensions=(970, 90),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_300x50": PlatformSpec(
        id="google_display_300x50",
        name="google_ads",
        display_name="Google Ads (300x50 – Mobile Banner)",
        dimensions=(300, 50),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_320x50": PlatformSpec(
        id="google_display_320x50",
        name="google_ads",
        display_name="Google Ads (320x50 – Mobile Banner)",
        dimensions=(320, 50),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_320x100": PlatformSpec(
        id="google_display_320x100",
        name="google_ads",
        display_name="Google Ads (320x100 – Large Mobile Banner)",
        dimensions=(320, 100),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_330x200": PlatformSpec(
        id="google_display_330x200",
        name="google_ads",
        display_name="Google Ads (330x200 – Responsive Mobile)",
        dimensions=(330, 200),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),

    # --- YouTube Image / Banner / Ad Sizes (IMAGE ONLY) ---

    "youtube_channel_banner": PlatformSpec(
        id="youtube_channel_banner",
        name="youtube",
        display_name="YouTube Channel Banner",
        dimensions=(2560, 1440),  # Recommended upload size
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_channel_banner_safe": PlatformSpec(
        id="youtube_channel_banner_safe",
        name="youtube",
        display_name="YouTube Channel Banner (Safe Area)",
        dimensions=(1546, 423),  # Safe zone visible on all devices
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_video_thumbnail": PlatformSpec(
        id="youtube_video_thumbnail",
        name="youtube",
        display_name="YouTube Video Thumbnail",
        dimensions=(1280, 720),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=92,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_video_thumbnail_min": PlatformSpec(
        id="youtube_video_thumbnail_min",
        name="youtube",
        display_name="YouTube Thumbnail (Minimum)",
        dimensions=(640, 360),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_300x250": PlatformSpec(
        id="youtube_display_ad_300x250",
        name="youtube",
        display_name="YouTube Display Ad (Medium Rectangle)",
        dimensions=(300, 250),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_300x60": PlatformSpec(
        id="youtube_display_ad_300x60",
        name="youtube",
        display_name="YouTube Display Ad (Banner)",
        dimensions=(300, 60),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_1200x628": PlatformSpec(
        id="youtube_display_ad_1200x628",
        name="youtube",
        display_name="YouTube Discovery Ad (Landscape)",
        dimensions=(1200, 628),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_1080x1080": PlatformSpec(
        id="youtube_display_ad_1080x1080",
        name="youtube",
        display_name="YouTube Square Ad",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_1080x1920": PlatformSpec(
        id="youtube_display_ad_1080x1920",
        name="youtube",
        display_name="YouTube Vertical Ad (Stories/Shorts-style)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),

    # --- TikTok Image / Ad Sizes ---
    "tiktok_feed_ad_9_16": PlatformSpec(
        id="tiktok_feed_ad_9_16",
        name="tiktok",
        display_name="TikTok Feed Ad (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
    ),
    "tiktok_feed_ad_1_1": PlatformSpec(
        id="tiktok_feed_ad_1_1",
        name="tiktok",
        display_name="TikTok Feed Ad (Square)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
    ),
    "tiktok_feed_ad_16_9": PlatformSpec(
        id="tiktok_feed_ad_16_9",
        name="tiktok",
        display_name="TikTok Feed Ad (16:9)",
        dimensions=(1920, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
    ),
    "tiktok_profile_banner": PlatformSpec(
        id="tiktok_profile_banner",
        name="tiktok",
        display_name="TikTok Profile Banner (Cover)",
        dimensions=(1125, 633),  # Recommended by TikTok for profile header
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
    ),
    # --- Twitter/X Image / Ad Sizes ---
    "twitter_feed_image_16_9": PlatformSpec(
        id="twitter_feed_image_16_9",
        name="twitter",
        display_name="Twitter Feed Image (Landscape)",
        dimensions=(1200, 675),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
    ),
    "twitter_feed_image_1_1": PlatformSpec(
        id="twitter_feed_image_1_1",
        name="twitter",
        display_name="Twitter Feed Image (Square)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
    ),
    "twitter_feed_image_9_16": PlatformSpec(
        id="twitter_feed_image_9_16",
        name="twitter",
        display_name="Twitter Feed Image (Portrait)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
    ),
    "twitter_ad_image_1200x628": PlatformSpec(
        id="twitter_ad_image_1200x628",
        name="twitter",
        display_name="Twitter Website Card / Ad",
        dimensions=(1200, 628),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
    ),


}


# =============================
# PLATFORM HELPERS
# =============================

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


# def validate_platform_ids(platform_ids: List[str], content_type: str) -> List[str]:
#     """Validate and filter platform IDs based on content type"""
#     expanded_ids = []

#     for pid in platform_ids:
#         if pid.lower() == "instagram":
#             expanded_ids.extend([
#                 key for key, p in PLATFORM_CONFIGS.items()
#                 if p.name == "instagram" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
#             ])
#         elif pid.lower() in ["google", "google_ads"]:
#             expanded_ids.extend([
#                 key for key, p in PLATFORM_CONFIGS.items()
#                 if p.name == "google_ads" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
#             ])
#         else:
#             expanded_ids.append(pid)

#     valid_platforms = []
#     compatible_platforms = get_compatible_platforms(content_type)
#     compatible_ids = {p.id for p in compatible_platforms}
#     for platform_id in expanded_ids:
#         if platform_id in compatible_ids:
#             valid_platforms.append(platform_id)

#     return valid_platforms


def validate_platform_ids(platform_ids: List[str], content_type: str) -> List[str]:
    """Validate and filter platform IDs based on content type"""
    expanded_ids = []

    for pid in platform_ids:
        if pid.lower() == "instagram":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "instagram" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() in ["google", "google_ads"]:
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "google_ads" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() == "youtube":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "youtube" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() == "tiktok":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "tiktok" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() in ["twitter", "x"]:
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "twitter" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        else:
            expanded_ids.append(pid)

    valid_platforms = []
    compatible_platforms = get_compatible_platforms(content_type)
    compatible_ids = {p.id for p in compatible_platforms}
    for platform_id in expanded_ids:
        if platform_id in compatible_ids:
            valid_platforms.append(platform_id)

    return valid_platforms


# =============================
# YOLO + IMAGE RESIZING LOGIC
# =============================

# Load YOLOv8 (downloads on first run)
yolo_model = YOLO("yolov8n.pt")


def detect_main_subject_yolo(image: np.ndarray) -> Optional[tuple]:
    """Detect main subject using YOLOv8"""
    results = yolo_model.predict(source=image, verbose=False)
    if not results or not results[0].boxes:
        return None

    boxes = results[0].boxes.xyxy.cpu().numpy()
    areas = [(x2 - x1) * (y2 - y1) for (x1, y1, x2, y2) in boxes]
    best_idx = np.argmax(areas)
    x1, y1, x2, y2 = boxes[best_idx]
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)
    w = int(x2 - x1)
    h = int(y2 - y1)
    return center_x, center_y, w, h




def intelligent_resize_with_padding(
    image: np.ndarray,
    target_width: int,
    target_height: int,
    center: tuple = None
) -> np.ndarray:
    """
    Resize image to fit target dimensions while keeping main subject centered.
    Uses padding (letterbox/pillarbox) if aspect ratios differ.
    """
    img_height, img_width = image.shape[:2]
    target_aspect = target_width / target_height
    img_aspect = img_width / img_height

    # Calculate scaling to fit within target
    scale = min(target_width / img_width, target_height / img_height)
    new_w = int(img_width * scale)
    new_h = int(img_height * scale)

    # Create blank canvas (black background)
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)

    # Calculate position to place resized image
    if center:
        # Try to center the subject
        cx, cy = center
        # Scale subject position
        scaled_cx = int(cx * scale)
        scaled_cy = int(cy * scale)

        # Place image so subject is centered
        x_offset = max(0, target_width // 2 - scaled_cx)
        y_offset = max(0, target_height // 2 - scaled_cy)

        # Ensure we don't go out of bounds
        x_offset = min(x_offset, target_width - new_w)
        y_offset = min(y_offset, target_height - new_h)
    else:
        # Center the whole image
        x_offset = (target_width - new_w) // 2
        y_offset = (target_height - new_h) // 2

    # Resize image
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Paste onto canvas
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

    return canvas




def resize_for_platforms(
    input_image_path: str,
    platform_ids: List[str],
    content_type: str = "image",
    output_dir: str = "outputs/"
) -> Dict[str, str]:
    """Resize image intelligently for all valid platforms using YOLO subject detection."""
    valid_ids = validate_platform_ids(platform_ids, content_type)
    if not valid_ids:
        raise ValueError("No valid platforms for this content type.")

    image = cv2.imread(input_image_path)
    if image is None:
        raise ValueError(f"Unable to load image: {input_image_path}")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_paths = {}

    # Detect main subject
    subject_center = detect_main_subject_yolo(image)
    center_xy = (subject_center[0], subject_center[1]) if subject_center else None


    for pid in valid_ids:
        spec = get_platform_by_id(pid)
        if not spec:
            continue

        # ✅ Use padding-aware resize
        resized = intelligent_resize_with_padding(
            image.copy(), 
            spec.dimensions[0], 
            spec.dimensions[1], 
            center_xy  # This keeps subject centered
        )

        resized_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(resized_rgb)

        format_pref = spec.format_preference[0]
        output_filename = f"{Path(input_image_path).stem}_{spec.id}.{format_pref}"
        output_path = f"{output_dir}/{output_filename}"
        pil_img.save(output_path, format=format_pref.upper(), quality=spec.quality)
        output_paths[pid] = output_path


    return output_paths
